import streamlit as st
import requests
import json

st.set_page_config(page_title="Multi-AI Agent", page_icon="🤖", layout="wide")

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

with st.sidebar:
    st.header("⚙️ Configurazione")
    groq_api_key = st.text_input("Groq API Key", type="password")
    
    st.markdown("---")
    st.markdown("""
    ### 📊 Modalità
    
    🟢 **QUICK** - 1 modello - 10s  
    🟡 **STANDARD** - 3 modelli - 30s  
    🟠 **DEEP** - 5 modelli - 60s  
    🔴 **EXPERT** - 7 modelli - 120s
    """)

st.markdown("""
<div class="main-header">
    <h1>🤖 Multi-AI Agent System</h1>
    <p>Consulta fino a 7 modelli AI</p>
</div>
""", unsafe_allow_html=True)

if not groq_api_key:
    st.warning("👈 Inserisci Groq API key")
    st.stop()

def query_groq(model, system_msg, user_msg, api_key):
    """Query Groq API directly via HTTP"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
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
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Errore: {str(e)}"

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
                "llama-3.3-70b-versatile",  # ✅ AGGIORNATO
                "Sei un esperto generalista. Fornisci risposta completa.",
                domanda,
                groq_api_key
            )
        st.markdown("### ✅ Risposta")
        st.markdown(risposta)
        st.caption("💰 Costo: $0.00 | Modello: Llama 3.3 70B")
    
    # STANDARD
    elif standard:
        st.success("🟡 Modalità STANDARD: 3 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico", "Analisi dettagliata"),
            ("gemma2-9b-it", "Esperto Pratico", "Esempi concreti"),
            ("llama-3.1-8b-instant", "Pensatore Critico", "Analisi critica")
        ]
        
        responses = []
        
        with st.spinner("⏳ 3 agenti..."):
            for model, role, goal in agents:
                r = query_groq(model, f"Sei un {role}. {goal}.", domanda, groq_api_key)
                responses.append((role, r))
        
        # Synthesis
        with st.spinner("🎯 Sintesi..."):
            synthesis_prompt = f"Sintetizza queste 3 analisi:\n\n"
            for role, resp in responses:
                synthesis_prompt += f"{role}: {resp}\n\n"
            
            finale = query_groq(
                "llama-3.3-70b-versatile",  # ✅ AGGIORNATO
                "Sintetizza le analisi in una risposta coerente.",
                synthesis_prompt,
                groq_api_key
            )
        
        st.markdown("### ✅ Risposta Finale")
        st.markdown(finale)
        
        with st.expander("📖 Risposte individuali"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 3 modelli consultati")
    
    # DEEP
    elif deep:
        st.warning("🟠 Modalità DEEP: 5 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico"),
            ("llama-3.3-70b-versatile", "Stratega"),  # ✅ AGGIORNATO
            ("gemma2-9b-it", "Esperto Pratico"),
            ("llama-3.1-8b-instant", "Pensatore Critico"),
            ("llama-3.2-90b-text-preview", "Prospettiva Globale")  # ✅ CAMBIATO (qwen non sempre disponibile)
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role) in enumerate(agents):
            st.text(f"⏳ {i+1}/5: {role}...")
            r = query_groq(model, f"Sei un {role}.", domanda, groq_api_key)
            responses.append((role, r))
            progress.progress((i+1)/6)
        
        st.text("🎯 Sintesi...")
        synthesis_prompt = "Sintetizza:\n\n"
        for role, resp in responses:
            synthesis_prompt += f"{role}: {resp}\n\n"
        
        finale = query_groq(
            "llama-3.3-70b-versatile",  # ✅ AGGIORNATO
            "Crea sintesi definitiva.",
            synthesis_prompt,
            groq_api_key
        )
        progress.progress(1.0)
        
        st.markdown("### ✅ Risposta DEEP")
        st.markdown(finale)
        
        with st.expander("📊 5 Prospettive"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 5 modelli consultati")
    
    # EXPERT
    elif expert:
        st.error("🔴 Modalità EXPERT: 6 modelli")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista Veloce"),
            ("llama-3.3-70b-versatile", "Stratega Master"),  # ✅ AGGIORNATO
            ("deepseek-r1-distill-llama-70b", "Pensatore Profondo"),  # ✅ AGGIORNATO
            ("gemma2-9b-it", "Esperto Pratico"),
            ("llama-3.1-8b-instant", "Critico Costruttivo"),
            ("llama-3.2-90b-text-preview", "Verificatore Globale")
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role) in enumerate(agents):
            st.text(f"⏳ {i+1}/6: {role}...")
            r = query_groq(model, f"Sei un {role}.", domanda, groq_api_key)
            responses.append((role, r))
            progress.progress((i+1)/7)
        
        st.text("🎯 Super-sintesi...")
        synthesis_prompt = "Sintesi da 6 AI:\n\n"
        for role, resp in responses:
            synthesis_prompt += f"{role}: {resp}\n\n"
        
        finale = query_groq(
            "llama-3.3-70b-versatile",  # ✅ AGGIORNATO
            "Sintesi definitiva master.",
            synthesis_prompt,
            groq_api_key
        )
        progress.progress(1.0)
        
        st.markdown("### 🏆 Risposta EXPERT")
        st.markdown(finale)
        
        with st.expander("📊 6 Prospettive"):
            for role, resp in responses:
                st.markdown(f"**{role}**")
                st.info(resp)
        
        st.caption("💰 Costo: $0.00 | 6 modelli premium consultati")

st.markdown("---")
st.markdown("**Multi-AI System** | Powered by Groq API | Modelli: Llama 3.3, Mixtral, Gemma")
