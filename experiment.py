import os
import time
import requests
import textwrap
import uuid
import json
import config
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from infra.ssh_tunnel import SSHTunnel
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSON
from rdflib import Graph
from urllib.parse import quote
from utils.utils import caminho_cache_abstract
from utils.utils import caminho_cache_triplas
from utils.utils import carregar_verbalizacoes
from utils.utils import verbalizar_tripla
from utils.utils import construir_grafo_filtrado
from utils.utils import contar_tokens_prompt
from utils.utils import salvar_execucao_csv
from utils.utils import salvar_resposta_e_csv_extraido
from utils.utils import get_logger
from utils.utils import formatar_qa_em_string

id_execucao = uuid.uuid4().hex[:8] 
logger = get_logger(id_execucao)

def query_abstract(topic, idioma):
    return textwrap.dedent(f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        SELECT ?abstract WHERE {{
          <http://dbpedia.org/resource/{topic}> dbo:abstract ?abstract .
          FILTER (lang(?abstract) = '{idioma}')
        }}
        LIMIT 1
    """).strip()

def consultar_abstract_wikipedia(topico, idioma='pt'):
    
    url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{topico}"
    print(url)
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            return dados.get("extract", None)
    except Exception as e:
        logger.error(f"Falha na API da Wikipedia para '{topico}': {e}")
    return None

def consultar_abstract(topico, idioma, limit=1):
    caminho_cache = caminho_cache_abstract(topico[idioma], idioma, limit)
    
    if os.path.exists(caminho_cache):
        with open(caminho_cache, 'r', encoding='utf-8') as f:
            return json.load(f).get("abstract")

    # Tenta via DBpedia sempre em inglês
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = query_abstract(topico['en'], idioma)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        bindings = results.get("results", {}).get("bindings", [])
        if bindings:
            abstract = bindings[0]["abstract"]["value"]
            with open(caminho_cache, 'w', encoding='utf-8') as f:
                json.dump({"abstract": abstract}, f, ensure_ascii=False, indent=2)
            return abstract
    except Exception as e:
        logger.error(f"Falha ao consultar DBpedia para '{topico[idioma]}': {e}")

    # Fallback: tenta via Wikipedia REST
    abstract = consultar_abstract_wikipedia(topico[idioma], idioma)
    if abstract:
        with open(caminho_cache, 'w', encoding='utf-8') as f:
            json.dump({"abstract": abstract}, f, ensure_ascii=False, indent=2)
    return abstract

def query_triplas_relacionadas(topic, limit, idioma):
    # Define o idioma padrão como 'en' para DBpedia pois é mais completo
    idioma='en'
    term_uri = f"<http://dbpedia.org/resource/{quote(topic[idioma])}>"
    predicados = "\n".join(config.PREDICADOS_IRRELEVANTES)

    return textwrap.dedent(f"""
        PREFIX dbo:   <http://dbpedia.org/ontology/>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:   <http://www.w3.org/2002/07/owl#>
        PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
        PREFIX prov:  <http://www.w3.org/ns/prov#>
        PREFIX wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX core:  <http://purl.org/dc/terms/>

        CONSTRUCT {{
          {term_uri} ?p ?o .
          ?s ?p {term_uri} .
        }}
        WHERE {{
          {{
            {term_uri} ?p ?o .
            FILTER (
              !isLiteral(?o) || lang(?o) = "{idioma}"
            )
            FILTER NOT EXISTS {{
              VALUES ?p {{
                {predicados}
              }}
            }}
          }}
          UNION
          {{
            ?s ?p {term_uri} .
            FILTER NOT EXISTS {{
              VALUES ?p {{
                {predicados}
              }}
            }}
          }}          
        }}
        LIMIT {limit}
    """).strip()

def consultar_triplas_em_rdf(topic, limit, idioma):
    # Define o idioma padrão como 'en' para DBpedia pois é mais completo
    idioma = 'en'
    caminho_cache = caminho_cache_triplas(topic, limit)
    
    g = Graph()
    if os.path.exists(caminho_cache):
        g.parse(caminho_cache, format="turtle")
        return g

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = query_triplas_relacionadas(topic, limit, idioma=idioma)
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)

    try:
        results = sparql.query().convert()
        g.parse(data=results, format="turtle")
        g.serialize(destination=caminho_cache, format="turtle")
        return g
    except Exception as e:
        logger.error(f"Falha ao consultar triplas para '{topic}': {e}")
        return Graph()

def verbalizar_triplas(triplas_rdf, caminho_csv, idioma):
    verbalizacoes = carregar_verbalizacoes(caminho_csv, idioma)
    frases = []

    for s, p, o in triplas_rdf:
        frases.append(verbalizar_tripla(s, p, o, verbalizacoes))
    
    return frases
  
def gerar_prompt(cenario, qtd_few_shot, limit, idioma):  
    
    topico = config.TOPICOS[cenario["topico"]]
    squad, en = topico["squad"], topico["en"]
    tecnica = cenario["tecnica"]
    formato = cenario.get("formato", None)
    qtd_triplas = cenario.get("qtd_triplas", 0)

    # Consulta ao abstract com cache parametrizado por limit e idioma
    abstract = consultar_abstract(topico, idioma=idioma, limit=limit)
    if not abstract:
        return None

    # Inicializa valores default
    triplas = ""
    fewshot = ""

    grafo_filtrado = Graph()
    grafo_original = Graph()
    
    if tecnica == "few-shot-triplas":
        # Extrai few-shot do tópico fixo (pode ser ajustado futuramente)
        qas = consultar_qas(squad, 'resources/Squad.json', qtd_few_shot=qtd_few_shot)
        fewshot = formatar_qa_em_string(qas)

        logger.info(f"Few-shot: {len(qas)}")

    if tecnica == "zero-shot-triplas" or tecnica == "few-shot-triplas":
        # Consulta e processa triplas
        grafo_original = consultar_triplas_em_rdf(en, limit=limit, idioma=idioma)
        triplas_selecionadas = list(grafo_original)[:qtd_triplas]
        grafo_filtrado = construir_grafo_filtrado(triplas_selecionadas)

        logger.info(f"Triplas: {len(grafo_filtrado)}")

        if formato == "verbalizado":
            triplas = verbalizar_triplas(
                grafo_filtrado,
                'resources/predicados_verbalizados_pt_en.csv',
                idioma=idioma
            )
            triplas = "\n".join(triplas)
        elif formato == "RDF":
            triplas = grafo_filtrado.serialize(format='turtle').strip()
        else:
            raise ValueError(f"Formato inválido para few-shot: {formato}")

    # Usa a função definida para gerar o prompt com base no tipo
    prompt = gerar_prompt_texto(
        topico=topico[idioma],
        abstract=abstract.strip(),
        triplas=triplas,
        fewshot=fewshot,
        tipo=tecnica
    )

    return prompt, fewshot, grafo_filtrado

def gerar_prompt_texto(topico, abstract, triplas=None, fewshot=None, tipo='zero-shot'):
    if tipo == 'zero-shot':
        return config.PROMPT_ZERO_SHOT_PT.format(
            topico=topico            
        )
    elif tipo == 'zero-shot-triplas':
        return config.PROMPT_TRIPLAS_PT.format(
            abstract=abstract,
            triplas=triplas if triplas else '',            
        )
    elif tipo == 'few-shot-triplas':
        return config.PROMPT_FEW_SHOT_TRIPLAS_PT.format(
            abstract=abstract,
            triplas=triplas if triplas else '',
            fewshot=fewshot if fewshot else ''
        )
    else:
        raise ValueError("Tipo de cenário inválido: use 'zero-shot' ou 'few-shot'")

def chamar_modelo(llm, prompt):
    messages = [
        SystemMessage(content="You are a helpful assistant that generates quizzes."),
        HumanMessage(content=prompt),
    ]
    try:
        resposta = llm.invoke(messages)
        return resposta.content
    except Exception as e:
        logger.error(f"Erro ao chamar o modelo: {llm.model} - {e}")
        return None

def gerar_cenarios(topicos, modelos, idioma):
    temperatures = [0.7]                                #["0.3", "0.7"]
    top_ks = [40]                                       #["40", "80"]
    top_ps = [0.95]                                     #["0.85", "0.95"]
    formatos = ["RDF", "verbalizado"]
    qtd_triplas = [140]                                 #["10", "25", "50", "75", "100"]

    cenarios = []

    for topico in topicos.values():
        
        for modelo, info in modelos.items():
            for temp in temperatures:
                for top_p in top_ps:
                    for top_k in top_ks:
                        cenarios.append({
                            "topico": topico['en'],
                            "tecnica": "zero-shot",
                            "modelo": modelo,
                            "temperature": temp,
                            "top_p": top_p,
                            "top_k": top_k,
                            "max_tokens": info['max_tokens'],
                            "nome": f"{topico[idioma]}_zero-shot_{modelo}_{temp}_{top_p}_{top_k}"
                        })
        
        for formato in formatos:
            for qtd in qtd_triplas:
                for modelo, info in modelos.items():
                    for temp in temperatures:
                        for top_p in top_ps:
                            for top_k in top_ks:
                                cenarios.append({
                                    "topico": topico['en'],
                                    "tecnica": "zero-shot-triplas",
                                    "formato": formato,
                                    "qtd_triplas": qtd,
                                    "modelo": modelo,
                                    "temperature": temp,
                                    "top_p": top_p,
                                    "top_k": top_k,
                                    "max_tokens": info['max_tokens'],
                                    "nome": f"{topico[idioma]}_zero-shot-triplas_{formato}_{qtd}_{modelo}_{temp}_{top_p}_{top_k}"
                                })
                                cenarios.append({
                                    "topico": topico['en'],
                                    "tecnica": "few-shot-triplas",
                                    "formato": formato,
                                    "qtd_triplas": qtd,
                                    "modelo": modelo,
                                    "temperature": temp,
                                    "top_p": top_p,
                                    "top_k": top_k,
                                    "max_tokens": info['max_tokens'],
                                    "nome": f"{topico[idioma]}_few-shot-triplas_{formato}_{qtd}_{modelo}_{temp}_{top_p}_{top_k}"
                                })

    return cenarios

def consultar_qas(topico, caminho_arquivo, qtd_few_shot=10):
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    resultado_topico = []
    total_qas = 0

    for entrada in dados['data']:
        if entrada['title'].lower() == topico.lower():
            for paragrafo in entrada['paragraphs']:
                contexto = paragrafo['context']
                qas_formatadas = []

                for qa in paragrafo['qas']:
                    if qa.get('is_impossible', False):
                        continue
                    respostas = [resp['text'] for resp in qa.get('answers', [])]
                    if not respostas:
                        continue
                    respostas_str = ", ".join(respostas)
                    qas_formatadas.append({
                        "Pergunta": qa['question'],
                        "Resposta": respostas_str
                    })
                    total_qas += 1
                    if total_qas >= qtd_few_shot:
                        break

                if qas_formatadas:
                    resultado_topico.append({
                        "context": contexto,
                        "qas": qas_formatadas
                    })

                if total_qas >= qtd_few_shot:
                    break
            break

    if not resultado_topico:
        logger.error(f"Tópico '{topico}' não encontrado ou sem perguntas válidas.")

    return resultado_topico

def main():
    
    start_total = time.perf_counter()

    _ = load_dotenv(find_dotenv())

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
        
        topicos_teste = {
                "Huguenots": {
                "squad": "Huguenot",
                "en": "Huguenots",
                "pt": "Huguenotes"
            },
        }     
        
        cenarios = gerar_cenarios(config.TOPICOS, config.MODELOS, idioma="pt")
        
        for i, cenario in enumerate(cenarios):
            
            start = time.perf_counter()
            
            id_cenario = i+1

            logger.info("-" * 80)
            logger.info(f"Execução: {id_execucao} | Cenário {id_cenario}/{len(cenarios)}: {cenario['nome']}")
            logger.info("-" * 80)

            prompt, fewshot, triplas = gerar_prompt(cenario, qtd_few_shot=10, limit=10000, idioma="pt")
            num_tokens = contar_tokens_prompt(prompt, cenario['modelo'])
            max_tokens = cenario["max_tokens"]
            
            logger.info(f"modelo: {cenario['modelo']}, num_tokens: {num_tokens}, max_tokens: {max_tokens}")
            
            llm = ChatOllama(
                model=cenario["modelo"],
                base_url=base_url,
                temperature=float(cenario["temperature"]),
                top_p=float(cenario["top_p"]),
                top_k=int(cenario["top_k"]),
            )
            resposta = chamar_modelo(llm, prompt)

            if(resposta is None):
                logger.error(f"Falha ao gerar resposta para o cenário {cenario['nome']}. Ignorando.")
                continue
            
            logger.info(f"Tempo de execução: {time.perf_counter() - start:.2f} segundos")
            
            execucao = {
                "id_cenario": id_cenario,
                "nome_cenario": cenario["nome"],
                #"query_abstract": query_abstract(cenario['topico'], idioma="en"),
                #"query_triplas": query_triplas_relacionadas(cenario['topico'], limit=10000, idioma="en"),
                #"fewshot": fewshot,
                "triplas": len(triplas),
                "prompt": prompt,
                "numero_tokens": num_tokens,
                "max_tokens": max_tokens
            }
            salvar_execucao_csv(id_execucao, execucao)
            salvar_resposta_e_csv_extraido(id_execucao, id_cenario, cenario['nome'], resposta)

        logger.info(f"Tempo total de execução: {time.perf_counter() - start_total:.2f} segundos")

def testar_pipeline_topicos(lista_topicos, qtd_triplas, limit, idioma):
    
    for idx, topico in enumerate(lista_topicos.values(), 1):
        
        squad, en, pt = topico["squad"], topico["en"], topico["pt"]
        
        #logger.info(f"\n[{idx}/{len(lista_topicos)}] Testando topico: {topico}")

        #logger.info(query_abstract(topico, idioma=idioma))
        
        # Consultar o abstract
        abstract = consultar_abstract(topico, idioma=idioma, limit=limit)
        if abstract:
            logger.info(f"Abstract: {abstract[:100]}...")
        else:            
            continue
        
        logger.info(query_triplas_relacionadas(topico, limit=limit, idioma=idioma))
        grafo_original = consultar_triplas_em_rdf(topico, limit=limit, idioma=idioma)
        
        if len(grafo_original) == 0:        
            continue

        triplas_selecionadas = list(grafo_original)[:qtd_triplas]
        logger.info(f"Triplas selecionadas (top {qtd_triplas}): {len(triplas_selecionadas)}")

        grafo_filtrado = construir_grafo_filtrado(triplas_selecionadas)

        triplas_verbalizadas = verbalizar_triplas(grafo_filtrado, 'resources/predicados_verbalizados_pt_en.csv', idioma=idioma)
        
        logger.info("\nTriplas verbalizadas:")
        for i, frase in enumerate(triplas_verbalizadas):
            logger.info(frase)

        logger.info("\nTriplas RDF:")
        for s, p, o in grafo_filtrado:
            logger.info(f"({s}, {p}, {o})")

if __name__ == "__main__":
    main()
    """
    topicos_teste = {
            "Huguenots": {
            "squad": "Huguenot",
            "en": "Huguenots",
            "pt": "Huguenotes"
        },
    }        
    testar_pipeline_topicos(topicos_teste, qtd_triplas=140, limit=10000, idioma="pt")
    """