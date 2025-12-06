import streamlit as st
import polars as pl
import plotly.express as px

from utils import format_currency
from data import load_data

st.set_page_config(
    page_title="Tablero Comercial",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Tablero Ejecutivo de Ventas")
st.markdown("---")

try:
    with st.spinner('Extrayendo data...'):
        df = load_data()

    if df.is_empty():
        st.warning("No se encontraron datos en la base de datos.")
        st.stop()

    st.sidebar.header("Filtros")
    
    # --- Make filter
    if 'car_make' in df.columns:
        makes_list = df['car_make'].unique().sort().to_list()
        all_makes = ["Todas"] + makes_list
        selected_make = st.sidebar.selectbox("Marca", all_makes)
    else:
        selected_make = "Todas"
    
    # --- Year filter
    if 'sale_date' in df.columns:
        years = df['sale_date'].dt.year()
        min_year = years.min()
        max_year = years.max()
        
        if min_year != max_year:
            selected_year_range = st.sidebar.slider(
                "Periodo de Venta", 
                int(min_year), int(max_year), 
                (int(min_year), int(max_year))
            )
        else:
            st.sidebar.info(f"Datos disponibles solo del año: {min_year}")
            selected_year_range = (int(min_year), int(max_year))
    else:
        selected_year_range = (2018, 2030)

    # --- Apply filters
    df_filtered = df.filter(
        (pl.col('sale_date').dt.year() >= selected_year_range[0]) & 
        (pl.col('sale_date').dt.year() <= selected_year_range[1])
    )
    
    if selected_make != "Todas":
        df_filtered = df_filtered.filter(pl.col('car_make') == selected_make)

    # --- KPIs
    total_sales = df_filtered['sale_price'].sum()
    total_commission = df_filtered['comm_earned'].sum()
    avg_price = df_filtered['sale_price'].mean()
    total_tx = df_filtered.height

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ingresos Totales", format_currency(total_sales))
    c2.metric("Comisiones Pagadas", format_currency(total_commission))
    c3.metric("Ticket Promedio", format_currency(avg_price), help="Valor promedio de venta por unidad")
    c4.metric("Unidades Vendidas", f"{total_tx:,}")

    st.markdown("###")

    # --- Graphs
    tab1, tab2 = st.tabs(["📈 Tendencia de Ingresos", "🏆 Ranking de Vendedores"])

    with tab1:
        st.subheader("Evolución Mensual de Ventas")
        if not df_filtered.is_empty():

            # Add and order
            sales_trend = (
                df_filtered
                .with_columns(pl.col("sale_date").dt.truncate("1mo").alias("mes"))
                .group_by("mes")
                .agg(pl.col("sale_price").sum().alias("total"))
                .sort("mes")
            )
            
            pdf_trend = sales_trend.to_pandas()
            
            # We determine the scale automatically.
            max_val = pdf_trend['total'].max()
            if max_val > 1_000_000_000:
                pdf_trend['total_visual'] = pdf_trend['total'] / 1_000_000_000
                y_label = "Ventas (Billones $)"
                y_format = ".2f"
                suffix = "B"
            else:
                pdf_trend['total_visual'] = pdf_trend['total'] / 1_000_000
                y_label = "Ventas (Millones $)"
                y_format = ".1f"
                suffix = "M"

            fig = px.line(pdf_trend, x='mes', y='total_visual', markers=True)
            
            fig.update_layout(
                yaxis_title=y_label,
                xaxis_title=None,
                hovermode="x unified"
            )

            # The tooltip displays the full ACTUAL value, not the scaled value.
            fig.update_traces(
                hovertemplate='<b>%{x|%B %Y}</b><br>Venta: $%{customdata:,.0f}',
                customdata=pdf_trend['total']
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Top 10 Vendedores")
        if not df_filtered.is_empty():
            top_sellers = (
                df_filtered
                .group_by("sales_person_name")
                .agg(pl.col("sale_price").sum().alias("total"))
                .top_k(10, by="total")
            )
            
            pdf_bar = top_sellers.to_pandas()
            pdf_bar['total_visual'] = pdf_bar['total'] / 1_000_000
            
            fig = px.bar(
                pdf_bar, 
                x='total_visual', 
                y='sales_person_name', 
                orientation='h', 
                text_auto='.1f'
            )
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                xaxis_title="Ventas Generadas (Millones $)",
                yaxis_title=None
            )
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Venta: $%{customdata:,.0f}',
                customdata=pdf_bar['total']
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Full details
    st.markdown("### Detalle Transaccional")
    with st.expander("🔎 Ver Datos", expanded=True):
        display_cols = {
            'sale_id': 'ID Venta',
            'sale_date': 'Fecha', 
            'car_make': 'Marca', 
            'car_model': 'Modelo', 
            'car_year': 'Año Auto',
            'sales_person_name': 'Vendedor',
            'customer_name': 'Cliente',
            'sale_price': 'Precio Venta', 
            'comm_rate': '% Comisión',
            'comm_earned': 'Comisión Ganada'
        }
        
        available = [c for c in display_cols.keys() if c in df_filtered.columns]
        
        st.dataframe(
            df_filtered.select(available)
            .head(100)
            .to_pandas()
            .rename(columns=display_cols),
            use_container_width=True, 
            hide_index=True
        )

except Exception as e:
    st.error(f"Error en la aplicación: {e}")