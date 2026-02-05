import pandas as pd
from datetime import datetime, timedelta

class Revise:
    def __init__(self):
        self.df_historico = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto"])
        self.df_calendario = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto", "Relevancia", "Proxima_Revisao", "Atraso_Dias", "Prioridade"])

    def processar_entradas(self, entradas=None, from_csv=None):
        if from_csv is not None:
            entradas = []
            # Ensure we are at the start of the file
            from_csv.seek(0)
            # Streamlit provides a file-like object in bytes, so we decode it
            content = from_csv.read().decode('utf-8').splitlines()
            
            for i, line in enumerate(content):
                if not line.strip() or (i == 0 and "semana" in line.lower()):
                    continue
                    
                row = line.strip().split(',')
                if len(row) < 4:
                    continue
                    
                entradas.append({
                    "semana": row[0],
                    "assuntos": row[1].split(';'),
                    "taxas": [float(t) for t in row[2].split(';') if t],
                    "relevancias": [float(r) for r in row[3].split(';') if r],
                })

        if entradas:
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

        df_prox_rev["Atraso_Dias"] = (pd.to_datetime(datetime.now().date()) - df_prox_rev["Proxima_Revisao"]).apply(lambda x: x.days)

        df_prox_rev["Prioridade"] = (1 - df_prox_rev['Taxa_Acerto']) + \
                                    (df_prox_rev["Atraso_Dias"] * 1.5) + \
                                    (df_prox_rev['Relevancia'] * 15)
        
        self.df_calendario = df_prox_rev.sort_values(by="Prioridade", ascending=False)