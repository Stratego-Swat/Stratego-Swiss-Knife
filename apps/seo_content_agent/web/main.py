"""
SEO Content Agent - Professional Web Interface
FastAPI backend with modern enterprise UI
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from seo_agent.agent import SEOContentAgent, CategoryInput
from seo_agent.utils.csv_loader import (
    load_seozoom_csv,
    get_top_keywords,
    get_keyword_clusters
)
from seo_agent.utils.product_scraper import scrape_products

app = FastAPI(title="SEO Content Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

uploaded_csv_path: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    global uploaded_csv_path
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a CSV")
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
        content = await file.read()
        f.write(content)
        uploaded_csv_path = f.name
    
    try:
        keywords = load_seozoom_csv(uploaded_csv_path)
        if not keywords:
            raise HTTPException(400, "No keywords found")
        
        top_kws = get_top_keywords(keywords, limit=10)
        clusters = get_keyword_clusters(keywords)
        main_kw = max(keywords, key=lambda k: k.volume)
        total_vol = sum(k.volume for k in keywords)
        
        return {
            "success": True,
            "filename": file.filename,
            "analysis": {
                "total_keywords": len(keywords),
                "main_keyword": main_kw.keyword,
                "total_volume": total_vol,
                "top_keywords": [
                    {
                        "keyword": k.keyword,
                        "volume": k.volume,
                        "difficulty": k.keyword_difficulty,
                        "opportunity": k.keyword_opportunity
                    }
                    for k in top_kws
                ],
                "clusters": {
                    name: [{"keyword": k.keyword, "volume": k.volume} for k in kws[:5]]
                    for name, kws in clusters.items()
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/generate")
async def generate_content(
    keyword: str = Form(...),
    site_products: str = Form(""),
    parent_url: str = Form(""),
    parent_name: str = Form(""),
    selected_keywords: str = Form("[]")
):
    global uploaded_csv_path
    
    import json
    
    if not uploaded_csv_path or not Path(uploaded_csv_path).exists():
        raise HTTPException(400, "Upload a CSV file first")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OpenAI API key not configured")
    
    try:
        # Parse products (uno per riga o separati da virgola)
        products = [
            p.strip() 
            for p in site_products.replace(',', '\n').split('\n') 
            if p.strip()
        ]
        
        # Log dei prodotti ricevuti
        print(f"📦 Prodotti ricevuti: {len(products)}")
        for i, p in enumerate(products[:5], 1):
            print(f"   {i}. {p[:50]}...")
        if len(products) > 5:
            print(f"   ... e altri {len(products) - 5} prodotti")
        
        # Parse selected keywords for SERP scraping
        try:
            serp_keywords = json.loads(selected_keywords)
        except:
            serp_keywords = []
        
        agent = SEOContentAgent(api_key=api_key)
        
        category_input = CategoryInput(
            keyword=keyword,
            site_products=products,
            parent_url=parent_url.strip(),
            parent_name=parent_name.strip()
        )
        
        # Genera contenuto con scraping SERP per le keyword selezionate
        result = agent.generate_category_content(
            csv_path=uploaded_csv_path,
            category_input=category_input,
            scrape_serp_results=True,
            serp_keywords=serp_keywords if serp_keywords else None
        )
        
        return {
            "success": True,
            "content": result.content,
            "meta_title": result.meta_title,
            "meta_description": result.meta_description,
            "h1": result.h1,
            "sections": result.sections,
            "faq": result.faq,
            "seo_keywords": result.seo_keywords,
            "serp_analyzed": len(result.serp_data) if result.serp_data else 0,
            "serp_results": result.serp_data if result.serp_data else []
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))


@app.get("/api/health")
async def health():
    return {"status": "ok", "api_key": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/api/iterate")
async def iterate_content(
    current_content: str = Form(...),
    instruction: str = Form(...)
):
    """
    Itera sul contenuto esistente applicando le modifiche richieste.
    Prende il contenuto attuale e un'istruzione, restituisce il contenuto modificato.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OpenAI API key not configured")
    
    if not current_content.strip():
        raise HTTPException(400, "Contenuto vuoto")
    
    if not instruction.strip():
        raise HTTPException(400, "Istruzione vuota")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        system_prompt = """Sei un esperto SEO copywriter. 
Il tuo compito è modificare il contenuto SEO esistente seguendo le istruzioni dell'utente.

REGOLE:
- Mantieni la struttura Markdown esistente (H1, H2, meta tags, ecc.)
- Applica SOLO le modifiche richieste, non riscrivere tutto
- Mantieni il tono professionale e SEO-oriented
- Non aggiungere o rimuovere sezioni a meno che non sia esplicitamente richiesto
- Restituisci il contenuto completo modificato in formato Markdown"""

        user_prompt = f"""## CONTENUTO ATTUALE:
{current_content}

## ISTRUZIONE DI MODIFICA:
{instruction}

---
Applica la modifica richiesta e restituisci il contenuto completo aggiornato."""

        print(f"🔄 Iterazione richiesta: {instruction[:50]}...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        new_content = response.choices[0].message.content
        
        # Pulisci eventuali code blocks markdown
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            new_content = "\n".join(lines)
        
        print(f"✅ Contenuto iterato con successo")
        
        return {
            "success": True,
            "content": new_content,
            "instruction": instruction
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Errore iterazione: {str(e)}")


@app.post("/api/scrape-products")
async def scrape_products_endpoint(url: str = Form(...)):
    """
    Scrapa i nomi dei prodotti da una pagina categoria e-commerce.
    Supporta WooCommerce, Shopify, Magento, PrestaShop e CMS custom.
    """
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(400, "URL non valido")
    
    try:
        result = scrape_products(url)
        
        if not result.get("success"):
            raise HTTPException(400, result.get("error", "Errore sconosciuto"))
        
        return {
            "success": True,
            "products": result.get("products", []),
            "cms_detected": result.get("cms_detected", "unknown"),
            "total_found": result.get("total_found", 0),
            "url": url
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Errore scraping: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
