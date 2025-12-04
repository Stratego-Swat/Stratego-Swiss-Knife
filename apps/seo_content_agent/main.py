#!/usr/bin/env python3
"""
Script principale per eseguire il SEO Content Agent
Genera contenuti SEO per pagine di categoria e-commerce
"""

import os
import sys
from pathlib import Path

# Aggiungi il path del progetto
sys.path.insert(0, str(Path(__file__).parent))

from seo_agent.agent import SEOContentAgent, CategoryInput


def main():
    """
    Esempio di utilizzo del SEO Content Agent
    """
    # Verifica API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Errore: OPENAI_API_KEY non configurata!")
        print("   Esegui: export OPENAI_API_KEY='la-tua-api-key'")
        sys.exit(1)
    
    # Configura i dati della categoria
    category_input = CategoryInput(
        categoria_merceologica="Sport e Tempo Libero",
        sottocategoria="Nuoto",
        tipologie_prodotti=[
            "Costumi da nuoto donna",
            "Costumi da nuoto uomo", 
            "Costumi da nuoto bambino",
            "Costumi nuoto agonistici",
            "Costumi nuoto allenamento",
            "Costumi piscina"
        ],
        parent_categoria_url="/sport/nuoto/",
        parent_categoria_nome="Nuoto"
    )
    
    # Percorso al file CSV di SEOZoom
    csv_path = "data/esempio_seozoom.csv"
    
    # Output path
    output_path = "output/categoria_costumi_nuoto.md"
    
    print("🚀 SEO Content Agent - Datapizza AI")
    print("=" * 50)
    print(f"📂 File CSV: {csv_path}")
    print(f"🏷️  Categoria: {category_input.sottocategoria}")
    print(f"🔗 Parent URL: {category_input.parent_categoria_url}")
    print("=" * 50)
    
    try:
        # Crea l'agente
        agent = SEOContentAgent(
            api_key=api_key,
            model="gpt-4o-mini"  # Puoi cambiare con "gpt-4o" per risultati migliori
        )
        
        print("\n⏳ Generazione contenuto in corso...")
        
        # Genera il contenuto
        output = agent.generate_category_content(
            csv_path=csv_path,
            category_input=category_input
        )
        
        # Salva l'output
        agent.save_output(output, output_path)
        
        # Mostra risultati
        print("\n📊 RISULTATO")
        print("-" * 50)
        print(f"📌 Meta Title: {output.meta_title}")
        print(f"📝 Meta Description: {output.meta_description}")
        print(f"🔑 Keywords usate: {len(output.keywords_used)}")
        print("-" * 50)
        print("\n✅ Generazione completata con successo!")
        print(f"📄 File salvato: {output_path}")
        
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore durante la generazione: {e}")
        raise


if __name__ == "__main__":
    main()
