import streamlit as st
import pandas as pd
import folium
from branca.colormap import linear

import plotly.express as px

from plotly.subplots import make_subplots


# Carregar os dados das lojas e dos produtos
df_lojas = pd.read_excel('df_lojas.xlsx')
df_precos = pd.read_excel('df_tilapia_2024_02_27.xlsx')

# st.set_page_config()
st.set_page_config(layout='wide', page_title="Painel dos Preços")
st.title("Painel dos Preços")

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
    
    st.write(produtos)


    # Mesclar os DataFrames com base no nome da loja
    df = pd.merge(df_lojas[['loja', 'lat', 'long']], df_precos_2, on='loja')

    # Criar um seletor para escolher se deseja exibir o preço ao lado do círculo
    exibir_preco = st.checkbox("Exibir preço ao lado da figura")

    # Criar um mapa Folium centrado no Brasil
    mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=4)

    # Definir a escala de cores para os preços
    preco_minimo = df['preco'].min()  # Menor preço dos produtos selecionados
    preco_maximo = df['preco'].max()  # Maior preço dos produtos selecionados
    colormap = linear.YlOrRd_09.scale(preco_minimo, preco_maximo)

    # Criar uma lista de formas geométricas para cada tipo de produto
    formas = ['circle', 'square', 'triangle', 'pentagon']

    # Adicionar marcadores para cada produto selecionado no mapa
    for i, produto in enumerate(produtos):
        # Filtrar o DataFrame para o produto atual
        df_produto = df[df['produto'] == produto]
        
        # Adicionar marcadores para cada loja que vende o produto atual
        for j, (_, row) in enumerate(df_produto.iterrows()):
            # Adicionar um pequeno deslocamento horizontal para cada forma
            offset = (j - len(df_produto) / 2) * 0.0001
            
            # Criar a forma geométrica com a cor do preço e borda preta
            marker = folium.RegularPolygonMarker(location=[row['lat'] + offset, row['long']], 
                                                fill_color=colormap(row['preco']), 
                                                color='black',  # Cor da borda preta
                                                number_of_sides=i+3,  # O número de lados aumenta com o índice
                                                radius=10).add_to(mapa)
            
            # Adicionar texto ao lado da forma se a opção "Exibir preço ao lado da figura" estiver selecionada
            if exibir_preco:
                folium.Marker(location=[row['lat'] + offset, row['long'] + 0.0003],  # Deslocamento vertical
                            icon=folium.DivIcon(html=f"<div style='font-size: 12pt; font-weight: bold;'>{row['preco']}</div>")).add_to(mapa)
            
            # Criar o popup com informações da loja, produto e preço
            popup_html = f"<b>Loja:</b> {row['loja']}<br><b>Produto:</b> {row['produto']}<br><b>Preço:</b> R${row['preco']:.2f}"
            popup = folium.Popup(popup_html, parse_html=False)
            marker.add_child(popup)

    # Adicionar a legenda da escala de cores
    colormap.caption = 'Preço'
    colormap.add_to(mapa)


    # Exibir o mapa no Streamlit
    mapa.save("mapa.html")
    st.components.v1.html(open("mapa.html", "r").read(), height=600)



#if st.button("Clique aqui para ver o gráfico com os produtos selecionados"):

    #select_produto_1 = st.selectbox("Escolha o produto:", options = occur_a['produto'].unique())
    #### JUNTANDO OS HISTÓRICOS
    #query = [select1, select2, select3, select4] 
    #quatro_historico = precos_carrefour_prod[precos_carrefour_prod['produto'].isin(query)]
    #quatro_historico = quatro_historico.drop_duplicates()
    
   

    fig = px.scatter(df, x="cidade/UF", y='preco', color='produto', title= "Registro Diário de Preços",  hover_data=df.columns.unique())
    st.plotly_chart(fig, use_container_width = True,height=800)

    fig2 = px.box(df, x="produto", y='preco', color='produto', title="Variação de Preços",  hover_data=df.columns.unique())
    st.plotly_chart(fig2, use_container_width = True,height=400)
    
    #down9 = to_excel(df)
    #st.download_button(label="Clique aqui para baixar a Tabela de Preços!", file_name="tabela_precos_cities.xlsx", data = down9,  key=7)



st.markdown(
        """
        Seleção por cidade

        **👈 
    """
    )


st.write("Selecione uma cidade: ")
select_city = st.selectbox("Lista de Cidades", df['cidade/UF'].unique())
if not select_city:
    st.error("Por favor, escolha pelo menos uma cidade.")
else:
    precos_carrefour_city = df[df['cidade/UF'].isin([select_city])]
    precos_carrefour_city = precos_carrefour_city.sort_values(by=['preco'], ascending=False).reset_index()
    st.write("Tabela de Preços de: ",precos_carrefour_city[['produto', 'preco', 'desconto', 'loja']])

    
#down10 = to_excel(precos_carrefour_city)
#st.download_button(label="Clique aqui para baixar a Tabela de Preços!", file_name="tabela_precos.xlsx", data = down10,  key=15)
