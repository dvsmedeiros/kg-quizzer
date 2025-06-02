PROMPT_ZERO_SHOT_PT = """ 
Você é um gerador de questões de avaliação baseado em conhecimento semântico.

## Instruções

A tarefa consiste em gerar **10 pares pergunta;resposta** no formato CSV:
- **1 pergunta** relevante ao contexto
- **1 resposta correta** curta (até 10 palavras)
- **Idioma** português
- **Separador**: ponto e vírgula (`;`)
- **Saída**: apenas um CSV no formato `pergunta;resposta`

### Exemplo de formato esperado:
```
pergunta;resposta
<pergunta 1>;<resposta 1>
<pergunta 2>;<resposta 2>
<pergunta 3>;<resposta 3>
<pergunta 4>;<resposta 4>
<pergunta 5>;<resposta 5>
<pergunta 6>;<resposta 6>
<pergunta 7>;<resposta 7>
<pergunta 8>;<resposta 8>
<pergunta 9>;<resposta 9>
<pergunta 10>;<resposta 10>
```

### Contexto
```
{abstract}
```
---
## Instrução Final
Gere agora o CSV conforme Instruções e Regras.
""".strip()

PROMPT_TEMPLATE_PT = """
Você é um gerador de questões de avaliação baseado em conhecimento semântico.

## Instruções

A tarefa consiste em gerar **10 pares pergunta;resposta ** no formato CSV, contendo:
- **1 pergunta** relevante ao contexto   
- **1 resposta correta** curta (até 10 palavras)  
- **Idioma** português
- **Separador**: ponto e vírgula (`;`)  
- **Saída**: apenas um CSV no formato `pergunta;resposta`.

### Exemplo de formato esperado:
```
{fewshot}
```

### Regras:
- Garanta que as perguntas sejam variadas e abrangentes ao contexto
- Use o conteúdo abaixo (abstract, triplas e exemplos few-shot) como base de conhecimento.
- A pergunta deve estar relacionada ao conteúdo e ter uma única resposta correta.
- A resposta deve estar contida ou inferível a partir do contexto (abstract, triplas ou few-shots).
- Não repita perguntas semelhantes.
- A saída final deve conter exatamente 10 linhas no seguinte formato:

### Contexto 
```
{abstract}
```
### Fatos
```
{triplas}
```

---
## Instrução Final
Gere agora o CSV conforme Instruções e Regras.
""".strip()

PREDICADOS_IRRELEVANTES = [
   "dbo:abstract",
    "dbo:wikiPageID",
    "dbo:wikiPageLength",
    "dbo:wikiPageRevisionID",
    "dbo:thumbnail",
    "dbo:wikiPageExternalLink",
    "dbo:wikiPageRedirects",
    "dbo:wikiPageDisambiguates",
    "dbo:isPartOf",
    "owl:sameAs",
    "rdfs:label",
    "rdfs:comment",
    "foaf:isPrimaryTopicOf",
    "dbo:depiction",
    "dbo:wikiPageUsesTemplate",
    "dbo:wikiPageWikiLink",
    "rdfs:seeAlso",
    "prov:wasDerivedFrom",
    "owl:differentFrom",
    "wgs84:lat",
    "wgs84:long",
    "core:exactMatch",
    "core:closeMatch",
    "core:narrower"
]

TOPICOS = [
    ("Normans", "Normans", "Normandos"),
    ("Computational_complexity_theory", "Computational_complexity_theory", "Teoria_da_complexidade_computacional"),
    ("Southern_California", "Southern_California", "Sul_da_Califórnia"),
    ("Sky_(United_Kingdom)", "British_Satellite_Broadcasting", "Sky_UK"),
    ("Victoria_(Australia)", "Victoria_(Australia)", "Vitória_(Austrália)"),
    ("Huguenot", "Huguenots", "Huguenotes"),
    ("Steam_engine", "Steam_engine", "Motor_a_vapor"),
    ("Oxygen", "Oxygen", ""),
    ("1973_oil_crisis", "1973_oil_crisis", "Crise_petrolífera_de_1973"),
    ("European_Union_law", "Law_of_the_European_Union", "Direito_da_União_Europeia"),
    ("Amazon_rainforest", "Amazon_rainforest", ""),
    ("Ctenophora", "Ctenophora", "Ctenophora"),
    ("Fresno,_California", "Fresno,_California", "Fresno"),
    ("Packet_switching", "Packet_switching", "Comutação_de_pacotes"),
    ("Black_Death", "Black_Death", "Peste_Negra"),
    ("Geology", "Geology", "Geologia"),
    ("Pharmacy", "Pharmacy", "Farmácia"),
    ("Civil_disobedience", "Civil_disobedience", "Desobediência_civil"),
    ("Construction", "Construction", ""),
    ("Private_school", "Private_school", "Escola"),
    ("Harvard_University", "Harvard_University", "Universidade_Harvard"),
    ("Jacksonville,_Florida", "Jacksonville,_Florida", "Jacksonville"),
    ("Economic_inequality", "Economic_inequality", "Desigualdade_econômica"),
    ("University_of_Chicago", "University_of_Chicago", "Universidade_de_Chicago"),
    ("Yuan_dynasty", "Yuan_dynasty", "Dinastia_Yuan"),
    ("Immune_system", "Immune_system", "Sistema_imunitário"),
    ("Intergovernmental_Panel_on_Climate_Change", "Intergovernmental_Panel_on_Climate_Change", "Painel_Intergovernamental_sobre_Mudanças_Climáticas"),
    ("Prime_number", "Prime_number", "Número_primo"),
    ("Rhine", "Rhine", "Rio_Reno"),
    ("Scottish_Parliament", "Scottish_Parliament", "Parlamento_da_Escócia"),
    ("Islamism", "Islamism", "Islamismo_político"),
    ("Imperialism", "Imperialism", "Imperialismo"),
    ("Warsaw", "Warsaw", "Varsóvia"),
    ("French_and_Indian_War", "French_and_Indian_War", "Guerra_Franco-Indígena"),
    ("Force", "Force", "Força")
]

# https://ollama.com/library/llama3

MODELOS = {
    #"codegemma:2b": {"max_tokens": 8000, "tokenizer": "google/codegemma-2b"},
    #"codegemma:7b": {"max_tokens": 8000, "tokenizer": "google/codegemma-2b"},
    #"codellama:13b": {"max_tokens": 16000, "tokenizer": "codellama/CodeLlama-7b-hf"},
    #"codellama:7b": {"max_tokens": 16000, "tokenizer": "codellama/CodeLlama-7b-hf"},
    "deepseek-r1:1.5b": {"max_tokens": 128000, "tokenizer": "deepseek-ai/deepseek-llm-7b-base"},
    "deepseek-r1:14b": {"max_tokens": 128000, "tokenizer": "deepseek-ai/deepseek-llm-7b-base"},
    "deepseek-r1:32b": {"max_tokens": 128000, "tokenizer": "deepseek-ai/deepseek-llm-7b-base"},
    "deepseek-r1:7b": {"max_tokens": 128000, "tokenizer": "deepseek-ai/deepseek-llm-7b-base"},
    "deepseek-r1:8b": {"max_tokens": 128000, "tokenizer": "deepseek-ai/deepseek-llm-7b-base"},
    # AUSENTE "dolphin3:8b": {"max_tokens": 128000, "tokenizer": "openchat/openchat-3.5-0106"},
    "gemma3:12b": {"max_tokens": 128000, "tokenizer": "google/gemma-7b"},
    "gemma3:27b": {"max_tokens": 128000, "tokenizer": "google/gemma-7b"},
    "gemma3:4b": {"max_tokens": 128000, "tokenizer": "google/gemma-7b"},
    "granite3.1-dense:8b": {"max_tokens": 128000, "tokenizer": "mistralai/Mistral-7B-v0.1"},
    # AUSENTE "llama3:8b": {"max_tokens": 8000, "tokenizer": "meta-llama/Meta-Llama-3-8B"},
    # AUSENTE "llama3.2-vision:11b": {"max_tokens": 128000, "tokenizer": "meta-llama/Meta-Llama-3-8B"},
    # AUSENTE "llama3.2:3b": {"max_tokens": 128000, "tokenizer": "meta-llama/Meta-Llama-3-8B"},
    #"mistral-nemo:12b": {"max_tokens": 1000, "tokenizer": "mistralai/Mistral-7B-v0.1"},
    # AUSENTE "mistral-small:24b": {"max_tokens": 32000, "tokenizer": "mistralai/Mistral-7B-v0.1"},
    # AUSENTE "mistral-small3.1:24b": {"max_tokens": 128000, "tokenizer": "mistralai/Mistral-7B-v0.1"},
    # AUSENTE "mistral:7b": {"max_tokens": 32000, "tokenizer": "mistralai/Mistral-7B-v0.1"},
    # AUSENTE "openchat:7b": {"max_tokens": 8000, "tokenizer": "openchat/openchat-3.5-0106"},
    #"orca-mini:13b": {"max_tokens": 4000, "tokenizer": "microsoft/Phi-2"},
    #"orca-mini:3b": {"max_tokens": 2000, "tokenizer": "microsoft/Phi-2"},
    #"orca-mini:7b": {"max_tokens": 4000, "tokenizer": "microsoft/Phi-2"},
    "phi4:14b": {"max_tokens": 16000, "tokenizer": "microsoft/Phi-2"},
    # AUSENTE "qwen:4b": {"max_tokens": 128000, "tokenizer": "Qwen/Qwen1.5-7B"},
    #"qwen2.5-coder:0.5b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    #"qwen2.5-coder:1.5b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    #"qwen2.5-coder:14b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    #"qwen2.5-coder:32b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    #"qwen2.5-coder:3b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    #"qwen2.5-coder:7b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B-Chat"},
    "qwen2.5:14b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen2.5:32b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen2.5:3b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B"},
    # AUSENTE "qwen2.5:7b": {"max_tokens": 32000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen3:14b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen3:30b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen3:32b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen3:4b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    "qwen3:8b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    # AUSENTE "qwq:32b": {"max_tokens": 40000, "tokenizer": "Qwen/Qwen1.5-7B"},
    #"starcoder2:15b": {"max_tokens": 16000, "tokenizer": "bigcode/starcoder2-7b"},
    #"starcoder2:3b": {"max_tokens": 16000, "tokenizer": "bigcode/starcoder2-7b"},
    #"starcoder2:7b": {"max_tokens": 16000, "tokenizer": "bigcode/starcoder2-7b"},
    #"sabia-3.1": {"max_tokens": 128000, "tokenizer": "maritaca-ai/sabia-7b"},
    #"sabia-3": {"max_tokens": 128000, "tokenizer": "maritaca-ai/sabia-7b"},
    #"sabiazinho-3": {"max_tokens": 128000, "tokenizer": "maritaca-ai/sabia-7b"},
}

