import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from mapas import *


# Carregamento dataset
df = pd.read_csv('dataset_anp_precos_gasolina_2004_a_2025.csv')

# Extrair anos únicos e ordenar
df['Ano'] = pd.to_datetime(df['Data Inicial']).dt.year
anos_disponiveis = sorted(df['Ano'].unique())

# Inicialização do App
app = dash.Dash(__name__)

# Layout do Dashboard
app.layout = html.Div(style={'backgroundColor': '#AABADD', 'fontFamily': 'Arial'}, children=[
# app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'fontFamily': 'Arial'}, children=[
    
    # Cabeçalho
    html.Div([
        html.H1("OEC - Observatório Econômico dos Combustíveis: Memória do Combustível (2004-2025)", 
                style={'textAlign': 'center', 'color': '#003366', 'padding': '20px'}),
        html.P("Análise histórica baseada em dados oficiais da ANP para soberania energética.",
               style={'textAlign': 'center', 'color': '#666'})
    ], style={'backgroundColor': '#F1A629', 'marginBottom': '10px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),

    # Filtros e KPIs
    html.Div([
        html.Div([
            # Conjunto de Dropdowns para filtrar os gráficos
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

            html.Br(),
            html.Label("Selecione o ano inicial:"),
            dcc.Dropdown(id='filtro-ano-inicio',
                        options=[{'label': str(ano), 'value': ano} for ano in anos_disponiveis],
                        value=anos_disponiveis[0], # Padrão: Primeiro ano da série (2004)                         
                        placeholder="Selecione ano inicial"),
            
            html.Br(),
            html.Label("Selecione o ano final:"),
            dcc.Dropdown(id='filtro-ano-fim', 
                        options=[{'label': str(ano), 'value': ano} for ano in anos_disponiveis],
                        value=anos_disponiveis[-1], # Padrão: Último ano da série (2025)                         
                        placeholder="Selecione ano final"),                        
        ], style={'width': '15%', 'display': 'inline-block', 'padding': '20px', 'verticalAlign': 'top'}),

        # Cards de KPI
        html.Div([
            html.Div([
                html.H4("Preço Médio Atual", style={'margin': '0'}),
                html.H2(id='kpi-medio', style={'color': '#c9302c'}) #d9534f
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'marginRight': '10px'}),
            
            html.Div([
                html.H4("UF mais Cara (Período)", style={'margin': '0'}),
                html.H2(id='kpi-max', style={'color': '#c9302c'})
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'marginRight': '10px'}),
            
            html.Div([
                html.H4("Postos Pesquisados", style={'margin': '0'}),
                html.H2(id='kpi-postos', style={'color': '#008080'})
            ], className='card', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px'}),

            html.Div([
                # Observações sobre os filtros aplicados
                html.H4("OBS == > Nenhum filtro selecionado = Preço Médio Nacional"),
                html.H4("Região Selecionada = Preço Médio da Região"),
                html.H4("Região e UF Selecionadas = Preço Médio da UF"),                
            ], style={'display': 'inline-block', 'width': '95%', 'textAlign': 'center', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '10px', 'margin-top': '10px'})            
        ], style={'width': '80%', 'display': 'inline-block', 'padding': '20px'}),
 
    ]),

    # Gráfico Principal
    html.Div([
        dcc.Graph(id='grafico-serie-temporal')
    ], style={'padding': '20px', 'backgroundColor': 'white', 'margin': '20px', 'borderRadius': '10px'}),

    # Mapa e Boxplot
    html.Div([
        html.Div([dcc.Graph(figure=criar_mapa_animado(df))], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='boxplot-regional')], style={'width': '50%', 'display': 'inline-block'})
    ])
])

# Callbacks para Interatividade

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

# Atualiza os Cards, o gráfico principal e o gráfico de dispersão com base nos filtros
@app.callback(
    [Output('grafico-serie-temporal', 'figure'),
    Output('boxplot-regional', 'figure'),
     Output('kpi-medio', 'children'),
     Output('kpi-max', 'children'),
     Output('kpi-postos', 'children')],
    [Input('filtro-regiao', 'value'),
     Input('filtro-uf', 'value'),
     Input('filtro-ano-inicio', 'value'),
     Input('filtro-ano-fim', 'value')]
)
def update_dashboard(regiao, uf, ano_inicio, ano_fim):
    dff = df.copy()
    
    # Filtros de Localidade e Tempo
    if regiao: dff = dff[dff['Regiao'] == regiao]
    if uf: dff = dff[dff['UF'] == uf]
    if ano_inicio and ano_fim: # Só filtra se os dois dropdopwns estiverem setados
        dff = dff[(dff['Ano'] >= ano_inicio) & (dff['Ano'] <= ano_fim)]
    
    # Ordenar por data para garantir que o preenchimento do gráfico não quebre
    dff = dff.sort_values('Data Inicial')

    # Lógica do Card (KPI - Valor Médio Atual) Obtem o valor do último semestre selecionado para o card
    if not dff.empty:
        ultima_data = dff['Data Inicial'].max()
        valor_atual = dff[dff['Data Inicial'] == ultima_data]['Valor Medio'].mean()
        valor_display = f"R$ {valor_atual:.2f}"
    else:
        valor_display = "R$ 0,00"

    # Identificar o último semestre disponível nos dados filtrados
    ultima_data = dff['Data Inicial'].max()

    # Filtrar apenas os dados do último semestre para os KPIs
    df_ultimo_semestre = dff[dff['Data Inicial'] == ultima_data]

    # Lógica para os outros Cards (UF mais cara e Quantidade de postos pesquisados)
    if not df_ultimo_semestre.empty:   
        # Identificar a UF mais cara apenas neste último semestre
        uf_mais_cara_atual = df_ultimo_semestre.loc[df_ultimo_semestre['Valor Medio'].idxmax(), 'UF']
        
        # Somar postos apenas do último semestre
        total_postos_atual = f"{df_ultimo_semestre['Qtd Postos Pesquisados'].sum():,}"
    else:
        uf_mais_cara_atual = "N/A"
        total_postos_atual = "0"


    # Gráfico 1 - Gráfico de linhas com Área de Variação (Min/Max)
    fig = go.Figure()

    if not dff.empty:
        # Camada 1: Linha do Valor Máximo (invisível, serve de borda superior)
        fig.add_trace(go.Scatter(
            x=dff['Data Inicial'], y=dff['Valor Maximo'],
            mode='lines', line=dict(width=0),
            showlegend=False, hoverinfo='skip'
        ))

        # Camada 2: Linha do Valor Mínimo com preenchimento até a camada superior (Máximo)
        fig.add_trace(go.Scatter(
            x=dff['Data Inicial'], y=dff['Valor Minimo'],
            mode='lines', line=dict(width=0),
            fill='tonexty', # Preenche até o traço anterior (Valor Máximo)
            fillcolor='rgba(0, 51, 102, 0.15)', # Azul transparente
            name='Variação Min/Max nos Postos',
            hoverinfo='skip'
        ))

        # Camada 3: Linha do Valor Médio (Destaque principal)
        fig.add_trace(go.Scatter(
            x=dff['Data Inicial'], y=dff['Valor Medio'],
            mode='lines+markers',
            line=dict(color='#FF0000', width=3),
            # line=dict(color='#003366', width=3),
            name='Preço Médio Semestral'
        ))

    # Estilização do Gráfico 1
    fig.update_layout(
        title=f"Evolução de Preços: {ano_inicio} a {ano_fim}",
        template="seaborn",
        xaxis_title="Período Semestral",
        yaxis_title="Preço (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Gráfico 2: Boxplot Regional (Dispersão)
    # Este gráfico reflete apenas o intervalo de anos selecionado
    fig_box = px.box(
        dff,
        x="Regiao",
        y="Valor Medio",
        color="Regiao",
        points="all", # Exibe os pontos individuais (semestres/UFs)
        title=f"Dispersão Regional ({ano_inicio} - {ano_fim})",
        template="seaborn"
    )
    
    fig_box.update_layout(showlegend=False)    

    return fig, fig_box, valor_display, uf_mais_cara_atual, total_postos_atual


if __name__ == '__main__':
    app.run(debug=True)