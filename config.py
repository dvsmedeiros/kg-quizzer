PROMPT_ZERO_SHOT_PT = """ 
Você é um gerador de questões objetivas com base em contexto e fatos fornecidos. Gere pares de perguntas e respostas relevantes e corretas, exclusivamente a partir do conteúdo fornecido. Gere apenas os dados requeridos, sem adicionar observações, justificativas ou qualquer conteúdo não estruturado.

## Objetivo
Gerar exatamente **10 pares** no formato CSV, com:
- **1 pergunta** relevante ao contexto
- **1 resposta correta** 
- **Separador**: ponto e vírgula (`;`)
- **Idioma**: português
- **Formato da saída**:
```csv
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

## Regras
- As perguntas devem ser **variadas** e **abranger diferentes aspectos** do conteúdo.
- As perguntas devem ser **claramente relacionadas ao conteúdo** apresentado abaixo.
- Cada pergunta deve ter uma **única resposta correta**, que esteja **explícita ou inferível** a partir do conteúdo.
- **Não repita perguntas semelhantes.**
- Gere **somente o conteúdo CSV**, sem explicações ou comentários adicionais.

---

## Instrução Final
**Gere agora os 10 pares `pergunta;resposta` conforme as instruções e regras acima.**
""".strip()

PROMPT_TRIPLAS_PT = """
Você é um gerador de questões objetivas com base em contexto e fatos fornecidos. Gere pares de perguntas e respostas relevantes e corretas, exclusivamente a partir do conteúdo fornecido. Gere apenas os dados requeridos, sem adicionar observações, justificativas ou qualquer conteúdo não estruturado.

## Objetivo
Gerar exatamente **10 pares** no formato CSV, com:
- **1 pergunta** relevante ao contexto
- **1 resposta correta** 
- **Separador**: ponto e vírgula (`;`)
- **Idioma**: português
- **Formato da saída**:
```csv
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

## Regras
- As perguntas devem ser **variadas** e **abranger diferentes aspectos** do conteúdo.
- As perguntas devem ser **claramente relacionadas ao conteúdo** apresentado abaixo.
- Cada pergunta deve ter uma **única resposta correta**, que esteja **explícita ou inferível** a partir do conteúdo.
- **Não repita perguntas semelhantes.**
- Gere **somente o conteúdo CSV**, sem explicações ou comentários adicionais.

### Contexto
{abstract}

### Fatos
{triplas}

---

## Instrução Final
**Gere agora os 10 pares `pergunta;resposta` conforme as instruções e regras acima.**
""".strip()

PROMPT_FEW_SHOT_TRIPLAS_PT = """
Você é um gerador de questões objetivas com base em contexto e fatos fornecidos. Gere pares de perguntas e respostas relevantes e corretas, exclusivamente a partir do conteúdo fornecido. Gere apenas os dados requeridos, sem adicionar observações, justificativas ou qualquer conteúdo não estruturado.

## Objetivo
Gerar exatamente **10 pares** no formato CSV, com:
- **1 pergunta** relevante ao contexto
- **1 resposta correta** 
- **Separador**: ponto e vírgula (`;`)
- **Idioma**: português
- **Formato da saída**:
```csv
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

## Regras
- As perguntas devem ser **variadas** e **abranger diferentes aspectos** do conteúdo.
- As perguntas devem ser **claramente relacionadas ao conteúdo** apresentado abaixo.
- Cada pergunta deve ter uma **única resposta correta**, que esteja **explícita ou inferível** a partir do conteúdo.
- **Não repita perguntas semelhantes.**
- Gere **somente o conteúdo CSV**, sem explicações ou comentários adicionais.

### Contexto
{abstract}

### Fatos
{triplas}

### Exemplos
{fewshot}

---

## Instrução Final
**Gere agora os 10 pares `pergunta;resposta` conforme as instruções e regras acima.**
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

TOPICOS = {
    "Normans": {
        "squad": "Normans",
        "en": "Normans",
        "pt": "Normandos"
    },
    "Computational_complexity_theory": {
        "squad": "Computational_complexity_theory",
        "en": "Computational_complexity_theory",
        "pt": "Teoria_da_complexidade_computacional"
    },
    "Southern_California": {
        "squad": "Southern_California",
        "en": "Southern_California",
        "pt": "Sul_da_Califórnia"
    },
    "British_Satellite_Broadcasting": {
        "squad": "Sky_(United_Kingdom)",
        "en": "British_Satellite_Broadcasting",
        "pt": "Sky_UK"
    },
    "Victoria_(Australia)": {
        "squad": "Victoria_(Australia)",
        "en": "Victoria_(Australia)",
        "pt": "Vitória_(Austrália)"
    },
    "Huguenots": {
        "squad": "Huguenot",
        "en": "Huguenots",
        "pt": "Huguenotes"
    },
    "Steam_engine": {
        "squad": "Steam_engine",
        "en": "Steam_engine",
        "pt": "Motor_a_vapor"
    },
    "Oxygen": {
        "squad": "Oxygen",
        "en": "Oxygen",
        "pt": "Oxygen" #topico em pt ausente
    },
    "1973_oil_crisis": {
        "squad": "1973_oil_crisis",
        "en": "1973_oil_crisis",
        "pt": "Crise_petrolífera_de_1973"
    },
    "Law_of_the_European_Union": {
        "squad": "European_Union_law",
        "en": "Law_of_the_European_Union",
        "pt": "Direito_da_União_Europeia"
    },
    "Amazon_rainforest": {
        "squad": "Amazon_rainforest",
        "en": "Amazon_rainforest",
        "pt": "Amazon_rainforest" #topico em pt ausente
    },
    "Ctenophora": {
        "squad": "Ctenophora",
        "en": "Ctenophora",
        "pt": "Ctenophora"
    },
    "Fresno,_California": {
        "squad": "Fresno,_California",
        "en": "Fresno,_California",
        "pt": "Fresno"
    },
    "Packet_switching": {
        "squad": "Packet_switching",
        "en": "Packet_switching",
        "pt": "Comutação_de_pacotes"
    },
    "Black_Death": {
        "squad": "Black_Death",
        "en": "Black_Death",
        "pt": "Peste_Negra"
    },
    "Geology": {
        "squad": "Geology",
        "en": "Geology",
        "pt": "Geologia"
    },
    "Pharmacy": {
        "squad": "Pharmacy",
        "en": "Pharmacy",
        "pt": "Farmácia"
    },
    "Civil_disobedience": {
        "squad": "Civil_disobedience",
        "en": "Civil_disobedience",
        "pt": "Desobediência_civil"
    },
    "Construction": {
        "squad": "Construction",
        "en": "Construction",
        "pt": "Construction" #topico em pt ausente
    },
    "Private_school": {
        "squad": "Private_school",
        "en": "Private_school",
        "pt": "Escola"
    },
    "Harvard_University": {
        "squad": "Harvard_University",
        "en": "Harvard_University",
        "pt": "Universidade_Harvard"
    },
    "Jacksonville,_Florida": {
        "squad": "Jacksonville,_Florida",
        "en": "Jacksonville,_Florida",
        "pt": "Jacksonville"
    },
    "Economic_inequality": {
        "squad": "Economic_inequality",
        "en": "Economic_inequality",
        "pt": "Desigualdade_econômica"
    },
    "University_of_Chicago": {
        "squad": "University_of_Chicago",
        "en": "University_of_Chicago",
        "pt": "Universidade_de_Chicago"
    },
    "Yuan_dynasty": {
        "squad": "Yuan_dynasty",
        "en": "Yuan_dynasty",
        "pt": "Dinastia_Yuan"
    },
    "Immune_system": {
        "squad": "Immune_system",
        "en": "Immune_system",
        "pt": "Sistema_imunitário"
    },
    "Intergovernmental_Panel_on_Climate_Change": {
        "squad": "Intergovernmental_Panel_on_Climate_Change",
        "en": "Intergovernmental_Panel_on_Climate_Change",
        "pt": "Painel_Intergovernamental_sobre_Mudanças_Climáticas"
    },
    "Prime_number": {
        "squad": "Prime_number",
        "en": "Prime_number",
        "pt": "Número_primo"
    },
    "Rhine": {
        "squad": "Rhine",
        "en": "Rhine",
        "pt": "Rio_Reno"
    },
    "Scottish_Parliament": {
        "squad": "Scottish_Parliament",
        "en": "Scottish_Parliament",
        "pt": "Parlamento_da_Escócia"
    },
    "Islamism": {
        "squad": "Islamism",
        "en": "Islamism",
        "pt": "Islamismo_político"
    },
    "Imperialism": {
        "squad": "Imperialism",
        "en": "Imperialism",
        "pt": "Imperialismo"
    },
    "Warsaw": {
        "squad": "Warsaw",
        "en": "Warsaw",
        "pt": "Varsóvia"
    },
    "French_and_Indian_War": {
        "squad": "French_and_Indian_War",
        "en": "French_and_Indian_War",
        "pt": "Guerra_Franco-Indígena"
    },
    "Force": {
        "squad": "Force",
        "en": "Force",
        "pt": "Força"
    }
}

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

