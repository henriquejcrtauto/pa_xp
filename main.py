# Importando bibliotecas
import pandas as pd
import os
import chardet


def gera_df(caminho):
    if caminho.endswith('2021-02.csv'):
        df = pd.read_csv(caminho, sep=';', encoding='iso-8859-1')
    else:
        # Carregando dataset
        df = pd.read_csv(caminho, sep=';')

    # Renomeando colunas
    df = df.rename(columns={'Regiao - Sigla': 'Regiao', 'Estado - Sigla': 'UF'})

    # Renomeando as siglas para o nome de cada região
    df['Regiao'] = df['Regiao'].str.replace('SE', 'SUDESTE').replace('S', 'SUL').replace('CO', 
                'CENTRO-OESTE').replace('N', 'NORTE').replace('NE', 'NORDESTE')
    
    # Selecionando apenas as linhas com o produto gasolina
    produtos = ['GASOLINA']
    df_filt_produto = df[df['Produto'].isin(produtos)]

    # Convertendo coluna 'Valor de Venda' de string para float e substituindo vírgula por ponto
    df_filt_produto['Valor de Venda'] = df_filt_produto['Valor de Venda'].str.replace(',', '.').astype(float)

    # Converte a coluna 'Data da Coleta' para o tipo datetime
    df_filt_produto['Data da Coleta'] = pd.to_datetime(df_filt_produto['Data da Coleta'], dayfirst=True)

    # Preço médio por estado
    df_media_por_uf = df_filt_produto.groupby(['Regiao', 'UF'])['Valor de Venda'].mean().reset_index()
    # Renomeando as colunas para ficar mais claro
    df_media_por_uf.columns = ['Regiao', 'UF', 'Valor Medio']

    # Quantidade de postos pesquisados por estado
    df_qtd_postos_por_uf = df_filt_produto.groupby(['Regiao', 'UF'])['CNPJ da Revenda'].count().reset_index()
    # Renomeando as colunas para ficar mais claro
    df_qtd_postos_por_uf.columns = ['Regiao', 'UF', 'Qtd Postos Pesquisados']

    # Preço máximo por estado
    df_vlr_max_por_uf = df_filt_produto.groupby(['Regiao', 'UF'])['Valor de Venda'].max().reset_index()
    # Renomeando as colunas para ficar mais claro
    df_vlr_max_por_uf.columns = ['Regiao', 'UF', 'Valor Maximo']

    # Preço mínimo por estado
    df_vlr_min_por_uf = df_filt_produto.groupby(['Regiao', 'UF'])['Valor de Venda'].min().reset_index()
    # Renomeando as colunas para ficar mais claro
    df_vlr_min_por_uf.columns = ['Regiao', 'UF', 'Valor Minimo']

    # Pegando o início (min) e fim (max) do período da coleta
    df_periodos = df_filt_produto.groupby(['Regiao', 'UF'])['Data da Coleta'].agg(['min', 'max']).reset_index()
    # Renomeando as colunas para ficar mais claro
    df_periodos.columns = ['Regiao', 'UF', 'Data Inicial', 'Data Final']

    # Concatenando todos os dataframes
    dfs = [df_qtd_postos_por_uf, df_periodos, df_vlr_min_por_uf, df_vlr_max_por_uf, df_media_por_uf]
    colunas_comuns = ['Regiao', 'UF']
    lista_para_juntar = [dfs[0]] + [d.drop(columns=colunas_comuns) for d in dfs[1:]]
    # Concatenando tudo horizontalmente (axis=1)
    df_final = pd.concat(lista_para_juntar, axis=1)

    return df_final


if __name__ == '__main__':
    # caminho = r'C:\pa_xp\datasets\ca-2004-01.csv'
    lista_dfs = []
    caminho_datasets = 'C:/datasets'
    for nome_arquivo in os.listdir(caminho_datasets):
        # Verifica se o caminho completo é um arquivo
        if os.path.isfile(os.path.join(caminho_datasets, nome_arquivo)):
            caminho = f'C:\\datasets\\{nome_arquivo}'
            print(f'Processando o arquivo -> {nome_arquivo}')
            with open(caminho, 'rb') as f:
                resultado = chardet.detect(f.read(10000)) # Lê os primeiros 10k bytes
                print(f'ENCODING USADO: {resultado["encoding"]}')
                # print(resultado['encoding'])
            lista_dfs.append(gera_df(caminho))

    # Empilha todos os DataFrames da lista
    df_consolidado = pd.concat(lista_dfs, axis=0, ignore_index=True)
    df_consolidado.to_csv('dataset_anp_precos_gasolina_2004_a_2025.csv', index=False)

