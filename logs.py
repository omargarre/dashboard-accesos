import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Dashboard de Accesos", layout="wide")

# Cargar archivo original
df = pd.read_excel("log_modelo.xlsx", sheet_name="Datos del informe 1", header=2)

# Renombrar columnas clave
df.rename(columns={
    "Id. de usuario": "Usuario",
    "Ocurrencia (GMT)": "Fecha",
    "Evento": "Acción",
    "Tipo de elemento": "Tipo de Elemento",
    "Ubicación del documento": "URL",
    "SourceFileName": "Nombre Archivo"
}, inplace=True)

df = df[df["Fecha"].notna()]  # eliminar basura

# Extraer tipo de archivo desde la URL
df["Tipo de Archivo"] = df["URL"].astype(str).str.extract(r"\.([a-zA-Z0-9]+)$", expand=False).str.lower()

# Filtrar solo documentos Word, PDF y Excel
tipos_validos = ["pdf", "doc", "docx", "xls", "xlsx"]
df = df[df["Tipo de Archivo"].isin(tipos_validos)]

# Cartel de auditoría
st.warning("⚠️ Toda la actividad en este dashboard es monitoreada y registrada con fines de auditoría. Uso indebido puede ser sancionado. — Gerencia de Auditoría Externa de Sistemas")

# Filtros interactivos
st.title("📄 Dashboard de Accesos a Documentos (PDF, Word y Excel)")

usuarios = sorted(df["Usuario"].dropna().unique())
acciones = sorted(df["Acción"].dropna().unique())
tipos_archivo = sorted(df["Tipo de Archivo"].dropna().unique())

col1, col2, col3 = st.columns(3)
usuario_sel = col1.selectbox("👤 Usuario", ["Todos"] + usuarios)
accion_sel = col2.selectbox("🧾 Acción", ["Todas"] + acciones)
tipo_sel = col3.selectbox("📂 Tipo de archivo", ["Todos"] + tipos_archivo)

# Filtro por nombre de archivo
nombre_archivo_filtro = st.text_input("🔍 Buscar por nombre de archivo (parcial):")

# Slider de fechas
fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()
fecha_sel = st.slider(
    "📆 Rango de fechas",
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
if nombre_archivo_filtro:
    df_filtrado = df_filtrado[df_filtrado["Nombre Archivo"].astype(str).str.contains(nombre_archivo_filtro, case=False, na=False)]

df_filtrado = df_filtrado[
    (df_filtrado["Fecha"].dt.date >= fecha_sel[0]) &
    (df_filtrado["Fecha"].dt.date <= fecha_sel[1])
]

# Métricas
col4, col5, col6 = st.columns(3)
col4.metric("Total de accesos", len(df_filtrado))
col5.metric("Usuarios únicos", df_filtrado["Usuario"].nunique())
col6.metric("Archivos únicos", df_filtrado["Nombre Archivo"].nunique())

# Gráficos
st.subheader("📁 Accesos por tipo de archivo")
st.bar_chart(df_filtrado["Tipo de Archivo"].value_counts())

st.subheader("👤 Accesos por usuario")
st.bar_chart(df_filtrado["Usuario"].value_counts())

st.subheader("🧾 Acciones realizadas")
st.bar_chart(df_filtrado["Acción"].value_counts())

st.subheader("📅 Accesos por día")
st.line_chart(df_filtrado.groupby(df_filtrado["Fecha"].dt.date).size())

# Tabla enfocada en usuario ↔ archivo
st.subheader("📋 Accesos por usuario y archivo")
st.dataframe(df_filtrado[["Usuario", "Fecha", "Acción", "Nombre Archivo"]])
