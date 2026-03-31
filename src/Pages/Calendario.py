import streamlit as st
import pandas as pd

def render_calendario(engine):
    st.header("📅 Calendário de Revisões")
    st.markdown("Aqui está o calendário das suas próximas revisões, priorizadas para otimizar seu aprendizado.")
    
    if engine.df_calendario.empty:
        st.info("Nenhum dado de calendário disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        df_cal = engine.df_calendario.copy()
        
        # Toggle para mostrar revisões futuras com session_state
        col1, col2 = st.columns([3, 1])
        with col2:
            show_all_reviews = st.toggle("Mostrar Revisões Futuras", value=False, key="show_all_reviews_toggle")
        
        # Filtrar revisões futuras se toggle estiver desativado
        if not show_all_reviews:
            df_cal = df_cal[df_cal["Proxima_Revisao"] < pd.Timestamp.now()]
        
        # Formatting
        df_cal["Ultima_Revisao"] = df_cal["Ultima_Revisao"].dt.strftime("%d/%m/%Y")
        df_cal["Proxima_Revisao"] = df_cal["Proxima_Revisao"].dt.strftime("%d/%m/%Y")
        
        # Verificar se há dados após filtro
        if df_cal.empty:
            st.info("Nenhuma revisão programada para esta semana")
        else:
            # Select specific columns
            colunas_exibir = ["Assunto", "Ultima_Revisao", "Proxima_Revisao", "Fase", "Questoes_a_fazer"]
            st.dataframe(df_cal[colunas_exibir].reset_index(drop=True), hide_index=True)