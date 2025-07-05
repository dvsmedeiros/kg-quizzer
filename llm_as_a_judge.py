
import pandas as pd
import json
from pathlib import Path
import os
import re
import time
import uuid
import config
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from infra.ssh_tunnel import SSHTunnel
from utils.utils import chamar_modelo
from utils.utils import get_logger
from utils.utils import salvar_resposta
from utils.utils import salvar_execucao_csv
from utils.utils import contar_tokens_prompt

PROMPT_AVALIACAO_V1 = """
Você é um avaliador imparcial e especializado em validar a qualidade de pares de pergunta e resposta gerados por modelos de linguagem. Avalie cuidadosamente o par abaixo com base nos seguintes critérios:

1. **Complexidade**: A pergunta exige raciocínio, síntese ou inferência além da simples memorização? Ela tem estrutura válida de pergunta?
2. **Completude**: A resposta aborda todos os aspectos solicitados na pergunta? É direta, clara e responde completamente ao que foi perguntado?
3. **Corretude**: A resposta está correta e condiz com a pergunta? O par é logicamente coerente e não há contradição entre os dois?
4. **Fluidez**: O par apresenta clareza na leitura e fluidez natural do idioma? A pergunta e a resposta “soam naturais” para um falante nativo?
5. **Qualidade do português**: A resposta está escrita com ortografia correta, boa gramática, concordância e estilo adequado?

### Par a ser avaliado:

**Pergunta**: {pergunta.strip()}  
**Resposta**: {resposta.strip()}

**Prompt de entrada** (usado como base para gerar o par):  
{limpar_prompt(prompt)}

Retorne exclusivamente um JSON com o seguinte formato:

```json
{{
  "pergunta": "{pergunta.strip()}",
  "resposta": "{resposta.strip()}",
  "complexidade": <1-5>,
  "completude": <1-5>,
  "corretude": <1-5>,
  "fluidez": <1-5>,
  "qualidade_portugues": <1-5>,
  "justificativa": "<explicação sucinta da avaliação>"
}}
"""

PROMPT_AVALIACAO_V2 = """
Você é um avaliador imparcial e especializado em validar a qualidade de pares de pergunta e resposta gerados por modelos de linguagem. Avalie cuidadosamente o par abaixo com base nos seguintes critérios, atribuindo uma nota de **1 a 5** para cada um deles:

1. **Complexidade**: O par pergunta e resposta exigem raciocínio, síntese ou inferência além da simples memorização? Possuem estrutura válida de pergunta e resposta?
   - 1: Muito simples, puramente factual ou trivial.
   - 2: Simples, mas com mínima exigência de compreensão.
   - 3: Média complexidade, exige compreensão do contexto.
   - 4: Alta complexidade, requer análise ou inferência.
   - 5: Muito desafiadora, exige raciocínio elaborado ou multidimensional.

2. **Completude**: A resposta aborda todos os aspectos solicitados na pergunta? É direta, clara e responde completamente ao que foi perguntado?
   - 1: Incompleta ou muito vaga.
   - 2: Parcialmente completa, mas relevante.
   - 3: Adequadamente completa.
   - 4: Quase totalmente completa, apenas com detalhes ausentes.
   - 5: Completude total e precisa.

3. **Corretude**: A resposta está correta e coerente com a pergunta? O par é logicamente coerente e não há contradição entre os dois?
   - 1: Incorreta ou contraditória.
   - 2: Parcialmente correta, com falhas.
   - 3: Correta, mas com margem de erro.
   - 4: Correta com boa precisão.
   - 5: Totalmente correta e precisa.

4. **Fluidez**: O par apresenta clareza na leitura e fluidez natural do idioma português? A pergunta e a resposta soam naturais e bem estruturadas em português para um falante nativo?
   - 1: Texto truncado ou mal estruturado.
   - 2: Levemente artificial ou confuso.
   - 3: Fluidez aceitável.
   - 4: Natural, com boa estrutura.
   - 5: Extremamente fluido e natural.

5. **Qualidade do português**: O par apresenta escrita com ortografia correta, boa gramática, concordância e estilo adequado?
   - 1: Muitos erros graves.
   - 2: Erros moderados, mas compreensível.
   - 3: Alguns erros leves.
   - 4: Correto com fluidez.
   - 5: Impecável, sem erros.

R### Par a ser avaliado:

**Pergunta**: {pergunta.strip()}  
**Resposta**: {resposta.strip()}

**Prompt de entrada** (usado como base para gerar o par):  
{limpar_prompt(prompt)}

Retorne exclusivamente um JSON com o seguinte formato:

```json
{{
  "pergunta": "",
  "resposta": "",
  "complexidade": <1-5>,
  "completude": <1-5>,
  "corretude": <1-5>,
  "fluidez": <1-5>,
  "qualidade_portugues": <1-5>,
  "justificativa": "<explicação sucinta da avaliação>"
}}
""".strip()


id_execucao = uuid.uuid4().hex[:8] 
logger = get_logger(id_execucao)

def limpar_prompt(prompt: str):
    """
    Remove instruções de geração do prompt, mantendo apenas:
    - Contexto
    - Fatos
    - Exemplos (opcional)

    Parâmetros:
    - prompt: string com o prompt original completo
    - manter_exemplos: se True, mantém o bloco ### Exemplos

    Retorna:
    - prompt limpo como string
    """
    # Define blocos a manter
    blocos_mantidos = ["### Contexto", "### Fatos", "### Exemplos"]
    
    # Regex para encontrar todos os títulos de bloco (### Título)
    blocos = re.split(r"(### .+)", prompt)
    resultado = []

    for i in range(1, len(blocos), 2):  # percorre apenas títulos (pares ímpares)
        titulo = blocos[i].strip()
        conteudo = blocos[i + 1] if i + 1 < len(blocos) else ""

        if titulo in blocos_mantidos:
            resultado.append(f"{titulo}\n{conteudo.strip()}")

    return "\n\n".join(resultado).strip()

def construir_prompt_avaliacao(pergunta: str, resposta: str, prompt: str) -> str:    
    return f"""
Você é um avaliador imparcial e especializado em validar a qualidade de pares de pergunta e resposta gerados por modelos de linguagem. Avalie criticamente o par abaixo com base nos seguintes critérios, atribuindo uma nota de **1 a 5** para cada um deles:

1. **Complexidade**: O par pergunta e resposta exigem raciocínio, síntese ou inferência além da simples memorização? Possuem estrutura válida de pergunta e resposta?
   - 1: Muito simples, puramente factual ou trivial.
   - 2: Simples, mas com mínima exigência de compreensão.
   - 3: Média complexidade, exige compreensão do contexto.
   - 4: Alta complexidade, requer análise ou inferência.
   - 5: Muito desafiadora, exige raciocínio elaborado ou multidimensional.

2. **Completude**: A resposta aborda todos os aspectos solicitados na pergunta? Responde completamente ao que foi perguntado?
   - 1: Incompleta ou muito vaga.
   - 2: Parcialmente completa, mas relevante.
   - 3: Adequadamente completa.
   - 4: Quase totalmente completa, apenas com detalhes ausentes.
   - 5: Completude total e precisa.

3. **Corretude**: A resposta está correta e coerente com a pergunta e contexto? O par é logicamente coerente e não há contradição entre os dois?
   - 1: Incorreta ou contraditória.
   - 2: Parcialmente correta, com falhas.
   - 3: Correta, mas com margem de erro.
   - 4: Correta com boa precisão.
   - 5: Totalmente correta e precisa.

4. **Fluidez**: O par apresenta clareza na leitura e fluidez natural do idioma português? A pergunta e a resposta soam naturais e bem estruturadas em português para um falante nativo?
   - 1: Texto truncado ou mal estruturado.
   - 2: Levemente artificial ou confuso.
   - 3: Fluidez aceitável.
   - 4: Natural, com boa estrutura.
   - 5: Extremamente fluido e natural.

5. **Qualidade do português**: O par apresenta escrita com ortografia correta, boa gramática, concordância e estilo adequado?
   - 1: Muitos erros graves.
   - 2: Erros moderados, mas compreensível.
   - 3: Alguns erros leves.
   - 4: Correto com fluidez.
   - 5: Impecável, sem erros.

### Par a ser avaliado:

**Pergunta**: {pergunta.strip()}  
**Resposta**: {resposta.strip()}

**Prompt de entrada** (usado como base para gerar o par):  
{limpar_prompt(prompt)}

Retorne exclusivamente um JSON com o seguinte formato:

```json
{{
  "pergunta": "{pergunta.strip()}",
  "resposta": "{resposta.strip()}",
  "complexidade": <1-5>,
  "completude": <1-5>,
  "corretude": <1-5>,
  "fluidez": <1-5>,
  "qualidade_portugues": <1-5>,
  "justificativa": "<explicação suscinta da avaliação>"
}}
"""

def processar_cenario(llm, id_cenario, nome_cenario, cenario: str, prompt: str, pasta_resultado: Path, pasta_avaliacao: Path):
    """Processa um único cenário e salva o resultado na pasta de avaliação."""    
    
    arquivo_cenario = pasta_resultado / f"{cenario}.csv"
    if not arquivo_cenario.exists():
        logger.error(f"Arquivo não encontrado: {arquivo_cenario}")
        return

    try:
        df_cenario = pd.read_csv(
            arquivo_cenario,
            sep=";",
            encoding="utf-8",
            on_bad_lines="warn"
        )
        df_cenario.columns = [col.strip().lower() for col in df_cenario.columns]
    except Exception as e:
        logger.error(f"Falha ao ler {arquivo_cenario}: {e}")
        return

    if 'pergunta' not in df_cenario.columns or 'resposta' not in df_cenario.columns:
        logger.info(f"Colunas 'pergunta' ou 'resposta' não encontradas em {cenario}")
        logger.info(f"Colunas disponíveis: {df_cenario.columns.tolist()}")
        return
    
    for i, linha in df_cenario.iterrows():

        start = time.perf_counter()

        pergunta = str(linha.get("pergunta", "")).strip()
        resposta = str(linha.get("resposta", "")).strip()

        if not pergunta or not resposta:
            logger.info(f"Par inválido em {cenario}: pergunta ou resposta vazia.")
            continue

        prompt_avaliacao = construir_prompt_avaliacao(pergunta, resposta, prompt)
        resposta = chamar_modelo(llm, prompt_avaliacao)

        tempo_execucao = time.perf_counter() - start
        logger.info(f"Tempo de execução: {tempo_execucao:.2f} segundos")
        modelo = "mistral:latest"
        tokens_contexto = contar_tokens_prompt(prompt_avaliacao, modelo)
        tokens_resposta = contar_tokens_prompt(resposta, modelo)
        logger.info(f"{id_cenario}_{i+1}_{modelo}, tokens_contexto: {tokens_contexto}, tokens_resposta: {tokens_resposta} max_tokens: {8000}")

        execucao = {
            "id_cenario": f"{id_cenario}_{i+1}",
            "nome_cenario": nome_cenario,                
            "prompt": prompt_avaliacao,
            "tokens_contexto": tokens_contexto,
            "tokens_resposta": tokens_resposta,
            "max_tokens": 8000,
            "tempo_execucao": tempo_execucao
        }

        salvar_execucao_csv(id_execucao, execucao)
        salvar_resposta(id_execucao, f"{id_cenario}_{i+1}_{modelo}", nome_cenario, resposta,  pasta_saida="julgamento")

def main():

    start_total = time.perf_counter()

    _ = load_dotenv(find_dotenv())

    #experimento_id = "d881d47f_e90feffe"
    experimento_id = "ffbe36d0"

    pasta_execucao = Path(f"execucao/{experimento_id}")    
    pasta_resultado = Path(f"resultado_csv/{experimento_id}/sucesso")
    pasta_avaliacao = Path(f"avaliacao/{experimento_id}")
    pasta_avaliacao.mkdir(parents=True, exist_ok=True)

    caminho_execucao = pasta_execucao / f"{experimento_id}_execucao.csv"
    if not caminho_execucao.exists():
        logger.error(f"Arquivo de execução não encontrado: {caminho_execucao}")
        return

    try:
        df_execucao = pd.read_csv(
            caminho_execucao,
            sep=";",
            encoding="utf-8",
            # on_bad_lines="warn"  # Ignora e avisa sobre linhas com erro de colunas
        )        
    except Exception as e:
        logger.error(f"Falha ao ler o arquivo de execução: {e}")
        return

    with SSHTunnel(
        ssh_host=os.getenv("OLLAMA_SSH_HOST"),
        ssh_port=int(os.getenv("OLLAMA_SSH_PORT")),
        ssh_username=os.getenv("OLLAMA_SSH_USERNAME"),
        ssh_password=os.getenv("OLLAMA_SSH_PASSWORD"),
        ssh_pkey=None,
        target_host=os.getenv("OLLAMA_HOST"),
        target_port=int(os.getenv("OLLAMA_PORT")),
    ) as tunnel:
        
        base_url = f"http://127.0.0.1:{tunnel.get_local_port()}"
        logger.info(f"Túnel SSH ativo em {base_url}")
        
        llm = ChatOllama(
            model="mistral:latest",
            base_url=base_url,            
        )

        for i, row in df_execucao.iterrows(): 

            experimento_id_split  = experimento_id.split("_")
            id_cenario = row.get("id_cenario")
            nome_cenario = row.get("nome_cenario")
            prompt = row.get("prompt", "")

            #if(len(experimento_id_split) > 1):            
            #    if(i < 1830):                    
            #        cenario = f"{experimento_id_split[0]}_{id_cenario}_{nome_cenario}" if id_cenario and nome_cenario else None    
            #    else:                    
            #        cenario = f"{experimento_id_split[1]}_{id_cenario}_{nome_cenario}" if id_cenario and nome_cenario else None    
            
            cenario = f"{experimento_id}_{id_cenario}_{nome_cenario}" if id_cenario and nome_cenario else None

            if not cenario:
                logger.error("Linha ignorada: 'id_cenario' ausente")
                continue
            
            id_cenario = i+1

            logger.info("-" * 80)
            logger.info(f"Execução: {id_execucao} | Cenário {id_cenario}/{len(df_execucao)}: {cenario}")
            logger.info("-" * 80)
            
            processar_cenario(llm, id_cenario, nome_cenario, cenario, prompt, pasta_resultado, pasta_avaliacao)
    
        logger.info(f"Tempo total de execução: {time.perf_counter() - start_total:.2f} segundos")

if __name__ == "__main__":
    main()    