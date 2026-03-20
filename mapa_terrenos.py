import pandas as pd
import folium

# Leer Excel (fila correcta de encabezados)
df = pd.read_excel(
    "terrenos excel 12-marzo-2026.xlsx",
    sheet_name="Modelo General",
    header=13
)

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

# Limpiar coordenadas
df["coordenadas"] = df["coordenadas"].astype(str).str.replace("\n", "").str.replace(" ", "")

# Separar lat y lon
df[["Lat", "Lon"]] = df["coordenadas"].str.split(",", expand=True)

# Convertir a número
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")

# 🔥 Limpiar precios (MUY IMPORTANTE para colores)
df["Precio limpio"] = df["Precio total"].astype(str).str.replace(",", "").str.replace("$", "")
df["Precio limpio"] = pd.to_numeric(df["Precio limpio"], errors="coerce")

# Eliminar filas con errores
df = df.dropna(subset=["Lat", "Lon", "Precio limpio"])

# 🔥 MEJORA 2: detectar terrenos baratos
df_baratos = df[df["Precio limpio"] < 500000]
print("🔥 Terrenos baratos detectados:", len(df_baratos))

# Crear mapa
mapa = folium.Map(location=[df["Lat"].mean(), df["Lon"].mean()], zoom_start=12)

# 🔥 MEJORA 1 + 3: colores + iconos pro
for _, row in df.iterrows():
    precio = row["Precio limpio"]

    # 🎨 Colores por rango
    if precio < 500000:
        color = "green"
    elif precio < 800000:
        color = "orange"
    else:
        color = "red"

    popup = f"""
    <b>💰 ${precio:,.0f}</b><br>
    📐 {row['Superficie (m²)']}<br>
    📍 {row['Colonia/Zona']}
    """

    folium.Marker(
        location=[row["Lat"], row["Lon"]],
        popup=popup,
        icon=folium.Icon(color=color, icon="home")
    ).add_to(mapa)

# Guardar mapa
mapa.save("mapa_terrenos.html")

print("🔥 Mapa PRO generado correctamente")