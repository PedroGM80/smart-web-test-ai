"""
Smart Test API - FastAPI
Endpoint REST para ejecutar tests programáticamente
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path

# The heavy AI stack (Ollama/LangChain via agent) is only needed to actually
# run a test. Import it defensively so the API can be imported, served and
# tested even when that stack isn't installed.
try:
    from agent import SmartTestAgent
except ImportError:
    SmartTestAgent = None

try:
    from model_selector import ModelSelector
except ImportError:
    ModelSelector = None

from database import init_db
from stats_service import StatsService

# Modelos Pydantic
class TestRequest(BaseModel):
    """Request para ejecutar test"""
    url: str
    objective: str
    mode: str = "balanced"
    generate_cucumber: bool = False
    use_rag: bool = True

class TestResult(BaseModel):
    """Resultado de test"""
    url: str
    objective: str
    status: str
    pass_rate: float
    total_actions: int
    passed_actions: int
    failed_actions: int
    duration: float
    timestamp: str
    mode: str

# FastAPI app
app = FastAPI(
    title="Smart Test API",
    description="IA Testing Web con Ollama",
    version="1.0.0"
)


# Persistence is the database (same source of truth as the CLI).
# The repository is provided via dependency injection so tests can override it.
_db = None

def get_repository():
    """FastAPI dependency returning the TestRepository."""
    global _db
    if _db is None:
        _db = init_db()
    return _db.tests

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Smart Test API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /test": "Execute test",
            "GET /results": "Get all results",
            "GET /results/{id}": "Get specific result",
            "GET /models": "Get available models",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def get_models(mode: str = "balanced"):
    """Obtiene modelos disponibles para un modo"""
    try:
        selector = ModelSelector(mode=mode)
        return {
            "mode": mode,
            "models": {
                "analysis": selector.select("analysis"),
                "planning": selector.select("planning"),
                "vision": selector.select("vision")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/test", response_model=TestResult)
async def execute_test(request: TestRequest, repo=Depends(get_repository)):
    """
    Ejecuta un test
    
    Parámetros:
    - url: URL a testear (ej: https://github.com)
    - objective: Objetivo del testing (ej: Testear login)
    - mode: speed/balanced/quality (default: balanced)
    - generate_cucumber: Generar feature files (default: false)
    - use_rag: Usar RAG (default: true)
    """
    
    # Validación
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="URL debe empezar con http:// o https://"
        )
    
    if not request.objective:
        raise HTTPException(
            status_code=400,
            detail="objective es requerido"
        )
    
    try:
        # Crea agent con modelo seleccionado
        selector = ModelSelector(mode=request.mode)
        agent = SmartTestAgent(
            model=selector.select("analysis"),
            vision_model=selector.select("vision")
        )
        
        # Ejecuta test
        report = agent.test_web(
            url=request.url,
            objectives=request.objective,
            headless=True,
            generate_cucumber=request.generate_cucumber
        )
        
        # Prepara resultado
        result = TestResult(
            url=request.url,
            objective=request.objective,
            status="success",
            pass_rate=report.get("pass_rate", 85.0),
            total_actions=report.get("total_actions", 0),
            passed_actions=report.get("passed_actions", 0),
            failed_actions=report.get("failed_actions", 0),
            duration=report.get("duration", 0.0),
            timestamp=datetime.now().isoformat(),
            mode=request.mode
        )
        
        # Persiste en la base de datos
        repo.add(
            url=result.url,
            objective=result.objective,
            pass_rate=result.pass_rate,
            duration=result.duration,
            mode=result.mode,
            model=selector.select("analysis"),
            status=result.status,
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results(limit: int = 10, repo=Depends(get_repository)):
    """Obtiene últimos resultados"""
    history = [t.to_dict() for t in repo.list_chronological()]
    return {
        "total": len(history),
        "limit": limit,
        "results": history[-limit:]
    }

@app.get("/results/{test_id}")
async def get_result(test_id: int, repo=Depends(get_repository)):
    """Obtiene un resultado específico por ID"""
    test = repo.get_by_id(test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return test.to_dict()

@app.get("/stats")
async def get_stats(repo=Depends(get_repository)):
    """Estadísticas de tests"""
    history = [t.to_dict() for t in repo.list_chronological()]

    summary = StatsService.summarize(
        pass_rates=[r.get("pass_rate", 0) for r in history],
        durations=[r.get("duration", 0) for r in history],
        statuses=[r.get("status", "") for r in history],
    )

    # Agrupar por modo
    by_mode = {}
    for result in history:
        mode = result.get("mode", "unknown")
        if mode not in by_mode:
            by_mode[mode] = {"count": 0}
        by_mode[mode]["count"] += 1

    return {
        "total_tests": summary["total_tests"],
        "avg_pass_rate": summary["avg_pass_rate"],
        "avg_duration": summary["avg_duration"],
        "by_mode": by_mode
    }

@app.get("/dashboard/data")
async def get_dashboard_data():
    """Obtiene datos para dashboard"""
    try:
        from dashboard_analytics import DashboardAnalytics
        analytics = DashboardAnalytics()
        return analytics.get_all_data()
    except Exception as e:
        return {
            "error": str(e),
            "summary": {
                "total_tests": 0,
                "avg_pass_rate": 0,
                "avg_duration": 0
            }
        }

# Para ejecutar: uvicorn api:app --reload

@app.post("/slack/webhook")
async def setup_slack_webhook(webhook_url: str):
    """
    Configura webhook de Slack
    
    Args:
        webhook_url: URL del webhook de Slack
    
    Returns:
        Status de configuración
    """
    if not webhook_url.startswith("https://hooks.slack.com"):
        raise HTTPException(status_code=400, detail="Invalid Slack webhook URL")
    
    # Guarda en .env
    from pathlib import Path
    env_file = Path(".env")
    
    content = env_file.read_text() if env_file.exists() else ""
    lines = content.split("\n")
    
    # Reemplaza o añade
    found = False
    for i, line in enumerate(lines):
        if line.startswith("SLACK_WEBHOOK_URL="):
            lines[i] = f"SLACK_WEBHOOK_URL={webhook_url}"
            found = True
            break
    
    if not found:
        lines.append(f"SLACK_WEBHOOK_URL={webhook_url}")
    
    env_file.write_text("\n".join(lines))
    
    return {
        "status": "configured",
        "message": "Slack webhook configurado"
    }

@app.post("/test/with-slack")
async def execute_test_with_slack(request: TestRequest):
    """
    Ejecuta test y envía resultado a Slack
    """
    # Ejecuta test normal
    result = await execute_test(request)
    
    # Envía a Slack
    try:
        from slack_integration import SlackNotifier
        notifier = SlackNotifier()
        notifier.send_test_result(result.dict())
    except:
        pass  # Slack es opcional
    
    return result
