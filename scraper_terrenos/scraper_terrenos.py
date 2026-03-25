from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# Configurar navegador automático
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = "https://inmuebles.mercadolibre.com.mx/terrenos/venta/toluca"
driver.get(url)

time.sleep(5)

# Obtener todos los anuncios
items = driver.find_elements(By.CLASS_NAME, "ui-search-layout__item")

print(f"Se encontraron {len(items)} elementos")

data = []

for item in items:
    try:
        # Obtener todo el texto del anuncio
        texto = item.text.split("\n")

        # Limpiar texto vacío
        texto = [t for t in texto if t.strip() != ""]

        # -------- EXTRAER DATOS --------

        titulo = texto[0] if len(texto) > 0 else "No disponible"
        precio = next((t for t in texto if "$" in t or "," in t), "No disponible")
        ubicacion = texto[-1] if len(texto) > 1 else "No disponible"

        # -------- FILTRO INTELIGENTE --------
        if "Terreno" in titulo and precio != "No disponible":
            data.append({
                "titulo": titulo,
                "precio": precio,
                "ubicacion": ubicacion
            })

    except:
        continue

driver.quit()

# Crear DataFrame
df = pd.DataFrame(data)

print("\nDATOS LIMPIOS:\n")
print(df.head())

# -------- GUARDAR EN EXCEL --------
df.to_excel("terrenos_filtrados.xlsx", index=False)

print("\nArchivo guardado como terrenos_filtrados.xlsx")