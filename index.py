import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from mapas import *

# 1. Carregamento e Simulação (Substitua pelo seu arquivo .csv)
df = pd.read_csv('dataset_anp_precos_gasolina_2004_a_2025.csv')
# Simulando a estrutura para execução do exemplo:

# =============================================================
# ============= MOCKADO =======================================
# =============================================================
# data = {
#     'Regiao': ['SUL', 'SUL', 'NORTE', 'NORTE'],
#     'UF': ['PR', 'RS', 'AM', 'PA'],
#     'Data Inicial': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01']),
#     'Valor Medio': [5.80, 6.10, 6.50, 6.30],
#     'Valor Minimo': [5.50, 5.90, 6.20, 6.00],
#     'Valor Maximo': [6.20, 6.40, 6.90, 6.70],
#     'Qtd Postos Pesquisados': [120, 150, 80, 95]
# }
# df = pd.DataFrame(data)

# Inicialização do App
app = dash.Dash(__name__)

# 2. Layout do Dashboard
app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'fontFamily': 'Arial'}, children=[
    
    # Cabeçalho
    html.Div([
        html.H1("OEC - Observatório Energético dos Combustíveis: Memória do Combustível (2004-2025)", 
                style={'textAlign': 'center', 'color': '#003366', 'padding': '20px'}),
        html.P("Análise histórica baseada em dados oficiais da ANP para soberania energética.",
               style={'textAlign': 'center', 'color': '#666'})
    ], style={'backgroundColor': 'white', 'marginBottom': '10px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),

    # Filtros e KPIs
    html.Div([
        html.Div([
            html.Label("Selecione a Região:"),
            dcc.Dropdown(
                id='filtro-regiao',
                options=[{'label': i, 'value': i} for i in df['Regiao'].unique()],
                placeholder="Todas as Regiões",
                clearable=True
            ),
            html.Br(),
            html.Label("Selecione a UF:"),
            dcc.Dropdown(id='filtro-uf', placeholder="Selecione uma UF"),
        ], style={'width': '15%', 'display': 'inline-block', 'padding': '20px', 'verticalAlign': 'top'}),

        # Cards de KPI
        html.Div([
            html.Div([
                html.H4("Preço Médio Atual", style={'margin': '0'}),
                html.H2(id='kpi-medio', style={'color': '#d9534f'})
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'marginRight': '10px'}),
            
            html.Div([
                html.H4("UF mais Cara (Período)", style={'margin': '0'}),
                html.H2(id='kpi-max', style={'color': '#c9302c'})
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'marginRight': '10px'}),
            
            html.Div([
                html.H4("Postos Pesquisados", style={'margin': '0'}),
                html.H2(id='kpi-postos', style={'color': '#337ab7'})
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px'})
        ], style={'width': '80%', 'display': 'inline-block', 'padding': '20px'}),
            html.Div([
                html.H4("OBS == > Nenhum filtro selecionado = Preço Médio Nacional, Região Selecionada = Preço Médio da Região, Região e UF Selecionadas = Preço Médi0 da UF")
        ], style={'display': 'inline-block', 'width': '95%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px'})
    ]),

    # Gráficos Principais
    html.Div([
        dcc.Graph(id='grafico-serie-temporal')
    ], style={'padding': '20px', 'backgroundColor': 'white', 'margin': '20px', 'borderRadius': '10px'}),

    # Mapa e Boxplot
    html.Div([
        html.Div([dcc.Graph(figure=criar_mapa_animado(df))], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=criar_boxplot_regional(df))], style={'width': '50%', 'display': 'inline-block'})
    ])

    # html.Div([
    #     html.Div([dcc.Graph(id='mapa-brasil')], style={'width': '50%', 'display': 'inline-block'}),
    #     html.Div([dcc.Graph(id='boxplot-regional')], style={'width': '50%', 'display': 'inline-block'})
    # ])
])

# 3. Callbacks para Interatividade

# Atualizar Filtro de UF baseado na Região
@app.callback(
    Output('filtro-uf', 'options'),
    Input('filtro-regiao', 'value')
)
def set_uf_options(selected_regiao):
    if selected_regiao:
        dff = df[df['Regiao'] == selected_regiao] # filtra as linhas pela Regiao
    else:
        dff = df # Df não filtrado - Todas as linhas
    return [{'label': i, 'value': i} for i in dff['UF'].unique()] # Retorna um dicionário com as UF de cada Regiao

# Atualizar Gráficos e KPIs
@app.callback(
    [Output('grafico-serie-temporal', 'figure'),
     Output('kpi-medio', 'children'),
     Output('kpi-max', 'children'),
     Output('kpi-postos', 'children')],
    [Input('filtro-regiao', 'value'),
     Input('filtro-uf', 'value')]
)
def update_dashboard(regiao, uf):
    # 1. Aplicar filtros de localidade
    dff = df.copy()
    if regiao: dff = dff[dff['Regiao'] == regiao] # Filtra as linhas pela Regiao
    if uf: dff = dff[dff['UF'] == uf] # Filtra as linhas pela UF

    # 2. Identificar o último semestre disponível nos dados filtrados
    # Assumindo que 'Data Inicial' é do tipo datetime
    ultima_data = dff['Data Inicial'].max()

    # 3. Filtrar apenas os dados do último semestre para os KPIs
    df_ultimo_semestre = dff[dff['Data Inicial'] == ultima_data]

    # 4. Calcular o Preço Médio Atual (da região/UF selecionada)
    if not df_ultimo_semestre.empty:
        preco_atual = df_ultimo_semestre['Valor Medio'].mean()
        label_kpi_medio = f"R$ {preco_atual:.2f}"
        
        # Opcional: Identificar a UF mais cara apenas neste último semestre
        uf_mais_cara_atual = df_ultimo_semestre.loc[df_ultimo_semestre['Valor Medio'].idxmax(), 'UF']
        
        # Somar postos apenas do último semestre
        total_postos_atual = f"{df_ultimo_semestre['Qtd Postos Pesquisados'].sum():,}"
    else:
        label_kpi_medio = "N/A"
        uf_mais_cara_atual = "N/A"
        total_postos_atual = "0"

    # Gráfico 1: Linha com Banda de Variação (Min/Max)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=dff['Data Inicial'], y=dff['Valor Maximo'], mode='lines', line=dict(width=0), showlegend=False))
    fig_line.add_trace(go.Scatter(x=dff['Data Inicial'], y=dff['Valor Minimo'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(217, 83, 79, 0.2)', name='Amplitude Min/Max'))
    fig_line.add_trace(go.Scatter(x=dff['Data Inicial'], y=dff['Valor Medio'], mode='lines+markers', line=dict(color='#d9534f'), name='Valor Médio'))
    
    # # Adicionar uma linha vertical ou anotação no gráfico destacando o último dado
    # fig_line.add_vline(x=ultima_data, line_dash="dash", line_color="gray", 
    #                    annotation_text="Último Semestre")    
    
    fig_line.update_layout(title="Evolução Semestral do Preço (R$)", template="plotly_dark")

    # Cálculos KPI
    preco_medio = f"R$ {dff['Valor Medio'].mean():.2f}"
    preco_medio_atual = f"R$ {dff['Valor Medio'].mean():.2f}"
    max_uf = dff.loc[dff['Valor Medio'].idxmax(), 'UF'] if not dff.empty else "-"
    total_postos = f"{dff['Qtd Postos Pesquisados'].sum():,}"

    # return fig_line, preco_medio, max_uf, total_postos
    return fig_line, label_kpi_medio, uf_mais_cara_atual, total_postos_atual    

if __name__ == '__main__':
    app.run(debug=True)