import os
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def extrair_infos_nome_arquivo(nome_arquivo):
    nome = nome_arquivo.replace('.txt', '')
    partes = nome.split('_')
    if len(partes) < 5:
        return None

    return {
        "codigo_execucao_julgamento": partes[0],
        "id_cenario": partes[1],
        "id_par": partes[2],
        "modelo_julgamento": partes[3],
        "nome_cenario": '_'.join(partes[4:])
    }

def processar_arquivos(diretorio_txts, caminho_saida_csv, caminho_saida_xlsx, id_resultado):
    registros = []
    diretorio = Path(diretorio_txts)
    arquivos_txt = list(diretorio.glob("*.txt"))

    for arquivo in tqdm(arquivos_txt, desc="Processando arquivos"):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
                dados_json = json.loads(conteudo)

            info_extra = extrair_infos_nome_arquivo(arquivo.stem)
            if info_extra is None:
                continue

            dados_json.update(info_extra)
            dados_json["id_resultado"] = id_resultado  # <<< adiciona o ID fornecido
            registros.append(dados_json)

        except Exception as e:
            print(f"Erro ao processar {arquivo.name}: {e}")
            continue

    df = pd.DataFrame(registros)

    # Forçar colunas-chave como string
    campos_chave = [
        "id_resultado",  # agora incluído
        "codigo_execucao_julgamento", "id_cenario", "id_par",
        "modelo_julgamento", "nome_cenario"
    ]
    for campo in campos_chave:
        df[campo] = df[campo].astype(str)

    # Calcular média dos critérios
    criterios = ["complexidade", "completude", "corretude", "fluidez", "qualidade_portugues"]
    df["media_avaliacao"] = df[criterios].mean(axis=1)

    # Ordenar por id_cenario e id_par como inteiros
    df = df.sort_values(by=["id_cenario", "id_par"], key=lambda col: col.astype(int))

    # Colunas na ordem desejada
    colunas_finais = [
        "id_resultado",
        "codigo_execucao_julgamento",
        "modelo_julgamento",
        "id_cenario",
        "id_par",
        "nome_cenario",
        "pergunta",
        "resposta",
        "complexidade",
        "completude",
        "corretude",
        "fluidez",
        "qualidade_portugues",
        "media_avaliacao",
        "justificativa"
    ]
    df = df[colunas_finais]

    # Salvar arquivos
    df.to_csv(caminho_saida_csv, sep=";", index=False, encoding="utf-8")
    df.to_excel(caminho_saida_xlsx, index=False)

    print(f"\n✅ Arquivos salvos em:\n- {caminho_saida_csv}\n- {caminho_saida_xlsx}")

# Exemplo de uso
if __name__ == "__main__":
    id_resultado = "ffbe36d0"  # exemplo de ID do resultado julgado
    diretorio_dos_txts = f"julgamento/{id_resultado}"  # ajuste aqui
    saida_csv = "consolidado_julgamento.csv"
    saida_xlsx = "consolidado_julgamento.xlsx"
    processar_arquivos(diretorio_dos_txts, saida_csv, saida_xlsx, id_resultado)