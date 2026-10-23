import os
import json
import streamlit as st
import graphviz

st.set_page_config(
    page_title="Sistema Experto: Revisión Preventiva de Motos",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

st.markdown("""
<style>
    /* Ocultar barra nativa de Streamlit (Deploy, Menú de 3 puntos, Footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Título principal con degradado técnico/automotriz */
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #F97316, #EF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Breadcrumb / Migas de pan */
    .breadcrumb-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        color: #F1F5F9;
    }
    .breadcrumb-item {
        color: #38BDF8;
        font-weight: 600;
    }
    .breadcrumb-sep {
        color: #64748B;
        font-weight: 400;
    }
    
    /* Tarjeta de pregunta actual */
    .question-card {
        background: #0F172A;
        border-radius: 14px;
        border: 1px solid #1E293B;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #1E3A8A;
        color: #93C5FD;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Configuración de Modelos Disponibles
# -------------------------------------------------------------
MODELOS = {
    "Modelo Base (Genérico)": {
        "nombre": "llama3.2:1b",
        "descripcion": "Modelo ligero para explicaciones generales de conceptos.",
        "usa_system_personalizado": False,
    },
    "Mecánico Virtual de Motos (Especializado)": {
        "nombre": "mecanico-moto-3b",
        "descripcion": "Modelo entrenado con Modelfile para diagnósticos técnicos en Colombia.",
        "usa_system_personalizado": True,
    },
}

JSON_FILE = "EstructurasDeDatos.json"

def cargar_arbol(ruta_archivo=JSON_FILE):
    if not os.path.exists(ruta_archivo):
        return None, f"No se encontró el archivo '{ruta_archivo}'."
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if not isinstance(datos, dict) or "valor" not in datos:
                return None, "El formato del JSON debe contener una raíz con la clave 'valor'."
            return datos, None
    except Exception as e:
        return None, f"Error al leer archivo: {e}"

# -------------------------------------------------------------
# Inicialización del Estado de la Sesión
# -------------------------------------------------------------
if "arbol" not in st.session_state or st.session_state.arbol is None:
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    st.session_state.historial = [arbol] if arbol else []
    st.session_state.explicacion_ia = None

def reiniciar_navegacion():
    if st.session_state.arbol:
        st.session_state.historial = [st.session_state.arbol]
    else:
        st.session_state.historial = []
    st.session_state.explicacion_ia = None

def recargar_archivo():
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    reiniciar_navegacion()


# Barra Lateral 

with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    
    seleccion_modelo = st.selectbox(
        "Seleccionar Modelo Ollama:",
        options=list(MODELOS.keys()),
        help="Elige entre el modelo genérico o el mecánico virtual especializado."
    )
    modelo_info = MODELOS[seleccion_modelo]
    modelo_nombre = modelo_info["nombre"]
    usa_system = modelo_info["usa_system_personalizado"]
    
    st.info(f"**Info:** {modelo_info['descripcion']}")
    
    temperatura = st.slider(
        "Temperatura (Creatividad):",
        min_value=0.0,
        max_value=1.0,
        value=0.05 if usa_system else 0.5,
        step=0.1
    )
    
    st.markdown("---")
    st.markdown("### 📂 Gestión de Datos")
    if st.button("🔄 Recargar JSON", use_container_width=True):
        recargar_archivo()
        st.toast("Estructura JSON recargada con éxito", icon="✅")
        st.rerun()

    if st.button("⏪ Reiniciar Exploración", use_container_width=True):
        reiniciar_navegacion()
        st.rerun()

    st.markdown("---")
    st.caption("🏫 **Institución Universitaria Colegio Mayor del Cauca**")
    st.caption("📚 Materia: Estructuras de Datos No Lineales")
    st.caption("👨‍🏫 Profesor: Álvaro Pinto")


# Cabecera Principal

st.markdown('<div class="main-title">🏍️ Sistema Experto: Revisión Preventiva de Motos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Implementación de Inteligencia Artificial Local con Ollama y Estructuras de Datos No Lineales</div>', unsafe_allow_html=True)

if st.session_state.error_arbol:
    st.error(st.session_state.error_arbol)
    st.stop()


tab_explorador, tab_diagrama, tab_json = st.tabs([
    "Explorador Interactivo", 
    "Diagrama del Árbol", 
    "Estructura JSON"
])


# PESTAÑA 1: EXPLORADOR INTERACTIVO

with tab_explorador:
    historial = st.session_state.historial
    if not historial:
        st.session_state.historial = [st.session_state.arbol]
        historial = st.session_state.historial

    nodo_actual = historial[-1]
    camino_titulos = [nodo["valor"] for nodo in historial]
    nivel_actual = len(historial)
    hijos = nodo_actual.get("hijos", [])


    breadcrumb_html = '<div class="breadcrumb-box"><span>📍 <b>Ruta actual:</b></span> '
    for idx, tit in enumerate(camino_titulos):
        if idx > 0:
            breadcrumb_html += '<span class="breadcrumb-sep">➔</span> '
        breadcrumb_html += f'<span class="breadcrumb-item">{tit}</span> '
    breadcrumb_html += '</div>'
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

    if hijos:
        st.session_state.explicacion_ia = None
        pregunta_texto = f"Dentro de **{nodo_actual['valor']}**, ¿qué categoría deseas consultar?" if nivel_actual > 1 else f"¿Qué sistema principal de la motocicleta deseas revisar?"

        st.markdown(f"""
        <div class="question-card">
            <span class="level-badge">Nivel {nivel_actual}</span>
            <h3 style="margin-top:0.3rem; margin-bottom:0.5rem; font-weight:600;">{pregunta_texto}</h3>
            <p style="color:#94A3B8; font-size:0.9rem; margin-bottom:0;">Selecciona una opción para avanzar en el árbol de decisión:</p>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(min(len(hijos), 3))
        for i, hijo in enumerate(hijos):
            col_act = cols[i % len(cols)]
            etiqueta = hijo.get("valor", f"Opción {i+1}")
            icono = "📁" if hijo.get("hijos") else "📄"
            
            if col_act.button(f"{icono} {etiqueta}", key=f"btn_hijo_{nivel_actual}_{i}", use_container_width=True):
                st.session_state.historial.append(hijo)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_nav1, col_nav2, _ = st.columns([1, 1, 2])
        with col_nav1:
            if nivel_actual > 1:
                if st.button("⬅️ Paso anterior", use_container_width=True):
                    st.session_state.historial.pop()
                    st.rerun()
        with col_nav2:
            if nivel_actual > 1:
                if st.button("🔄 Desde el inicio", use_container_width=True):
                    reiniciar_navegacion()
                    st.rerun()

    else:
        # HOJA FINAL - CONSULTA A OLLAMA
        st.markdown(f"""
        <div class="question-card" style="border-left: 5px solid #10B981;">
            <span class="level-badge" style="background-color: #D1FAE5; color: #047857;">Diagnóstico de Hoja</span>
            <h3 style="margin-top: 0.3rem; margin-bottom: 0.5rem;">Condición: <b>{nodo_actual['valor']}</b></h3>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 0;">
                Se ha alcanzado el nodo final. Generando diagnóstico técnico con el modelo local de Ollama.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_back1, col_back2, _ = st.columns([1, 1, 2])
        with col_back1:
            if st.button("⬅️ Elegir otra opción", use_container_width=True):
                st.session_state.historial.pop()
                st.rerun()
        with col_back2:
            if st.button("🔄 Reiniciar exploración", use_container_width=True):
                reiniciar_navegacion()
                st.rerun()

        st.markdown("---")
        st.subheader(f"🤖 Diagnóstico IA ({modelo_nombre})")

        if usa_system:
            prompt = (
                f"Ruta: {' > '.join(camino_titulos)}\n"
                f"Hoja: {nodo_actual['valor']}\n\n"
                "Genera el diagnóstico final con el formato obligatorio."
            )
            system_content = ""
        else:
            prompt = (
                f"Explícame qué es '{nodo_actual['valor']}' en el contexto de la revisión "
                f"preventiva de una moto para un viaje. Ruta: {' > '.join(camino_titulos)}. "
                "Da una explicación breve y útil."
            )
            system_content = "Eres un experto en mecánica de motos. Da respuestas claras y breves."

        try:
            import ollama

            if st.session_state.explicacion_ia is None:
                with st.spinner(f"Consultando a {modelo_nombre} en Ollama..."):
                    mensajes = []
                    if system_content:
                        mensajes.append({"role": "system", "content": system_content})
                    mensajes.append({"role": "user", "content": prompt})

                    stream = ollama.chat(
                        model=modelo_nombre,
                        messages=mensajes,
                        options={"temperature": temperatura},
                        stream=True
                    )
                    
                    def generar_stream():
                        for chunk in stream:
                            yield chunk['message']['content']

                    respuesta_completa = st.write_stream(generar_stream)
                    st.session_state.explicacion_ia = respuesta_completa
            else:
                st.markdown(st.session_state.explicacion_ia)
                if st.button("🔄 Regenerar diagnóstico"):
                    st.session_state.explicacion_ia = None
                    st.rerun()

        except Exception as e:
            st.error(f"⚠️ No se pudo conectar con Ollama. Asegúrate de ejecutar `ollama serve` en tu terminal.\n\n**Error técnico:** {e}")


# PESTAÑA 2: DIAGRAMA VISUAL DEL ÁRBOl

with tab_diagrama:
    st.subheader("📊 Diagrama Jerárquico de la Estructura de Datos")
    st.markdown("Representación visual del árbol JSON cargado en el sistema:")

    def construir_grafo(nodo, dot=None):
        if dot is None:
            dot = graphviz.Digraph(comment='Árbol de Decisión')
            dot.attr(rankdir='LR', size='10,8')
            dot.attr('node', shape='box', style='rounded,filled', fillcolor='#1E293B', color='#38BDF8', fontcolor='#F1F5F9', fontname='Segoe UI', fontsize='11')
        
        val_actual = nodo.get('valor', 'Nodo')
        dot.node(val_actual, val_actual)
        
        for hijo in nodo.get('hijos', []):
            val_hijo = hijo.get('valor', 'Hijo')
            dot.node(val_hijo, val_hijo)
            dot.edge(val_actual, val_hijo)
            if 'hijos' in hijo:
                construir_grafo(hijo, dot)
        return dot

    try:
        if st.session_state.arbol:
            grafo = construir_grafo(st.session_state.arbol)
            st.graphviz_chart(grafo, use_container_width=True)
        else:
            st.warning("No hay árbol disponible para graficar.")
    except Exception as e:
        st.info("Para visualizar el diagrama gráfico en tiempo real, Graphviz se encarga del renderizado.")
        st.text(f"Detalle técnico: {e}")


# PESTAÑA 3: ESTRUCTURA JSON

with tab_json:
    st.subheader("📄 Código Fuente del Árbol (`EstructurasDeDatos.json`)")
    st.markdown("Estructura jerárquica en formato JSON que alimenta la inteligencia artificial:")
    if st.session_state.arbol:
        st.json(st.session_state.arbol)
    else:
        st.warning("Archivo JSON no cargado.")
