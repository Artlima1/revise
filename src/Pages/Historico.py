import streamlit as st

def render_historico(engine):
    st.header("📊 Histórico de Estudos")
    st.markdown("Aqui está o histórico detalhado dos seus estudos e revisões.")
    
    if engine.df_historico.empty:
        st.info("Nenhum dado de histórico disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        # Filters
        assuntos = sorted(engine.df_historico["Assunto"].unique())
        filtro_assunto = st.multiselect("Filtrar por Assunto", options=assuntos, default=[])

        df_display = engine.df_historico.copy()
        if filtro_assunto:
            df_display = df_display[df_display["Assunto"].isin(filtro_assunto)]

        # Formatting
        df_display["Data"] = df_display["Data"].dt.date
        
        st.dataframe(df_display, hide_index=True)

