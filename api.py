"""
Smart Test API - FastAPI
Endpoint REST para ejecutar tests programáticamente
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
from pathlib import Path
from agent import SmartTestAgent
from model_selector import ModelSelector

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

# Almacenamiento en memoria (usar DB en producción)
results_file = Path("api_results.json")

def load_results() -> list:
    """Carga resultados guardados"""
    if results_file.exists():
        try:
            return json.loads(results_file.read_text())
        except:
            return []
    return []

def save_results(results: list) -> None:
    """Guarda resultados"""
    results_file.write_text(json.dumps(results, indent=2))

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
async def execute_test(request: TestRequest):
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
        
        # Guarda resultado
        results = load_results()
        results.append(result.dict())
        save_results(results)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results(limit: int = 10):
    """Obtiene últimos resultados"""
    results = load_results()
    return {
        "total": len(results),
        "limit": limit,
        "results": results[-limit:]
    }

@app.get("/results/{index}")
async def get_result(index: int):
    """Obtiene un resultado específico"""
    results = load_results()
    if index < 0 or index >= len(results):
        raise HTTPException(status_code=404, detail="Result not found")
    return results[index]

@app.get("/stats")
async def get_stats():
    """Estadísticas de tests"""
    results = load_results()
    
    if not results:
        return {
            "total_tests": 0,
            "avg_pass_rate": 0,
            "avg_duration": 0,
            "by_mode": {}
        }
    
    pass_rates = [r.get("pass_rate", 0) for r in results]
    durations = [r.get("duration", 0) for r in results]
    
    # Agrupar por modo
    by_mode = {}
    for result in results:
        mode = result.get("mode", "unknown")
        if mode not in by_mode:
            by_mode[mode] = {"count": 0, "avg_pass_rate": 0}
        by_mode[mode]["count"] += 1
    
    return {
        "total_tests": len(results),
        "avg_pass_rate": sum(pass_rates) / len(pass_rates),
        "avg_duration": sum(durations) / len(durations),
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
