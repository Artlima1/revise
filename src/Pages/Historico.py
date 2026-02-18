import streamlit as st

def render_historico(engine):
    st.header("📊 Histórico de Estudos")
    st.markdown("Aqui está o histórico detalhado dos seus estudos e revisões.")
    
    if engine.df_historico.empty:
        st.info("Nenhum dado de histórico disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        # Filters
        st.subheader("Filtros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            assuntos = sorted(engine.df_historico["Assunto"].unique())
            filtro_assunto = st.multiselect("Filtrar por Assunto", options=assuntos, default=[])
        
        with col2:
            fases = sorted(engine.df_historico["Fase"].unique())
            filtro_fase = st.multiselect("Filtrar por Fase", options=fases, default=[])
            
        with col3:
            min_date = engine.df_historico["Data"].min().date()
            max_date = engine.df_historico["Data"].max().date()
            filtro_data = st.date_input(
                "Filtrar por Período", 
                value=(min_date, max_date), 
                min_value=min_date, 
                max_value=max_date,
                format="DD/MM/YYYY"
            )

        df_display = engine.df_historico.copy()
        
        # Apply Filters
        if filtro_assunto:
            df_display = df_display[df_display["Assunto"].isin(filtro_assunto)]
            
        if filtro_fase:
            df_display = df_display[df_display["Fase"].isin(filtro_fase)]
            
        if isinstance(filtro_data, tuple) and len(filtro_data) == 2:
            start_date, end_date = filtro_data
            df_display = df_display[(df_display["Data"].dt.date >= start_date) & (df_display["Data"].dt.date <= end_date)]

        # Formatting to BR Date
        df_display["Data"] = df_display["Data"].dt.strftime("%d/%m/%Y")
        
        st.dataframe(df_display, hide_index=True, use_container_width=True)

