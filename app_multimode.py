import streamlit as st
from groq import Groq
import os

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

client = Groq(api_key=groq_api_key)

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
    
    def query_model(model_name, role, goal, question):
        """Query a single model"""
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": f"Sei un {role}. {goal}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Errore: {str(e)}"
    
    def synthesize(responses, question):
        """Synthesize responses"""
        synthesis_prompt = f"Sintetizza queste {len(responses)} analisi su '{question}':\n\n"
        for i, r in enumerate(responses):
            synthesis_prompt += f"Analisi {i+1}: {r}\n\n"
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Sintetizza le analisi in una risposta coerente."},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content
    
    # QUICK
    if quick:
        st.success("🟢 Modalità QUICK")
        with st.spinner("⏳ Elaborazione..."):
            risposta = query_model(
                "llama-3.1-70b-versatile",
                "Esperto Generalista",
                "Fornisci risposta completa.",
                domanda
            )
        st.markdown("### ✅ Risposta")
        st.markdown(risposta)
    
    # STANDARD
    elif standard:
        st.success("🟡 Modalità STANDARD")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico", "Analisi dettagliata."),
            ("mixtral-8x7b-32768", "Esperto Pratico", "Esempi concreti."),
            ("gemma-7b-it", "Pensatore Critico", "Analisi critica.")
        ]
        
        responses = []
        with st.spinner("⏳ 3 agenti..."):
            for model, role, goal in agents:
                r = query_model(model, role, goal, domanda)
                responses.append(r)
        
        with st.spinner("🎯 Sintesi..."):
            finale = synthesize(responses, domanda)
        
        st.markdown("### ✅ Risposta Finale")
        st.markdown(finale)
        
        with st.expander("📖 Risposte individuali"):
            for i, (agent, resp) in enumerate(zip(agents, responses)):
                st.markdown(f"**{agent[1]}**")
                st.info(resp)
    
    # DEEP
    elif deep:
        st.warning("🟠 Modalità DEEP")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista", "Dettagli tecnici."),
            ("llama-3.1-70b-versatile", "Stratega", "Visione strategica."),
            ("mixtral-8x7b-32768", "Pratico", "Applicazioni."),
            ("gemma-7b-it", "Critico", "Analisi critica."),
            ("qwen2-72b-instruct", "Globale", "Contesto globale.")
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role, goal) in enumerate(agents):
            st.text(f"⏳ {i+1}/5: {role}...")
            r = query_model(model, role, goal, domanda)
            responses.append(r)
            progress.progress((i+1)/6)
        
        st.text("🎯 Sintesi...")
        finale = synthesize(responses, domanda)
        progress.progress(1.0)
        
        st.markdown("### ✅ Risposta DEEP")
        st.markdown(finale)
        
        with st.expander("📊 5 Prospettive"):
            for i, (agent, resp) in enumerate(zip(agents, responses)):
                st.markdown(f"**{agent[1]}**")
                st.info(resp)
    
    # EXPERT
    elif expert:
        st.error("🔴 Modalità EXPERT")
        
        agents = [
            ("llama-3.1-8b-instant", "Analista", "Tecnico."),
            ("llama-3.1-70b-versatile", "Stratega", "Strategico."),
            ("llama-3.3-70b-versatile", "Innovatore", "Creativo."),
            ("mixtral-8x7b-32768", "Pratico", "Operativo."),
            ("gemma-7b-it", "Critico", "Rischi."),
            ("gemma2-9b-it", "Verificatore", "Facts."),
            ("qwen2-72b-instruct", "Globale", "Internazionale.")
        ]
        
        responses = []
        progress = st.progress(0)
        
        for i, (model, role, goal) in enumerate(agents):
            st.text(f"⏳ {i+1}/7: {role}...")
            r = query_model(model, role, goal, domanda)
            responses.append(r)
            progress.progress((i+1)/8)
        
        st.text("🎯 Super-sintesi...")
        finale = synthesize(responses, domanda)
        progress.progress(1.0)
        
        st.markdown("### 🏆 Risposta EXPERT")
        st.markdown(finale)
        
        with st.expander("📊 7 Prospettive"):
            for i, (agent, resp) in enumerate(zip(agents, responses)):
                st.markdown(f"**{agent[1]}**")
                st.info(resp)

st.markdown("---")
st.markdown("**Multi-AI System** | Powered by Groq")
