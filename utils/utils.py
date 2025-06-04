import logging
import os
import re
import csv
import pandas as pd
import config
from transformers import AutoTokenizer
from rdflib import Literal, BNode
from rdflib import Graph, URIRef

_logger = None  # logger global interno

_logger = None

def get_logger(id_execucao: str, pasta_base: str = "execucao"):
    global _logger
    if _logger is not None:
        return _logger

    os.makedirs(os.path.join(pasta_base, id_execucao), exist_ok=True)
    caminho_log = os.path.join(pasta_base, id_execucao, f"{id_execucao}.log")

    logger = logging.getLogger("execucao_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        file_handler = logging.FileHandler(caminho_log, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    _logger = logger
    return logger

def get_active_logger():
    """
    Retorna o logger configurado globalmente após chamada de `get_logger(...)`.
    """
    global _logger
    if _logger is None:
        raise RuntimeError("Logger ainda não foi configurado. Use get_logger(id_execucao) antes.")
    return _logger

def csv_escape(text):
    if text is None:
        return ""
    text = str(text)
    if ";" in text or "\n" in text or "\"" in text:
        text_escaped = text.replace('"', '""')
        return f'"{text_escaped}"'
    return text

def salvar_execucao_csv(id_execucao, execucao, pasta_saida="execucao"):
    logger = get_active_logger()
    pasta_saida = os.path.join(pasta_saida, id_execucao)
    os.makedirs(pasta_saida, exist_ok=True)

    nome_arquivo = f"{id_execucao}_execucao.csv"
    caminho_arquivo = os.path.join(pasta_saida, nome_arquivo)

    arquivo_existe = os.path.exists(caminho_arquivo)

    with open(caminho_arquivo, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        if not arquivo_existe:
            writer.writerow([
                "id_cenario",
                "nome_cenario",
                #"query_abstract",
                #"query_triplas",
                #"fewshot",
                "triplas",
                "prompt",
                "numero_tokens",
                "max_tokens"
            ])

        writer.writerow([
            execucao.get("id_cenario", ""),
            csv_escape(execucao.get("nome_cenario", "")),
            #csv_escape(execucao.get("query_abstract", "")),
            #csv_escape(execucao.get("query_triplas", "")),
            #csv_escape(execucao.get("fewshot", "")),
            csv_escape(execucao.get("triplas", "")),
            csv_escape(execucao.get("prompt", "")),
            execucao.get("numero_tokens", ""),
            execucao.get("max_tokens", "")
        ])

    logger.info(f"Execução adicionada em: {caminho_arquivo}")

def salvar_resposta_e_csv_extraido(id_execucao, id_cenario, cenario, resposta, pasta_saida="resultado"):
    logger = get_active_logger()
    pasta_saida += f"/{id_execucao}"

    os.makedirs(pasta_saida, exist_ok=True)

    nome_base = f"{id_execucao}_{id_cenario}_{cenario}"
    caminho_txt = os.path.join(pasta_saida, f"{nome_base}.txt")
    caminho_csv = os.path.join(pasta_saida, f"{nome_base}.csv")

    # Salva resposta bruta
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(resposta)

    # Extrai CSV e salva
    csv_formatado = extrair_csv_pergunta_resposta(resposta)
    with open(caminho_csv, "w", encoding="utf-8") as f:
        f.write(csv_formatado)

    logger.info(f"Arquivos salvos em:")
    logger.info(caminho_txt)
    logger.info(caminho_csv)
    logger.info(resposta)
    logger.info("-" * 80)
    logger.info(f"CSV")
    logger.info("-" * 80)
    logger.info(f"{csv_formatado}")

def extrair_csv_pergunta_resposta(texto):
    """
    Extrai linhas válidas no formato 'pergunta;resposta' e garante que a primeira linha seja o cabeçalho.
    Também tenta corrigir linhas onde ',' foi usado como separador.
    """
    logger = get_active_logger()

    padrao = re.compile(
        r'^[^;\n\r]{3,}\??\s*;[^;\n\r]{2,}$',  # padrão correto
        re.MULTILINE
    )
    
    linhas = padrao.findall(texto)

    # Se não encontrar nenhuma linha com ';', tenta encontrar com ',' como fallback
    if not linhas:
        padrao_virgula = re.compile(
            r'^[^,\n\r]{3,}\??\s*,[^,\n\r]{2,}$',  # mesmo padrão mas com ','
            re.MULTILINE
        )
        linhas_virgula = padrao_virgula.findall(texto)
        if linhas_virgula:
            logger.info("[AVISO] Substituindo ',' por ';' nas linhas do modelo.")
            linhas = [linha.replace(",", ";") for linha in linhas_virgula]

    if not linhas:
        return "pergunta;resposta"

    if linhas[0].strip().lower() != "pergunta;resposta":
        linhas.insert(0, "pergunta;resposta")

    return "\n".join(linhas)

def formatar_qa_em_string(qa_por_topico):
    partes = []
    #for i, item in enumerate(qa_por_topico, 1):
    #    contexto = item.get("context", "").strip()
    #    partes.append(f"\n{contexto}\n")
    partes.append("pergunta;resposta")
    for i, item in enumerate(qa_por_topico, 1):
        for qa in item.get("qas", []):
            pergunta = qa.get("Pergunta", "").strip()
            resposta = qa.get("Resposta", "").strip()

            # Garante interrogação ao final da pergunta
            if not pergunta.endswith("?"):
                pergunta += "?"

            partes.append(f"{pergunta};{resposta}")            

    return "\n".join(partes)

# Mapeamento com aproximações seguras ou placeholders
MAPA_MODELOS_TOKENIZERS = {    
    "qwen3": "Qwen/Qwen1.5-7B",  # aproximação para Qwen3
    "qwen": "Qwen/Qwen1.5-7B",
    "qwen2.5": "Qwen/Qwen1.5-7B",
    "qwen2.5-coder": "Qwen/Qwen1.5-7B-Chat",

    # Mistral
    "mistral": "mistralai/Mistral-7B-v0.1",
    "mistral-small": "mistralai/Mistral-7B-v0.1",
    "mistral-small3.1": "mistralai/Mistral-7B-v0.1",
    "mistral-nemo": "mistralai/Mistral-7B-v0.1",

    # Gemma
    "gemma3": "google/gemma-7b",

    # LLaMA
    "llama3": "meta-llama/Meta-Llama-3-8B",
    "llama3.1": "meta-llama/Meta-Llama-3-70B",
    "llama3.2": "meta-llama/Meta-Llama-3-8B",
    "llama3.3": "meta-llama/Meta-Llama-3-70B",  # aproximação
    "llama3.2-vision": "meta-llama/Meta-Llama-3-8B",  # sem tokenizer visual oficial

    # CodeGemma
    "codegemma": "google/codegemma-2b",

    # Orca
    "orca-mini": "microsoft/Phi-2",  # aproximação para OrcaMini

    # DeepSeek
    "deepseek-r1": "deepseek-ai/deepseek-llm-7b-base",

    # StarCoder
    "starcoder2": "bigcode/starcoder2-7b",

    # CodeLLaMA
    "codellama": "codellama/CodeLlama-7b-hf",

    # OpenChat / Dolphin
    "openchat": "openchat/openchat-3.5-0106",
    "dolphin3": "openchat/openchat-3.5-0106",

    # Granite e Sabiá (placeholders)
    "granite3.1-dense": "mistralai/Mistral-7B-v0.1",

    # Sabiá    
    "sabia-3": "maritaca-ai/sabia-7b",
    "sabia-3.1": "maritaca-ai/sabia-7b",
    "sabiazinho-3": "maritaca-ai/sabia-7b",

    # QWQ (sem equivalente exato conhecido)
    "qwq": "Qwen/Qwen1.5-7B",  # aproximação

    # Phi
    "phi4": "microsoft/Phi-2",  # aproximação para Phi-4
}

def contar_tokens_prompt(prompt: str, modelo_nome: str):
    logger = get_active_logger()
    modelo_lower = modelo_nome.lower()

    if modelo_lower not in config.MODELOS:
        logger.error(f"Modelo '{modelo_nome}' não encontrado em MODELOS.")
        return None

    tokenizer_nome = config.MODELOS[modelo_lower]["tokenizer"]

    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_nome)
        num_tokens = len(tokenizer.encode(prompt))
        return num_tokens
    except Exception as e:
        logger.error(f"Falha ao carregar tokenizer '{tokenizer_nome}' para o modelo '{modelo_nome}': {e}")
        return None

def limpar_elemento(elem):
    if isinstance(elem, URIRef):
        return re.sub(r'^.*[/#]', '', str(elem)).replace("_", " ")
    elif isinstance(elem, Literal):
        return str(elem).replace("_", " ")
    elif isinstance(elem, BNode):
        return "[nó anônimo]"
    else:
        return str(elem).replace("_", " ")

def verbalizar_tripla(sujeito, predicado_uri, objeto, verbalizacoes):
    sujeito_str = limpar_elemento(sujeito)
    objeto_str = limpar_elemento(objeto)
    predicado = verbalizacoes.get(str(predicado_uri), str(predicado_uri))
    return f"{sujeito_str} {predicado} {objeto_str}"

def carregar_verbalizacoes(caminho_csv, idioma='pt'):
    colunas = {
        'pt': 'verbalizacao_pt',
        'en': 'verbalizacao_en'
    }
    if idioma not in colunas:
        raise ValueError("Idioma inválido. Use 'pt' ou 'en'.")

    df = pd.read_csv(caminho_csv, sep=";")
    return dict(zip(df['uri'], df[colunas[idioma]]))

def construir_grafo_filtrado(triplas_relevantes):
    logger = get_active_logger()
    grafo_filtrado = Graph()

    for s, p, o in triplas_relevantes:
        try:
            s_uri = URIRef(str(s))
            p_uri = URIRef(str(p))

            # Decide se 'o' será URI ou Literal
            o_str = str(o)
            if o_str.startswith("http://") or o_str.startswith("https://"):
                o_node = URIRef(o_str)
            else:
                o_node = Literal(o_str)

            grafo_filtrado.add((s_uri, p_uri, o_node))

        except Exception as e:
            logger.error(f"Tripla ignorada por erro de URI: ({s}, {p}, {o}) — {e}")

    return grafo_filtrado

def caminho_cache_triplas(topic, limit, pasta_cache="cache/triplas"):
    os.makedirs(pasta_cache, exist_ok=True)
    nome_arquivo = f"{topic}_lim{limit}.ttl"
    return os.path.join(pasta_cache, nome_arquivo)

def caminho_cache_abstract(topic, idioma, limit, pasta_cache="cache/abstracts"):
    os.makedirs(pasta_cache, exist_ok=True)
    nome_arquivo = f"{topic}_{idioma}_lim{limit}.json"
    return os.path.join(pasta_cache, nome_arquivo)

"""
def coletar_predicados_filtrados(topicos, limit, idioma):
    logger = get_active_logger()
    predicados_unicos = set()

    for idx, (_, _, topico) in enumerate(topicos, 1):
        if not topico:
            continue

        logger.info(f"[{idx}/{len(topicos)}] Consultando triplas para: {topico}")
        g = consultar_triplas_em_rdf(topico, limit, idioma=idioma)
        
        for _, p, _ in g:
            predicados_unicos.add(str(p))

    logger.info(f"\nTotal de predicados únicos filtrados: {len(predicados_unicos)}")
    return sorted(predicados_unicos)
"""


