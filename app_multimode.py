import streamlit as st
import requests
import json
import os
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CONFIGURAZIONE SICURA ==========
st.set_page_config(page_title="Multi-AI Agent", page_icon="🤖", layout="wide")

# API Key master (DA ENVIRONMENT - invisibile agli utenti)
MASTER_GROQ_KEY = os.getenv("GROQ_API_KEY", "")

# Email autorizzate (DA ENVIRONMENT - invisibile su GitHub)
AUTHORIZED_EMAILS_RAW = os.getenv("AUTHORIZED_EMAILS", "")
AUTHORIZED_EMAILS = [email.strip().lower() for email in AUTHORIZED_EMAILS_RAW.split(",") if email.strip()]

# Password temporanea sistema (DA ENVIRONMENT)
SYSTEM_PASSWORD = os.getenv("SYSTEM_PASSWORD", "")

# Configurazione sessione
SESSION_TIMEOUT_HOURS = 24

# Rate limiting - max tentativi login
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 60

# ========== VERIFICA CONFIGURAZIONE ==========
if not MASTER_GROQ_KEY:
    st.error("⚠️ GROQ_API_KEY non configurata. Contatta l'amministratore.")
    st.stop()

if not AUTHORIZED_EMAILS:
    st.error("⚠️ AUTHORIZED_EMAILS non configurata. Contatta l'amministratore.")
    st.stop()

if not SYSTEM_PASSWORD:
    st.error("⚠️ SYSTEM_PASSWORD non configurata. Contatta l'amministratore.")
    st.stop()

# ========== RATE LIMITING ==========
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = defaultdict(list)

def is_rate_limited(email):
    """Verifica se utente è bloccato per troppi tentativi"""
    now = datetime.now()
    attempts = st.session_state.login_attempts[email]
    
    # Rimuovi tentativi vecchi (>1 ora)
    recent_attempts = [t for t in attempts if now - t < timedelta(minutes=LOCKOUT_DURATION_MINUTES)]
    st.session_state.login_attempts[email] = recent_attempts
    
    if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
        minutes_left = LOCKOUT_DURATION_MINUTES - int((now - recent_attempts[0]).total_seconds() / 60)
        return True, minutes_left
    
    return False, 0

def record_login_attempt(email):
    """Registra tentativo di login"""
    st.session_state.login_attempts[email].append(datetime.now())

# ========== SESSION MANAGEMENT ==========
def init_session():
    """Inizializza session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.login_time = None

def is_session_valid():
    """Verifica validità sessione"""
    if not st.session_state.authenticated:
        return False
    
    if st.session_state.login_time:
        elapsed = datetime.now() - st.session_state.login_time
        if elapsed > timedelta(hours=SESSION_TIMEOUT_HOURS):
            logger.info(f"Session expired for {st.session_state.user_email}")
            return False
    
    return True

def login_user(email):
    """Login utente"""
    st.session_state.authenticated = True
    st.session_state.user_email = email
    st.session_state.user_name = email.split('@')[0].title()
    st.session_state.login_time = datetime.now()
    logger.info(f"✅ Login successful: {email}")

def logout_user():
    """Logout utente"""
    email = st.session_state.user_email
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.login_time = None
    logger.info(f"🚪 Logout: {email}")
    st.rerun()

# ========== AUTENTICAZIONE ==========
def verify_credentials(email, password):
    """Verifica credenziali utente"""
    email_lower = email.strip().lower()
    
    # Verifica email autorizzata
    if email_lower not in AUTHORIZED_EMAILS:
        logger.warning(f"❌ Login attempt from unauthorized email: {email}")
        return False
    
    # Verifica password
    if password != SYSTEM_PASSWORD:
        logger.warning(f"❌ Invalid password for: {email}")
        return False
    
    return True

# ========== PAGINA LOGIN ==========
def show_login_page():
    """Mostra pagina di login"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-box {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Multi-AI Agent System</h1>
        <p>Accesso Riservato</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Login")
        
        email_input = st.text_input(
            "Email autorizzata",
            placeholder="tuo.email@gmail.com",
            key="login_email"
        )
        
        password_input = st.text_input(
            "Password di accesso",
            type="password",
            key="login_password"
        )
        
        if st.button("🚀 Accedi", use_container_width=True, type="primary"):
            
            if not email_input or not password_input:
                st.error("❌ Inserisci email e password")
                return
            
            # Check rate limiting
            is_limited, minutes = is_rate_limited(email_input.lower())
            if is_limited:
                st.error(f"🚫 Troppi tentativi falliti. Riprova tra {minutes} minuti.")
                logger.warning(f"🚫 Rate limited: {email_input}")
                return
            
            # Verifica credenziali
            if verify_credentials(email_input, password_input):
                login_user(email_input.lower())
                st.success("✅ Login effettuato!")
                st.rerun()
            else:
                record_login_attempt(email_input.lower())
                remaining = MAX_LOGIN_ATTEMPTS - len(st.session_state.login_attempts[email_input.lower()])
                
                if remaining > 0:
                    st.error(f"❌ Credenziali non valide. Tentativi rimasti: {remaining}")
                else:
                    st.error(f"🚫 Account bloccato per {LOCKOUT_DURATION_MINUTES} minuti")
        
        st.markdown("---")
        st.info("👥 **Solo utenti autorizzati**\n\nContatta l'amministratore per richiedere l'accesso")
        st.caption(f"🔒 Sessione valida per {SESSION_TIMEOUT_HOURS} ore")
        st.caption(f"🛡️ Massimo {MAX_LOGIN_ATTEMPTS} tentativi di login")

# ========== GROQ API ==========
def query_groq(model, system_msg, user_msg):
    """Query Groq API usando chiave master"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {MASTER_GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        # Log utilizzo
        logger.info(f"API call: {model} by {st.session_state.user_email}")
        
        return result
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"Errore API: {str(e)}"

# ========== MAIN APP ==========
init_session()

# Check autenticazione
if not is_session_valid():
    show_login_page()
    st.stop()

# ========== INTERFACCIA PER UTENTI AUTENTICATI ==========
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.success(f"👤 **{st.session_state.user_name}**")
    st.caption(f"📧 {st.session_state.user_email}")
    
    # Session info
    if st.session_state.login_time:
        elapsed = datetime.now() - st.session_state.login_time
        hours_left = SESSION_TIMEOUT_HOURS - (elapsed.total_seconds() / 3600)
        st.caption(f"⏱️ Sessione: {hours_left:.1f}h rimaste")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
    
    st.markdown("---")
    st.header("⚙️ Modalità")
    st.markdown("""
    🟢 **QUICK** - 1 modello - 10s  
    🟡 **STANDARD** - 3 modelli - 30s  
    🟠 **DEEP** - 5 modelli - 60s  
    🔴 **EXPERT** - 6 modelli - 120s
    """)
    
    st.markdown("---")
    st.caption("💰 Servizio gratuito")
    st.caption("🔒 Accesso protetto")
    st.caption(f"👥 {len(AUTHORIZED_EMAILS)} utenti autorizzati")

st.markdown("""
<div class="main-header">
    <h1>🤖 Multi-AI Agent System</h1>
    <p>Consulta fino a 6 modelli AI contemporaneamente</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 💭 Fai la tua domanda")
domanda = st.text_area("", height=120, placeholder="Esempio: Dovrei cambiare lavoro?")

if domanda.strip():
    st.markdown("### ⚙️ Seleziona Modalità")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quick = st.button("🟢 QUICK", use_container_width=True)
    with col2:
        standard = st.button("🟡 STANDARD", use_container_width=True)
    with col3:
        deep = st.button("🟠 DEEP", use_container_width=True)
    with col4:
        expert = st.button("🔴 EXPERT", use_container_width=True)
    
    # QUICK
    if quick:
        st.success("🟢 Modalità QUICK")
        with st.spinner("⏳ Elaborazione..."):
            risposta = query_groq(
                "llama-3.3-70b-versatile",
                "Sei un esperto generalista. Fornisci risposta completa.",
                domanda
            )
        st.markdown("### ✅ Risposta")
        st.markdown(risposta)
        st.caption("💰 Costo: $0.00 | Modello: Llama 3.3 70B")
    
    # STANDARD
    elif standard:
        st.success("🟡 Modalità STANDARD: 3 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico", "Analisi dettagliata"),
            ("openai/gpt-oss-20b", "Esperto Pratico", "Esempi concreti"),
            ("qwen/qwen3-32b", "Pensatore Critico", "Analisi critica")
        ]
        
        responses = []
        
        with st.spinner("⏳ 3 agenti..."):
            for model, role, goal in agents:
                r = query_groq(model, f"Sei un {role}. {goal}.", domanda)
                responses.append((role, r))
        
        with st.spinner("🎯 Sintesi..."):
            synthesis_prompt = f"Sintetizza queste 3 analisi:\n\n"
            for role, resp in responses:
                synthesis_prompt += f"{role}: {resp}\n\n"
            
            finale = query_groq(
                "llama-3.3-70b-versatile",
                "Sintetizza le analisi in una risposta coerente.",
                synthesis_prompt
            )
        
        st.markdown("### ✅ Risposta Finale")
        st.markdown(finale)
        
        with st.expander("📖 Risposte individuali"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 3 modelli")
    
    # DEEP
    elif deep:
        st.warning("🟠 Modalità DEEP: 5 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista"),
            ("llama-3.3-70b-versatile", "Stratega"),
            ("openai/gpt-oss-20b", "Pratico"),
            ("qwen/qwen3-32b", "Alternativo"),
            ("meta-llama/llama-4-scout-17b-16e-instruct", "Verificatore")
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role) in enumerate(agents):
            st.text(f"⏳ {i+1}/5: {role}...")
            r = query_groq(model, f"Sei un {role}.", domanda)
            responses.append((role, r))
            progress.progress((i+1)/6)
        
        st.text("🎯 Sintesi...")
        synthesis = "Sintetizza:\n\n"
        for role, resp in responses:
            synthesis += f"{role}: {resp}\n\n"
        
        finale = query_groq("llama-3.3-70b-versatile", "Sintesi.", synthesis)
        progress.progress(1.0)
        
        st.markdown("### ✅ Risposta DEEP")
        st.markdown(finale)
        
        with st.expander("📊 5 Prospettive"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 5 modelli")
    
    # EXPERT
    elif expert:
        st.error("🔴 Modalità EXPERT: 6 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista"),
            ("llama-3.3-70b-versatile", "Stratega"),
            ("openai/gpt-oss-120b", "Profondo"),
            ("openai/gpt-oss-20b", "Pratico"),
            ("qwen/qwen3-32b", "Critico"),
            ("meta-llama/llama-guard-4-12b", "Verificatore")
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role) in enumerate(agents):
            st.text(f"⏳ {i+1}/6: {role}...")
            r = query_groq(model, f"Sei un {role}.", domanda)
            responses.append((role, r))
            progress.progress((i+1)/7)
        
        st.text("🎯 Super-sintesi...")
        synthesis = "Sintesi da 6 AI:\n\n"
        for role, resp in responses:
            synthesis += f"{role}: {resp}\n\n"
        
        finale = query_groq("llama-3.3-70b-versatile", "Sintesi master.", synthesis)
        progress.progress(1.0)
        
        st.markdown("### 🏆 Risposta EXPERT")
        st.markdown(finale)
        
        with st.expander("📊 6 Prospettive"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 6 modelli")

st.markdown("---")
st.markdown(f"**Multi-AI System** | Utente: {st.session_state.user_name} | Sicuro e Privato")
