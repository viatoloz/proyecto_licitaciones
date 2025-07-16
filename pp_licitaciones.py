import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =============================
# CONFIGURACIÓN GENERAL Y ESTILO
# =============================
st.set_page_config(page_title="Análisis Licitaciones", layout="wide")

# Estilo gráfico con tonos lila y palo rosa
PALETA_PASTEL = ["#d8bfd8", "#dda0dd", "#e6a9ec", "#e5bcd1", "#f7d6e0"]  # tonos pastel
plt.style.use("seaborn-v0_8-muted")  # estilo suave

# =============================
# CARGA DE DATOS
# =============================
@st.cache_data
def cargar_datos():
    return pd.read_parquet("data_licitaciones_2023_2024_reducido.parquet")

DF = cargar_datos()

# =============================
# SIDEBAR Y FILTROS
# =============================
st.sidebar.image("logo_ust.png", width=180)  # Logo UST
st.sidebar.title("📊 Navegación")

seccion = st.sidebar.radio("Ir a sección:", [
    "Introducción", "Gasto Público", "Competitividad", "Eficiencia", "Transparencia",
    "Municipios", "Comparación 2023 vs 2024", "Conclusiones"
])

st.sidebar.markdown("---")
selected_year = st.sidebar.selectbox("📅 Selecciona el año", sorted(DF["Año"].unique()))
selected_rubro = st.sidebar.selectbox("🏷️ Filtrar por Rubro (opcional)", ["Todos"] + sorted(DF["RubroN1"].dropna().unique()))
selected_muni = st.sidebar.selectbox("🏛️ Filtrar por Municipio (opcional)", ["Todos"] + sorted(DF["Institucion"].dropna().unique()))

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
    st.image("logo_ust.png", width=200)

    st.title("📘 Análisis de Licitaciones Municipales 2023–2024")
    st.markdown("""
    Bienvenido al panel interactivo de análisis de licitaciones públicas realizadas por municipalidades de Chile entre 2023 y 2024.

    🔍 **Objetivo**: Evaluar la eficiencia, transparencia y competitividad del proceso de contratación pública.

    🧠 **¿Por qué es importante?**  
    Porque una licitación transparente y eficiente permite un mejor uso de los recursos públicos y una mayor participación de proveedores, incluyendo PYMES.

    📌 Este proyecto forma parte del curso *Business Intelligence* de la Universidad Santo Tomás.
    """)
    st.divider()

# =============================
# SECCIÓN: GASTO PÚBLICO
# =============================
elif seccion == "Gasto Público":
    st.header("💸 Objetivo 1: Evaluar el gasto público")

    st.subheader("🏷️ Top rubros por monto estimado")
    top_rubros = df.groupby("RubroN1")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    top_rubros.plot(kind="bar", ax=ax1, color=PALETA_PASTEL[0])
    ax1.set_ylabel("Monto Estimado")
    ax1.set_title("Top 10 Rubros")
    st.pyplot(fig1)
    st.caption("Rubros con mayor gasto público estimado, destacando sectores como salud, infraestructura y servicios generales.")

    st.divider()

    st.subheader("💰 Distribución de financiamiento")
    top_fin = df["FuenteFinanciamiento"].fillna("Desconocido").value_counts().head(10)
    otros = df["FuenteFinanciamiento"].fillna("Desconocido").value_counts()[10:].sum()
    top_fin["Otros"] = otros
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax2.pie(
        top_fin, labels=None, autopct='%1.1f%%', startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=PALETA_PASTEL
    )
    ax2.set_title("Fuente de Financiamiento")
    ax2.legend(top_fin.index, loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(fig2)
    st.caption("La mayoría del financiamiento proviene de fondos municipales (99.8%), lo que limita la escala de los proyectos.")

# =============================
# SECCIÓN: COMPETITIVIDAD
# =============================
elif seccion == "Competitividad":
    st.header("📈 Objetivo 2: Competitividad del mercado")

    st.subheader("👥 Distribución de oferentes por licitación")
    oferentes = df.groupby("NroLicitacion")["Proveedor"].nunique()
    fig3, ax3 = plt.subplots()
    sns.histplot(oferentes, bins=30, ax=ax3, color=PALETA_PASTEL[1])
    ax3.set_title("Número de oferentes por licitación")
    st.pyplot(fig3)
    st.caption("Casi el 20% de licitaciones tienen un solo oferente, lo cual puede indicar baja competencia.")

    st.divider()

    st.subheader("🏢 Adjudicaciones por tamaño de proveedor")
    df_adjudicada = df[df["ResultadoOferta"] == "Adjudicada"]
    tamano = df_adjudicada["TamanoProveedor"].value_counts(normalize=True) * 100
    if tamano.empty:
        st.warning("No hay datos de adjudicaciones disponibles para los filtros seleccionados.")
    else:
        fig4, ax4 = plt.subplots()
        tamano.plot(kind="barh", ax=ax4, color=PALETA_PASTEL[2])
        ax4.set_title("% Adjudicado por Tamaño de Proveedor")
        st.pyplot(fig4)
        st.caption("Las grandes empresas concentran el 56% de las adjudicaciones. Las PYMES siguen en desventaja.")

# =============================
# SECCIÓN: EFICIENCIA
# =============================
elif seccion == "Eficiencia":
    st.header("⏱️ Objetivo 3: Eficiencia del proceso")

    df["FechaPublicacion"] = pd.to_datetime(df["FechaPublicacion"], errors="coerce")
    df["FechaAdjudicacion"] = pd.to_datetime(df["FechaAdjudicacion"], errors="coerce")
    df["Plazo"] = (df["FechaAdjudicacion"] - df["FechaPublicacion"]).dt.days

    fig5, ax5 = plt.subplots()
    sns.histplot(df["Plazo"].dropna(), bins=30, ax=ax5, color=PALETA_PASTEL[3])
    ax5.set_title("Días entre publicación y adjudicación")
    st.pyplot(fig5)
    st.caption("El plazo promedio es de 39 a 45 días. Las licitaciones multietapa demoran un 70% más que las simples.")

# =============================
# SECCIÓN: TRANSPARENCIA
# =============================
elif seccion == "Transparencia":
    st.header("🔎 Objetivo 4: Transparencia")

    st.subheader("📄 Tipo de licitación")
    fig6, ax6 = plt.subplots()
    df["TipoLicitacion"].value_counts().plot(kind="bar", ax=ax6, color=PALETA_PASTEL[4])
    ax6.set_title("Distribución de tipos de licitación")
    st.pyplot(fig6)
    st.caption("99.95% de las licitaciones son públicas, lo que refleja transparencia formal, pero no sustantiva.")

    st.divider()

    st.subheader("📢 Publicación de ofertas técnicas")
    fig7, ax7 = plt.subplots()
    values = df["PublicidadOfertasTecnicas"].value_counts()
    wedges, texts, autotexts = ax7.pie(
        values, labels=None, autopct="%1.1f%%", startangle=90,
        pctdistance=1.25, labeldistance=1.4,
        colors=PALETA_PASTEL
    )
    ax7.legend(values.index, loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(fig7)
    st.caption("Solo el 37% de licitaciones publican su evaluación técnica, un punto débil en la rendición de cuentas.")

# =============================
# SECCIÓN: MUNICIPIOS
# =============================
elif seccion == "Municipios":
    st.header("🏙️ Análisis por Municipio")
    st.subheader("🏆 Top 10 Municipios por Monto Estimado")
    top_muni = df.groupby("Institucion")["MontoEstimadoLicitacion"].sum().sort_values(ascending=False).head(10)
    fig_muni, ax_muni = plt.subplots()
    top_muni.plot(kind="barh", ax=ax_muni, color=PALETA_PASTEL[0])
    ax_muni.set_title("Top 10 Instituciones por Monto Total Estimado")
    ax_muni.set_xlabel("Monto Estimado")
    st.pyplot(fig_muni)
    st.caption("Municipios como La Cisterna y Concepción concentran el mayor volumen de gasto estimado.")

# =============================
# SECCIÓN: COMPARACIÓN ANUAL
# =============================
elif seccion == "Comparación 2023 vs 2024":
    st.header("📊 Comparación entre Años: 2023 vs 2024")

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
    st.caption("Se observa una mejora de eficiencia y aumento en diversidad de proveedores en 2024.")

# =============================
# SECCIÓN: CONCLUSIONES
# =============================
elif seccion == "Conclusiones":
    st.header("🧾 Conclusiones y Recomendaciones")
    st.markdown("## ✅ Principales Hallazgos")
    st.markdown("""
    - 🏢 **Financiamiento**: El 99.8% proviene de fondos propios municipales.
    - 💰 **Gasto**: Rubros como infraestructura concentran la mayoría del presupuesto.
    - 🏆 **Competencia**: Las grandes empresas tienen mayor tasa de adjudicación.
    - ⏱️ **Eficiencia**: Mejora en plazos entre 2023 y 2024.
    - 🔍 **Transparencia**: Falta justificación en muchos procesos.
    """)
    st.divider()
    st.markdown("## 🛠️ Recomendaciones")
    st.markdown("""
    - 🔄 Mejorar la trazabilidad y validación de los datos.
    - 📢 Publicar la justificación de montos en todas las licitaciones.
    - 🤝 Incluir más PYMES mediante incentivos y difusión.
    - 📍 Incorporar población para gasto per cápita.
    - 🚨 Crear alertas de concentración o proveedor único.
    """)
    st.image("logo_ust.png", width=150)
    st.markdown("**Universidad Santo Tomás – Escuela de Auditoría y Control de Gestión**")
