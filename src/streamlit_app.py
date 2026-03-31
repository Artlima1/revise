from Classes.Revise import Revise
from Pages.Calendario import render_calendario
from Pages.Historico import render_historico
import streamlit as st
import pandas as pd

# ==================== Configuration ====================
CONFIG_FILE = './league_config.json'

# ==================== Initialization Functions ====================

@st.cache_resource
def init_revise():
    engine = Revise()
    return engine
# ==================== Page Configuration ====================

st.set_page_config(
    page_title="Revise - Sistema de Revisão para Estudos",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Main Application ====================

def main():
    # Title and Header with Logo

    st.title("Revise - Sistema de Revisão para Estudos")
    st.markdown("---")

    # Initialize league and load data
    with st.spinner("Loading league data..."):
        engine = init_revise()

    # Sidebar for data upload
    st.sidebar.header("Upload de Dados")
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")
    
    with st.sidebar.expander("Ver formato esperado"):
        exemplo_data = {
            "semana": ["2026-01-11"],
            "assuntos": ["Diabetes;SUS"],
            "taxas": ["0.90;0.95"],
            "relevancias": ["0.6;0.7"],
            "questoes_no_banco": ["100;150"],
            "questoes_feitas": ["80;120"]
        }
        st.dataframe(pd.DataFrame(exemplo_data), use_container_width=True)

    if uploaded_file is not None:
        try:
            engine.processar_entradas(from_csv=uploaded_file)
            engine.gerar_calendario_revisoes()
            st.sidebar.success("Dados carregados e processados com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao processar arquivo: {e}")

    # Store data in session state for later use
    if 'engine' not in st.session_state:
        st.session_state.engine = engine

    # Create tabs with key to preserve state
    tab1, tab2 = st.tabs([
        "📊 Historico",
        "📅 Calendário de Revisões",
    ])

    with tab1:
        render_historico(st.session_state.engine)

    with tab2:
        render_calendario(st.session_state.engine)

if __name__ == "__main__":
    main()
