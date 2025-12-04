"""
CSV Loader per file SEOZoom
Carica e processa i dati delle keyword esportati da SEOZoom
"""

import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KeywordData:
    """Rappresenta una singola keyword con i suoi dati SEO"""
    keyword: str
    volume: int
    cpc_medio: float
    keyword_difficulty: int
    keyword_opportunity: int
    search_appearance: int
    intent_commerciale: int
    
    @property
    def priority_score(self) -> float:
        """
        Calcola un punteggio di priorità per la keyword
        Alto volume + bassa difficulty + alta opportunity = priorità alta
        """
        if self.keyword_difficulty == 0:
            difficulty_factor = 1.0
        else:
            difficulty_factor = 1 / self.keyword_difficulty
        
        opportunity_factor = self.keyword_opportunity / 100
        volume_factor = min(self.volume / 1000, 10)  # Cap a 10
        
        return (volume_factor * 0.4 + 
                difficulty_factor * 0.3 + 
                opportunity_factor * 0.3) * 100


def load_seozoom_csv(file_path: str) -> List[KeywordData]:
    """
    Carica un file CSV esportato da SEOZoom
    
    Args:
        file_path: Percorso del file CSV
        
    Returns:
        Lista di KeywordData con tutte le keyword
    """
    keywords = []
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {file_path}")
    
    # Usa utf-8-sig per rimuovere automaticamente il BOM
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Fix per header SEOZoom con newline nelle colonne quotate
    # Es: "_t(""CPC\nMedio"")" diventa "_t(""CPC Medio"")"
    lines = content.split('\n')
    fixed_lines = []
    current_line = ""
    
    for line in lines:
        current_line += line
        # Conta le virgolette - se dispari, la riga continua
        if current_line.count('"') % 2 == 0:
            fixed_lines.append(current_line)
            current_line = ""
        else:
            current_line += " "  # Sostituisci newline con spazio
    
    if current_line:
        fixed_lines.append(current_line)
    
    content = '\n'.join(fixed_lines)
    
    # Determina il delimitatore
    first_line = fixed_lines[0] if fixed_lines else ''
    if ';' in first_line:
        delimiter = ';'
    elif '\t' in first_line:
        delimiter = '\t'
    else:
        delimiter = ','
    
    # Parse CSV
    import io
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    
    for row in reader:
        try:
            # Normalizza le chiavi del row (lowercase, strip)
            norm_row = {}
            for k, v in row.items():
                if k:
                    # Pulisci la chiave
                    clean_key = k.strip().lower()
                    # Rimuovi caratteri speciali come _t("")
                    clean_key = clean_key.replace('_t("', '').replace('")', '')
                    clean_key = clean_key.replace('"', '').strip()
                    norm_row[clean_key] = v.strip() if v else ''
            
            # Cerca la keyword
            keyword = ''
            for key in ['keywords', 'keyword', 'kw', 'query']:
                if key in norm_row and norm_row[key]:
                    keyword = norm_row[key]
                    break
            
            if not keyword:
                continue
            
            # Volume
            volume = 0
            for key in ['volume', 'vol', 'search volume']:
                if key in norm_row:
                    volume = _parse_int(norm_row[key])
                    break
            
            # CPC
            cpc = 0.0
            for key in ['cpc medio', 'cpc', 'cost per click']:
                if key in norm_row:
                    cpc = _parse_float(norm_row[key])
                    break
            
            # Keyword Difficulty
            difficulty = 0
            for key in ['keyword difficulty', 'kd', 'difficulty']:
                if key in norm_row:
                    difficulty = _parse_int(norm_row[key])
                    break
            
            # Keyword Opportunity
            opportunity = 0
            for key in ['keyword opportunity', 'ko', 'opportunity']:
                if key in norm_row:
                    opportunity = _parse_int(norm_row[key])
                    break
            
            # Search Appearance
            sa = 0
            for key in ['sa', 'search appearance']:
                if key in norm_row:
                    sa = _parse_int(norm_row[key])
                    break
            
            # Intent Commerciale
            ic = 0
            for key in ['ic', 'intent commerciale']:
                if key in norm_row:
                    ic = _parse_int(norm_row[key])
                    break
            
            keywords.append(KeywordData(
                keyword=keyword,
                volume=volume,
                cpc_medio=cpc,
                keyword_difficulty=difficulty,
                keyword_opportunity=opportunity,
                search_appearance=sa,
                intent_commerciale=ic
            ))
            
        except Exception:
            continue
    
    return keywords


def _parse_int(value: str) -> int:
    """Parse un valore stringa a int, gestendo formati europei"""
    if not value:
        return 0
    # Rimuovi separatori migliaia
    clean = value.replace('.', '').replace(',', '').strip()
    try:
        return int(clean)
    except ValueError:
        return 0


def _parse_float(value: str) -> float:
    """Parse un valore stringa a float, gestendo formati europei"""
    if not value:
        return 0.0
    # Sostituisci virgola con punto per decimali
    clean = value.replace(',', '.').strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0


def get_top_keywords(
    keywords: List[KeywordData], 
    limit: int = 10
) -> List[KeywordData]:
    """
    Restituisce le keyword con priorità più alta
    
    Args:
        keywords: Lista di KeywordData
        limit: Numero massimo di keyword da restituire
        
    Returns:
        Lista ordinata per priority_score
    """
    return sorted(
        keywords, 
        key=lambda k: k.priority_score, 
        reverse=True
    )[:limit]


def get_keyword_clusters(
    keywords: List[KeywordData]
) -> dict:
    """
    Raggruppa le keyword in cluster semantici basati su pattern comuni
    
    Returns:
        Dizionario con cluster di keyword
    """
    clusters = {
        'principale': [],
        'prezzi': [],
        'tipologie': [],
        'utilizzi': [],
        'caratteristiche': [],
        'altro': []
    }
    
    price_terms = ['prezzo', 'prezzi', 'costo', 'economico', 'offerta']
    type_terms = ['tipo', 'tipi', 'modello', 'modelli', 'varietà']
    use_terms = ['per', 'come', 'quando', 'dove', 'utilizzo']
    feature_terms = ['materiale', 'qualità', 'migliore', 'professionale']
    
    for kw in keywords:
        kw_lower = kw.keyword.lower()
        
        if any(term in kw_lower for term in price_terms):
            clusters['prezzi'].append(kw)
        elif any(term in kw_lower for term in type_terms):
            clusters['tipologie'].append(kw)
        elif any(term in kw_lower for term in use_terms):
            clusters['utilizzi'].append(kw)
        elif any(term in kw_lower for term in feature_terms):
            clusters['caratteristiche'].append(kw)
        elif kw.volume >= 500:  # Keywords ad alto volume = principali
            clusters['principale'].append(kw)
        else:
            clusters['altro'].append(kw)
    
    return clusters


def format_keywords_for_prompt(keywords: List[KeywordData]) -> str:
    """
    Formatta le keyword per l'inserimento nel prompt dell'agente
    """
    lines = ["### DATI KEYWORD (da SEOZoom)"]
    lines.append("| Keyword | Volume | KD | Opportunity | IC |")
    lines.append("|---------|--------|----|-----------|----|")
    
    for kw in sorted(keywords, key=lambda k: k.volume, reverse=True):
        lines.append(
            f"| {kw.keyword} | {kw.volume} | "
            f"{kw.keyword_difficulty} | {kw.keyword_opportunity} | "
            f"{kw.intent_commerciale} |"
        )
    
    return "\n".join(lines)
