"""
Universal Product Scraper - Supporta Shopify, WooCommerce, Magento e CMS custom

Utilizza selettori multipli per adattarsi automaticamente a diversi e-commerce.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


# Selettori per diversi CMS e-commerce
CMS_SELECTORS = {
    "woocommerce": [
        ".woocommerce-loop-product__title",
        ".woocommerce-loop-product__title a",
        "li.product .product-title",
        ".product-title",
        ".product-title a",
        "h2.woocommerce-loop-product__title",
    ],
    "shopify": [
        ".product-card__title",
        ".product-card__name", 
        ".product-item__title",
        ".product__title",
        ".product-title",
        "h3.card__heading a",
        ".card__heading a",
        ".product-card h3 a",
        ".product-grid-item__title",
        "[data-product-title]",
    ],
    "magento": [
        ".product-item-name",
        ".product-item-name a",
        ".product-item-link",
        ".product.name a",
        ".product-name a",
        "h2.product-name",
        ".product-info-main .page-title",
    ],
    "prestashop": [
        ".product-title",
        ".product-title a", 
        "h3.product-name a",
        ".product-miniature .product-title",
        "h2.product-name",
    ],
    "generic": [
        # Selettori generici che funzionano su molti CMS
        ".product-title",
        ".product-name",
        ".product h2",
        ".product h3",
        "h2.product-title",
        "h3.product-title",
        "[class*='product-title']",
        "[class*='product-name']",
        ".products h2 a",
        ".products h3 a",
        ".product-card__title",
        ".product-item__name",
        "li.product h2",
        "li.product h3",
        ".card-title a",
        "article.product h2",
        "[data-product-name]",
    ]
}


def detect_cms(soup: BeautifulSoup, html: str) -> str:
    """
    Rileva il CMS dell'e-commerce dalla struttura HTML.
    """
    html_lower = html.lower()
    
    # Shopify
    if 'shopify' in html_lower or 'cdn.shopify.com' in html_lower:
        return 'shopify'
    
    # WooCommerce
    if 'woocommerce' in html_lower or 'wc-block' in html_lower:
        return 'woocommerce'
    
    # Magento
    if 'magento' in html_lower or 'mage' in html_lower:
        return 'magento'
    
    # PrestaShop
    if 'prestashop' in html_lower or 'presta' in html_lower:
        return 'prestashop'
    
    return 'generic'


def clean_product_name(name: str) -> str:
    """
    Pulisce il nome del prodotto rimuovendo caratteri inutili.
    """
    # Rimuovi spazi multipli e newline
    name = re.sub(r'\s+', ' ', name)
    # Rimuovi prezzo se presente alla fine
    name = re.sub(r'\s*[€$£]\s*[\d.,]+\s*$', '', name)
    # Strip
    name = name.strip()
    return name


def scrape_products(url: str, max_products: int = 50) -> Dict:
    """
    Scrapa i nomi dei prodotti da una pagina categoria e-commerce.
    
    Args:
        url: URL della pagina categoria
        max_products: Numero massimo di prodotti da estrarre
        
    Returns:
        Dict con:
        - products: lista di nomi prodotto
        - cms_detected: CMS rilevato
        - total_found: totale prodotti trovati
        - url: URL originale
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        logger.info(f"🔍 Scraping prodotti da: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        html = response.text
        
        # Rileva CMS
        cms = detect_cms(soup, html)
        logger.info(f"📦 CMS rilevato: {cms}")
        
        # Costruisci lista selettori: prima quelli specifici del CMS, poi generici
        selectors_to_try = CMS_SELECTORS.get(cms, []) + CMS_SELECTORS['generic']
        
        products = []
        selector_used = None
        
        for selector in selectors_to_try:
            try:
                elements = soup.select(selector)
                if elements:
                    for el in elements:
                        name = clean_product_name(el.get_text())
                        if name and len(name) > 3 and name not in products:
                            products.append(name)
                    
                    if len(products) >= 3:  # Almeno 3 prodotti per considerarlo valido
                        selector_used = selector
                        logger.info(f"✅ Selettore funzionante: {selector} ({len(products)} prodotti)")
                        break
            except Exception as e:
                continue
        
        # Limita al massimo
        products = products[:max_products]
        
        return {
            "success": True,
            "products": products,
            "cms_detected": cms,
            "selector_used": selector_used,
            "total_found": len(products),
            "url": url
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout durante lo scraping di {url}")
        return {
            "success": False,
            "error": "Timeout: la pagina non risponde",
            "products": [],
            "url": url
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Errore richiesta: {e}")
        return {
            "success": False,
            "error": f"Errore di connessione: {str(e)}",
            "products": [],
            "url": url
        }
    except Exception as e:
        logger.error(f"❌ Errore generico: {e}")
        return {
            "success": False,
            "error": f"Errore: {str(e)}",
            "products": [],
            "url": url
        }


def format_products_for_prompt(products: List[str]) -> str:
    """
    Formatta la lista prodotti per includerla nel prompt dell'agent.
    """
    if not products:
        return ""
    
    formatted = "### Prodotti presenti nella categoria:\n"
    for i, product in enumerate(products, 1):
        formatted += f"{i}. {product}\n"
    
    return formatted


# Test diretto
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test con AquaJoy
    result = scrape_products("https://aquajoy.it/categoria/costumi-piscina/donna/intero/")
    
    print("\n=== RISULTATO ===")
    print(f"CMS: {result.get('cms_detected')}")
    print(f"Selettore: {result.get('selector_used')}")
    print(f"Prodotti trovati: {result.get('total_found')}")
    print("\nProdotti:")
    for p in result.get('products', [])[:10]:
        print(f"  - {p}")
