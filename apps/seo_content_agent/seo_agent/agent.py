"""
SEO Content Agent - Agente per generazione contenuti SEO E-commerce
Utilizza Datapizza AI per analizzare keyword e generare testi ottimizzati
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient

from .prompts.system_prompt import SYSTEM_PROMPT, build_user_prompt
from .utils.csv_loader import load_seozoom_csv
from .utils.serp_scraper import scrape_serp, format_serp_for_prompt


@dataclass
class CategoryInput:
    """Input per la generazione del contenuto di categoria"""
    keyword: str  # La keyword/categoria principale
    site_products: List[str] = field(default_factory=list)
    parent_url: str = ""  # URL categoria padre per internal linking
    parent_name: str = ""  # Nome categoria padre


@dataclass
class SEOOutput:
    """Output generato dall'agente SEO"""
    content: str  # Contenuto Markdown completo
    meta_title: str = ""
    meta_description: str = ""
    h1: str = ""
    sections: List[dict] = field(default_factory=list)
    faq: List[dict] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)
    serp_data: List[dict] = field(default_factory=list)


class SEOContentAgent:
    """
    Agente SEO Content Strategist per E-commerce.
    
    Funzionalità:
    - Analisi semantica delle keyword
    - Scraping SERP automatico
    - Generazione contenuti strutturati (H1, H2, H3)
    - FAQ basate su PAA
    - Internal linking
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4o-mini"
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key non trovata. Imposta OPENAI_API_KEY "
                "o passa api_key al costruttore."
            )
        
        self.client = OpenAIClient(
            api_key=self.api_key,
            model=model
        )
        
        self.agent = Agent(
            name="seo_content_strategist",
            client=self.client,
            system_prompt=SYSTEM_PROMPT
        )
    
    def generate_category_content(
        self,
        csv_path: str,
        category_input: CategoryInput,
        scrape_serp_results: bool = True,
        serp_keywords: List[str] = None
    ) -> SEOOutput:
        """
        Genera contenuto SEO per una pagina di categoria.
        
        Args:
            csv_path: Percorso al file CSV di SEOZoom
            category_input: Dati della categoria
            scrape_serp_results: Se True, esegue scraping SERP automatico
            serp_keywords: Lista di keyword per lo scraping SERP (opzionale)
            
        Returns:
            SEOOutput con il contenuto generato
        """
        # Carica keyword dal CSV
        keywords = load_seozoom_csv(csv_path)
        queries = [kw.keyword for kw in keywords]
        
        # Scraping SERP automatico
        serp_data = []
        if scrape_serp_results:
            # Usa le keyword selezionate dall'utente, altrimenti la keyword principale
            keywords_to_scrape = serp_keywords if serp_keywords else [category_input.keyword]
            print(f"🔍 Scraping SERP per {len(keywords_to_scrape)} keyword...")
            
            for kw in keywords_to_scrape[:5]:  # Max 5 keyword per evitare rate limiting
                print(f"  → Scraping: {kw}")
                results = scrape_serp(kw, num_results=10)  # Aumentato a 10 per keyword
                formatted = format_serp_for_prompt(results)
                
                # Log dei risultati trovati
                for r in formatted:
                    print(f"     📄 {r.get('title', '')[:50]}...")
                    print(f"        URL: {r.get('url', '')[:60]}")
                
                serp_data.extend(formatted)
            
            # Rimuovi duplicati basati su URL
            seen_urls = set()
            unique_serp = []
            for item in serp_data:
                if item.get('url') not in seen_urls:
                    seen_urls.add(item.get('url'))
                    unique_serp.append(item)
            serp_data = unique_serp[:20]  # Aumentato a 20 risultati totali
            print(f"✅ Trovati {len(serp_data)} risultati SERP unici (su {len(seen_urls)} totali)")
        
        # Costruisci il prompt utente
        user_prompt = build_user_prompt(
            keyword=category_input.keyword,
            site_products=category_input.site_products,
            queries=queries,
            serp_data=serp_data,
            parent_url=category_input.parent_url,
            parent_name=category_input.parent_name
        )
        
        # Esegui l'agente
        print("🤖 Generazione contenuto SEO...")
        response = self.agent.run(user_prompt)
        
        # Parsing output
        return self._parse_markdown_output(
            content=response.text,
            keywords=queries[:15],
            serp_data=serp_data
        )
    
    def _parse_markdown_output(
        self,
        content: str,
        keywords: List[str],
        serp_data: List[dict]
    ) -> SEOOutput:
        """Estrae i componenti dall'output Markdown"""
        
        meta_title = ""
        meta_description = ""
        h1 = ""
        sections = []
        faq = []
        seo_keywords = []
        
        lines = content.split("\n")
        
        for line in lines:
            # Meta Title
            if "Meta Title:" in line:
                meta_title = line.replace("**Meta Title:**", "").replace("Meta Title:", "").strip()
            # Meta Description
            elif "Meta Description:" in line:
                meta_description = line.replace("**Meta Description:**", "").replace("Meta Description:", "").strip()
            # H1
            elif line.startswith("# ") and not h1:
                h1 = line[2:].strip()
            # SEO Keywords
            elif "SEO Keywords:" in line:
                kw_text = line.replace("**SEO Keywords:**", "").replace("SEO Keywords:", "").strip()
                seo_keywords = [k.strip() for k in kw_text.split(",")]
        
        # Estrai sezioni H2
        h2_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
        h2_matches = h2_pattern.findall(content)
        for h2 in h2_matches:
            if "Domande Frequenti" not in h2 and "FAQ" not in h2:
                sections.append({"h2": h2})
        
        # Estrai FAQ
        faq_section = content.split("Domande Frequenti")[-1] if "Domande Frequenti" in content else ""
        if faq_section:
            q_pattern = re.compile(r'\*\*(.+?)\*\*\s*\n(.+?)(?=\n\*\*|\n---|\Z)', re.DOTALL)
            for match in q_pattern.finditer(faq_section):
                faq.append({
                    "question": match.group(1).strip(),
                    "answer": match.group(2).strip()
                })
        
        return SEOOutput(
            content=content,
            meta_title=meta_title,
            meta_description=meta_description,
            h1=h1,
            sections=sections,
            faq=faq,
            seo_keywords=seo_keywords if seo_keywords else keywords[:10],
            serp_data=serp_data
        )
    
    def save_output(
        self,
        output: SEOOutput,
        output_path: str
    ) -> None:
        """Salva l'output in un file"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(output.content)
        
        print(f"✅ Contenuto salvato in: {output_path}")


def create_agent(
    api_key: str = None,
    model: str = "gpt-4o-mini"
) -> SEOContentAgent:
    """Factory function per creare un SEOContentAgent"""
    return SEOContentAgent(api_key=api_key, model=model)
