import streamlit as st

def render_historico(engine):
    st.header("📊 Histórico de Estudos")
    st.markdown("Aqui está o histórico detalhado dos seus estudos e revisões.")
    
    if engine.df_historico.empty:
        st.info("Nenhum dado de histórico disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        st.dataframe(engine.df_historico.reset_index(drop=True))

