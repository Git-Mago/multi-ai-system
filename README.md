# 🤖 Multi-AI Agent Cloud

Sistema di orchestrazione multi-agente che interroga 3 modelli AI diversi in parallelo e sintetizza le risposte in un'unica risposta completa e bilanciata.

## 🌟 Caratteristiche

- **3 Agenti AI Specializzati**:
  - 🔵 Llama 3.1 8B - Analista Tecnico
  - 🟠 Mixtral 8x7B - Esperto Pratico
  - 🟢 Gemma 7B - Pensatore Critico
  
- **Agente Sintetizzatore**: Combina le 3 risposte in una sintesi finale

- **100% Gratuito**: Usa il free tier di Groq API (14,400 richieste/giorno)

- **Interfaccia Web**: Accessibile da qualsiasi dispositivo (PC, smartphone, tablet)

## 💰 Costi

- **Groq API**: FREE (14,400 richieste/giorno)
- **Hosting Render**: FREE (750 ore/mese)
- **Totale**: $0/mese per uso personale

## 🚀 Deploy su Render (5 minuti)

### Step 1: Ottieni la Groq API Key

1. Vai su [console.groq.com](https://console.groq.com)
2. Crea un account gratuito
3. Vai su "API Keys" nel menu laterale
4. Clicca "Create API Key"
5. Copia la chiave (la userai nell'app)

### Step 2: Carica il progetto su GitHub

```bash
# Clona o scarica questo progetto
# Crea un nuovo repository su GitHub
# Carica i file:

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TUO-USERNAME/multi-ai-cloud.git
git push -u origin main
```

### Step 3: Deploy su Render

1. Vai su [render.com](https://render.com) e crea un account (gratis)
2. Clicca "New +" → "Web Service"
3. Connetti il tuo repository GitHub
4. Configura il servizio:
   - **Name**: `multi-ai-agent` (o quello che preferisci)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Instance Type**: `Free`
5. Clicca "Create Web Service"
6. Attendi 2-3 minuti per il deploy

### Step 4: Usa l'app!

1. Render ti fornirà un URL tipo: `https://multi-ai-agent-xxxxx.onrender.com`
2. Apri l'URL nel browser
3. Inserisci la tua Groq API key nella sidebar
4. Inizia a fare domande! 🎉

## 📱 Accesso da Smartphone

L'app è completamente responsive - salvati il link Render nei preferiti del tuo smartphone e usalo come una normale app web!

## 🛠️ Test in Locale (Opzionale)

Se vuoi testare l'app sul tuo computer prima del deploy:

```bash
# Installa le dipendenze
pip install -r requirements.txt

# Esegui l'app
streamlit run app.py

# Apri il browser su http://localhost:8501
```

## ⚙️ Come Funziona

1. **Inserisci una domanda** - Qualsiasi argomento tu voglia esplorare
2. **3 agenti AI diversi** analizzano la domanda da prospettive differenti
3. **Un quarto agente sintetizzatore** combina le 3 risposte
4. **Ricevi una risposta completa** che incorpora molteplici punti di vista

### Vantaggi del Multi-Agent Approach

- ✅ Risposte più complete e sfaccettate
- ✅ Riduzione dei bias di un singolo modello
- ✅ Maggiore affidabilità e accuratezza
- ✅ Copertura di diversi aspetti della domanda

## 📊 Performance

**Velocità (con Groq API):**
- Risposta singola agente: 2-5 secondi
- 3 agenti in sequenza: 10-20 secondi
- Sintesi finale: 3-5 secondi
- **Totale: ~15-30 secondi**

**Limiti Free Tier:**
- 14,400 richieste al giorno
- ~6,000 token per richiesta
- Completamente sufficiente per uso personale

## 🔧 Troubleshooting

**Problema: "Error initializing models"**
- Soluzione: Verifica che la tua Groq API key sia corretta

**Problema: "Service sleeping" su Render**
- Normale: il free tier dorme dopo 15 minuti di inattività
- Soluzione: Basta ricaricare la pagina, si riattiva in ~30 secondi

**Problema: Render supera 750 ore/mese**
- Improbabile per uso personale
- Soluzione: Upgrade a $7/mese per servizio always-on

## 📚 Struttura del Progetto

```
multi-ai-cloud/
├── app.py              # App Streamlit principale
├── requirements.txt    # Dipendenze Python
└── README.md          # Questa guida
```

## 🎯 Alternative / Espansioni Future

- Aggiungere più modelli AI (es. Claude, GPT-4)
- Implementare memoria conversazionale
- Aggiungere supporto per file upload
- Creare API REST per integrazioni

## 📄 Licenza

Progetto open source - usa liberamente!

## 🙏 Credits

- **Groq**: API ultra-veloce per LLM
- **CrewAI**: Framework per multi-agent orchestration
- **Streamlit**: Framework per web app Python
- **Render**: Hosting cloud gratuito

---

**Enjoy! 🚀**

Per domande o supporto, apri una issue su GitHub.
