import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(page_title="Análisis Licitaciones", layout="wide")
plt.style.use("seaborn-v0_8-colorblind")

# =============================
# FUNCIÓN PARA CARGAR DATOS
# =============================
@st.cache_data
def cargar_datos():
    """
    Carga el archivo parquet con datos de licitaciones y lo devuelve como DataFrame.
    """
    return pd.read_parquet("data_licitaciones_2023_2024_reducido.parquet")

DF = cargar_datos()

# =============================
# CONFIGURACIÓN DE FILTROS LATERALES
# =============================
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a sección:", [
    "Introducción", "Gasto Público", "Competitividad", "Eficiencia", "Transparencia",
    "Municipios", "Comparación 2023 vs 2024", "Conclusiones y Propuestas"
])

st.sidebar.markdown("---")
selected_year = st.sidebar.selectbox("Selecciona el año", sorted(DF["Año"].unique()))
selected_rubro = st.sidebar.selectbox("Filtrar por Rubro (opcional)", ["Todos"] + sorted(DF["RubroN1"].dropna().unique()))
selected_muni = st.sidebar.selectbox("Filtrar por Municipio (opcional)", ["Todos"] + sorted(DF["Institucion"].dropna().unique()))

# =============================
# APLICAR FILTROS
# =============================
df = DF.copy()
df = df[df["Año"] == selected_year]
if selected_rubro != "Todos":
    df = df[df["RubroN1"] == selected_rubro]
if selected_muni != "Todos":
    df = df[df["Institucion"] == selected_muni]

# =============================
# SECCIÓN: INTRODUCCIÓN
# =============================
if seccion == "Introducción":
    st.title("Análisis de Licitaciones Municipales 2023–2024")
    st.markdown("""
    Este proyecto analiza los procesos de licitación municipal en Chile entre 2023 y 2024. 
    Se evalúan los montos adjudicados, la eficiencia del proceso, la competencia entre oferentes 
    y los niveles de transparencia de las instituciones municipales.
    """)

# =============================
# SECCIÓN: GASTO PÚBLICO
# =============================
elif seccion == "Gasto Público":
    st.header("Objetivo 1: Evaluar el gasto público")

    st.subheader("Top rubros por monto estimado")
    top_rubros = df.groupby("RubroN1")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    top_rubros.plot(kind="bar", ax=ax1, color="#c71585")
    ax1.set_ylabel("Monto Estimado (CLP)")
    ax1.set_title("Top 10 Rubros")
    st.pyplot(fig1)
    st.caption("Los rubros con mayor gasto reflejan las prioridades estratégicas de los municipios, destacando salud, infraestructura y servicios generales.")

    st.subheader("Distribución de financiamiento")
    top_fin = df["FuenteFinanciamiento"].fillna("Desconocido").value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax2.pie(
        top_fin, labels=None, autopct='%1.1f%%', startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=sns.color_palette("RdPu", len(top_fin))
    )
    ax2.legend(top_fin.index, loc="center left", bbox_to_anchor=(1, 0.5))
    ax2.set_title("Fuente de Financiamiento")
    for autotext in autotexts:
        autotext.set_fontsize(9)
    st.pyplot(fig2)
    st.caption("El 99.8% de los recursos provienen de fondos municipales propios, lo que refleja gran autonomía pero limita el financiamiento para proyectos de gran envergadura.")

# =============================
# SECCIÓN: COMPETITIVIDAD
# =============================
elif seccion == "Competitividad":
    st.header("Objetivo 2: Competitividad del mercado")

    # ==========================
    # Distribución de oferentes por licitación
    # ==========================
    st.subheader("Distribución de oferentes por licitación")

    # Agrupar por número de licitación y contar proveedores únicos
    oferentes = df.groupby("NroLicitacion")["Proveedor"].nunique()

    # Graficar histograma
    fig3, ax3 = plt.subplots()
    sns.histplot(oferentes, bins=30, ax=ax3, color="#db7093")
    ax3.set_title("Número de oferentes por licitación")
    st.pyplot(fig3)
    st.caption(
        "El promedio general es de 4.8 oferentes por licitación. Sin embargo, alrededor del 20% tienen solo un participante, "
        "lo que podría indicar baja competitividad o barreras de entrada para nuevos proveedores."
    )

    # ==========================
    # Adjudicaciones por tamaño de proveedor
    # ==========================
    st.subheader("Adjudicaciones por tamaño de proveedor")

    # Filtrar adjudicaciones
    df_adjudicada = df[df["ResultadoOferta"] == "Adjudicada"]

    # Calcular porcentaje adjudicado por tamaño
    tamano = df_adjudicada["TamanoProveedor"].value_counts(normalize=True) * 100

    if tamano.empty:
        st.warning("No hay datos de adjudicaciones disponibles para los filtros seleccionados.")
    else:
        fig4, ax4 = plt.subplots()
        tamano.plot(kind="barh", ax=ax4, color="#ba55d3")
        ax4.set_title("% Adjudicado por Tamaño de Proveedor")
        st.pyplot(fig4)
        st.caption(
            "Se observa que las grandes empresas concentran aproximadamente el 56% de las adjudicaciones, "
            "mientras que las PYMES tienen menor participación, mostrando dificultades para competir."
        )

    # ==========================
    # Top 10 proveedores adjudicados
    # ==========================
    st.subheader("Top 10 proveedores adjudicados")

    # Contar adjudicaciones por proveedor
    top_proveedores = df_adjudicada["Proveedor"].value_counts().head(10)

    # Pasar a DataFrame para evitar errores de plot
    df_top_prov = top_proveedores.reset_index()
    df_top_prov.columns = ["Proveedor", "Adjudicaciones"]

    # Graficar
    fig5, ax5 = plt.subplots()
    ax5.bar(df_top_prov["Proveedor"], df_top_prov["Adjudicaciones"], color="#9932CC")
    ax5.set_ylabel("Cantidad de adjudicaciones")
    ax5.set_title("Top 10 proveedores adjudicados")
    ax5.tick_params(axis='x', rotation=45, ha='right')
    st.pyplot(fig5)
    st.caption(
        "Aquí se identifican los proveedores con mayor número de adjudicaciones. Concentrar en pocos proveedores puede reducir eficiencia, "
        "incrementar riesgos de dependencia y dificultar la participación de nuevos actores en el mercado público."
    )

# =============================
# SECCIÓN: EFICIENCIA
# =============================
elif seccion == "Eficiencia":
    st.header("Objetivo 3: Eficiencia del proceso")
    df["FechaPublicacion"] = pd.to_datetime(df["FechaPublicacion"], errors="coerce")
    df["FechaAdjudicacion"] = pd.to_datetime(df["FechaAdjudicacion"], errors="coerce")
    df["Plazo"] = (df["FechaAdjudicacion"] - df["FechaPublicacion"]).dt.days

    fig6, ax6 = plt.subplots()
    sns.histplot(df["Plazo"].dropna(), bins=30, ax=ax6, color="#cc66cc")
    ax6.set_title("Días entre publicación y adjudicación")
    st.pyplot(fig6)
    st.caption("El plazo promedio entre publicación y adjudicación es de 39-45 días. Las licitaciones multietapa son hasta 70% más lentas, lo que sugiere áreas de mejora en eficiencia.")

# =============================
# SECCIÓN: TRANSPARENCIA
# =============================
elif seccion == "Transparencia":
    st.header("Objetivo 4: Transparencia")

    st.subheader("Tipo de licitación")
    fig7, ax7 = plt.subplots()
    df["TipoLicitacion"].value_counts().plot(kind="bar", ax=ax7, color="#e75480")
    ax7.set_title("Distribución de tipos de licitación")
    st.pyplot(fig7)
    st.caption("El 99.95% de las licitaciones son públicas, lo que indica alto cumplimiento formal en transparencia.")

    st.subheader("Publicidad de ofertas técnicas")
    fig8, ax8 = plt.subplots()
    values = df["PublicidadOfertasTecnicas"].value_counts()
    wedges, texts, autotexts = ax8.pie(
        values, labels=None, autopct="%1.1f%%", startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=sns.color_palette("pink", len(values))
    )
    ax8.legend(values.index, loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(fig8)
    st.caption("Solo el 37% de las licitaciones incluyen justificación detallada del monto estimado, generando dudas sobre la rendición de cuentas.")

# =============================
# SECCIÓN: MUNICIPIOS
# =============================
elif seccion == "Municipios":
    st.header("Análisis por Municipio")
    st.subheader("Top 10 Municipios por Monto Estimado")
    top_muni = df.groupby("Institucion")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig_muni, ax_muni = plt.subplots()
    top_muni.plot(kind="barh", ax=ax_muni, color="#da70d6")
    ax_muni.set_title("Top 10 Municipios por Gasto Estimado")
    ax_muni.set_xlabel("Monto Estimado (CLP)")
    st.pyplot(fig_muni)
    st.caption("Municipios como La Cisterna y Concepción concentran grandes montos en pocas licitaciones, mientras que otros priorizan volumen sobre valor unitario.")

# =============================
# SECCIÓN: COMPARACIÓN 2023 vs 2024
# =============================
elif seccion == "Comparación 2023 vs 2024":
    st.header("Comparación entre Años: 2023 vs 2024")
    df_comp = DF.copy()
    df_comp["FechaPublicacion"] = pd.to_datetime(df_comp["FechaPublicacion"], errors="coerce")
    df_comp["FechaAdjudicacion"] = pd.to_datetime(df_comp["FechaAdjudicacion"], errors="coerce")
    df_comp["Plazo"] = (df_comp["FechaAdjudicacion"] - df_comp["FechaPublicacion"]).dt.days
    df_comp = df_comp[df_comp["Plazo"].notna() & (df_comp["Plazo"] >= 0)]

    resumen = df_comp.groupby("Año").agg({
        "MontoEstimadoLicitacion": "sum",
        "NroLicitacion": "nunique",
        "Proveedor": "nunique",
        "Plazo": "mean"
    }).rename(columns={
        "MontoEstimadoLicitacion": "Total Monto Estimado (CLP)",
        "NroLicitacion": "Licitaciones Únicas",
        "Proveedor": "Proveedores Únicos",
        "Plazo": "Plazo Promedio (días)"
    })

    resumen["Plazo Promedio (días)"] = resumen["Plazo Promedio (días)"].round(2)
    resumen["Total Monto Estimado (CLP)"] = resumen["Total Monto Estimado (CLP)"].astype(int)

    st.dataframe(resumen.style.format({
        "Total Monto Estimado (CLP)": "{:,} CLP",
        "Plazo Promedio (días)": "{:.2f} días"
    }))
    st.caption("Comparativa de gasto, cantidad de licitaciones, diversidad de proveedores y eficiencia temporal entre los dos años.")

# =============================
# SECCIÓN: CONCLUSIONES Y PROPUESTAS
# =============================
elif seccion == "Conclusiones y Propuestas":
    st.header("Conclusiones y Recomendaciones")
    st.markdown("""
    - Mejorar trazabilidad y validación de datos para reducir inconsistencias.
    - Promover políticas que fomenten mayor participación de PYMES.
    - Optimizar los tiempos de adjudicación, especialmente en procesos multietapa.
    - Fortalecer mecanismos de transparencia activa, especialmente en justificación de montos.
    - Integrar análisis poblacional para medir gasto per cápita por comuna.
    - Desarrollar alertas automáticas para identificar concentración excesiva en pocos proveedores.
    """)

