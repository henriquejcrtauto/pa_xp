import plotly.express as px

# Configuração do Mapa Coroplético Animado
# É necessário um arquivo GeoJSON das UFs do Brasil. 
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson" # Arquivo Público

def criar_mapa_animado(df_consolidado):
    # O animation_frame cria o slider de tempo (Semestres)
    fig_mapa = px.choropleth(
        df_consolidado,
        geojson=geojson_url,
        locations='UF', 
        featureidkey="properties.sigla", # Chave correspondente no GeoJSON
        color='Valor Medio',
        animation_frame='Data Inicial', # Cria a linha do tempo de 2004 a 2025
        range_color=[df_consolidado['Valor Medio'].min(), df_consolidado['Valor Medio'].max()],
        color_continuous_scale="Reds",
        scope="south america",
        labels={'Valor Medio': 'Preço Médio (R$)'},
        title="Expansão dos Preços dos Combustíveis no Brasil (2004-2025)"
    )
    
    # Focar o mapa apenas no Brasil
    fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor="lightcyan")
    fig_mapa.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    
    return fig_mapa
