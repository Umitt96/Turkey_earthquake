import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Türkiye Deprem Verisi Analizi", layout="wide")
st.title("🌍 Türkiye Deprem Verisi Analizi")

# 📁 Veriyi yükleyen fonksiyon
@st.cache_data
def load_data():
    df = pd.read_excel("earthquakes.xlsx")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    return df


def apply_filters(df, year_range, selected_magnitude,  selected_region):
    filtered = df.copy()

    # Yıl filtresi
    filtered = filtered[
        (filtered['Date'].dt.year >= year_range[0]) & (filtered['Date'].dt.year <= year_range[1])
    ]
    
    # Şiddet filtresi
    if selected_magnitude != "Hepsi":
        filtered = filtered[filtered['Magnitude'] == selected_magnitude]
    
    
    # Bölge filtresi
    if selected_region != "Hepsi":
        filtered = filtered[filtered['Location'] == selected_region]
    
    return filtered

def plot_total_magnitude_per_year(df):
    total_mag = df.groupby(df['Date'].dt.year)['Magnitude'].sum().reset_index()
    total_mag.columns = ['Yıl', 'Toplam Şiddet']
    
    fig = px.bar(
        total_mag,
        x='Yıl',
        y='Toplam Şiddet',
        hover_data={'Toplam Şiddet': True},
        title='📍 Yıllara Göre Deprem Sayısı',
        color='Toplam Şiddet',
        color_continuous_scale='Sunset'
    )
    
    fig.update_layout(template='plotly_dark', xaxis_title='Yıl', yaxis_title='Toplam Şiddet')
    st.plotly_chart(fig, use_container_width=True)

  
def plot_top_regions(df):
    top_regions = df['Location'].value_counts().nlargest(10).reset_index()
    top_regions.columns = ['Bölge', 'Deprem Sayısı']
    
    # "-" değerlerini kaldırıyoruz
    top_regions = top_regions[top_regions['Bölge'] != 'Bilinmiyor']

    fig = px.bar(
        top_regions,
        x='Deprem Sayısı',
        y='Bölge',
        title='📍 En Çok Deprem Olan 10 Bölge',
        color='Deprem Sayısı',
        color_continuous_scale='Brwnyl',
        orientation='h'
    )

    fig.update_layout(
        template='plotly_dark',
        yaxis_title='',
        showlegend=False,
    )
    
    # Renk skalasını gizliyoruz
    fig.update_layout(coloraxis_showscale=False)
    
    st.plotly_chart(fig, use_container_width=True)

def plot_earthquake_map(df):
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="Magnitude",
        size="Magnitude",
        hover_name="Location",
        color_continuous_scale="Inferno",
        size_max=10,
        zoom=10,
        mapbox_style="carto-darkmatter",  # Harita stili
    )

    fig.update_layout(
        mapbox_center={"lat": 38.96, "lon": 35.24},  # Türkiye'nin merkezi
        mapbox_zoom=4,  # Harita zoom seviyesini açıyoruz
        geo=dict(showland=True, landcolor='rgba(0,0,0,0)')  # Yalnızca harita verisi görünür
    )

    fig.update_traces(marker=dict(opacity=0.2))  # Noktaların yarı saydam olması için opaklık
    st.plotly_chart(fig, use_container_width=True)  

def plot_information(df):
    total_earthquakes = len(df)
    avg_earthquakes_per_year = df.groupby(df['Date'].dt.year).size().mean()
    max_magnitude = df['Magnitude'].max()
    
    st.metric("Bütün Depremler", f"{total_earthquakes:.0f}")
    st.divider()
    st.metric("Yıllık Ortalama Deprem", f"{avg_earthquakes_per_year:.0f}")
    st.divider()
    st.metric("En Büyük Deprem Şiddeti", f"{max_magnitude:.1f} (mw)")

def main():
    df = load_data()

    # Sidebar: Filtreleme seçenekleri
    st.sidebar.title("Filtreler")
    
    year_range = st.sidebar.slider("Yıl Aralığı", 1900, 2025, (1900, 2025))
    magnitude_options = ["Hepsi", 4, 5, 6, 7]
    selected_magnitude = st.sidebar.selectbox("Deprem Şiddeti", magnitude_options, index=0)

        
    df['Location'] = df['Location'].replace("-", "Bilinmiyor")
    top_regions = df['Location'].value_counts().nlargest(10).index
    selected_region = st.sidebar.selectbox("Bölge Seçin", ["Hepsi"] + list(top_regions))
    
    filtered_df = apply_filters(df, year_range, selected_magnitude,selected_region)


    # 📈 Grafikler
    col1, col2 = st.columns([3,1])

    with col1:
        plot_earthquake_map(filtered_df)
    with col2:
        plot_information(filtered_df)
    

    col1, col2 = st.columns([1,2])

    with col1:
        plot_top_regions(filtered_df)
    with col2:
        plot_total_magnitude_per_year(filtered_df)
        

if __name__ == "__main__":
    main()
