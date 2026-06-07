# Architecture - Smart Test

Documentación técnica de Smart Test.

---

## 🏗️ Visión General

```
User (CLI/Web/API)
    ↓
┌─────────────────────────────────────┐
│      Smart Test Agent               │
│  (Orchestración de testing)         │
└─────────────────────────────────────┘
    ↓
    ├─→ Model Selector (5 niveles)
    │   ├─→ Speed mode
    │   ├─→ Balanced mode
    │   └─→ Quality mode
    │
    ├─→ Page Analysis
    │   ├─→ HTML parsing
    │   └─→ Screenshot analysis (Llava)
    │
    ├─→ Test Plan Generation
    │   └─→ Mistral reasoning
    │
    ├─→ Action Execution
    │   └─→ Playwright browser
    │
    └─→ Results & Learning
        ├─→ JSON reports
        ├─→ RAG storage (ChromaDB)
        └─→ Advanced RAG (Clustering)
```

---

## 📦 Componentes Principales

### 1. **agent.py** - Core Engine
```
SmartTestAgent
├── analyze_page(html, screenshot)
├── generate_test_plan(analysis)
├── generate_actions(plan)
├── execute_actions(actions)
├── final_validation(results)
└── test_web(url, objectives)
```

**Responsabilidades:**
- Orquestar todo el flujo
- Comunicar con Ollama
- Ejecutar Playwright
- Generar reportes

---

### 2. **model_selector.py** - Model Management
```
ModelSelector
├── select(task) → model_name
├── set_model(task, model)
├── get_llm(task) → OllamaLLM
├── info() → config dict
└── print_info() → table
```

**Niveles:**
- Level 1: Selector simple (3 presets)
- Level 2: CLI interactivo
- Level 3: Auto-detection
- Level 4: Benchmarking
- Level 5: Learning

---

### 3. **model_detector.py** - Auto-Detection
```
ModelDetector
├── detect_models() → List[str]
├── suggest_optimal_config() → Dict
├── download_missing_models()
└── suggest_setup()
```

**Características:**
- Detecta modelos instalados
- Sugiere configuración óptima
- Descarga faltantes automáticamente
- No falla si faltan modelos

---

### 4. **model_benchmarker.py** - Performance Testing
```
ModelBenchmarker
├── benchmark_model(name) → metrics
├── benchmark_models(list) → results
├── show_results()
├── compare()
├── recommend()
└── save_results(filename)
```

**Métricas:**
- Tiempo de ejecución
- Tokens generados
- Tokens por segundo
- Tasa de éxito

---

### 5. **model_learner.py** - Learning System
```
ModelLearner
├── record_result(url, model, task, duration, success)
├── recommend_model(url, task, optimize)
├── get_stats() → Dict
└── print_stats()
```

**Learning:**
- Histórico por dominio
- Recomendaciones automáticas
- Predicción de mejor modelo

---

### 6. **advanced_rag.py** - Inteligencia Avanzada
```
AdvancedRAG
├── cluster_domains(n_clusters)
├── predict_defects(url, objective)
├── transfer_learning(source, target)
└── get_recommendations(url, objective)
```

**Capacidades:**
- Clustering K-means
- Predicción de defectos
- Transfer learning entre dominios
- Recomendaciones inteligentes

---

### 7. **smart_test_ui.py** - Web Interface
```
Streamlit App
├── Sidebar
│   ├── Mode selector
│   ├── Model viewer
│   └── Learning stats
└── Main
    ├── URL + Objective input
    ├── Execute/Demo/History buttons
    └── Results + Historial
```

**Características:**
- Interfaz visual bonita
- Demo mode sin Ollama
- Historial persistente
- Real-time progress

---

### 8. **api.py** - REST Interface
```
FastAPI App
├── POST /test → execute test
├── GET /results → get results
├── GET /stats → statistics
├── GET /models → available models
└── GET /health → health check
```

**Endpoints:**
- 6 endpoints principales
- Swagger UI documentation
- Persistent storage
- Statistics aggregation

---

## 🔄 Flujos Principales

### Flujo 1: Testing Normal

```
User Input (URL + Objective)
    ↓
SmartTestAgent.test_web()
    ↓
1. Analyze Page
   ├─ agent.py: analyze_page()
   ├─ Ollama: Extract elements
   └─ Screenshot analysis
    ↓
2. Generate Plan
   ├─ agent.py: generate_test_plan()
   ├─ Model Selector: Choose model
   └─ Mistral: Reasoning
    ↓
3. Generate Actions
   ├─ agent.py: generate_actions()
   ├─ Identify locators
   └─ Create action sequence
    ↓
4. Execute
   ├─ agent.py: execute_actions()
   ├─ Playwright: Browser automation
   └─ Real-time progress
    ↓
5. Validate
   ├─ agent.py: final_validation()
   ├─ Llava: Screenshot comparison
   └─ Results compilation
    ↓
Report + Storage
```

### Flujo 2: Learning System

```
Test Execution
    ↓
Record Result
├─ model_learner.py: record_result()
└─ Store in model_learning.json
    ↓
Next Test (Similar Domain)
    ↓
recommend_model()
├─ Look up domain history
└─ Return best model
    ↓
Improved Execution
```

### Flujo 3: Advanced RAG

```
New Test (URL + Objective)
    ↓
Advanced RAG Analysis
├─ cluster_domains()
│  └─ Find similar domains
├─ predict_defects()
│  └─ Risk assessment
└─ transfer_learning()
   └─ Apply patterns
    ↓
Recommendations
├─ Probable errors
├─ Suggested checks
└─ Expected success rate
    ↓
Optimized Test Plan
```

---

## 💾 Almacenamiento

### model_learning.json
```json
{
  "by_domain": {
    "github.com": {
      "mistral": {
        "runs": 10,
        "successes": 9,
        "total_time": 52.5
      }
    }
  },
  "total_runs": 10
}
```

### advanced_rag_data.json
```json
{
  "domain_clusters": {
    "cluster_0": ["github.com", "gitlab.com"],
    "cluster_1": ["amazon.com", "ebay.com"]
  },
  "defect_predictions": {...},
  "transfer_learning": {...}
}
```

### api_results.json
```json
[
  {
    "url": "https://github.com",
    "objective": "Testear repo",
    "status": "success",
    "pass_rate": 95.5,
    "timestamp": "2026-06-07T20:00:00"
  }
]
```

---

## 🔌 Integraciones

### Ollama (IA Local)
- Mistral: Razonamiento
- Llava: Visión
- Neural-Chat: Análisis rápido
- Orca-mini: Velocidad

### Playwright
- Browser automation
- Cross-browser support
- Screenshot capture
- Network interception

### Chromadb
- Vector storage
- Semantic search
- Embeddings locales
- Persistent storage

### Streamlit
- Web UI
- Real-time updates
- Data visualization
- Demo mode

### FastAPI
- REST endpoints
- Swagger documentation
- Request validation
- Background tasks

---

## 🎯 Decision Records

### Decision 1: Local vs Cloud IA
**Decision:** Local with Ollama

**Rationale:**
- Zero API costs
- Privacy compliance
- Offline capability
- Full control

**Trade-offs:**
- Slower than Claude API
- Requires local setup
- Hardware dependent

---

### Decision 2: 5 Model Levels
**Decision:** 5 levels from basic to expert

**Rationale:**
- Accessible to everyone
- Progressive complexity
- Clear learning path
- Flexible for use cases

**Trade-offs:**
- Complex codebase
- Many configuration options
- Steeper learning curve

---

### Decision 3: RAG over Simple Storage
**Decision:** Advanced RAG with clustering

**Rationale:**
- Intelligent recommendations
- Domain-specific learning
- Transfer learning capability
- Predictive power

**Trade-offs:**
- More complex
- Requires ML knowledge
- Heavier dependencies

---

## 📈 Scalability

### Current Capacity
- Sequential testing
- Single instance
- Local storage
- ~100 tests/day

### Future Scaling
- **Horizontal:** Multiple workers
- **Vertical:** Larger models
- **Distributed:** Cloud deployment
- **Database:** PostgreSQL instead of JSON

---

## 🔐 Security

### Current Implementation
- Local execution only
- No external APIs
- File-based storage
- No authentication

### Security Considerations
- Secure token storage (for API)
- Input validation (URL, objective)
- Rate limiting (future)
- HTTPS only (production)

---

## 🚀 Performance Optimization

### Bottlenecks
1. Ollama inference (5-10s)
2. Playwright page load (2-5s)
3. Screenshot analysis (2-3s)

### Optimization Strategies
1. Model quantization
2. Caching pages
3. Parallel execution
4. Request batching

---

## 📊 Metrics & Monitoring

### Current
- Pass/fail rate
- Execution duration
- Model performance
- Domain statistics

### Future
- Error categorization
- Bottleneck analysis
- Resource usage
- Cost tracking

---

## 🔄 Extension Points

### 1. Custom Models
```python
selector.set_model("analysis", "custom-model")
```

### 2. Custom Actions
```python
agent.register_action("custom_action", handler)
```

### 3. Custom Storage
```python
class CustomStorage(BaseStorage):
    def store(self, result): ...
```

### 4. Custom Validators
```python
agent.register_validator("custom", validator_fn)
```

---

## 📚 References

- [Model Selector](MODEL_SELECTOR.md)
- [Web UI](WEB_UI.md)
- [REST API](API.md)
- [RAG](RAG.md)
- [Cucumber/BDD](CUCUMBER.md)
- [Grafana](GRAFANA.md)

---

**Smart Test Architecture = Modular, Extensible, Local-First**
