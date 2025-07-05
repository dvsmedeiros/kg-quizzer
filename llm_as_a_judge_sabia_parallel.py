
# coding: utf-8
import pandas as pd
import re
import uuid
import time
import asyncio
import datetime
from aiolimiter import AsyncLimiter
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import openai
from pydantic import BaseModel
from maritalk import count_tokens
from utils.utils import get_logger, salvar_resposta, salvar_execucao_csv

OPENAI_API_KEY = ""

id_execucao = uuid.uuid4().hex[:8]
logger = get_logger(id_execucao)

RPM = 60
TPM_INPUT = 120000  # 120.000 tokens de entrada por minuto, 8000 de margem de segurança
TPM_OUTPUT = 9000   # 9.000 tokens de saída por minuto, 1000 de margem de segurança

limiter = AsyncLimiter(RPM, 60)  # 60 requisições por minuto
lock = asyncio.Lock()
contador_input = 0
contador_output = 0

async def resetar_contadores():
    global contador_input, contador_output
    while True:
        await asyncio.sleep(90) # Reseta os contadores a cada 90 segundos, 30 segundos de margem de segurança
        async with lock:
            contador_input = 0
            contador_output = 0
            logger.info("🔁 Contadores de tokens resetados.")

async def contabilizar_tokens_e_esperar(tokens_in, tokens_out):
    global contador_input, contador_output
    while True:
        async with lock:
            if (contador_input + tokens_in <= TPM_INPUT) and (contador_output + tokens_out <= TPM_OUTPUT):
                contador_input += tokens_in
                contador_output += tokens_out
                return
            else:
                logger.info(f"⏳ Aguardando liberação de tokens: input={contador_input}/{TPM_INPUT}, output={contador_output}/{TPM_OUTPUT}")
        await asyncio.sleep(2)

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

class AvaliacaoQA(BaseModel):
    pergunta: str
    resposta: str
    complexidade: int
    completude: int
    corretude: int
    fluidez: int
    qualidade_portugues: int
    justificativa: str

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
async def avaliar_par(llm, i, linha, id_cenario, nome_cenario, prompt, pasta_avaliacao):
    pergunta = str(linha.get("pergunta", "")).strip()
    resposta = str(linha.get("resposta", "")).strip()

    if not pergunta or not resposta:
        logger.info(f"Par inválido em {id_cenario}: pergunta ou resposta vazia.")
        return

    prompt_avaliacao = construir_prompt_avaliacao(pergunta, resposta, prompt)
    tokens_input = count_tokens(prompt_avaliacao, model="sabia-3")

    async with limiter:
        await contabilizar_tokens_e_esperar(tokens_input, 0)  # contabiliza input antes
        logger.info(f"[INÍCIO] {id_cenario}_{i+1} às {datetime.datetime.now().strftime('%H:%M:%S')}")
        start = time.perf_counter()
        try:
            response = await asyncio.to_thread(
                
                llm.beta.chat.completions.parse,
                    model = "sabia-3",
                    messages=[
                        {"role": "system", "content": "Extraia detalhes da avaliação."},
                        {"role": "user", "content": prompt_avaliacao}
                    ],
                    response_format=AvaliacaoQA
                )                        
            avaliacao = response.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Erro ao avaliar par {id_cenario}_{i+1}: {e}")
            return

        tokens_output = count_tokens(str(avaliacao), model="sabia-3")
        await contabilizar_tokens_e_esperar(0, tokens_output)  # contabiliza output após

        tempo_execucao = time.perf_counter() - start
        execucao = {
            "id_cenario": f"{id_cenario}_{i+1}",
            "nome_cenario": nome_cenario,
            "prompt": prompt_avaliacao,
            "tokens_contexto": tokens_input,
            "tokens_resposta": tokens_output,
            "max_tokens": 300,
            "tempo_execucao": tempo_execucao
        }

        salvar_execucao_csv(id_execucao, execucao)
        salvar_resposta(id_execucao, f"{id_cenario}_{i+1}_sabia-3", nome_cenario, avaliacao.model_dump_json(indent=2), pasta_saida="julgamento")
        logger.info(f"[FIM] {id_cenario}_{i+1} às {datetime.datetime.now().strftime('%H:%M:%S')}")

async def processar_cenario_async(llm, id_cenario, nome_cenario, cenario, prompt, pasta_resultado, pasta_avaliacao):
    arquivo_cenario = pasta_resultado / f"{cenario}.csv"
    if not arquivo_cenario.exists():
        logger.error(f"Arquivo não encontrado: {arquivo_cenario}")
        return

    df_cenario = pd.read_csv(arquivo_cenario, sep=";", encoding="utf-8", on_bad_lines="warn")
    df_cenario.columns = [col.strip().lower() for col in df_cenario.columns]

    tarefas = [
        avaliar_par(llm, i, linha, id_cenario, nome_cenario, prompt, pasta_avaliacao)
        for i, linha in df_cenario.iterrows()
    ]
    await asyncio.gather(*tarefas)

async def main():
    start_total = time.perf_counter()
    _ = load_dotenv(find_dotenv())

    asyncio.create_task(resetar_contadores())

    experimento_id = "ffbe36d0"
    pasta_execucao = Path(f"execucao/{experimento_id}")
    pasta_resultado = Path(f"resultado_csv/{experimento_id}/sucesso")
    pasta_avaliacao = Path(f"avaliacao/{experimento_id}")
    pasta_avaliacao.mkdir(parents=True, exist_ok=True)

    caminho_execucao = pasta_execucao / f"{experimento_id}_execucao.csv"
    if not caminho_execucao.exists():
        logger.error(f"Arquivo de execução não encontrado: {caminho_execucao}")
        return

    df_execucao = pd.read_csv(caminho_execucao, sep=";", encoding="utf-8")

    llm = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://chat.maritaca.ai/api",
    )

    for i, row in df_execucao.iterrows():

        reprocessar = [2476, 2479, 2575, 2591, 2816, 2946, 3079, 3085]
        #[100, 105, 1087, 1088, 1103, 114, 1144, 1151, 1166, 1179, 121, 1220, 1221, 1258, 128, 1341, 1361, 1362, 1363, 1364, 138, 1402, 1422, 1460, 1467, 1468, 1478, 1525, 1526, 1527, 1540, 1542, 1543, 1544, 1549, 1551, 1573, 1583, 1603, 1604, 1642, 1695, 1805, 1806, 1814, 1815, 1882, 1907, 1963, 1973, 1984, 2013, 2016, 2057, 2079, 2223, 2255, 2261, 2262, 2263, 2264, 2265, 2348, 2362, 2371, 2412, 262, 2776, 2836, 2852, 308, 3141, 33, 340, 380, 381, 396, 476, 484, 501, 545, 551, 552, 553, 554, 555, 603, 656, 668, 709, 728, 733, 734, 735, 736, 756, 760, 818, 839, 850, 851, 852, 858, 859, 865, 902, 909, 910, 911, 912, 915, 916, 922, 923, 924, 93, 94, 95]
        
        if(i + 1 not in reprocessar):
            logger.info(f"Pulando execução {i+1} de {len(df_execucao)}")
            continue

        id_cenario = i + 1
        nome_cenario = row.get("nome_cenario")
        prompt = row.get("prompt", "")
        cenario = f"{experimento_id}_{id_cenario}_{nome_cenario}"

        logger.info("-" * 80)
        logger.info(f"Execução: {id_execucao} | Cenário {id_cenario}/{len(df_execucao)}: {cenario}")
        logger.info("-" * 80)

        await processar_cenario_async(llm, id_cenario, nome_cenario, cenario, prompt, pasta_resultado, pasta_avaliacao)

    logger.info(f"Tempo total de execução: {time.perf_counter() - start_total:.2f} segundos")

if __name__ == "__main__":
    asyncio.run(main())
