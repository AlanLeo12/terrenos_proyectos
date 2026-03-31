from firecrawl import FirecrawlApp
import json
import time
import os
import re
from dotenv import load_dotenv

# -------- CONFIG --------
load_dotenv()
API_KEY = os.getenv('FIRECRAWL_API_KEY')

print(f"API KEY: {API_KEY}")

app = FirecrawlApp(api_key=API_KEY)

# -------- VARIABLES --------

zonas = [
    'estado-de-mexico/toluca',
    'estado-de-mexico/metepec'
]

urls = [
    f'https://inmuebles.mercadolibre.com.mx/terrenos/venta/{zona}'
    for zona in zonas
]

# -------- FUNCIONES --------

def extraer_precio(texto):
    match = re.search(r'MXN[\s]?[0-9,]+', texto)
    return match.group(0) if match else None


def extraer_metros(texto):
    match = re.search(r'[0-9,.]+\s*m²', texto)
    return match.group(0) if match else None


def scrapear_links(url):
    print(f"Scrapeando: {url}")

    try:
        data = app.scrape(url, formats=["links"], proxy="stealth")
    except:
        print("Reintentando...")
        time.sleep(2)
        data = app.scrape(url, formats=["links"], proxy="stealth")

    links = data.links if hasattr(data, "links") else []

    links_filtrados = [
        l for l in links if "/MLM-" in l
    ]

    return list(set(links_filtrados))


def scrapear_detalles(links):
    resultados = []

    print(f"Scrapeando {len(links)} propiedades...")

    links = links[:10]  # limitar uso de API

    for i, link in enumerate(links):
        print(f"{i+1}/{len(links)}")

        try:
            data = app.scrape(link, formats=["markdown"], proxy="stealth")
        except:
            print("Reintentando...")
            time.sleep(2)
            continue

        texto = data.markdown if hasattr(data, "markdown") else ""
        texto_lower = texto.lower()

        # 🔥 FILTRO SOLO TOLUCA / METEPEC
        if "toluca" not in texto_lower and "metepec" not in texto_lower:
            continue

        resultados.append({
            "url": link,
            "precio": extraer_precio(texto),
            "metros": extraer_metros(texto),
            "contenido": texto[:500]
        })

        time.sleep(1)

    return resultados


# -------- MAIN --------

if __name__ == "__main__":

    all_links = []

    for url in urls:
        links = scrapear_links(url)
        print(f"Links encontrados: {len(links)}")
        all_links.extend(links)

    all_links = list(set(all_links))

    print(f"TOTAL LINKS: {len(all_links)}")

    resultados = scrapear_detalles(all_links)

    with open("resultados_mercadolibre.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print("Proceso terminado")