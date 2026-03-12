import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Amazon Sales Analysis", layout="wide")

@st.cache_data
def load_data():
    """Carga datos de ejemplo o desde URL. Reemplaza con tu CSV real."""
    # Para demo: datos típicos de Amazon sales (ajusta columnas a tu dataset)
    data = {
        'date': pd.date_range('2024-01-01', periods=1000, freq='D').strftime('%Y-%m-%d'),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], 1000),
        'product_name': ['Product ' + str(i) for i in range(1000)],
        'sales': np.random.randint(10, 500, 1000),
        'quantity': np.random.randint(1, 50, 1000),
        'revenue': np.random.uniform(100, 10000, 1000).round(2),
        'price': np.random.uniform(10, 200, 1000).round(2),
        'region': np.random.choice(['US', 'EU', 'Asia', 'LATAM'], 1000),
        'rating': np.random.uniform(1, 5, 1000).round(1)
    }
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['date']).dt.month_name()
    df['revenue'] = df['price'] * df['quantity']
    return df

df = load_data()
st.success(f"📊 Dataset cargado: {len(df):,} filas, {len(df.columns)} columnas")

## Métricas clave
col1, col2, col3, col4, col5 = st.columns(5)
total_revenue = df['revenue'].sum()
total_sales = df['sales'].sum()
avg_price = df['price'].mean()
top_category = df.groupby('product_category')['revenue'].sum().idxmax()
total_orders = len(df)

col1.metric("💰 Ingresos Totales", f"${total_revenue:,.0f}")
col2.metric("📦 Ventas Totales", f"{total_sales:,}")
col3.metric("💵 Precio Promedio", f"${avg_price:.2f}")
col4.metric("🏆 Categoría Top", top_category)
col5.metric("📋 Órdenes", f"{total_orders:,}")

## Ventas por Categoría (Bar Chart)
if st.checkbox("📈 Ventas por Categoría"):
    col1, col2 = st.columns(2)
    
    with col1:
        cat_revenue = df.groupby('product_category')['revenue'].sum().sort_values( descending=True)
        fig1 = px.bar(x=cat_revenue.index, y=cat_revenue.values, 
                      title="Ingresos por Categoría",
                      color=cat_revenue.values, color_continuous_scale='Viridis')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        cat_qty = df.groupby('product_category')['quantity'].sum().sort_values( descending=True)
        fig2 = px.pie(values=cat_qty.values, names=cat_qty.index, 
                      title="Distribución de Cantidades por Categoría")
        st.plotly_chart(fig2, use_container_width=True)

## Tendencia de Ventas Temporales (Line Chart)
if st.checkbox("📊 Tendencia de Ventas"):
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_revenue = df.groupby('month')['revenue'].sum().reindex(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        )
        fig3 = px.line(x=monthly_revenue.index, y=monthly_revenue.values, 
                       title="Ingresos Mensuales", markers=True)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = px.scatter(df, x='rating', y='revenue', color='product_category',
                         title="Revenue vs Rating por Categoría", trendline='ols')
        st.plotly_chart(fig4, use_container_width=True)

## Ventas por Región (Map & Heatmap)
if st.checkbox("🌍 Ventas por Región"):
    col1, col2 = st.columns(2)
    
    with col1:
        region_revenue = df.groupby('region')['revenue'].sum()
        fig5 = px.bar(x=region_revenue.index, y=region_revenue.values,
                      title="Ingresos por Región")
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        fig6 = px.choropleth(df, locations='region', 
                            color='revenue', locationmode='country names',
                            title="Mapa de Ingresos por Región",
                            color_continuous_scale='Blues')
        st.plotly_chart(fig6, use_container_width=True)

## Top Productos (Table + Bar)
if st.checkbox("⭐ Top Productos"):
    top_products = df.groupby('product_name')['revenue'].sum().nlargest(10).reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tabla Top 10")
        st.dataframe(top_products, use_container_width=True)
    
    with col2:
        fig7 = px.bar(top_products, x='product_name', y='revenue',
                     title="Top 10 Productos por Ingresos")
        fig7.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig7, use_container_width=True)

## Filtros Interactivos
st.sidebar.header("🔍 Filtros")
selected_category = st.sidebar.multiselect("Categoría", df['product_category'].unique())
selected_region = st.sidebar.multiselect("Región", df['region'].unique())

filtered_df = df
if selected_category:
    filtered_df = filtered_df[filtered_df['product_category'].isin(selected_category)]
if selected_region:
    filtered_df = filtered_df[filtered_df['region'].isin(selected_region)]

st.sidebar.metric("Filas filtradas", len(filtered_df))

# Actualiza métricas con filtros
if st.sidebar.button("Aplicar Filtros y Actualizar"):
    st.rerun()

st.subheader("🔢 Vista de Datos Filtrados")
st.dataframe(filtered_df.head(500), use_container_width=True)

# Descarga
csv = filtered_df.to_csv(index=False)
st.download_button("📥 Descargar CSV filtrado", csv, "amazon_sales_filtered.csv")
