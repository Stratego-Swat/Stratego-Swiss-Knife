#!/usr/bin/env python3
"""
SEO Content Agent - Interfaccia Web
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from seo_agent.agent import SEOContentAgent, CategoryInput
from seo_agent.utils.csv_loader import load_seozoom_csv

# Configurazione pagina
st.set_page_config(
    page_title="SEO Content Agent",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Enterprise Style
st.markdown("""
<style>
    /* === ENTERPRISE THEME === */
    
    /* Root variables */
    :root {
        --primary: #0052CC;
        --primary-dark: #003D99;
        --primary-light: #E6F0FF;
        --secondary: #172B4D;
        --text-primary: #172B4D;
        --text-secondary: #5E6C84;
        --text-muted: #97A0AF;
        --border: #DFE1E6;
        --border-light: #EBECF0;
        --surface: #FFFFFF;
        --surface-raised: #F4F5F7;
        --surface-sunken: #FAFBFC;
        --success: #00875A;
        --warning: #FF991F;
        --error: #DE350B;
        --radius-sm: 4px;
        --radius-md: 6px;
        --radius-lg: 8px;
        --shadow-sm: 0 1px 2px rgba(9,30,66,0.08);
        --shadow-md: 0 4px 8px rgba(9,30,66,0.08), 0 0 1px rgba(9,30,66,0.08);
        --shadow-lg: 0 8px 16px rgba(9,30,66,0.15), 0 0 1px rgba(9,30,66,0.1);
    }
    
    /* Base layout */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Header styles */
    .enterprise-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    
    .enterprise-logo {
        width: 36px;
        height: 36px;
        background: var(--primary);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 16px;
    }
    
    .enterprise-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin: 0;
    }
    
    .enterprise-subtitle {
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 32px;
        padding-left: 48px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
    }
    
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 14px;
        color: var(--text-primary);
        font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
        line-height: 1.5;
        word-break: break-word;
    }
    
    /* Section headers */
    .section-header {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--border-light);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface-sunken);
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 24px;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 11px;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 16px;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h5 {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        margin-top: 8px;
        margin-bottom: 12px;
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        font-size: 14px;
        color: var(--text-primary);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px var(--primary-light);
        outline: none;
    }
    
    .stTextInput label, .stTextArea label, .stSelectbox label {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: var(--radius-md);
        font-weight: 500;
        font-size: 14px;
        padding: 10px 16px;
        border: none;
        transition: all 0.15s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button[kind="primary"] {
        background: var(--primary);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background: var(--surface);
        color: var(--text-primary);
        border: 1px solid var(--border);
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        background: var(--surface-raised);
        border-color: var(--text-muted);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--surface-raised);
        border-radius: var(--radius-md);
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 500;
        color: var(--text-secondary);
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--surface);
        color: var(--text-primary);
        box-shadow: var(--shadow-sm);
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border: none;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: var(--radius-lg);
        padding: 20px;
        background: var(--surface);
        transition: border-color 0.15s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: var(--radius-md);
        border: none;
        font-size: 14px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-secondary);
        background: var(--surface-raised);
        border-radius: var(--radius-md);
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border-light);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
    }
    
    /* Download button */
    .stDownloadButton > button {
        width: 100%;
    }
    
    /* Checkbox */
    .stCheckbox label {
        font-size: 13px;
        color: var(--text-secondary);
    }
    
    /* Divider */
    hr {
        margin: 24px 0;
        border: none;
        border-top: 1px solid var(--border-light);
    }
    
    /* Caption */
    .stCaption {
        font-size: 12px;
        color: var(--text-muted);
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
    }
    
    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Success message */
    .element-container:has(.stSuccess) {
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-badge.success {
        background: #E3FCEF;
        color: #006644;
    }
    
    .status-badge.info {
        background: var(--primary-light);
        color: var(--primary);
    }
</style>
""", unsafe_allow_html=True)

# Header Enterprise
st.markdown('''
<div class="enterprise-header">
    <div class="enterprise-logo">S</div>
    <h1 class="enterprise-title">SEO Content Agent</h1>
</div>
<p class="enterprise-subtitle">Generazione automatica di contenuti ottimizzati per pagine categoria</p>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### IMPOSTAZIONI")
    
    uploaded_file = st.file_uploader(
        "File keyword (.csv)",
        type=['csv'],
        help="File CSV con keyword e metriche"
    )
    
    st.markdown("---")
    st.markdown("##### Categoria")
    
    categoria_merceologica = st.text_input(
        "Settore",
        placeholder="Es: Elettronica, Sport..."
    )
    
    sottocategoria = st.text_input(
        "Categoria",
        placeholder="Es: Smartphone, Nuoto..."
    )
    
    tipologie_prodotti = st.text_area(
        "Prodotti (uno per riga)",
        height=100,
        placeholder="Prodotto 1\nProdotto 2\nProdotto 3"
    )
    
    st.markdown("---")
    st.markdown("##### Link interno")
    
    parent_url = st.text_input(
        "URL parent",
        placeholder="/categoria/"
    )
    
    parent_nome = st.text_input(
        "Anchor text",
        placeholder="Nome categoria"
    )
    
    st.markdown("---")
    
    model = st.selectbox(
        "Modello",
        options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        index=0
    )

# Layout principale
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(
        '<p class="section-header">Analisi Keyword</p>',
        unsafe_allow_html=True
    )
    
    csv_path = None
    keywords = None
    
    if uploaded_file is not None:
        # Salva il file temporaneo con encoding corretto
        temp_path = Path("temp_upload.csv")
        
        # Leggi il contenuto e decodifica
        content = uploaded_file.getvalue()
        
        # Prova diversi encoding
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                decoded = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            decoded = content.decode('utf-8', errors='ignore')
        
        temp_path.write_text(decoded, encoding='utf-8')
        csv_path = str(temp_path)
        
        try:
            keywords = load_seozoom_csv(csv_path)
            
            if keywords:
                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Keyword": kw.keyword,
                        "Volume": kw.volume,
                        "Difficulty": kw.keyword_difficulty,
                        "Opportunity": kw.keyword_opportunity
                    }
                    for kw in sorted(
                        keywords,
                        key=lambda k: k.volume,
                        reverse=True
                    )[:12]
                ])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown(
                    f'<span class="status-badge info">{len(keywords)} keyword</span>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("Nessuna keyword trovata nel file")
            
        except Exception as e:
            st.error(f"Errore nel file: {e}")
    else:
        st.info("Carica un file CSV per analizzare le keyword")

with col_right:
    st.markdown(
        '<p class="section-header">Generazione Contenuto</p>',
        unsafe_allow_html=True
    )
    
    can_generate = all([
        csv_path,
        categoria_merceologica,
        sottocategoria,
        tipologie_prodotti,
        parent_url,
        parent_nome
    ])
    
    if not can_generate:
        st.caption("Compila tutti i campi per abilitare la generazione")
    
    generate_btn = st.button(
        "Genera contenuto SEO",
        type="primary",
        use_container_width=True,
        disabled=not can_generate
    )
    
    if generate_btn and can_generate:
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            st.error("API Key non configurata")
        else:
            tipologie_list = [
                t.strip() 
                for t in tipologie_prodotti.split("\n") 
                if t.strip()
            ]
            
            category_input = CategoryInput(
                categoria_merceologica=categoria_merceologica,
                sottocategoria=sottocategoria,
                tipologie_prodotti=tipologie_list,
                parent_categoria_url=parent_url,
                parent_categoria_nome=parent_nome
            )
            
            with st.spinner("Generazione in corso..."):
                try:
                    agent = SEOContentAgent(
                        api_key=api_key,
                        model=model
                    )
                    
                    output = agent.generate_category_content(
                        csv_path=csv_path,
                        category_input=category_input
                    )
                    
                    st.session_state['output'] = output
                    st.session_state['generated'] = True
                    st.session_state['category'] = sottocategoria
                    
                except Exception as e:
                    st.error(f"Errore: {e}")
                finally:
                    temp = Path("temp_upload.csv")
                    if temp.exists():
                        temp.unlink()

# Output
if st.session_state.get('generated') and st.session_state.get('output'):
    output = st.session_state['output']
    category = st.session_state.get('category', 'categoria')
    
    st.markdown("---")
    st.markdown(
        '<p class="section-header">Risultato</p>',
        unsafe_allow_html=True
    )
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown(
            f'''<div class="metric-card">
                <div class="metric-label">Meta Title</div>
                <div class="metric-value">{output.meta_title}</div>
            </div>''',
            unsafe_allow_html=True
        )
    
    with col_m2:
        st.markdown(
            f'''<div class="metric-card">
                <div class="metric-label">Meta Description</div>
                <div class="metric-value">{output.meta_description}</div>
            </div>''',
            unsafe_allow_html=True
        )
    
    tab_preview, tab_code = st.tabs(["Anteprima", "Codice Markdown"])
    
    with tab_preview:
        st.markdown(output.content)
    
    with tab_code:
        st.code(output.content, language="markdown")
    
    with st.expander("Keyword utilizzate nel contenuto"):
        st.write(", ".join(output.keywords_used))
    
    col_a1, col_a2, col_a3 = st.columns([1, 1, 1])
    
    with col_a1:
        st.download_button(
            label="Esporta file",
            data=output.content,
            file_name=f"{category.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col_a2:
        if st.button("Salva localmente", use_container_width=True):
            out_path = Path("output") / f"{category.lower().replace(' ', '_')}.md"
            out_path.parent.mkdir(exist_ok=True)
            out_path.write_text(output.content, encoding='utf-8')
            st.success(f"File salvato: {out_path}")
    
    with col_a3:
        if st.button("Nuova generazione", use_container_width=True):
            st.session_state['generated'] = False
            st.session_state['output'] = None
            st.rerun()
