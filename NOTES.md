## Parâmetros do Experimento

| **Fator**                  | **Valores possíveis**                              | **Variações**  |
|---------------------------|-----------------------------------------------------|----------------|
| Termos                    | 35 termos com versão `pt`                           | 35             |
| Técnica                   | `zero-shot`, `zero-shot-triplas`, `few-shot-triplas`| 3              |
| Formato (few-shot)        | `RDF`, `verbalizado`                                | 2              |
| Qtd. de triplas (few-shot)| 140 (média para contexto 8k tokens)                 | 1              |
| Modelos                   | 18 modelos selecionados                             | 18             |
| `temperature`             | 0.7                                                 | 1              |
| `top-k`                   | 40                                                  | 1              |
| `top-p`                   | 0.95                                                | 1              |

## Lista de Tópicos 

| #  | **SQuAD**                                           | **en_us**                                   | **pt_br**                                               |
|----|-----------------------------------------------------|---------------------------------------------|----------------------------------------------------------|
| 1  | Normans                                             | Normans                                     | Normandos                                                |
| 2  | Computational_complexity_theory                     | Computational_complexity_theory             | Teoria_da_complexidade_computacional                    |
| 3  | Southern_California                                 | Southern_California                         | Sul_da_Califórnia                                        |
| 4  | Sky_(United_Kingdom)                                | British_Satellite_Broadcasting             | Sky_UK                                                   |
| 5  | Victoria_(Australia)                                | Victoria_(Australia)                        | Vitória_(Austrália)                                     |
| 6  | Huguenot                                            | Huguenots                                   | Huguenotes                                               |
| 7  | Steam_engine                                        | Steam_engine                                | Motor_a_vapor                                            |
| 8  | Oxygen                                              | Oxygen                                      |                                                          |
| 9  | 1973_oil_crisis                                     | 1973_oil_crisis                             | Crise_petrolífera_de_1973                               |
| 10 | European_Union_law                                  | Law_of_the_European_Union                   | Direito_da_União_Europeia                              |
| 11 | Amazon_rainforest                                   | Amazon_rainforest                           |                                                          |
| 12 | Ctenophora                                          | Ctenophora                                  | Ctenophora                                               |
| 13 | Fresno,_California                                  | Fresno,_California                          | Fresno                                                   |
| 14 | Packet_switching                                    | Packet_switching                            | Comutação_de_pacotes                                    |
| 15 | Black_Death                                         | Black_Death                                 | Peste_Negra                                              |
| 16 | Geology                                             | Geology                                     | Geologia                                                 |
| 17 | Pharmacy                                            | Pharmacy                                    | Farmácia                                                 |
| 18 | Civil_disobedience                                  | Civil_disobedience                          | Desobediência_civil                                     |
| 19 | Construction                                        | Construction                                |                                                          |
| 20 | Private_school                                      | Private_school                              | Escola                                                   |
| 21 | Harvard_University                                  | Harvard_University                          | Universidade_Harvard                                    |
| 22 | Jacksonville,_Florida                               | Jacksonville,_Florida                       | Jacksonville                                              |
| 23 | Economic_inequality                                 | Economic_inequality                         | Desigualdade_econômica                                  |
| 24 | University_of_Chicago                               | University_of_Chicago                       | Universidade_de_Chicago                                 |
| 25 | Yuan_dynasty                                        | Yuan_dynasty                                | Dinastia_Yuan                                            |
| 26 | Immune_system                                       | Immune_system                               | Sistema_imunitário                                       |
| 27 | Intergovernmental_Panel_on_Climate_Change           | Intergovernmental_Panel_on_Climate_Change   | Painel_Intergovernamental_sobre_Mudanças_Climáticas     |
| 28 | Prime_number                                        | Prime_number                                | Número_primo                                             |
| 29 | Rhine                                               | Rhine                                       | Rio_Reno                                                 |
| 30 | Scottish_Parliament                                 | Scottish_Parliament                         | Parlamento_da_Escócia                                   |
| 31 | Islamism                                            | Islamism                                    | Islamismo_político                                      |
| 32 | Imperialism                                         | Imperialism                                 | Imperialismo                                             |
| 33 | Warsaw                                              | Warsaw                                      | Varsóvia                                                 |
| 34 | French_and_Indian_War                               | French_and_Indian_War                       | Guerra_Franco-Indígena                                  |
| 35 | Force                                               | Force                                       | Força                                                    |

## Fórmulas Detalhadas dos Cenários

> **Nota:** O plano experimental considera apenas combinações únicas de parâmetros, sem duplicação de cenários. A execução será exclusivamente em língua portuguesa, o que elimina a necessidade de variação por idioma. Isso garante eficiência e representatividade sem redundâncias.

#### Zero-shot
$$
\text{Zero-shot} = T_{\text{pt}} \times (\text{modelos}) = 35 \times 18 = \boxed{630}
$$

#### Zero-shot-triplas
$$
\text{Zero-shot-triplas} = T_{\text{pt}} \times (\text{formatos} \times \text{modelos}) = 35 \times (2 \times 18) = \boxed{1,260}
$$

#### Few-shot-triplas
$$
\text{Few-shot-triplas} = T_{\text{pt}} \times (\text{formatos} \times \text{modelos}) = 35 \times (2 \times 18) = \boxed{1,260}
$$

#### Total de Cenários
$$
\text{Total} = 630 + 1,260 + 1,260 = \boxed{3,150}
$$

#### Fórmula Paramétrica
$$
\text{Total} = T_{\text{pt}} \times (\text{modelos}) + 2 \times T_{\text{pt}} \times (\text{formatos} \times \text{modelos})
$$

## Critérios para Seleção dos Modelos

A escolha dos modelos LLMs utilizados no experimento considerou os seguintes fatores:
1. Diversidade arquitetural: foram selecionados modelos de diferentes famílias (Qwen, LLaMA, Phi, DeepSeek, etc.) para evitar viés arquitetural específico.
2. Porte variado: os modelos foram classificados em três categorias – pequeno (≤ 4B), médio (5B–14B), grande (até 32B) – garantindo uma análise comparativa entre diferentes capacidades de processamento.
3. Tamanho mínimo do contexto: apenas modelos com suporte a pelo menos 8.000 tokens de contexto foram considerados, visando garantir que os prompts e dados estruturados pudessem ser processados de forma completa.
4. Limite superior de 32B: esse valor foi adotado como teto devido a restrições práticas de execução local e custo computacional. Modelos acima disso foram excluídos.
5. Disponibilidade~~ local (offline): todos os modelos utilizados estão disponíveis em ambientes controlados, sem depender de APIs externas, o que garante reprodutibilidade e controle de custos.
6. Representatividade nacional: o modelo brasileiro sabiá-3 foi incluído para representar soluções locais e avaliar seu desempenho em língua portuguesa.
7. Foco geralista: modelos explicitamente otimizados para tarefas de programação ou geração de código foram desconsiderados, priorizando aqueles com capacidades generalistas em linguagem natural.

## Lista de Modelos Selecionados *(FALTA FILTRAR)*

| #  | **Nome**                       | **Tamanho do Contexto**   | **Tokenizer**                         |**Status**     |**Observação**|
|----|--------------------------------|---------------------------|---------------------------------------|---------------|--------------| 
| 1  | ~~codegemma:2b~~               | 8000                      | google/codegemma-2b                   |Excluído       |Critério 7    |
| 2  | ~~codegemma:7b~~               | 8000                      | google/codegemma-2b                   |Excluído       |Critério 7    |
| 3  | ~~codellama:13b~~              | 16000                     | codellama/CodeLlama-7b-hf             |Excluído       |Critério 7    |
| 4  | ~~codellama:7b~~               | 16000                     | codellama/CodeLlama-7b-hf             |Excluído       |Critério 7    |
| 5  | deepseek-r1:1.5b               | 128000                    | deepseek-ai/deepseek-llm-7b-base      |Elegível       |              |
| 6  | deepseek-r1:14b                | 128000                    | deepseek-ai/deepseek-llm-7b-base      |Elegível       |              |
| 7  | deepseek-r1:32b                | 128000                    | deepseek-ai/deepseek-llm-7b-base      |Elegível       |              |
| 8  | deepseek-r1:7b                 | 128000                    | deepseek-ai/deepseek-llm-7b-base      |Elegível       |              |
| 9  | deepseek-r1:8b                 | 128000                    | deepseek-ai/deepseek-llm-7b-base      |Elegível       |              |
| 10 | ~~dolphin3:8b~~                | 128000                    | openchat/openchat-3.5-0106            |Indisponível   |              |
| 11 | gemma3:12b                     | 128000                    | google/gemma-7b                       |Elegível       |              |
| 12 | gemma3:27b                     | 128000                    | google/gemma-7b                       |Elegível       |              |
| 13 | gemma3:4b                      | 128000                    | google/gemma-7b                       |Elegível       |              |
| 14 | granite3.1-dense:8b            | 128000                    | mistralai/Mistral-7B-v0.1             |Elegível       |              |
| 15 | ~~llama3:8b~~                  | 8000                      | meta-llama/Meta-Llama-3-8B            |Indisponível   |              |
| 16 | ~~llama3.2~~-vision:11b        | 128000                    | meta-llama/Meta-Llama-3-8B            |Indisponível   |              |
| 17 | ~~llama3.2~~:3b                | 128000                    | meta-llama/Meta-Llama-3-8B            |Indisponível   |              |
| 18 | ~~mistral-nemo~~:12b           | 1000                      | mistralai/Mistral-7B-v0.1             |Excluído       |Critério 3    |
| 19 | ~~mistral-small~~:24b          | 32000                     | mistralai/Mistral-7B-v0.1             |Indisponível   |              |
| 20 | ~~mistral-small3~~.1:24b       | 128000                    | mistralai/Mistral-7B-v0.1             |Indisponível   |              |
| 21 | ~~mistral:7b~~                 | 32000                     | mistralai/Mistral-7B-v0.1             |Indisponível   |              |
| 22 | ~~openchat:7b~~                | 8000                      | openchat/openchat-3.5-0106            |Indisponível   |              |
| 23 | ~~orca-mini~~:13b              | 4000                      | microsoft/Phi-2                       |Excluído       |Critério 3    |
| 24 | ~~orca-mini~~:3b               | 2000                      | microsoft/Phi-2                       |Excluído       |Critério 3    |
| 25 | ~~orca-mini~~:7b               | 4000                      | microsoft/Phi-2                       |Excluído       |Critério 3    |
| 26 | phi4:14b                       | 16000                     | microsoft/Phi-2                       |Elegível       |              |
| 27 | ~~qwen:4b~~                    | 128000                    | Qwen/Qwen1.5-7B                       |Indisponível   |              |
| 28 | ~~qwen2.5~~-coder:0.5b         | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 29 | ~~qwen2.5~~-coder:1.5b         | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 30 | ~~qwen2.5~~-coder:14b          | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 31 | ~~qwen2.5~~-coder:32b          | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 32 | ~~qwen2.5~~-coder:3b           | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 33 | ~~qwen2.5~~-coder:7b           | 32000                     | Qwen/Qwen1.5-7B-Chat                  |Excluído       |Critério 7    |
| 34 | qwen2.5:14b                    | 32000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 35 | qwen2.5:32b                    | 32000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 36 | qwen2.5:3b                     | 32000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 37 | ~~qwen2.5~~:7b                 | 32000                     | Qwen/Qwen1.5-7B                       |Indisponível   |              |
| 38 | qwen3:14b                      | 40000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 39 | qwen3:30b                      | 40000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 40 | qwen3:32b                      | 40000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 41 | qwen3:4b                       | 40000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 42 | qwen3:8b                       | 40000                     | Qwen/Qwen1.5-7B                       |Elegível       |              |
| 43 | ~~qwq:32b~~                    | 40000                     | Qwen/Qwen1.5-7B                       |Indisponível   |              |
| 44 | ~~starcoder2:15b~~             | 16000                     | bigcode/starcoder2-7b                 |Excluído       |Critério 7    |
| 45 | ~~starcoder2:3b~~              | 16000                     | bigcode/starcoder2-7b                 |Excluído       |Critério 7    |
| 46 | ~~starcoder2:7b~~              | 16000                     | bigcode/starcoder2-7b                 |Excluído       |Critério 7    |
| 47 | sabia-3.1                      | 128000                    | maritaca-ai/sabia-7b                  |Judge          |              |
| 48 | sabia-3                        | 128000                    | maritaca-ai/sabia-7b                  |Judge          |              |
| 49 | sabiazinho-3                   | 128000                    | maritaca-ai/sabia-7b                  |Judge          |              |

## Critérios para Definição dos Hiperparâmetros
Apenas uma configuração foi escolhida para garantir consistência e limitar o espaço amostral. O valor 0.7 oferece um bom equilíbrio entre diversidade e estabilidade.

1. temperature = 0.7: valor moderado, que oferece um bom compromisso entre criatividade e coerência nas respostas.
2. top-k = 40: foco nos tokens de maior probabilidade, reduzindo ruído sem eliminar diversidade.
3. top-p = 0.95: sampling por núcleo com margem de diversidade maior, evitando repetições sem comprometer a qualidade.

## Critério para Quantidade de Triplas nos cenários (Few-shot-triplas)

Para as execuções com técnica few-shot-triplas, a quantidade de triplas RDF incluídas no prompt foi definida com base na capacidade de contexto dos modelos utilizados no experimento:

1. O tamanho mínimo de contexto considerado é de 8.000 tokens e o máximo é de 128.000 tokens, conforme os limites suportados por cada modelo.
2. Uma reserva de tokens é alocada para instruções, contexto textual (instruções, abstract, formato de resposta), sendo o restante destinado à inclusão de triplas RDF.
3. O parâmetro limite_triplas define o número máximo de triplas a serem incluídas, respeitando o espaço disponível em cada execução.
4. Quando a quantidade total de triplas exceder o limite do contexto disponível, serão selecionadas até atingir o limite de contexto as triplas conforme a ordem original retornada pela consulta SPARQL.
5. O objetivo é maximizar o uso do contexto sem ultrapassá-lo, garantindo compatibilidade com todos os modelos avaliados.

## Critério para Quantidade de Few-shots (exemplos SQuAD)

Os exemplos few-shot com perguntas e respostas (fonte: SQuAD) inseridos no prompt seguem os seguintes critérios:

1. Selecionar apenas os exemplos cujo tópico (title) seja igual ao do cenário.
2. Filtrar exemplos com perguntas válidas e que possuam ao menos uma resposta.
3. A seleção é realizada diretamente a partir do segmento title['topico']['paragraphs'][0]["qas"][:10], ou seja, os primeiros 10 pares disponíveis são utilizados.
4. O valor 10 foi escolhido por ser compatível com o número de perguntas e respostas utilizadas posteriormente na avaliação automática do modelo (prompt-as-judge), garantindo consistência entre treino e avaliação.
5. A quantidade final de exemplos pode ser ajustada para não exceder o limite de contexto do menor modelo envolvido no experimento.

## Consulta por Termos em Inglês (Tradução)

Apesar de a avaliação ser realizada em português, a consulta à DBpedia é feita com termos em inglês, por motivos de:

- Cobertura insuficiente da DBpedia em pt-br;
- Qualidade inferior de conteúdo nas versões traduzidas;
- Maior consistência estrutural e semântica nos dados em inglês.

Esse fator introduz um viés de tradução, mas é necessário para garantir a qualidade da extração de conhecimento.

## Verbalização das Triplas RDF

Foi realizada uma verbalização completa de todas as triplas RDF retornadas da DBpedia para os 35 tópicos utilizados. O processo envolveu:

- Extração das triplas RDF com predicados relevantes (limitadas a 10.000 por tópico).
- Remoção de predicados irrelevantes (metadados, links externos, etc.).
- Mapeamento de cada predicado para duas formas verbalizadas:
- Português (pt-br): Ex: birthPlace -> “nasceu em”
- Inglês (en-us): Ex: birthPlace -> “was born in”
- A verbalização completa foi aplicada a cada tripla no formato:
sujeito + verbalização do predicado + objeto.

Exemplo:
- Tripla: ```xml<http://dbpedia.org/resource/Einstein> <dbo:birthPlace> <http://dbpedia.org/resource/Ulm>```
- Verbalização pt-br: Einstein nasceu em Ulm
- Verbalização en-us: Einstein was born in Ulm

Esse processo garantiu que o modelo pudesse receber uma representação legível e semântica do conhecimento extraído para auxiliar nas respostas few-shot.

## Predicados Semanticamente Irrelevantes

Classificamos alguns predicados semanticamente irrelevantes ao contexto, por não contribuírem diretamente para o entendimento conceitual das entidades descritas. Esses predicados incluem metadados técnicos, descritores auxiliares, links de redirecionamento ou equivalência e coordenadas geográficas. Eles são filtrados diretamente nas consultas SPARQL de triplas RDF para garantir que apenas relações semanticamente informativas sejam incluídas no contexto.
Em particular, o predicado dbo~~:abstract foi excluído das consultas de triplas porque seu conteúdo já é recuperado integralmente em uma consulta separada e incorporado ao contexto.

| #  | Predicado                      | Classificação     |
|----|--------------------------------|-------------------|
| 1  | dbo:abstract                   | descritor         |
| 2  | dbo:wikiPageID                 | metadado          |
| 3  | dbo:wikiPageLength             | metadado          |
| 4  | dbo:wikiPageRevisionID         | metadado          |
| 5  | dbo:thumbnail                  | metadado          |
| 6  | dbo:wikiPageExternalLink       | link              |
| 7  | dbo:wikiPageRedirects          | link              |
| 8  | dbo:wikiPageDisambiguates      | link              |
| 9  | dbo:isPartOf                   | metadado          |
| 10 | owl:sameAs                     | link              |
| 11 | rdfs:label                     | descritor         |
| 12 | rdfs:comment                   | descritor         |
| 13 | foaf:isPrimaryTopicOf          | link              |
| 14 | dbo:depiction                  | metadado          |
| 15 | dbo:wikiPageUsesTemplate       | metadado          |
| 16 | dbo:wikiPageWikiLink           | link              |
| 17 | rdfs:seeAlso                   | link              |
| 18 | prov:wasDerivedFrom            | metadado          |
| 19 | owl:differentFrom              | link              |
| 20 | wgs84:lat                      | geolocalização    |
| 21 | wgs84:long                     | geolocalização    |
| 22 | core:exactMatch                | link              |
| 23 | core:closeMatch                | linkagem          |
| 24 | core:narrower                  | linkagem          |

## Execução e Estrutura de Armazenamento dos Resultados

Cada execução do experimento é identificada por um `id_execucao` exclusivo. Os dados gerados são organizados em duas pastas principais, permitindo rastreabilidade e reprodutibilidade dos experimentos.

---

### `execucao/<id_execucao>/`

Armazena os **metadados e logs da execução**.

**Log da execução**
Arquivo: `<id_execucao>.log`
Conteúdo: mensagens de log com o fluxo geral da execução, tokens utilizados, status dos modelos e falhas (se houver).

Exemplo: [`5ad0e5d5_execucao.log`](/execucao/5ad0e5d5/5ad0e5d5_execucao.log)

**CSV com os parâmetros utilizados nos prompts**
Arquivo: `<id_execucao>_execucao.csv`
Colunas:
|`id_cenario`|`nome_cenario`|`query_abstract`|`query_triplas`|`fewshot`|`triplas`|`prompt`|`numero_tokens`|`max_tokens`|
|------------|--------------|----------------|---------------|---------|---------|--------|---------------|------------|

Exemplo: [`5ad0e5d5_execucao.csv`](/execucao/5ad0e5d5/5ad0e5d5_execucao.csv)

---

### `resultado/<id_execucao>/`

Armazena os **resultados gerados por cenário**, com base no modelo LLM e parâmetros de entrada.

Para cada cenário executado, são gerados:

**Arquivo `.txt` com a resposta bruta do modelo**F
  - Conteúdo: resposta completa sem pós-processamento
  - Exemplo: [`5ad0e5d5_1004_Ctenophora_few-shot_RDF_140_phi4%3A14b_0.7_0.95_40.txt`](https://github.com/dvsmedeiros/qa-prompt-kg/blob/main/resultado/5ad0e5d5/5ad0e5d5_1004_Ctenophora_few-shot_RDF_140_phi4%3A14b_0.7_0.95_40.txt)

**Arquivo `.csv` com perguntas e respostas extraídas**
  - Formato: `pergunta;resposta`
  - Utilizado em análises e métricas de qualidade.
  - Exemplo: [`5ad0e5d5_1004_Ctenophora_few-shot_RDF_140_phi4%3A14b_0.7_0.95_40.csv`](https://github.com/dvsmedeiros/qa-prompt-kg/blob/main/resultado/5ad0e5d5/5ad0e5d5_1004_Ctenophora_few-shot_RDF_140_phi4%3A14b_0.7_0.95_40.csv)

---

Essa estrutura garante:

- Organização dos **parâmetros e contexto de execução**.
- Clareza na separação entre **entradas e saídas**.
- Facilidade de rastreio e replicação de cenários específicos.

## Extração de Perguntas e Respostas em CSV

Durante a execução de cada cenário, o resultado retornado pelo modelo LLM é salvo como um arquivo `.txt`, contendo a resposta bruta gerada a partir do prompt. Em seguida, esse conteúdo é processado com o objetivo de extrair pares estruturados no formato `pergunta;resposta`, os quais são armazenados em um arquivo `.csv`.

### Regras para Extração

As linhas extraídas devem seguir um padrão mínimo de estrutura para garantir que representem de fato uma pergunta e uma resposta válidas. As regras aplicadas são:

- A linha deve conter **uma pergunta e uma resposta separadas por ponto-e-vírgula (`;`)**.
- A **pergunta** deve conter pelo menos **3 caracteres não vazios**, podendo ou não terminar com um ponto de interrogação (`?`).
- A **resposta** deve conter pelo menos **2 caracteres não vazios**.
- Linhas contendo apenas uma parte da informação (ex: só a resposta) ou com separadores incorretos (ex: vírgula) são **ignoradas**.
- Se a primeira linha válida não for o cabeçalho `"pergunta;resposta"`, ele será automaticamente inserido no início do arquivo CSV.

### Expressão Regular Utilizada

A filtragem é realizada por meio da seguinte expressão regular:

```regex
^[^;\n\r]{3,}\??\s*;[^;\n\r]{2,}$
```

#### Detalhamento dos Componentes

| Componente                     | Significado                                                                                     |
|-------------------------------|--------------------------------------------------------------------------------------------------|
| `^`                            | Início da linha                                                                                 |
| `[^;\n\r]{3,}`                 | Pelo menos 3 caracteres que não sejam `;`, `\n` ou `\r` – representa a pergunta                  |
| `\??`                          | Um ponto de interrogação opcional após a pergunta                                               |
| `\s*`                          | Espaços em branco opcionais antes do separador `;`                                              |
| `;`                            | Delimitador obrigatório entre pergunta e resposta                                               |
| `[^;\n\r]{2,}`                 | Pelo menos 2 caracteres que não sejam `;`, `\n` ou `\r` – representa a resposta                 |
| `$`                            | Final da linha                                                                                  |

# Estratégia de Cache para Abstracts e Triplas RDF

Para melhorar a eficiência das execuções e reduzir o número de consultas redundantes às APIs externas (DBpedia e Wikipedia), o experimento implementa uma estratégia de **cache local persistente**. Essa estratégia é aplicada tanto para o *abstract* textual dos tópicos quanto para as *triplas RDF* associadas.

## Estrutura de Armazenamento

Os arquivos de cache são salvos em duas pastas distintas:

| Diretório             | Conteúdo                         | Formato     |
|----------------------|----------------------------------|-------------|
| `cache/abstracts/`   | Abstracts de tópicos             | `.json`     |
| `cache/triplas/`     | Triplas RDF de tópicos           | `.ttl`      |

## Lógica de Consulta com Cache

### Abstracts

- Primeiro, verifica-se se o arquivo já existe na pasta `cache/abstracts/` (arquivo JSON).
- Se encontrado, o conteúdo é lido diretamente do disco.
- Se não encontrado, tenta-se consultar o abstract na seguinte ordem:
   - **DBpedia SPARQL**
   - **Wikipedia REST API** (fallback)
- O resultado, se obtido, é armazenado localmente em JSON.

### Triplas RDF

- Verifica-se se o arquivo `.ttl` existe em `cache/triplas/`.
- Se encontrado, os dados são carregados localmente como um grafo RDF.
- Caso contrário, a consulta SPARQL à DBpedia é executada.
- O grafo resultante é serializado e salvo como arquivo `.ttl` para futuras execuções.

## Parâmetros do Cache

| Tipo       | Parâmetro                     | Finalidade                                                |
|------------|-------------------------------|------------------------------------------------------------|
| Abstract   | `topic`, `idioma`, `limit`    | Define o nome do arquivo JSON para cache de abstract       |
| Triplas    | `topic`, `limit`              | Define o nome do arquivo Turtle para cache de triplas      |
| Caminhos   | `cache/abstracts`, `cache/triplas` | Diretórios-padrão de armazenamento                        |

## Convenções de Nome de Arquivo

| Tipo       | Nome do Arquivo                            | Exemplo                              |
|------------|--------------------------------------------|--------------------------------------|
| Abstract   | `<topic>_<idioma>_lim<limit>.json`         | `Normans_en_lim1.json`               |
| Triplas    | `<topic>_lim<limit>.ttl`                   | `Normans_lim100.ttl`                 |
