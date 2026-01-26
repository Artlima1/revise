import pandas as pd
from datetime import datetime, timedelta

class SistemaEstudoMedico:
    def __init__(self):
        self.df_history = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto"])

    def processar_entradas(self, entries):
        history = []
        for entry in entries:
            date_sunday = pd.to_datetime(entry['semana'])
            
            for assunto, taxa, relevancia in zip(entry['assuntos'], entry['taxas'], entry['relevancias']):
                history.append({
                    "Assunto": assunto,
                    "Data": date_sunday,
                    "Taxa_Acerto": taxa,
                    "Relevancia": relevancia,
                })

        self.df_history = pd.DataFrame(history)
        self.df_history.sort_values(by=["Data"], inplace=True)
        self.df_history['Fase'] = self.df_history.groupby('Assunto').cumcount() + 1


    def gerar_lista_prioridades(self):
        today = pd.to_datetime(datetime.now().date())
        min_window = {1: 7, 2: 28, 3: 56}
        
        df = self.df_history.copy()
        df = df[df['Fase'] == df.groupby('Assunto')['Fase'].transform('max')]
        df = df[df['Fase'] < 4]

        sugestoes = []
        for _, row in df.iterrows():
            dias_passados = (today - row['Data']).days
            min_dias = min_window.get(row["Fase"], 0)
            
            if dias_passados >= min_dias:
                atraso = dias_passados - min_dias
                erro = 1 - row['Taxa_Acerto'] 
                final_score = (row["Relevancia"] * 15) + (atraso * 1.5) + (erro * 40)
                
                sugestoes.append([
                    row['Assunto'], 
                    row['Fase'] + 1,
                    round(final_score, 2), 
                    f"{atraso} dias de atraso"
                ])

        df_final = pd.DataFrame(sugestoes, columns=["Assunto", "Próxima Fase", "Score", "Status"])
        return df_final.sort_values(by="Score", ascending=False)

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

print("### LISTA DE ESTUDOS PRIORITÁRIOS ###")
print(gestor.gerar_lista_prioridades().to_string(index=False))