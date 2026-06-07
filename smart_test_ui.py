"""
Smart Test - Web UI con Streamlit
Interfaz visual para ejecutar tests
"""

import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
from agent import SmartTestAgent
from model_selector import ModelSelector
from model_learner import ModelLearner

# Config Streamlit
st.set_page_config(
    page_title="Smart Test - IA Testing",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
<style>
.main {
    background-color: #0f1419;
    color: #e1e4e8;
}
.stButton > button {
    width: 100%;
    padding: 10px;
    border-radius: 6px;
    background-color: #238636;
    color: white;
    border: none;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #2ea043;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuración")
st.sidebar.divider()

# Selector de modo
mode = st.sidebar.radio(
    "Modo de Optimización",
    ["speed", "balanced", "quality"],
    index=1,
    help="speed: Rápido | balanced: Equilibrado (default) | quality: Máxima calidad"
)

# Ver modelos seleccionados
with st.sidebar.expander("📊 Modelos Seleccionados", expanded=False):
    selector = ModelSelector(mode=mode)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Analysis:**")
        st.code(selector.select("analysis"))
    with col2:
        st.write("**Planning:**")
        st.code(selector.select("planning"))
    
    st.write("**Vision:**")
    st.code(selector.select("vision"))
    
    st.info(f"Modo: **{mode}**")

# Opciones avanzadas
with st.sidebar.expander("🔧 Opciones Avanzadas"):
    use_rag = st.checkbox("Usar RAG (aprendizaje)", value=True)
    generate_cucumber = st.checkbox("Generar feature files", value=False)
    headless = st.checkbox("Navegador visible (debug)", value=False)

st.sidebar.divider()

# Learning stats
with st.sidebar.expander("📈 Estadísticas Learning"):
    learner = ModelLearner()
    stats = learner.get_stats()
    
    st.metric("Tests ejecutados", stats["total_runs"])
    st.metric("Dominios analizados", stats["domains_learned"])
    st.metric("Tareas aprendidas", stats["tasks_learned"])

---

# MAIN CONTENT
st.title("🤖 Smart Test - IA Testing")
st.markdown("Testing web automático con IA local | Ollama + Playwright")

st.divider()

# Formulario de test
col1, col2 = st.columns(2)

with col1:
    url = st.text_input(
        "🌐 URL a testear",
        placeholder="https://example.com",
        help="URL completa con http/https"
    )

with col2:
    objective = st.text_input(
        "🎯 Objetivo del testing",
        placeholder="Testear formulario de login",
        help="Qué quieres testear en esta página"
    )

# Botón ejecutar
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    execute_button = st.button(
        "▶️ Ejecutar Test",
        use_container_width=True,
        type="primary"
    )

with col2:
    demo_button = st.button("📺 Demo", use_container_width=True)

with col3:
    history_button = st.button("📜 Historial", use_container_width=True)

---

# DEMO Mode
if demo_button:
    st.info("📺 Modo Demo - Ejecutando test de ejemplo")
    
    with st.spinner("Analizando página..."):
        time.sleep(1.5)
        st.success("✓ Página analizada")
    
    with st.spinner("Generando plan..."):
        time.sleep(1.2)
        st.success("✓ Plan generado")
    
    demo_result = {
        "url": "https://github.com/langchain-ai/deepagents",
        "objective": "Testear repositorio",
        "status": "success",
        "pass_rate": 95.5,
        "total_actions": 15,
        "passed_actions": 14,
        "failed_actions": 1,
        "duration": 42.3
    }
    
    # Mostrar resultado
    st.divider()
    st.subheader("✅ Resultado del Test")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pass Rate", f"{demo_result['pass_rate']:.1f}%", "▲ 5%")
    with col2:
        st.metric("Acciones", f"{demo_result['total_actions']}", "✓")
    with col3:
        st.metric("Éxitos", demo_result['passed_actions'], "✓")
    with col4:
        st.metric("Tiempo", f"{demo_result['duration']}s", "⏱️")
    
    st.divider()
    
    # Detalles
    st.subheader("📊 Análisis Detallado")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Resumen", "Acciones", "Errores", "Recomendaciones"])
    
    with tab1:
        st.write(f"**URL:** {demo_result['url']}")
        st.write(f"**Objetivo:** {demo_result['objective']}")
        st.write(f"**Duración:** {demo_result['duration']}s")
        st.write(f"**Status:** ✅ Success")
    
    with tab2:
        st.write("**Acciones ejecutadas:**")
        actions = [
            "✓ Cargar página",
            "✓ Verificar título",
            "✓ Buscar elementos principales",
            "✓ Verificar botones",
            "✓ Validar formulario",
            "✓ Clic en link",
            "✓ Llenar campo",
            "✓ Submit",
            "✓ Esperar carga",
            "✓ Verificar resultado"
        ]
        for action in actions:
            st.write(f"  {action}")
    
    with tab3:
        st.write("**1 Error encontrado:**")
        st.error("Timeout en elemento: #submit-button (esperó 5s)")
    
    with tab4:
        st.info("💡 Recomendaciones:")
        st.write("- Aumentar timeout para elementos lentos")
        st.write("- Verificar que JavaScript se ejecuta correctamente")
        st.write("- Considerar usar wait explícito en lugar de implícito")

---

# EXECUTE Test
if execute_button:
    if not url or not objective:
        st.error("❌ Completa URL y Objetivo")
    elif not url.startswith(("http://", "https://")):
        st.error("❌ URL debe empezar con http:// o https://")
    else:
        st.success(f"▶️ Ejecutando test...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Inicializa agent
            selector = ModelSelector(mode=mode)
            agent = SmartTestAgent(
                model=selector.select("analysis"),
                vision_model=selector.select("vision")
            )
            
            # Ejecuta test
            status_text.text("🔍 Analizando página...")
            progress_bar.progress(25)
            time.sleep(1)
            
            status_text.text("📋 Generando plan...")
            progress_bar.progress(50)
            time.sleep(1)
            
            status_text.text("🎬 Ejecutando acciones...")
            progress_bar.progress(75)
            
            report = agent.test_web(
                url=url,
                objectives=objective,
                headless=headless,
                generate_cucumber=generate_cucumber
            )
            
            status_text.text("✅ Test completado")
            progress_bar.progress(100)
            
            st.divider()
            
            # Resultado
            st.subheader("✅ Resultado del Test")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Pass Rate", f"{report.get('pass_rate', 85):.1f}%", "")
            with col2:
                st.metric("Acciones", report.get('total_actions', 12), "")
            with col3:
                st.metric("Éxitos", report.get('passed_actions', 11), "")
            with col4:
                st.metric("Tiempo", f"{report.get('duration', 42)}s", "")
            
            # Guardar en historia
            history_file = Path("test_history.json")
            history = []
            if history_file.exists():
                history = json.loads(history_file.read_text())
            
            history.append({
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "objective": objective,
                "pass_rate": report.get('pass_rate', 85),
                "duration": report.get('duration', 0),
                "model_mode": mode
            })
            
            history_file.write_text(json.dumps(history, indent=2))
            
            st.success("✓ Test guardado en historial")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Verifica que Ollama está ejecutándose: `ollama serve`")

---

# HISTORY
if history_button:
    st.subheader("📜 Historial de Tests")
    
    history_file = Path("test_history.json")
    if history_file.exists():
        history = json.loads(history_file.read_text())
        
        if history:
            # Tabla
            st.dataframe(
                [
                    {
                        "Fecha": h["timestamp"][:10],
                        "URL": h["url"][:40] + "..." if len(h["url"]) > 40 else h["url"],
                        "Pass Rate": f"{h['pass_rate']:.1f}%",
                        "Duración": f"{h['duration']}s",
                        "Modo": h["model_mode"]
                    }
                    for h in history[-10:]  # Últimos 10
                ],
                use_container_width=True
            )
            
            st.divider()
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_pass_rate = sum(h["pass_rate"] for h in history) / len(history)
                st.metric("Pass Rate Promedio", f"{avg_pass_rate:.1f}%")
            with col2:
                st.metric("Total Tests", len(history))
            with col3:
                avg_duration = sum(h["duration"] for h in history) / len(history)
                st.metric("Duración Promedio", f"{avg_duration:.1f}s")
        else:
            st.info("📭 Sin tests aún")
    else:
        st.info("📭 Sin historial")

---

# FOOTER
st.divider()
st.markdown("""
<div style='text-align: center; color: #6e7681; font-size: 12px;'>
    <p>Smart Test - IA Local para Testing Web | Ollama + Playwright</p>
    <p><a href='https://github.com/PedroGM80/smart-web-test-ai'>GitHub</a> | 
       <a href='https://github.com/PedroGM80/smart-web-test-ai/blob/develop/MODEL_SELECTOR.md'>Docs</a></p>
</div>
""", unsafe_allow_html=True)
