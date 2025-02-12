import streamlit as st
import pandas as pd
import folium
from branca.colormap import linear

# st.set_page_config()
st.set_page_config(layout='wide', page_title="Painel dos Preços")
st.title("Painel dos Preços")

# Carregar os dados das lojas e dos produtos
df_lojas = pd.read_excel('df_lojas.xlsx')
df_precos = pd.read_excel('df_picanha_2024_03_25.xlsx')

#data_load_state = st.text('Loading data...')
st.write("Data de coleta: ",df_precos['data'].max())
# Create a text element and let the reader know the data is loading.


def to_excel(dados):
    saida  = BytesIO()
    writer = pd.ExcelWriter(saida, engine='xlsxwriter')
    dados.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:A', None)  
    writer.save()
    dados_excel = saida.getvalue()
    return dados_excel

#st.write(precos_carrefour_prod.head(5))


# Criando DataFrame por Produto
### Encontrando os produtos que ocorrem com mais frequencia
occur = df_precos.groupby(['produto']).count()
c = occur.sort_values(by=['data'], ascending=False).reset_index()
c = c[['produto', 'preco', 'estado']]
c = c.rename(columns={'preco': 'Frequência'})

# Criando DataFrame por Cidade
### Encontrando os produtos que ocorrem com mais frequencia
occur2 = df_precos.groupby(['cidade/UF']).count().reset_index()
d = occur2.sort_values(by=['data'], ascending=False)
d = d[['cidade/UF', 'data', 'estado']]
d = d.rename(columns={'data': 'Frequência'})


if st.checkbox('Deseja ver a tabela de frequência de produtos e das cidades coletadas?'):
    col1, col2 = st.columns(2)

    with col1:
        num_pro = str(len(df_precos.produto.unique()))
        st.write("Número de produtos disponíveis: "+ num_pro, c)


    with col2:
        num_cidades = str(len(df_precos['cidade/UF'].unique()))
        st.write("Número de cidades coletadas: "+ num_cidades, d)
    


produtos = st.multiselect(
        "Escolha quantos produtos quiser", list(df_precos['produto'].unique()))#, [## colocar aqui os primeiros itens da lista]
if not produtos:
    st.error("Por favor, escolha pelo menos um produto.")
else:
    df_precos_2 = df_precos[df_precos['produto'].isin(produtos)]
    
st.write(produtos[0])


# Mesclar os DataFrames com base no nome da loja
df = pd.merge(df_lojas, df_precos_2, on='loja')

# Criar um seletor para escolher se deseja exibir o preço ao lado do círculo
exibir_preco = st.checkbox("Exibir preço ao lado do círculo")

# Criar um mapa Folium centrado no Brasil
mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=4)

# Definir a escala de cores para os preços
preco_minimo = df['preco'].min()
preco_maximo = df['preco'].max()
colormap = linear.YlOrRd_09.scale(preco_minimo, preco_maximo)

# Adicionar círculos para representar os preços das lojas
for _, row in df.iterrows():
    circle = folium.CircleMarker(location=[row['lat'], row['long']], radius=10, color='black', fill=True, 
                                 fill_opacity=0.7, fill_color=colormap(row['preco']))
    
    # Adicionar popup com o nome da loja e preço ao clicar no círculo
    popup_html = f"<b>{row['loja']}</b><br>Preço: <b>R${row['preco']:.2f}</b>"
    popup = folium.Popup(popup_html, parse_html=False)
    circle.add_child(popup)
    
    # Se o seletor estiver marcado, exibir o preço ao lado do círculo
    if exibir_preco:
        preco_popup = f"<b>R${row['preco']:.2f}</b>"
        folium.Marker(location=[row['lat'] - 0.01, row['long']],  # Ajuste na posição vertical
                      icon=folium.DivIcon(html=f"<div style='font-size: 12pt;'>{preco_popup}</div>")).add_to(mapa)  # Ajuste no tamanho da fonte
    
    circle.add_to(mapa)

# Adicionar a legenda da escala de cores
colormap.caption = 'Preço'
colormap.add_to(mapa)

# Exibir o mapa no Streamlit
mapa.save("mapa.html")
st.components.v1.html(open("mapa.html", "r").read(), height=600)
