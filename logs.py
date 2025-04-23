
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Dashboard de Accesos", layout="wide")

# Cargar archivo
df = pd.read_excel("log_modelo.xlsx", sheet_name="Datos del informe 1", header=2)

# Renombrar columnas
df.rename(columns={
    "Id. de usuario": "Usuario",
    "Ocurrencia (GMT)": "Fecha",
    "Evento": "Acción",
    "Tipo de elemento": "Tipo de Elemento",
    "Ubicación del documento": "URL",
    "SourceFileName": "Nombre Archivo"
}, inplace=True)

df = df[df["Fecha"].notna()]
df["Tipo de Archivo"] = df["URL"].astype(str).str.extract(r"\.([a-zA-Z0-9]+)$", expand=False).str.lower()
df = df[df["Tipo de Archivo"].isin(["pdf", "doc", "docx", "xls", "xlsx"])]

# Cartel
st.warning("⚠️ Toda la actividad en este dashboard es monitoreada y registrada con fines de auditoría. Uso indebido puede ser sancionado. — Gerencia de Auditoría Externa de Sistemas")

# Título
st.title("📄 Dashboard de Accesos a Documentos (PDF, Word y Excel)")

# Filtros
usuarios = sorted(df["Usuario"].dropna().unique())
acciones = sorted(df["Acción"].dropna().unique())
tipos_archivo = sorted(df["Tipo de Archivo"].dropna().unique())

col1, col2, col3 = st.columns(3)
usuario_sel = col1.selectbox("👤 Usuario", ["Todos"] + usuarios)
accion_sel = col2.selectbox("🧾 Acción", ["Todas"] + acciones)
tipo_sel = col3.selectbox("📂 Tipo de archivo", ["Todos"] + tipos_archivo)

# Combo + texto libre de archivo
col_txt, col_combo = st.columns([2, 2])
with col_txt:
    nombre_archivo_filtro = st.text_input("🔍 Buscar por nombre de archivo (parcial):")
with col_combo:
    if "Nombre Archivo" in df.columns:
        lista_archivos = sorted(df["Nombre Archivo"].dropna().unique())
    else:
        lista_archivos = []
    archivo_seleccionado = st.selectbox("📁 Elegí un archivo puntual:", ["Todos"] + lista_archivos)

# Filtro por fechas
fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()
fecha_sel = st.slider(
    "📅 Rango de fechas",
    min_value=fecha_min.date(),
    max_value=fecha_max.date(),
    value=(fecha_min.date(), fecha_max.date()),
    format="YYYY-MM-DD"
)

# Aplicar filtros
df_filtrado = df.copy()
if usuario_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Usuario"] == usuario_sel]
if accion_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Acción"] == accion_sel]
if tipo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Tipo de Archivo"] == tipo_sel]

if "Nombre Archivo" in df_filtrado.columns:
    if nombre_archivo_filtro:
        df_filtrado = df_filtrado[df_filtrado["Nombre Archivo"].astype(str).str.contains(nombre_archivo_filtro, case=False, na=False)]
    if archivo_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Nombre Archivo"] == archivo_seleccionado]

df_filtrado = df_filtrado[
    (df_filtrado["Fecha"].dt.date >= fecha_sel[0]) &
    (df_filtrado["Fecha"].dt.date <= fecha_sel[1])
]

# Métricas
col4, col5, col6 = st.columns(3)
col4.metric("Total de accesos", len(df_filtrado))
col5.metric("Usuarios únicos", df_filtrado["Usuario"].nunique())
col6.metric("Archivos únicos", df_filtrado["Nombre Archivo"].nunique() if "Nombre Archivo" in df_filtrado.columns else 0)

# Gráficos
st.subheader("📁 Accesos por tipo de archivo")
st.bar_chart(df_filtrado["Tipo de Archivo"].value_counts())

st.subheader("👤 Accesos por usuario")
st.bar_chart(df_filtrado["Usuario"].value_counts())

st.subheader("🧾 Acciones realizadas")
st.bar_chart(df_filtrado["Acción"].value_counts())

st.subheader("📅 Accesos por día")
st.line_chart(df_filtrado.groupby(df_filtrado["Fecha"].dt.date).size())

# Gráfico tipo torta
st.subheader("🥧 Distribución por tipo de archivo")
if not df_filtrado.empty and "Tipo de Archivo" in df_filtrado.columns:
    fig_pie = px.pie(df_filtrado, names="Tipo de Archivo", title="Distribución de accesos por tipo de archivo")
    st.plotly_chart(fig_pie)
else:
    st.info("No hay datos para mostrar el gráfico de torta.")

# Tabla
st.subheader("📋 Accesos por usuario y archivo")
if not df_filtrado.empty and all(col in df_filtrado.columns for col in ["Usuario", "Fecha", "Acción", "Nombre Archivo"]):
    st.dataframe(df_filtrado[["Usuario", "Fecha", "Acción", "Nombre Archivo"]])
else:
    st.info("No hay datos que coincidan con los filtros seleccionados.")
