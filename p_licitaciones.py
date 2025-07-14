import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Análisis Licitaciones", layout="wide")
plt.style.use("seaborn-v0_8-colorblind")

@st.cache_data
def cargar_datos():
    return pd.read_parquet("data_licitaciones_2023_2024_reducido.parquet")

DF = cargar_datos()

st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a sección:", [
    "Introducción", "Gasto Público", "Competitividad", "Eficiencia", "Transparencia",
    "Municipios", "Comparación 2023 vs 2024", "Conclusiones"
])

st.sidebar.markdown("---")
selected_year = st.sidebar.selectbox("Selecciona el año", sorted(DF["Año"].unique()))
selected_rubro = st.sidebar.selectbox("Filtrar por Rubro (opcional)", ["Todos"] + sorted(DF["RubroN1"].dropna().unique()))
selected_muni = st.sidebar.selectbox("Filtrar por Municipio (opcional)", ["Todos"] + sorted(DF["Institucion"].dropna().unique()))

df = DF.copy()
df = df[df["Año"] == selected_year]
if selected_rubro != "Todos":
    df = df[df["RubroN1"] == selected_rubro]
if selected_muni != "Todos":
    df = df[df["Institucion"] == selected_muni]

if seccion == "Introducción":
    st.title("Análisis de Licitaciones Municipales 2023–2024")
    st.markdown("""
    Este proyecto analiza los procesos de licitación municipal en Chile entre 2023 y 2024. 
    Se evalúan los montos adjudicados, la eficiencia del proceso, la competencia entre oferentes 
    y los niveles de transparencia de las instituciones municipales.
    """)

elif seccion == "Gasto Público":
    st.header("Objetivo 1: Evaluar el gasto público")

    st.subheader("Top rubros por monto estimado")
    top_rubros = df.groupby("RubroN1")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    top_rubros.plot(kind="bar", ax=ax1, color="#c71585")
    ax1.set_ylabel("Monto Estimado")
    ax1.set_title("Top 10 Rubros")
    st.pyplot(fig1)
    st.caption("Se identifican los rubros con mayor volumen de gasto público estimado por parte de los municipios. Esto permite evaluar si los recursos se concentran en áreas críticas como salud, transporte o equipamiento, o si existen desviaciones presupuestarias hacia rubros menos prioritarios.")

    st.subheader("Distribución de financiamiento")
    top_fin = df["FuenteFinanciamiento"].fillna("Desconocido").value_counts().head(10)
    otros = df["FuenteFinanciamiento"].fillna("Desconocido").value_counts()[10:].sum()
    top_fin["Otros"] = otros
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax2.pie(
        top_fin, labels=None, autopct='%1.1f%%', startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=sns.color_palette("RdPu", len(top_fin))
    )
    ax2.set_title("Fuente de Financiamiento")
    ax2.legend(top_fin.index, loc="center left", bbox_to_anchor=(1, 0.5))
    for autotext in autotexts:
        autotext.set_fontsize(9)
    st.pyplot(fig2)
    st.caption("Se analiza qué proporción del financiamiento proviene de fondos municipales, regionales u otras fuentes. Una alta dependencia del financiamiento interno podría limitar la escala o el alcance de las licitaciones.")

elif seccion == "Competitividad":
    st.header("Objetivo 2: Competitividad del mercado")

    st.subheader("Distribución de oferentes por licitación")
    oferentes = df.groupby("NroLicitacion")["Proveedor"].nunique()
    fig3, ax3 = plt.subplots()
    sns.histplot(oferentes, bins=30, ax=ax3, color="#db7093")
    ax3.set_title("Número de oferentes por licitación")
    st.pyplot(fig3)
    st.caption("Este histograma muestra la cantidad de oferentes distintos por licitación. Un alto número sugiere un mercado competitivo; mientras que licitaciones con 1 solo oferente podrían indicar problemas de transparencia o barreras de entrada.")

    st.subheader("Adjudicaciones por tamaño de proveedor")
    df_adjudicada = df[df["ResultadoOferta"] == "Adjudicada"]
    tamano = df_adjudicada["TamanoProveedor"].value_counts(normalize=True) * 100
    if tamano.empty:
        st.warning("No hay datos de adjudicaciones disponibles para los filtros seleccionados.")
    else:
        fig4, ax4 = plt.subplots()
        tamano.plot(kind="barh", ax=ax4, color="#ba55d3")
        ax4.set_title("% Adjudicado por Tamaño de Proveedor")
        st.pyplot(fig4)
        st.caption("Se examina si las licitaciones están siendo adjudicadas mayoritariamente a grandes empresas o si existe participación de pequeñas y medianas. Esto permite evaluar la inclusión de MIPYMES en compras públicas.")

elif seccion == "Eficiencia":
    st.header("Objetivo 3: Eficiencia del proceso")
    df["FechaPublicacion"] = pd.to_datetime(df["FechaPublicacion"], errors="coerce")
    df["FechaAdjudicacion"] = pd.to_datetime(df["FechaAdjudicacion"], errors="coerce")
    df["Plazo"] = (df["FechaAdjudicacion"] - df["FechaPublicacion"]).dt.days
    fig5, ax5 = plt.subplots()
    sns.histplot(df["Plazo"].dropna(), bins=30, ax=ax5, color="#cc66cc")
    ax5.set_title("Días entre publicación y adjudicación")
    st.pyplot(fig5)
    st.caption("Se mide la eficiencia del proceso licitatorio observando el plazo en días entre publicación y adjudicación. Procesos muy largos pueden implicar trabas administrativas; plazos demasiado cortos podrían poner en duda la calidad del proceso.")

elif seccion == "Transparencia":
    st.header("Objetivo 4: Transparencia")

    st.subheader("Tipo de licitación")
    fig6, ax6 = plt.subplots()
    df["TipoLicitacion"].value_counts().plot(kind="bar", ax=ax6, color="#e75480")
    ax6.set_title("Distribución de tipos de licitación")
    st.pyplot(fig6)
    st.caption("Se analiza la distribución de tipos de licitación. Un alto porcentaje de licitaciones públicas es deseable, ya que promueve mayor apertura y participación. Licitaciones privadas o restringidas pueden ser justificadas en ciertos casos, pero deben ser monitoreadas.")

    st.subheader("Publicidad de ofertas técnicas")
    fig7, ax7 = plt.subplots()
    values = df["PublicidadOfertasTecnicas"].value_counts()
    wedges, texts, autotexts = ax7.pie(
        values, labels=None, autopct="%1.1f%%", startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=sns.color_palette("pink", len(values))
    )
    ax7.set_ylabel("")
    ax7.legend(values.index, loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(fig7)
    st.caption("Este gráfico refleja si los municipios están haciendo pública la evaluación técnica de las ofertas, un elemento clave de transparencia. La falta de publicación puede limitar la fiscalización y el control social.")

elif seccion == "Municipios":
    st.header("Análisis por Municipio")
    st.subheader("Top 10 Municipios por Monto Estimado")
    top_muni = df.groupby("Institucion")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig_muni, ax_muni = plt.subplots()
    top_muni.plot(kind="barh", ax=ax_muni, color="#da70d6")
    ax_muni.set_title("Top 10 Instituciones por Monto Total Estimado")
    ax_muni.set_xlabel("Monto Estimado")
    st.pyplot(fig_muni)
    st.caption("Se presentan los municipios con mayor gasto estimado en licitaciones. Este ranking puede correlacionarse con el tamaño poblacional, presupuestos locales o prioridades políticas. Es útil para detectar posibles sobregastos o concentración del poder de compra.")

elif seccion == "Comparación 2023 vs 2024":
    st.header("Comparación entre Años: 2023 vs 2024")
    df_comp = DF.copy()
    df_comp["FechaPublicacion"] = pd.to_datetime(df_comp["FechaPublicacion"], errors="coerce")
    df_comp["FechaAdjudicacion"] = pd.to_datetime(df_comp["FechaAdjudicacion"], errors="coerce")
    df_comp["Plazo"] = (df_comp["FechaAdjudicacion"] - df_comp["FechaPublicacion"]).dt.days
    df_comp = df_comp[df_comp["Plazo"].notna() & (df_comp["Plazo"] >= 0)]

    resumen = df_comp.groupby("Año").agg({
        "MontoEstimadoLicitacion": "sum",
        "NroLlicitacion": "nunique",
        "Proveedor": "nunique",
        "Plazo": "mean"
    }).rename(columns={
        "MontoEstimadoLicitacion": "Total Monto Estimado (CLP)",
        "NroLlicitacion": "Licitaciones Únicas",
        "Proveedor": "Proveedores Únicos",
        "Plazo": "Plazo Promedio (días)"
    })

    resumen["Plazo Promedio (días)"] = resumen["Plazo Promedio (días)"].round(2)
    resumen["Total Monto Estimado (CLP)"] = resumen["Total Monto Estimado (CLP)"].astype(int)

    st.dataframe(resumen.style.format({
        "Total Monto Estimado (CLP)": "{:,} CLP",
        "Plazo Promedio (días)": "{:.2f} días"
    }))
    st.caption("Se comparan los indicadores clave entre años: gasto total, cantidad de licitaciones únicas, diversidad de proveedores y eficiencia temporal. Esto permite evaluar la evolución del comportamiento licitatorio municipal, e identificar mejoras o retrocesos.")

elif seccion == "Conclusiones":
    st.header("Conclusiones y Recomendaciones")
    st.markdown("""
    - Es necesario mejorar la trazabilidad y validación de datos.
    - Se recomienda estandarizar los formatos y campos obligatorios.
    - Mayor fiscalización sobre procesos con proveedor único.
    - Integrar población municipal para gasto per cápita.
    - Desarrollar alertas para licitaciones sin justificación.
    """)
