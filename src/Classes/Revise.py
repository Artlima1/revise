import pandas as pd
from datetime import datetime, timedelta

# - Mais filtros 


class Revise:
    MIN_REV_QUESTIONS = 20
    MAX_REV_QUESTIONS = 80
    REV_WINDOWS = {1: 21, 2: 49, 3: 77}  # Dias para cada fase de revisão

    def __init__(self):
        self.df_historico = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto", "Questoes_no_Banco", "Questoes_Feitas"])
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
                    "questoes_no_banco": [float(r) for r in row[3].split(';') if r],
                    "questoes_feitas": [float(q) for q in row[4].split(';') if q],
                })

        if entradas:
            historico = []
            for entrada in entradas:
                data_domingo = pd.to_datetime(entrada['semana'], dayfirst=True)
                
                for assunto, taxa, questoes_no_banco, questoes_feitas in zip(entrada['assuntos'], entrada['taxas'], entrada['questoes_no_banco'], entrada['questoes_feitas']):
                    historico.append({
                        "Assunto": assunto,
                        "Data": data_domingo,
                        "Taxa_Acerto": taxa,
                        "Questoes_no_Banco": questoes_no_banco,
                        "Questoes_Feitas": questoes_feitas
                    })

            self.df_historico = pd.DataFrame(historico)
            self.df_historico.sort_values(by=["Data"], inplace=True)
            self.df_historico['Fase'] = self.df_historico.groupby('Assunto').cumcount() + 1


    def gerar_calendario_revisoes(self):
        df_prox_rev = self.df_historico.copy()
        df_prox_rev = df_prox_rev[df_prox_rev['Fase'] == df_prox_rev.groupby('Assunto')['Fase'].transform('max')]
        df_prox_rev = df_prox_rev[df_prox_rev['Fase'] < 4]
        
        df_prox_rev.rename(columns={"Data": "Ultima_Revisao"}, inplace=True)
        df_prox_rev["Proxima_Revisao"] = df_prox_rev['Ultima_Revisao'] + pd.to_timedelta(df_prox_rev['Fase'].map(self.REV_WINDOWS), unit='D')
        df_prox_rev["Fase"] = df_prox_rev['Fase']+1

        taxa_erro = (1 - df_prox_rev['Taxa_Acerto'])
        taxa_erro = taxa_erro.clip(0, 1)

        # Normalize Questoes_no_Banco between 200 and 1400 with clipping
        fator_banco = (df_prox_rev['Questoes_no_Banco'] - 200) / (1400 - 200)
        fator_banco = fator_banco.clip(0, 1)

        # Weighted score (50% error rate, 50% bank size)
        score = (taxa_erro * 0.5) + (fator_banco * 0.5)

        # Scale score (0 to 1) to range [30, 80]
        min_q, max_q = self.MIN_REV_QUESTIONS, self.MAX_REV_QUESTIONS
        df_prox_rev["Questoes_a_fazer"] = min_q + (score * (max_q - min_q))
        df_prox_rev["Questoes_a_fazer"] = df_prox_rev["Questoes_a_fazer"].round().astype(int)

        self.df_calendario = df_prox_rev.sort_values(by="Proxima_Revisao").reset_index(drop=True)

        print(self.df_calendario)