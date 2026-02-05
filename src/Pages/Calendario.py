import streamlit as st

def render_calendario(engine):
    st.header("📅 Calendário de Revisões")
    st.markdown("Aqui está o calendário das suas próximas revisões, priorizadas para otimizar seu aprendizado.")
    
    if engine.df_calendario.empty:
        st.info("Nenhum dado de calendário disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        st.dataframe(engine.df_calendario.reset_index(drop=True))