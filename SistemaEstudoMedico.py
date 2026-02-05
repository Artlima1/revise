import pandas as pd
from datetime import datetime, timedelta

class SistemaEstudoMedico:
    def __init__(self):
        self.df_historico = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto"])

    def processar_entradas(self, entradas):
        historico = []
        for entrada in entradas:
            data_domingo = pd.to_datetime(entrada['semana'])
            
            for assunto, taxa, relevancia in zip(entrada['assuntos'], entrada['taxas'], entrada['relevancias']):
                historico.append({
                    "Assunto": assunto,
                    "Data": data_domingo,
                    "Taxa_Acerto": taxa,
                    "Relevancia": relevancia,
                })

        self.df_historico = pd.DataFrame(historico)
        self.df_historico.sort_values(by=["Data"], inplace=True)
        self.df_historico['Fase'] = self.df_historico.groupby('Assunto').cumcount() + 1


    def gerar_calendario_revisoes(self):
        min_window = {1: 7, 2: 28, 3: 56}

        df_prox_rev = self.df_historico.copy()
        df_prox_rev = df_prox_rev[df_prox_rev['Fase'] == df_prox_rev.groupby('Assunto')['Fase'].transform('max')]
        df_prox_rev = df_prox_rev[df_prox_rev['Fase'] < 4]
        df_prox_rev["Proxima_Revisao"] = df_prox_rev['Data'] + pd.to_timedelta(df_prox_rev['Fase'].map(min_window), unit='D')
        df_prox_rev["Fase"] = df_prox_rev['Fase']+1


        df_prox_rev = df_prox_rev[df_prox_rev["Proxima_Revisao"] <= pd.to_datetime(datetime.now().date())]

        df_prox_rev["Atraso_Dias"] = (pd.to_datetime(datetime.now().date()) - df_prox_rev["Proxima_Revisao"]).dt.days

        df_prox_rev["Prioridade"] = (1 - df_prox_rev['Taxa_Acerto']) + \
                                    (df_prox_rev["Atraso_Dias"] * 1.5) + \
                                    (df_prox_rev['Relevancia'] * 15)
        
        self.df_calendario = df_prox_rev.sort_values(by="Prioridade", ascending=False)

# --- Exemplo de Uso Prático ---

gestor = SistemaEstudoMedico()

# Entrada de dados (Simulando que hoje é 24/01/2026)
entradas_usuario = [
    {
        "semana": "2025-12-28", # Domingo retrasado
        "assuntos": ["SUS", "Apendicite"], 
        "taxas": [0.85, 0.60],
        "relevancias": [0.7, 0.5]
    },
    {
        "semana": "2026-01-11", # Domingo passado
        "assuntos": ["Diabetes", "SUS"], # SUS indo para R1
        "taxas": [0.90, 0.95],
        "relevancias": [0.6, 0.7]
    }
]

gestor.processar_entradas(entradas_usuario)
gestor.gerar_calendario_revisoes()

print("### LISTA DE ESTUDOS PRIORITÁRIOS ###")
print(gestor.df_calendario)