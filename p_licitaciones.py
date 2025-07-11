import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo
st.set_page_config(page_title="Análisis Licitaciones", layout="wide")
plt.style.use("seaborn-v0_8-colorblind")

# ----------- CARGA DE DATOS -----------
@st.cache_data
def cargar_datos():
    df = pd.read_parquet("data_licitaciones_2023_2024_reducido.parquet")
    return df

DF = cargar_datos()

# ----------- SIDEBAR DE NAVEGACIÓN -----------
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a sección:", [
    "Introducción", "Gasto Público", "Competitividad", "Eficiencia", "Transparencia",
    "Municipios", "Comparación 2023 vs 2024", "Hallazgos", "Conclusiones"
])

# ----------- FILTROS ----------- 
st.sidebar.markdown("---")
selected_year = st.sidebar.selectbox("Selecciona el año", options=sorted(DF['Año'].unique()))
selected_rubro = st.sidebar.selectbox("Filtrar por Rubro (opcional)", options=["Todos"] + sorted(DF['RubroN1'].dropna().unique()))
selected_muni = st.sidebar.selectbox("Filtrar por Municipio (opcional)", options=["Todos"] + sorted(DF['Institucion'].dropna().unique()))

# Aplicar filtros
df = DF.copy()
df = df[df['Año'] == selected_year]
if selected_rubro != "Todos":
    df = df[df['RubroN1'] == selected_rubro]
if selected_muni != "Todos":
    df = df[df['Institucion'] == selected_muni]

# ----------- DESCARGA DE DATOS FILTRADOS -----------
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Descargar datos filtrados (.csv)",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="datos_filtrados.csv",
    mime="text/csv"
)

# ----------- SECCIONES -----------
if seccion == "Introducción":
    st.title("Análisis de Licitaciones Municipales 2023-2024")
    st.markdown("""
    Este proyecto analiza los procesos de licitación municipal en Chile entre 2023 y 2024. 
    Buscamos identificar patrones de gasto, medir la competencia de proveedores, 
    evaluar la eficiencia del proceso y estudiar mecanismos de transparencia.
    """)

elif seccion == "Gasto Público":
    st.header("Objetivo 1: Evaluar el gasto público")

    st.subheader("Top rubros por monto estimado")
    top_rubros = df.groupby("RubroN1")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    top_rubros.plot(kind='bar', ax=ax1, color="#c71585")
    ax1.set_ylabel("Monto Estimado")
    ax1.set_title("Top 10 Rubros")
    st.pyplot(fig1)

    st.subheader("Distribución de financiamiento")
    top_financiamiento = df['FuenteFinanciamiento'].fillna("Desconocido").value_counts().head(10)
    otros = df['FuenteFinanciamiento'].fillna("Desconocido").value_counts()[10:].sum()
    top_financiamiento["Otros"] = otros
    fig2, ax2 = plt.subplots()
    top_financiamiento.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax2, colors=sns.color_palette("RdPu", len(top_financiamiento)))
    ax2.set_ylabel("")
    ax2.set_title("Fuente de Financiamiento")
    st.pyplot(fig2)

elif seccion == "Competitividad":
    st.header("Objetivo 2: Competitividad del mercado")

    st.subheader("Distribución de oferentes por licitación")
    oferentes = df.groupby("NroLicitacion")["Proveedor"].nunique()
    fig3, ax3 = plt.subplots()
    sns.histplot(oferentes, bins=30, ax=ax3, color="#db7093")
    ax3.set_title("Número de oferentes por licitación")
    st.pyplot(fig3)

    st.subheader("Adjudicaciones por tamaño de proveedor")
    df_adjudicada = df[df['ResultadoOferta'] == 'Adjudicada']
    tamano = df_adjudicada['TamanoProveedor'].value_counts(normalize=True) * 100
    if tamano.empty:
        st.warning("No hay datos de adjudicaciones disponibles para los filtros seleccionados.")
    else:
        fig4, ax4 = plt.subplots()
        tamano.plot(kind='barh', ax=ax4, color="#ba55d3")
        ax4.set_title("% Adjudicado por Tamaño de Proveedor")
        st.pyplot(fig4)

elif seccion == "Eficiencia":
    st.header("Objetivo 3: Eficiencia del proceso")
    df['FechaPublicacion'] = pd.to_datetime(df['FechaPublicacion'], errors='coerce')
    df['FechaAdjudicacion'] = pd.to_datetime(df['FechaAdjudicacion'], errors='coerce')
    df['Plazo'] = (df['FechaAdjudicacion'] - df['FechaPublicacion']).dt.days

    st.subheader("Tiempo entre publicación y adjudicación")
    fig5, ax5 = plt.subplots()
    sns.histplot(df['Plazo'].dropna(), bins=30, ax=ax5, color="#cc66cc")
    ax5.set_title("Días entre publicación y adjudicación")
    st.pyplot(fig5)

elif seccion == "Transparencia":
    st.header("Objetivo 4: Transparencia")

    st.subheader("Tipo de licitación")
    fig6, ax6 = plt.subplots()
    df['TipoLicitacion'].value_counts().plot(kind='bar', ax=ax6, color="#e75480")
    ax6.set_title("Distribución de tipos de licitación")
    st.pyplot(fig6)

    st.subheader("Publicidad de ofertas técnicas")
    fig7, ax7 = plt.subplots()
    df['PublicidadOfertasTecnicas'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax7, colors=sns.color_palette("pink"))
    ax7.set_ylabel("")
    st.pyplot(fig7)

elif seccion == "Municipios":
    st.header("Análisis por Municipio")
    st.subheader("Top 10 Municipios por Monto Estimado")
    top_muni = df.groupby("Institucion")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig_muni, ax_muni = plt.subplots()
    top_muni.plot(kind='barh', ax=ax_muni, color="#da70d6")
    ax_muni.set_title("Top 10 Instituciones por Monto Total Estimado")
    ax_muni.set_xlabel("Monto Estimado")
    st.pyplot(fig_muni)

elif seccion == "Comparación 2023 vs 2024":
    st.header("Comparación entre Años: 2023 vs 2024")

    df_comp = DF.copy()
    df_comp['FechaPublicacion'] = pd.to_datetime(df_comp['FechaPublicacion'], errors='coerce')
    df_comp['FechaAdjudicacion'] = pd.to_datetime(df_comp['FechaAdjudicacion'], errors='coerce')
    df_comp['Plazo'] = (df_comp['FechaAdjudicacion'] - df_comp['FechaPublicacion']).dt.days

    resumen = df_comp.groupby("Año").agg({
        "MontoEstimadoLicitacion": "sum",
        "NroLicitacion": "nunique",
        "Proveedor": "nunique",
        "Plazo": "mean"
    }).rename(columns={
        "MontoEstimadoLicitacion": "Total Monto Estimado",
        "NroLicitacion": "Total Licitaciones",
        "Proveedor": "Proveedores Únicos",
        "Plazo": "Plazo Promedio (días)"
    })

    st.dataframe(resumen)

    fig_comp, ax_comp = plt.subplots()
    resumen["Total Monto Estimado"].plot(kind="bar", ax=ax_comp, color=["#ffb6c1", "#d87093"])
    ax_comp.set_title("Comparación de Gasto Total por Año")
    ax_comp.set_ylabel("Monto Total Estimado")
    st.pyplot(fig_comp)

elif seccion == "Hallazgos":
    st.header("Principales Hallazgos")
    st.markdown("""
    - Rubros líderes: Equipamiento médico, maquinaria y vehículos.
    - 99.8% del financiamiento es municipal.
    - Promedio de 4.8 oferentes por licitación.
    - 19.93% de licitaciones con solo un proveedor.
    - 56% adjudicadas a grandes empresas.
    - Tiempo medio de 39-45 días de publicación a adjudicación.
    - Solo 37% justifican el monto estimado.
    """)

elif seccion == "Conclusiones":
    st.header("Conclusiones y Recomendaciones")
    st.markdown("""
    - Es necesario mejorar la trazabilidad y validación de datos.
    - Se recomienda estandarizar los formatos y campos obligatorios.
    - Mayor fiscalización sobre procesos con proveedor único.
    - Integrar población municipal para gasto per cápita.
    - Desarrollar alertas para licitaciones sin justificación.
    """)

