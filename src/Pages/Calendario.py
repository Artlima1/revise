import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
        
        # Verificar se há dados após filtro
        if df_cal.empty:
            st.info("Nenhuma revisão programada para esta semana")
        else:
            # Agrupar por semana (usando a data como referência de domingo)
            weeks = sorted(df_cal['Proxima_Revisao'].unique())
            
            # Display calendar for each week
            for week_sunday in weeks:
                # Calculate Monday from Sunday (Sunday is the end of the week)
                week_start = pd.Timestamp(week_sunday)
                week_end = pd.Timestamp(week_sunday) + pd.Timedelta(days=6)
                
                st.subheader(f"Semana de {week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}")
                
                # Get revisions for this week
                week_revisions = df_cal[df_cal['Proxima_Revisao'] == week_sunday].copy()
                
                # Display revisions in a nice format
                for idx, (_, row) in enumerate(week_revisions.iterrows()):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"{row['Assunto']}")
                    with col2:
                        st.write(f"📝 {row['Fase']}° Revisão")
                    with col3:
                        st.write(f"📅 Última Revisão: {row['Ultima_Revisao'].strftime('%d/%m/%Y')}")
                    with col4:
                        st.write(f"🎯 {row['Questoes_a_fazer']} questões")
                    
                    if idx < len(week_revisions) - 1:
                        st.divider()
                
                st.markdown("---")