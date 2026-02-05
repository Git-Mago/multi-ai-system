import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import os
from datetime import datetime

st.set_page_config(
    page_title="Multi-AI Agent - Modalità Multiple",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .mode-card {
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .mode-quick { border-color: #22c55e; background: #dcfce7; }
    .mode-standard { border-color: #eab308; background: #fef9c3; }
    .mode-deep { border-color: #f97316; background: #ffedd5; }
    .mode-expert { border-color: #ef4444; background: #fee2e2; }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Ottieni la tua chiave gratuita su console.groq.com"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Modalità Disponibili")
    st.markdown("""
    🟢 **QUICK** (1 modello)  
    ⏱️ 5-10 secondi  
    💡 Domande semplici
    
    🟡 **STANDARD** (3 modelli)  
    ⏱️ 20-30 secondi  
    💡 Uso normale
    
    🟠 **DEEP** (5 modelli)  
    ⏱️ 40-60 secondi  
    💡 Analisi complessa
    
    🔴 **EXPERT** (7 modelli)  
    ⏱️ 60-120 secondi  
    💡 Decisioni critiche
    """)
    
    st.markdown("---")
    
    st.markdown("### 💰 Costi")
    st.success("**Completamente Gratis!**\n\nGroq: 14,400 richieste/giorno")

# Main content
st.markdown("""
<div class="main-header">
    <h1>🤖 Multi-AI Agent System</h1>
    <p>Sistema Intelligente con 4 Modalità di Analisi</p>
</div>
""", unsafe_allow_html=True)

# Check API key
if not groq_api_key:
    st.warning("👈 **Inserisci la tua Groq API key nella sidebar per iniziare**")
    
    st.info("""
    ### 🚀 Come Funziona
    
    Questo sistema consulta **multipli modelli AI** in base alla complessità della tua domanda:
    
    - 🟢 **QUICK**: 1 modello potente per risposte rapide
    - 🟡 **STANDARD**: 3 modelli diversi per risposte bilanciate  
    - 🟠 **DEEP**: 5 modelli per analisi approfondita
    - 🔴 **EXPERT**: 7 modelli per massima qualità
    
    ### 💡 Vantaggi Multi-Agent
    
    ✅ Prospettive diverse e complementari  
    ✅ Maggiore accuratezza e affidabilità  
    ✅ Riduzione bias di singoli modelli  
    ✅ Sintesi intelligente finale
    """)
    st.stop()

os.environ["GROQ_API_KEY"] = groq_api_key

# Function to analyze question complexity
def analizza_complessita(domanda):
    """Analizza la domanda e suggerisce la modalità ottimale"""
    parole = len(domanda.split())
    domande_count = domanda.count('?')
    
    # Keywords
    keywords_simple = ['cos è', 'cos\'è', 'quando', 'dove', 'chi è', 'chi e', 'definisci', 'significa']
    keywords_complex = ['dovrei', 'strategia', 'analizza', 'confronta', 'valuta', 'pro e contro', 'pros cons', 'differenza']
    keywords_expert = ['decisione', 'investimento', 'importante', 'critico', 'business', 'contratto', 'legale', 'acquisizione']
    
    domanda_lower = domanda.lower()
    
    # Calcola score
    score = 0
    
    if parole < 10:
        score += 0
    elif parole < 30:
        score += 1
    elif parole < 50:
        score += 2
    else:
        score += 3
    
    if domande_count > 1:
        score += 1
    
    if any(kw in domanda_lower for kw in keywords_simple):
        score -= 1
    if any(kw in domanda_lower for kw in keywords_complex):
        score += 2
    if any(kw in domanda_lower for kw in keywords_expert):
        score += 3
    
    # Determina modalità
    if score <= 0:
        return "quick", "🟢 Domanda semplice rilevata"
    elif score <= 2:
        return "standard", "🟡 Domanda standard rilevata"
    elif score <= 4:
        return "deep", "🟠 Domanda complessa rilevata"
    else:
        return "expert", "🔴 Domanda critica rilevata"

# User input
st.markdown("### 💭 Fai la tua domanda")
domanda = st.text_area(
    "",
    height=120,
    placeholder="Esempio: Dovrei cambiare lavoro o restare nella mia azienda attuale? Ho 35 anni, famiglia, e un buon stipendio ma poche prospettive di crescita...",
    help="Scrivi una domanda. Il sistema analizzerà automaticamente la complessità e suggerirà la modalità ottimale."
)

if domanda.strip():
    
    # Analisi automatica
    modalita_suggerita, motivo = analizza_complessita(domanda)
    
    st.info(f"**💡 Suggerimento automatico:** {motivo}")
    
    # Selezione modalità
    st.markdown("### ⚙️ Seleziona Modalità")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quick_btn = st.button("🟢 QUICK", help="1 modello • 5-10 sec", use_container_width=True)
    with col2:
        standard_btn = st.button("🟡 STANDARD", help="3 modelli • 20-30 sec", use_container_width=True)
    with col3:
        deep_btn = st.button("🟠 DEEP", help="5 modelli • 40-60 sec", use_container_width=True)
    with col4:
        expert_btn = st.button("🔴 EXPERT", help="7 modelli • 1-2 min", use_container_width=True)
    
    # Determina modalità
    if quick_btn:
        modalita = "quick"
    elif standard_btn:
        modalita = "standard"
    elif deep_btn:
        modalita = "deep"
    elif expert_btn:
        modalita = "expert"
    else:
        modalita = None
    
    # Procedi solo se modalità selezionata
    if modalita:
        
        start_time = datetime.now()
        
        # ========== QUICK MODE ==========
        if modalita == "quick":
            st.success("🟢 **Modalità QUICK**: 1 modello (Llama 3.1 70B)")
            st.caption("Risposta rapida e diretta da un modello potente")
            
            try:
                llama_70b = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7)
                
                agent = Agent(
                    role="Esperto Generalista",
                    goal="Fornisci risposta completa, chiara e diretta",
                    backstory="Sei un esperto versatile con vasta conoscenza",
                    llm=llama_70b,
                    verbose=False
                )
                
                task = Task(
                    description=domanda,
                    agent=agent,
                    expected_output="Risposta completa e diretta"
                )
                
                with st.spinner("⏳ Elaborazione in corso..."):
                    crew = Crew(agents=[agent], tasks=[task], verbose=False)
                    risultato = crew.kickoff()
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                st.markdown("---")
                st.success(f"### ✅ Risposta (in {elapsed:.1f} secondi)")
                st.markdown(risultato.raw)
                
                st.caption("💰 Costo: $0.00 • Modello: Llama 3.1 70B")
                
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")
        
        # ========== STANDARD MODE ==========
        elif modalita == "standard":
            st.success("🟡 **Modalità STANDARD**: 3 modelli AI")
            st.caption("Analisi bilanciata da 3 prospettive diverse")
            
            try:
                # Initialize models
                llama = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
                mixtral = ChatGroq(model="mixtral-8x7b-32768", temperature=0.7)
                gemma = ChatGroq(model="gemma-7b-it", temperature=0.7)
                
                # Create agents
                agents = [
                    Agent(role="Analista Tecnico", goal="Fornisci analisi dettagliata e precisa", backstory="Esperto analitico", llm=llama, verbose=False),
                    Agent(role="Esperto Pratico", goal="Fornisci esempi concreti e applicabili", backstory="Professionista sul campo", llm=mixtral, verbose=False),
                    Agent(role="Pensatore Critico", goal="Analizza criticamente e offri prospettive alternative", backstory="Devil's advocate", llm=gemma, verbose=False)
                ]
                
                # Create tasks
                tasks = [Task(description=domanda, agent=agent, expected_output="Risposta specializzata") for agent in agents]
                
                with st.spinner("⏳ 3 agenti stanno lavorando..."):
                    crew1 = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
                    crew1.kickoff()
                
                # Synthesis
                agent_synth = Agent(
                    role="Sintetizzatore",
                    goal="Combina le 3 prospettive in una sintesi coerente",
                    backstory="Esperto in sintesi multi-prospettica",
                    llm=llama,
                    verbose=False
                )
                
                sintesi_prompt = f"Sintetizza queste 3 analisi sulla domanda '{domanda}':\n\n"
                sintesi_prompt += f"Analisi 1 (Tecnica): {tasks[0].output.raw}\n\n"
                sintesi_prompt += f"Analisi 2 (Pratica): {tasks[1].output.raw}\n\n"
                sintesi_prompt += f"Analisi 3 (Critica): {tasks[2].output.raw}\n\n"
                
                task_synth = Task(description=sintesi_prompt, agent=agent_synth, expected_output="Sintesi finale")
                
                with st.spinner("🎯 Sintetizzazione finale..."):
                    crew2 = Crew(agents=[agent_synth], tasks=[task_synth], verbose=False)
                    risultato_finale = crew2.kickoff()
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                st.markdown("---")
                st.success(f"### ✅ Risposta Finale Sintetizzata (in {elapsed:.1f} secondi)")
                st.markdown(risultato_finale.raw)
                
                # Show individual responses
                with st.expander("📖 Mostra risposte individuali"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**🔵 Analista Tecnico**")
                        st.info(tasks[0].output.raw)
                    with col2:
                        st.markdown("**🟠 Esperto Pratico**")
                        st.warning(tasks[1].output.raw)
                    with col3:
                        st.markdown("**🟢 Pensatore Critico**")
                        st.success(tasks[2].output.raw)
                
                st.caption("💰 Costo: $0.00 • Modelli: Llama 8B, Mixtral 8x7B, Gemma 7B")
                
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")
        
        # ========== DEEP MODE ==========
        elif modalita == "deep":
            st.warning("🟠 **Modalità DEEP**: 5 modelli AI")
            st.caption("Analisi approfondita multi-prospettica (40-60 secondi)")
            
            try:
                # Initialize 5 models
                models = {
                    "Llama 8B": ChatGroq(model="llama-3.1-8b-instant", temperature=0.7),
                    "Llama 70B": ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7),
                    "Mixtral": ChatGroq(model="mixtral-8x7b-32768", temperature=0.7),
                    "Gemma": ChatGroq(model="gemma-7b-it", temperature=0.7),
                    "Qwen": ChatGroq(model="qwen2-72b-instruct", temperature=0.7)
                }
                
                agents = [
                    Agent(role="Analista Tecnico", goal="Dettagli tecnici", llm=models["Llama 8B"], verbose=False),
                    Agent(role="Stratega", goal="Visione strategica", llm=models["Llama 70B"], verbose=False),
                    Agent(role="Esperto Pratico", goal="Applicazioni concrete", llm=models["Mixtral"], verbose=False),
                    Agent(role="Pensatore Critico", goal="Analisi critica", llm=models["Gemma"], verbose=False),
                    Agent(role="Prospettiva Globale", goal="Contesto internazionale", llm=models["Qwen"], verbose=False)
                ]
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                tasks = []
                for i, agent in enumerate(agents):
                    status_text.text(f"⏳ Agente {i+1}/5: {agent.role}...")
                    progress_bar.progress((i + 1) / 6)
                    
                    task = Task(description=domanda, agent=agent, expected_output="Risposta specializzata")
                    tasks.append(task)
                    
                    mini_crew = Crew(agents=[agent], tasks=[task], verbose=False)
                    mini_crew.kickoff()
                
                # Synthesis
                status_text.text("🎯 Sintetizzazione finale...")
                progress_bar.progress(5/6)
                
                agent_synth = Agent(
                    role="Master Sintetizzatore",
                    goal="Sintesi definitiva da 5 prospettive",
                    llm=models["Llama 70B"],
                    verbose=False
                )
                
                sintesi_prompt = f"Sintetizza queste 5 analisi:\n\n"
                for i, task in enumerate(tasks):
                    sintesi_prompt += f"{agents[i].role}: {task.output.raw}\n\n"
                
                task_synth = Task(description=sintesi_prompt, agent=agent_synth, expected_output="Sintesi")
                crew_synth = Crew(agents=[agent_synth], tasks=[task_synth], verbose=False)
                risultato_finale = crew_synth.kickoff()
                
                progress_bar.progress(1.0)
                status_text.text("✅ Completato!")
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                st.markdown("---")
                st.success(f"### ✅ Risposta DEEP (in {elapsed:.1f} secondi)")
                st.markdown(risultato_finale.raw)
                
                with st.expander("📊 Vedi tutte le 5 prospettive"):
                    for i, (agent, task) in enumerate(zip(agents, tasks)):
                        st.markdown(f"**{i+1}. {agent.role}**")
                        st.info(task.output.raw)
                        st.markdown("---")
                
                st.caption("💰 Costo: $0.00 • 5 modelli consultati")
                
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")
        
        # ========== EXPERT MODE ==========
        elif modalita == "expert":
            st.error("🔴 **Modalità EXPERT**: 7 modelli AI")
            st.caption("Massima qualità e profondità (60-120 secondi)")
            
            try:
                # All 7 models
                models = {
                    "Llama 8B": ChatGroq(model="llama-3.1-8b-instant", temperature=0.7),
                    "Llama 70B": ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7),
                    "Llama 3.3": ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7),
                    "Mixtral": ChatGroq(model="mixtral-8x7b-32768", temperature=0.7),
                    "Gemma": ChatGroq(model="gemma-7b-it", temperature=0.7),
                    "Gemma 2": ChatGroq(model="gemma2-9b-it", temperature=0.7),
                    "Qwen": ChatGroq(model="qwen2-72b-instruct", temperature=0.7)
                }
                
                agents = [
                    Agent(role="Analista Tecnico", goal="Profondità tecnica", llm=models["Llama 8B"], verbose=False),
                    Agent(role="Stratega Senior", goal="Visione long-term", llm=models["Llama 70B"], verbose=False),
                    Agent(role="Innovatore", goal="Soluzioni creative", llm=models["Llama 3.3"], verbose=False),
                    Agent(role="Esperto Pratico", goal="Implementazione", llm=models["Mixtral"], verbose=False),
                    Agent(role="Critico Costruttivo", goal="Identificare rischi", llm=models["Gemma"], verbose=False),
                    Agent(role="Verificatore", goal="Fact-checking", llm=models["Gemma 2"], verbose=False),
                    Agent(role="Prospettiva Globale", goal="Contesto geopolitico", llm=models["Qwen"], verbose=False)
                ]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                tasks = []
                for i, agent in enumerate(agents):
                    status_text.text(f"⏳ Agente {i+1}/7: {agent.role}...")
                    progress_bar.progress((i + 1) / 8)
                    
                    task = Task(description=domanda, agent=agent, expected_output="Risposta")
                    tasks.append(task)
                    
                    mini_crew = Crew(agents=[agent], tasks=[task], verbose=False)
                    mini_crew.kickoff()
                
                status_text.text("🎯 Super-sintesi finale...")
                progress_bar.progress(7/8)
                
                agent_master = Agent(
                    role="Master Sintetizzatore",
                    goal="Sintesi definitiva da 7 prospettive",
                    llm=models["Llama 70B"],
                    verbose=False
                )
                
                master_prompt = f"Crea sintesi definitiva da 7 analisi:\n\n"
                for i, task in enumerate(tasks):
                    master_prompt += f"{agents[i].role}: {task.output.raw}\n\n"
                
                task_master = Task(description=master_prompt, agent=agent_master, expected_output="Sintesi")
                crew_master = Crew(agents=[agent_master], tasks=[task_master], verbose=False)
                risultato_finale = crew_master.kickoff()
                
                progress_bar.progress(1.0)
                status_text.text("✅ Analisi EXPERT completata!")
                
                elapsed = (datetime.now() - start_time).total_seconds()
                
                st.markdown("---")
                st.success(f"### 🏆 Risposta EXPERT (in {elapsed:.1f} secondi)")
                st.markdown(risultato_finale.raw)
                
                st.markdown("### 📊 Breakdown delle 7 Prospettive")
                for i, (agent, task) in enumerate(zip(agents, tasks)):
                    with st.expander(f"{i+1}. {agent.role} - {agent.goal}"):
                        st.info(task.output.raw)
                
                st.caption("💰 Costo: $0.00 • 7 modelli premium consultati")
                
            except Exception as e:
                st.error(f"❌ Errore: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Multi-AI Agent System</strong> | Powered by Groq API</p>
    <p>Stack: Llama 3.1 • Mixtral • Gemma • Qwen | Completamente Gratis</p>
</div>
""", unsafe_allow_html=True)
