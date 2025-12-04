# Stratego Swiss Knife

Stratego Swiss Knife e una piattaforma centralizzata che raccoglie tutte le applicazioni sviluppate

## Descrizione

La piattaforma funge da hub centrale con sistema di autenticazione e dashboard per accedere alle diverse applicazioni. Ogni app e sviluppata come modulo indipendente e integrata nella dashboard principale.

## Applicazioni

### SEO Content Agent

La prima applicazione disponibile sulla piattaforma. Un agente intelligente per la generazione automatica di contenuti SEO ottimizzati per pagine categoria e-commerce.

Funzionalita principali:
- Analisi di file CSV esportati da SEOZoom con keyword e metriche
- Clustering automatico delle keyword per volume e opportunita
- Scraping prodotti da URL categoria
- Scraping SERP per analisi competitiva
- Generazione contenuti SEO completi tramite AI

Output generato:
- Meta Title ottimizzato
- Meta Description con call-to-action
- Intestazione H1 con keyword principale
- Contenuto strutturato con H2 e H3
- Link interni alla categoria parent
- Sezione FAQ basata sulle query degli utenti
- Riepilogo SEO con keyword utilizzate

## Requisiti

- Python 3.10 o superiore
- Chiave API OpenAI

## Installazione

Clona il repository:

```
git clone https://github.com/Stratego-Swat/Stratego-Swiss-Knife
cd Stratego-Swiss-Knife
```

Crea e attiva un ambiente virtuale:

```
python3 -m venv .venv
source .venv/bin/activate
```

Installa le dipendenze:

```
pip install fastapi uvicorn python-multipart jinja2 itsdangerous python-dotenv openai beautifulsoup4 requests
```

Configura le variabili ambiente:

```
cp .env.example .env
```

Modifica il file .env inserendo la tua chiave API.

## Avvio

Avvia il server Login/Dashboard sulla porta 8000:

```
cd Login
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Avvia il SEO Content Agent sulla porta 8001:

```
cd apps/seo_content_agent/web
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Accesso

| Servizio | URL |
|----------|-----|
| Dashboard | http://localhost:8000 |
| SEO Agent | http://localhost:8001 |

## Struttura del Progetto

```
Stratego Swiss/
|-- Login/
|   |-- main.py
|   |-- templates/
|   |-- static/
|-- apps/
|   |-- seo_content_agent/
|       |-- web/
|       |-- seo_agent/
|       |-- data/
|       |-- output/
|-- .env
|-- .gitignore
|-- start.sh
```

## Formato CSV SEOZoom

Il SEO Content Agent accetta file CSV con le seguenti colonne:

| Colonna | Descrizione |
|---------|-------------|
| Keywords | Keyword target |
| Volume | Volume di ricerca mensile |
| CPC Medio | Costo per click |
| Keyword Difficulty | Difficolta (0-100) |
| Keyword Opportunity | Opportunita (0-100) |

## Modelli AI Disponibili

| Modello | Descrizione |
|---------|-------------|
| gpt-4o-mini | Veloce ed economico (default) |
| gpt-4o | Qualita superiore |
| gpt-4-turbo | Contesto esteso |

Valutare Uppgrade dei modelli! 

## Note sulla Sicurezza

- Utilizzare variabili ambiente per dati sensibili
- Abilitare HTTPS in produzione

## Licenza

MIT License

## Autore

Sviluppato da Nicolas Micolani
