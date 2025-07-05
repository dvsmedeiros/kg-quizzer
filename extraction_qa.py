import os
import ast
import json
import re
import pandas as pd
import logging
import dirtyjson
import demjson3
import shutil
import config
from glob import glob
from pathlib import Path
from utils.utils import chamar_modelo
from utils.utils import get_logger
import uuid
import datetime
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from infra.ssh_tunnel import SSHTunnel

def get_active_logger(): 
    
    # Nome do script atual (sem extensão)
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Data e hora atual no formato desejado
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Nome do arquivo de log
    log_filename = f"{script_name}_{now}.log"

    log_file_path = f"logs/{log_filename}"

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        # File handler
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Adiciona os handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

def corrigir_aspas_abertas(json_str):
    def corrigir_campo(campo, texto):
        padrao = rf'("{campo}"\s*:\s*")([^"\n]*\n[^"]*?)(?=(?:,\s*"?\w+"\s*:|}}|\n))'
        return re.sub(padrao, lambda m: f'{m.group(1)}{m.group(2).strip()}"', texto)

    json_str = corrigir_campo("pergunta", json_str)
    json_str = corrigir_campo("resposta", json_str)
    return json_str

def escapar_aspas_internas(json_str):
    """
    Escapa aspas duplas internas nos valores dos campos 'pergunta' e 'resposta'.
    Exemplo: 'Quantos países têm "Amazonas" em seus nomes?' → 'Quantos países têm \"Amazonas\" em seus nomes?'
    """
    def escapar_em_campo(campo, texto):
        # Expressão para encontrar os valores de campos e escapar aspas internas
        padrao = rf'("{campo}"\s*:\s*")((?:[^"\\]|\\.)*?)(")'
        def replacer(match):
            prefixo = match.group(1)
            valor = match.group(2)
            sufixo = match.group(3)
            # Escapa aspas duplas não escapadas no valor
            valor_escapado = valor.replace('"', r'\"')
            return f'{prefixo}{valor_escapado}{sufixo}'

        return re.sub(padrao, replacer, texto, flags=re.DOTALL)

    json_str = escapar_em_campo("pergunta", json_str)
    json_str = escapar_em_campo("resposta", json_str)
    return json_str

def remover_valores_fora_da_string(json_str):
    """
    Remove conteúdo entre parênteses fora da string em campos como "resposta".
    Exemplo:
      "resposta": "texto" (nota) -> "resposta": "texto"
    """
    padrao = r'("resposta"\s*:\s*")([^"]*?)"\s*\([^)]*\)'
    return re.sub(padrao, lambda m: f'{m.group(1)}{m.group(2)}"', json_str)

PERGUNTA_ALIASES = [
    "pergunta",         # padrão esperado
    "question",         # inglês
    "Pergunta",         # maiúscula
    "Question",         # inglês com maiúscula
    "Q",                # abreviação
    "Q.", "Q:", "Q-",   # variações pontuadas
]

RESPOSTA_ALIASES = [
    "resposta",         # padrão esperado
    "answer",           # inglês
    "Resposta",         # maiúscula
    "Answer",           # inglês com maiúscula
    "A",                # abreviação
    "A.", "A:", "A-",   # variações pontuadas
]
def padronizar_chaves_qa(texto):
    for alias in PERGUNTA_ALIASES:
        texto = re.sub(rf'"{alias}"\s*:', '"pergunta":', texto)
    for alias in RESPOSTA_ALIASES:
        texto = re.sub(rf'"{alias}"\s*:', '"resposta":', texto)
    return texto

def limpar_json_extra(resposta: str) -> str:
    """
    Limpeza extra para ajudar na sanitização do JSON:
    - Remove blocos <think>...</think>
    - Remove espaços indesejados antes de ":" e ","
    - Normaliza quebras de linha internas dentro de strings
    """
    # Remove blocos <think>...</think>
    resposta = re.sub(r"<think>.*?</think>", "", resposta, flags=re.DOTALL)

    # Remove espaços antes de ":" e ","
    resposta = re.sub(r'\s+(:|,)', r'\1', resposta)

    # Normaliza aspas fantasmas (ex: “texto”) e BOM
    resposta = resposta.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
    resposta = resposta.replace("\ufeff", "")
    resposta = resposta.replace("\\\\", "\\")

    # Substitui quebras de linha entre strings por \n explícito
    resposta = re.sub(r'(?<=")\s*\n\s*(?=")', r'\\n', resposta)

    return resposta

def corrigir_json_quebrado_final(json_str):
    """
    Corrige entradas JSON onde o último objeto está malformado (ex: falta de fechamento).
    Remove objetos claramente inválidos ou incompletos.
    """
    try:
        # Tenta carregar normalmente
        json.loads(json_str)
        return json_str
    except Exception:
        # Se falhar, tenta sanitizar removendo entradas claramente quebradas no final
        objetos = re.findall(r'{.*?}', json_str, re.DOTALL)
        objetos_corrigidos = []
        for obj in objetos:
            try:
                json.loads(obj)
                objetos_corrigidos.append(obj)
            except Exception:
                continue
        if objetos_corrigidos:
            return "[" + ",".join(objetos_corrigidos) + "]"
        return None

def extrair_perguntas_respostas_aprimorado(texto: str):
    texto_limpo = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL)
    resultados = []

    # Padrão 1: "1. Pergunta?\nResposta: ..."
    matches1 = re.findall(
        r"\d+\.\s*\*?\*?(.*?)\?[^\n]*\n\s*[Rr]esposta\s*[:\-–]\s*(.*?)(?=(\n\d+\.|\Z))",
        texto_limpo,
        flags=re.DOTALL,
    )
    for pergunta, resposta, _ in matches1:
        resultados.append({
            "pergunta": pergunta.strip() + "?",
            "resposta": resposta.strip()
        })

    # Padrão 2: "**Pergunta:** ...\n- **Resposta:** ..."
    matches2 = re.findall(
        r"\*\*Pergunta:\*\*\s*(.*?)\s*[\r\n]+\s*[-–•]*\s*\*\*Resposta:\*\*\s*(.*?)(?=(\n\d+\.|\n\*\*Pergunta:|\Z))",
        texto_limpo,
        flags=re.DOTALL,
    )
    for pergunta, resposta, _ in matches2:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 3: "1. **Pergunta:** ...\n   - **Resposta:** ..."
    matches3 = re.findall(
        r"\d+\.\s*\*\*Pergunta:\*\*\s*(.*?)\s*[\r\n]+\s*[-–•]+\s*\*\*Resposta:\*\*\s*(.*?)(?=(\n\d+\.|\n\*\*Pergunta:|\Z))",
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta, _ in matches3:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 4: "**Question**: ...\n**Answer**: ..."
    matches4 = re.findall(
        r"\*\*Question\*\*\s*[:：]\s*(.*?)\s*[\r\n]+\s*\*\*Answer\*\*\s*[:：]\s*(.*?)(?=(\n\d+\.|\n\*\*Question:|\Z))",
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta, _ in matches4:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 5: **pergunta:** "..." \n **resposta:** "..."
    matches5 = re.findall(
        r'\d+\.\s+\*\*pergunta:\*\*\s*"(.*?)"\s*\n\s*\*\*resposta:\*\*\s*"(.*?)"',
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for pergunta, resposta in matches5:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 6: **Pergunta: ...** \n **Resposta:** ...
    matches6 = re.findall(
        r'\d+\.\s+\*\*Pergunta:\s*(.*?)\*\*\s*\n\s*\*\*Resposta:\*\*\s*(.*?)(?=(\n\d+\.|\Z))',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta, _ in matches6:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 7: Inline — Ex: 1. "Pergunta?" — "Resposta."
    matches7 = re.findall(
        r'\d+\.\s*["“](.*?)["”]\s*[—\-]\s*["“](.*?)["”]',
        texto_limpo,
        flags=re.DOTALL,
    )
    for pergunta, resposta in matches7:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 8: Inline com aspas seguidas: 1. "Pergunta?" "Resposta."
    matches8 = re.findall(
        r'\d+\.\s*["“](.*?)["”]\s+["“](.*?)["”]',
        texto_limpo,
        flags=re.DOTALL,
    )
    for pergunta, resposta in matches8:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 9: Pergunta com "**pergunta:** ..." e próxima linha com "**resposta:** ..."
    matches9 = re.findall(
        r'\d+\.\s+\*\*pergunta:\*\*\s*(.*?)\??\s*\n\s*\*\*resposta:\*\*\s*(.*?)(?=(\n\d+\.|\Z))',
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE
    )
    for pergunta, resposta, _ in matches9:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    # Padrão 10: Pergunta simples numerada \n Answer: resposta
    matches10 = re.findall(
        r'\d+\.\s+(.*?\?)\s*\n\s*Answer\s*[:\-–]\s*(.*?)(?=(\n\d+\.|\Z))',
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for pergunta, resposta, _ in matches10:
        resultados.append({
            "pergunta": pergunta.strip(),
            "resposta": resposta.strip()
        })
    
    # Padrão 11: Pergunta com "Q: ..." e resposta com "A: ..."
    matches11 = re.findall(
        r"Q[:\-–]?\s*(.*?)\s*[\r\n]+A[:\-–]?\s*(.*?)(?=(\nQ[:\-–]|\Z))",
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for pergunta, resposta, _ in matches11:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches12 = re.findall(
        r'\|\s*(.*?)\?\s*\|\s*(.*?)\s*\|',
        texto_limpo
    )
    for pergunta, resposta in matches12:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })
    
    matches13 = re.findall(
        r'\d+\.\s*(.*?\?)\s*\n\s*Answer:\s*(.*?)(?=\n\d+\.|\Z)',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta in matches13:
        resultados.append({
            "pergunta": pergunta.strip(),
            "resposta": resposta.strip()
        })

    matches14 = re.findall(
        r'\*\*pergunta:\*\*\s*(.*?)\s*\n\s*\*\*resposta:\*\*\s*(.*?)(?=(\n\*\*pergunta:\*\*|\Z))',
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for pergunta, resposta, _ in matches14:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches15 = re.findall(
        r"\*\*Pergunta\s*\d+\s*:\*\*\s*(.*?)\s*\n\s*\*\*Resposta\s*\d+\s*:\*\*\s*(.*?)(?=\n\*\*Pergunta\s*\d+\s*:\*\*|\Z)",
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta in matches15:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })
    
    matches16 = re.findall(
        r"\*\s*Pergunta\s*:\s*(.*?)\n\s*Resposta\s*:\s*(.*?)(?=\n\*|$)",
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE
    )
    for pergunta, resposta in matches16:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches17 = re.findall(
        r"^(.{5,100}?)\s*;\s*(.{1,300}?)$",
        texto_limpo,
        flags=re.MULTILINE
    )
    for pergunta, resposta in matches17:
        if pergunta.strip().endswith("?"):
            resultados.append({
                "pergunta": pergunta.strip(),
                "resposta": resposta.strip()
            })

    matches18 = re.findall(
        r"### Pair \d+\s+\*\*Question:\*\*\s*(.*?)\s*\n\s*\*\*Answer:\*\*\s*(.*?)(?=\n### Pair|\Z)",
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta in matches18:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })
    
    matches19 = re.findall(
        r"Pergunta:\s*(.*?)\n+Resposta:\s*(.*?)(?:\n+[-–]{3,}|$)",
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for pergunta, resposta in matches19:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches20 = re.findall(
        r"\*\*Pergunta\s*\d+\s*:\*\*\s*(.*?)\s*\n\s*\*\*Resposta\s*:\*\*\s*(.*?)(?=\n\*\*Pergunta|\Z)",
        texto_limpo,
        flags=re.DOTALL | re.IGNORECASE
    )
    for pergunta, resposta in matches20:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })
    
    # Padrão 21: Aspas seguidas com ou sem separador (–, —, espaço ou nada)
    matches21 = re.findall(
        r'\d+\.\s*"(.*?)"\s*(?:—|–|-)?\s*"(.*?)"',
        texto_limpo
    )
    for pergunta, resposta in matches21:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches22 = re.findall(
        r'^\s*(.*?)\?\s*\n\s*Resposta\s*[:\-–]?\s*(.*?)\.\s*$',
        texto_limpo,
        flags=re.MULTILINE
    )
    for pergunta, resposta in matches22:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })
    
    matches23 = re.findall(
        r'### \*\*Question \d+:\*\*\s*\n\*\*"(.+?)"\s*\n\*\*"(.+?)"\*\*',
        texto_limpo
    )
    for pergunta, resposta in matches23:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches24 = re.findall(
        r'###\s*Q\d+\s*:\s*(.*?)\n((?:\s*-\s*A\d+\s*:\s*.*\n?)+)',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, bloco_respostas in matches24:
        respostas = re.findall(r'-\s*A\d+\s*:\s*(.*)', bloco_respostas)
        resposta_final = ' '.join([r.strip() for r in respostas])
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta_final
        })
    
    matches25 = re.findall(
        r'\*\*\d+\.\*\*\s*(.*?)\?\s*\n\*\*Resposta:\*\*\s*(.*?)(?=(\n\*\*\d+\.|\Z))',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta, _ in matches25:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches26 = re.findall(
        r"\*\*Question:\*\*\s*(.*?)\s*\n\s*\*\*Answer:\*\*\s*(.*?)(?=\n---|\Z)",
        texto_limpo,
        flags=re.DOTALL,
    )
    for pergunta, resposta in matches26:
        resultados.append({
            "pergunta": pergunta.strip().rstrip("?") + "?",
            "resposta": resposta.strip()
        })

    matches_g1 = re.findall(
        r'\d+\.\s+\*\*(.*?)\?\*\*',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta in matches_g1:
        resultados.append({
            "pergunta": pergunta.strip() + "?",
            "resposta": ""
        }) 

    matches_g2 = re.findall(
        r'\d+\.\s+\*?\*?(.*?\?)\*?\*?\s*(?:\((.*?)\))?',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta in matches_g2:
        resultados.append({
            "pergunta": pergunta.strip(),
            "resposta": resposta.strip() if resposta else ""
        })
    
    matches_g3 = re.findall(
        r'\d+\.\s+(.*?\?)\s*(?:(?!\d+\.).*?\b([A-Z][a-zA-Z0-9\-]{2,}))?',
        texto_limpo,
        flags=re.DOTALL
    )
    for pergunta, resposta in matches_g3:
        resultados.append({
            "pergunta": pergunta.strip(),
            "resposta": resposta.strip() if resposta else ""
        })
    
    return resultados if resultados else None

def limpar_resultados_qa(resultados: list[dict]) -> list[dict]:
    blacklist_respostas = [
        "Desculpe, não posso responder", 
        "Essa é uma boa pergunta", 
        "Como modelo de linguagem",
        "Infelizmente não tenho essa informação",
        "Desculpe, mas não posso ajudar com isso"
    ]

    def limpar_texto(texto: str, is_pergunta=False) -> str:
        texto = texto.strip()

        # Remover markdown básico
        texto = texto.replace("**", "")

        # Substituições padrão
        texto = texto.replace("\n", " ")
        texto = re.sub(r'\s+', ' ', texto)  # normalizar espaços
        texto = re.sub(r'\s+([.,!?;:])', r'\1', texto)  # espaço antes de pontuação
        texto = re.sub(r'([?.!]){2,}', r'\1', texto)  # remover pontuação duplicada
        texto = re.sub(r'^["\']|["\']$', '', texto)  # aspas externas
        texto = re.sub(r'["]{2,}', '"', texto)  # aspas internas duplicadas

        # Remover prefixos e tokens especiais
        texto = re.sub(r'^(Q\d+:|P:|[-•*]\s*|\d+\.\s*)', '', texto)
        texto = re.sub(r'[\[\]<>|#_]', '', texto)
        texto = re.sub(r'\b(Pergunta|Resposta)\b', '', texto, flags=re.IGNORECASE)
        texto = re.sub(r'^(Question|Pergunta|Resposta|Answer)\s*[:\-]\s*', '', texto, flags=re.IGNORECASE)

        # Substituição de aspas tipográficas
        texto = texto.replace("“", "\"").replace("”", "\"")
        texto = texto.replace("‘", "'").replace("’", "'")

        # Padronização de capitalização
        texto = texto.strip()
        if texto:
            if is_pergunta:
                texto = texto[0].upper() + texto[1:]
            else:
                texto = texto[0].lower() + texto[1:]

        return texto.strip()

    mapa_perguntas = {}

    for item in resultados:
        pergunta = limpar_texto(item.get("pergunta", ""), is_pergunta=True)
        resposta = limpar_texto(item.get("resposta", ""), is_pergunta=False)

        if not pergunta or not resposta:
            continue

        if len(pergunta.split()) < 3 or re.fullmatch(r"[?\.…]+", pergunta):
            continue

        if not pergunta.endswith("?"):
            pergunta += "?"

        if "?" in resposta:
            continue

        if any(black in resposta.lower() for black in blacklist_respostas):
            continue

        if len(resposta.split()) > 60:
            continue

        if pergunta not in mapa_perguntas or (resposta and not mapa_perguntas[pergunta]):
            mapa_perguntas[pergunta] = resposta

    resultados_limpos = [
        {"pergunta": p, "resposta": r}
        for p, r in mapa_perguntas.items()
        if r and not "?" in r  # segurança adicional
    ]

    return resultados_limpos

def extrair_json_de_resposta(resposta: str, fallback=False) -> str:
    if(fallback):        
        logger.info("Fallback resposta")        
        logger.info(resposta)
        
    """
    Extrai um JSON de perguntas e respostas a partir de uma resposta textual.

    Estratégia em etapas:
    1. Bloco Markdown ```json ... ```
    2. Bloco entre colchetes: [ {...}, {...} ]
    3. Vários objetos soltos entre chaves
    4. Regex textual de pergunta/resposta

    Retorna:
        Uma string JSON se encontrada, senão None.
    """
    # 1. Bloco entre ```json ... ```
    bloco_json = re.search(r"```json\s*($begin:math:display$.*?$end:math:display$)\s*```", resposta, re.DOTALL)
    if bloco_json:
        return bloco_json.group(1).strip()

    # 2. Bloco JSON simples entre colchetes
    match = re.search(r'\[\s*{.*?}\s*\]', resposta, re.DOTALL)
    if match:
        return match.group(0).strip()

    # 3. Vários objetos JSON soltos
    blocos = re.findall(r'{[^{}]*}', resposta, re.DOTALL)
    if blocos:
        return "[" + ",".join(blocos) + "]"

    # 4. Padrão textual: pergunta: "...", resposta: "..."
    matches_raw = re.findall(
        r'pergunta\s*[:=]\s*"(.*?)"\s*,?\s*resposta\s*[:=]\s*"(.*?)"',
        resposta,
        re.DOTALL | re.IGNORECASE
    )

    if matches_raw:
        matches = json.dumps(
            [{"pergunta": p.strip(), "resposta": r.strip()} for p, r in matches_raw],
            ensure_ascii=False
        )
        matches = re.sub(r',\s*([\]}])', r'\1', matches)
        matches = re.sub(r'(?<!\\)"\s*\n\s*"', r'\\n', matches)
        matches = corrigir_aspas_abertas(matches)
        matches = remover_valores_fora_da_string(matches)
        matches = padronizar_chaves_qa(matches)
        matches = corrigir_json_quebrado_final(matches)

        if(fallback):            
            logger.info("Fallback JSON extraído")
            logger.info(matches)       
                 
        return matches
    else:
        return None

def salvar_resposta_e_csv_extraido(llm, id_execucao, id_cenario, cenario, resposta, pasta_saida="resultado"):
    logger = get_active_logger()
    os.makedirs(pasta_saida, exist_ok=True)

    nome_base = f"{id_execucao}_{id_cenario}_{cenario}"
    caminho_txt = os.path.join(pasta_saida, f"{nome_base}.txt")
    caminho_csv = os.path.join(pasta_saida, f"{nome_base}.csv")    

    # Salvar sempre o .txt original
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(resposta)

    dados = []

    try:
        resposta = limpar_json_extra(resposta)
        json_str = extrair_json_de_resposta(resposta)

        if not json_str:
            # Tentar fallback com regex estruturado se JSON não foi encontrado
            # fallback_resultado = extrair_perguntas_respostas_aprimorado(resposta)
            # fallback_resultado = limpar_resultados_qa(fallback_resultado)
            # df = pd.DataFrame(fallback_resultado)

            # os.makedirs("bla", exist_ok=True)
            #x = df.to_json(caminho_csv.replace(pasta_saida, "bla").replace(".csv", ".json"), orient="records", force_ascii=False, indent=4)            
            prompt = config.PROMPT_EXTRACAO_JSON.format(resposta=resposta)

            #print("*" * 50)
            #print("Fallback prompt")
            #print(prompt)
            #print("*" * 50)

            fallback_resultado = chamar_modelo(llm, prompt)            
            fallback_resultado = limpar_json_extra(fallback_resultado)
            fallback_resultado = extrair_json_de_resposta(fallback_resultado, fallback=True)

            if fallback_resultado:
                json_str = fallback_resultado                
                logger.info(f"[{nome_base}] Status: SUCESSO (extraído via fallback regex com {len(fallback_resultado)} pares)")                
            else:    
                logger.error(f"JSON não encontrado no cenário '{nome_base}'.")
                return "erro"
        
        if not json_str:
            logger.error(f"Falha ao corrigir JSON no cenário '{nome_base}' (JSON muito corrompido).")
            return "warning"

        try:
            dados = demjson3.decode(json_str)
        except Exception:
            try:
                dados = demjson3.decode(json_str.encode("utf-8").decode("unicode_escape"))
            except Exception:
                try:
                    dados = ast.literal_eval(json_str)
                except Exception as e:                    
                    logger.error(f"Falha ao decodificar JSON no cenário '{nome_base}': {str(e)}")
                    prompt = config.PROMPT_EXTRACAO_JSON.format(resposta=resposta)
                    fallback_resultado = chamar_modelo(llm, prompt)            
                    fallback_resultado = limpar_json_extra(fallback_resultado)
                    fallback_resultado = extrair_json_de_resposta(fallback_resultado, fallback=True)

                    if fallback_resultado:
                        json_str = fallback_resultado                
                        logger.info(f"[{nome_base}] Status: SUCESSO (extraído via fallback regex)")

                        try:
                            dados = demjson3.decode(json_str)
                        except Exception:
                            try:
                                dados = json.loads(json_str)
                            except Exception as e:
                                logger.error(f"Erro ao decodificar o fallback JSON no cenário '{nome_base}': {e}")
                                return "erro"

                        if not dados:
                            logger.error(f"[{nome_base}] JSON extraído, mas o conteúdo está vazio.")
                            return "erro"
                    else:    
                        logger.error(f"JSON não encontrado no cenário '{nome_base}'.")
                        return "erro"
                            
        if not isinstance(dados, list):
            dados = [dados]

        dados_corrigidos = []
        for item in dados:
            if isinstance(item, list):
                try:
                    item = dict(item)
                except Exception:
                    continue
            dados_corrigidos.append(item)
        dados = dados_corrigidos

        for item in dados:
            if "pergunta" not in item:
                for k in list(item.keys()):
                    if isinstance(item[k], str) and "?" in item[k]:
                        item["pergunta"] = item.pop(k)
                        break

        dados_validos = []        

        for item in dados:
            pergunta = item.get("pergunta", "").strip()
            resposta_txt = item.get("resposta", "").strip()

            pergunta = pergunta.replace("\\\\", "\\").replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
            resposta_txt = resposta_txt.replace("\\\\", "\\").replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

            pergunta = re.sub(r'^["\']|["\']$', '', pergunta)
            resposta_txt = re.sub(r'^["\']|["\']$', '', resposta_txt)

            item["pergunta"] = pergunta
            item["resposta"] = resposta_txt
            
            dados_validos.append(item)            

        if dados_validos:
            df = pd.DataFrame(dados_validos)
            df.drop_duplicates(subset=["pergunta", "resposta"], inplace=True)
            df.to_csv(caminho_csv, sep=";", index=False)
            logger.info(f"[{nome_base}] Status: SUCESSO ({len(dados_validos)} válidos")            
            return "sucesso"
        else:        
            return "warning"

    except Exception as e:        
        logger.error(f"[{nome_base}] Erro inesperado: {str(e)}")
        return "erro"

import shutil
from glob import glob

def extrair_json_resultado(llm, diretorio_falhas="sem_extracao", pasta_saida="resultado_lote"):
    logger = get_active_logger()
    arquivos = sorted(Path(diretorio_falhas).glob("*.txt"))
    total = len(arquivos)
    contadores = {"sucesso": 0, "warning": 0, "erro": 0, "descartado": 0}
    resultados = []

    if total == 0:
        logger.error(f"Nenhum arquivo .txt encontrado em {diretorio_falhas}")
        return

    for i, arquivo in enumerate(arquivos):
        with open(arquivo, encoding="utf-8") as f:
            conteudo = f.read()

        partes = arquivo.stem.split("_")
        id_execucao = partes[0]
        id_cenario = partes[1]        
        cenario = "_".join(partes[2:])  

        nome_base = f"{id_execucao}_{id_cenario}_{cenario}"        

        pasta_tmp = os.path.join(pasta_saida, "_tmp")
        os.makedirs(pasta_tmp, exist_ok=True)

        # Gera os arquivos na pasta temporária
        status = salvar_resposta_e_csv_extraido(
            llm,
            id_execucao=id_execucao,
            id_cenario=id_cenario,
            cenario=cenario,
            resposta=conteudo,
            pasta_saida=pasta_tmp
        )

        resultados.append((cenario, status))
        contadores[status] = contadores.get(status, 0) + 1

        # Move arquivos com o prefixo para a pasta de status
        origem_prefixo = os.path.join(pasta_tmp, nome_base)
        destino_pasta = os.path.join(pasta_saida, status)
        os.makedirs(destino_pasta, exist_ok=True)

        for caminho_origem in glob(f"{origem_prefixo}*"):
            caminho_destino = os.path.join(destino_pasta, os.path.basename(caminho_origem))
            shutil.move(caminho_origem, caminho_destino)

    # Remove tmp se vazio
    tmp_final = os.path.join(pasta_saida, "_tmp")
    if os.path.exists(tmp_final) and not os.listdir(tmp_final):
        os.rmdir(tmp_final)

    logger.info("\n===== RESUMO FINAL (DIRETÓRIO) =====")
    for k, v in contadores.items():
        logger.info(f"{k.upper()}: {v} arquivos ({(v/total*100):.2f}%)")
    logger.info(f"TOTAL: {total} arquivos\n")

    # Salva o CSV com o resumo
    df_resultados = pd.DataFrame(resultados, columns=["cenario", "status"])
    df_resultados.to_csv(os.path.join(pasta_saida, "resumo_status.csv"), sep=";", index=False)
    logger.info(f"Resumo detalhado salvo em: {pasta_saida}/resumo_status.csv")

if __name__ == "__main__":
    
    id_execucao = uuid.uuid4().hex[:8] 
    logger = get_logger(id_execucao)
    logger = get_active_logger()

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
            model="gemma3:27b",
            base_url=base_url,            
        )

        # Exemplo 1: Testar todos os arquivos de um diretório
        experimento_id = "ffbe36d0"  # Substitua pelo ID do experimento desejado
        extrair_json_resultado(llm, f"resultado_csv_6/{experimento_id}/erro", pasta_saida=f"resultado_csv_7/{experimento_id}")        
    
    
