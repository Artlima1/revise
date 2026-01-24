import pandas as pd
from datetime import datetime, timedelta

class SistemaEstudoMedico:
    def __init__(self):
        # 1. Cadastro Estático (Catálogo)
        self.catalogo = {
            "Assunto": ["Aleitamento", "Crescimento", "Vacinação", "Pré-natal", "Parto", 
                        "Apendicite", "Trauma", "Hipertensão", "Diabetes", "SUS"],
            "Area": ["PED", "PED", "PED", "GO", "GO", "CIR", "CIR", "CM", "CM", "PREV"],
            "Relevancia": [3, 2, 3, 3, 2, 3, 3, 3, 3, 3] # 1: Pouco, 2: Médio, 3: Muito
        }
        self.df_catalogo = pd.DataFrame(self.catalogo)
        
        # 2. Histórico (Inicia vazio)
        self.df_historico = pd.DataFrame(columns=["Assunto", "Fase", "Data", "Taxa_Acerto"])

    def processar_entradas(self, lista_entradas):
        """
        Entrada: Lista de dicts {semana: 'AAAA-MM-DD', assuntos: [], taxas: []}
        'semana' deve ser o domingo da semana.
        """
        registros = []
        for entrada in lista_entradas:
            data_domingo = pd.to_datetime(entrada['semana'])
            
            for assunto, taxa in zip(entrada['assuntos'], entrada['taxas']):
                # Descobrir em qual fase o assunto está entrando
                # Filtramos o histórico acumulado + os registros que estamos criando nesta rodada
                historico_previo = self.df_historico[self.df_historico['Assunto'] == assunto]
                fase_atual = len(historico_previo) + 1 
                
                registros.append({
                    "Assunto": assunto,
                    "Fase": fase_atual,
                    "Data": data_domingo,
                    "Taxa_Acerto": taxa
                })
                
                # Atualiza o dataframe temporariamente para o próximo loop da mesma lista reconhecer a fase
                temp_df = pd.DataFrame([registros[-1]])
                self.df_historico = pd.concat([self.df_historico, temp_df], ignore_index=True)

    def gerar_lista_prioridades(self, data_hoje=None):
        if data_hoje is None:
            data_hoje = pd.to_datetime(datetime.now().date())
        else:
            data_hoje = pd.to_datetime(data_hoje)

        # Configuração das Janelas (Mínimo de dias após o último estudo)
        # EI(1) -> R1(2): 7 dias | R1(2) -> R2(3): 28 dias | R2(3) -> R3(4): 56 dias
        janelas_minimas = {1: 7, 2: 28, 3: 56}
        proxima_fase_map = {0: "EI", 1: "R1", 2: "R2", 3: "R3"}

        sugestoes = []

        for _, row in self.df_catalogo.iterrows():
            assunto = row['Assunto']
            relevancia = row['Relevancia']
            
            # Pega o último estudo desse assunto
            historico = self.df_historico[self.df_historico['Assunto'] == assunto]
            
            if historico.empty:
                # Caso nunca estudado: Sempre disponível
                score = relevancia * 20
                sugestoes.append([assunto, row['Area'], "EI", score, "Novo"])
            else:
                ultimo = historico.sort_values(by="Data").iloc[-1]
                fase_concluida = ultimo['Fase']
                
                if fase_concluida >= 4: # R3 concluída
                    continue
                
                dias_passados = (data_hoje - ultimo['Data']).days
                min_dias = janelas_minimas.get(fase_concluida, 0)
                
                # REGRA 1: Caso não esteja na hora, não incluir
                if dias_passados >= min_dias:
                    # Cálculo de Prioridade
                    atraso = dias_passados - min_dias
                    erro = 1 - ultimo['Taxa_Acerto']
                    
                    # Score: Relevância + Peso do Atraso + Peso do Erro
                    score = (relevancia * 15) + (atraso * 1.5) + (erro * 40)
                    
                    sugestoes.append([
                        assunto, 
                        row['Area'], 
                        proxima_fase_map[fase_concluida], 
                        round(score, 2), 
                        f"{atraso} dias de atraso"
                    ])

        df_final = pd.DataFrame(sugestoes, columns=["Assunto", "Área", "Próxima Revisão", "Score", "Status"])
        return df_final.sort_values(by="Score", ascending=False)

# --- Exemplo de Uso Prático ---

gestor = SistemaEstudoMedico()

# Entrada de dados (Simulando que hoje é 24/01/2026)
entradas_usuario = [
    {
        "semana": "2025-12-28", # Domingo retrasado
        "assuntos": ["SUS", "Apendicite"], 
        "taxas": [0.85, 0.60]
    },
    {
        "semana": "2026-01-11", # Domingo passado
        "assuntos": ["Diabetes", "SUS"], # SUS indo para R1
        "taxas": [0.90, 0.95]
    }
]

gestor.processar_entradas(entradas_usuario)

print("### LISTA DE ESTUDOS PRIORITÁRIOS ###")
print(gestor.gerar_lista_prioridades().to_string(index=False))