from firecrawl import FirecrawlApp
import json
import os
import time
from dotenv import load_dotenv

# -------- CONFIG --------
load_dotenv()
api_key = os.getenv("FIRECRAWL_API_KEY")

if not api_key:
    raise ValueError("❌ No se encontró la API KEY. Revisa tu archivo .env")

app = FirecrawlApp(api_key=api_key)

# -------- FUNCIONES --------

def guardar_json(data, nombre):
    with open(nombre, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def obtener_links(url):
    print("🔎 Obteniendo links...")

    try:
        data = app.scrape(url, params={
            "formats": ["links"]
        })

        links = data.get("links", [])

        # Filtrar solo propiedades reales
        links = [l for l in links if "inmueble.mercadolibre.com.mx" in l]

        print(f"✅ {len(links)} links encontrados")
        return links

    except Exception as e:
        print("❌ Error obteniendo links:", e)
        return []

def scrapear_propiedades(links):
    print("📦 Scrapeando propiedades...")
    resultados = []

    batch_size = 10

    for i in range(0, len(links), batch_size):
        batch = links[i:i+batch_size]
        print(f"➡️ Batch {i} - {i+len(batch)}")

        try:
            data = app.batch_scrape_urls(batch, params={
                "formats": ["markdown"]
            })

            if data and "data" in data:
                for item in data["data"]:
                    resultados.append({
                        "url": item.get("metadata", {}).get("url", ""),
                        "contenido": item.get("markdown", "")
                    })

            time.sleep(1)

        except Exception as e:
            print("❌ Error en batch:", e)

    return resultados

# -------- MAIN --------

url = "https://inmuebles.mercadolibre.com.mx/terrenos/venta/toluca"

links = obtener_links(url)

guardar_json(links, "links_terrenos.json")

# prueba con pocos
links = links[:30]

resultados = scrapear_propiedades(links)

guardar_json(resultados, "terrenos_firecrawl.json")

print("✅ SCRAPER FIRECRAWL TERMINADO")