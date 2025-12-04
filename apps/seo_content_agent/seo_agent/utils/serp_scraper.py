"""
SERP Scraper - Scraping dei risultati di ricerca Google
Utilizza DuckDuckGo Search come alternativa a Google (no API key richiesta)
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SerpResult:
    """Singolo risultato SERP"""
    position: int
    title: str
    url: str
    description: str


def scrape_serp(
    keyword: str,
    num_results: int = 10,
    region: str = "it-it"
) -> List[SerpResult]:
    """
    Esegue scraping dei risultati di ricerca per una keyword.
    Usa DuckDuckGo Search come fonte (no blocchi, no API key).
    
    Args:
        keyword: La keyword da cercare
        num_results: Numero di risultati da ottenere (default 10)
        region: Regione per i risultati (default it-it per Italia)
    
    Returns:
        Lista di SerpResult con i dati dei primi risultati
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            print("⚠️ ddgs non installato. Installalo con: pip install ddgs")
            return []
    
    results = []
    
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                keyword,
                region=region,
                max_results=num_results
            ))
            
            for i, item in enumerate(search_results, 1):
                results.append(SerpResult(
                    position=i,
                    title=item.get('title', ''),
                    url=item.get('href', ''),
                    description=item.get('body', '')
                ))
    
    except Exception as e:
        print(f"⚠️ Errore durante lo scraping SERP: {e}")
    
    return results


def analyze_serp_titles(results: List[SerpResult]) -> Dict:
    """
    Analizza i titoli SERP per identificare pattern.
    
    Args:
        results: Lista di SerpResult
    
    Returns:
        Dict con analisi dei titoli
    """
    if not results:
        return {"patterns": [], "common_words": [], "avg_length": 0}
    
    titles = [r.title for r in results]
    
    # Lunghezza media titoli
    avg_length = sum(len(t) for t in titles) / len(titles)
    
    # Pattern comuni
    patterns = []
    
    # Cerca pattern con separatori
    separators = [' - ', ' | ', ' – ', ': ']
    for sep in separators:
        count = sum(1 for t in titles if sep in t)
        if count >= len(titles) // 2:
            patterns.append(f"Usa '{sep}' come separatore")
    
    # Cerca anni nei titoli
    year_pattern = re.compile(r'\b20\d{2}\b')
    year_count = sum(1 for t in titles if year_pattern.search(t))
    if year_count >= 3:
        patterns.append("Include l'anno nel titolo")
    
    # Parole più frequenti (escluse stop words)
    stop_words = {'il', 'la', 'i', 'le', 'di', 'da', 'in', 'su', 'per', 'con', 'e', 'a', 'the', 'and', 'or', 'for'}
    all_words = []
    for title in titles:
        words = re.findall(r'\b\w+\b', title.lower())
        all_words.extend(w for w in words if w not in stop_words and len(w) > 2)
    
    word_freq = {}
    for word in all_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "patterns": patterns,
        "common_words": [w[0] for w in common_words],
        "avg_length": round(avg_length),
        "titles_analyzed": len(titles)
    }


def format_serp_for_prompt(results: List[SerpResult]) -> List[Dict]:
    """
    Formatta i risultati SERP per il prompt dell'agente.
    
    Args:
        results: Lista di SerpResult
    
    Returns:
        Lista di dict pronti per il prompt
    """
    return [
        {
            "position": r.position,
            "title": r.title,
            "url": r.url,
            "description": r.description[:150] + "..." if len(r.description) > 150 else r.description
        }
        for r in results
    ]


def get_competitor_insights(keyword: str, num_results: int = 10) -> Dict:
    """
    Ottiene insights completi sui competitor dalla SERP.
    
    Args:
        keyword: La keyword da analizzare
        num_results: Numero di risultati da analizzare
    
    Returns:
        Dict con risultati SERP e analisi
    """
    results = scrape_serp(keyword, num_results)
    analysis = analyze_serp_titles(results)
    
    return {
        "keyword": keyword,
        "results": format_serp_for_prompt(results),
        "analysis": analysis,
        "total_results": len(results)
    }
