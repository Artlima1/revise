import streamlit as st

def render_calendario(engine):
    st.header("📅 Calendário de Revisões")
    st.markdown("Aqui está o calendário das suas próximas revisões, priorizadas para otimizar seu aprendizado.")
    
    if engine.df_calendario.empty:
        st.info("Nenhum dado de calendário disponível. Por favor, carregue seus dados na barra lateral.")
    else:
        df_cal = engine.df_calendario.copy()
        
        # Formatting
        df_cal["Ultima_Revisao"] = df_cal["Ultima_Revisao"].dt.strftime("%d/%m/%Y")
        df_cal["Proxima_Revisao"] = df_cal["Proxima_Revisao"].dt.strftime("%d/%m/%Y")
        
        # Select specific columns
        colunas_exibir = ["Assunto", "Ultima_Revisao", "Proxima_Revisao", "Fase", "Questoes_a_fazer"]
        st.dataframe(df_cal[colunas_exibir].reset_index(drop=True), hide_index=True)