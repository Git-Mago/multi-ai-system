import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
APP_URL = os.getenv('APP_URL', 'http://localhost:8501')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_message = """
🤖 *Benvenuto nel Multi-AI Agent Bot!*

Sono il tuo assistente AI che consulta 3 modelli diversi per darti risposte complete e bilanciate.

*Come funziono:*
• Scrivi una domanda
• 3 agenti AI la analizzano da prospettive diverse
• Ricevi una sintesi completa

*Puoi anche:*
📸 Inviarmi foto per analisi AI
🎤 Mandarmi messaggi vocali (convertiti in testo)
💬 Fare domande su qualsiasi argomento

*Comandi disponibili:*
/start - Mostra questo messaggio
/help - Guida rapida
/stats - Statistiche utilizzo (presto)

Inizia facendomi una domanda! 🚀
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    help_text = """
📚 *Guida Rapida*

*Fare domande:*
Scrivi semplicemente la tua domanda come in una chat normale.

*Esempi di buone domande:*
• "Quali sono i pro e contro del lavoro remoto?"
• "Spiegami la blockchain in termini semplici"
• "Come posso migliorare la mia produttività?"
• "Confronta Python e JavaScript"

*Foto:*
Inviami una foto e scrivi cosa vuoi sapere.
Esempio: [foto] + "Analizza questo prodotto"

*Messaggi vocali:*
Tieni premuto il microfono e parla.
Telegram converte automaticamente in testo.

⏱️ Tempo medio risposta: 20-40 secondi
🤖 Modelli usati: Llama 3.1, Mixtral, Gemma
💰 Costo: $0 (completamente gratis)

Domande? Scrivimi qualcosa! 😊
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Handle text messages
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user text messages and query the AI system."""
    user_question = update.message.text
    user_name = update.effective_user.first_name
    
    # Send acknowledgment
    thinking_msg = await update.message.reply_text(
        "⏳ *3 agenti AI stanno analizzando la tua domanda...*\n\n"
        "Questo richiederà circa 20-40 secondi.",
        parse_mode='Markdown'
    )
    
    try:
        # Call the main app API endpoint
        # Note: This assumes you've added an API endpoint to app.py
        # For now, we'll simulate calling Groq directly
        
        from langchain_groq import ChatGroq
        from crewai import Agent, Task, Crew, Process
        
        # Configure models
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY
        
        llama = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
        mixtral = ChatGroq(model="mixtral-8x7b-32768", temperature=0.7)
        gemma = ChatGroq(model="gemma-7b-it", temperature=0.7)
        
        # Create agents
        agent_llama = Agent(
            role="Analista Tecnico",
            goal="Fornisci una risposta dettagliata e tecnicamente accurata",
            backstory="Sei un esperto analitico con anni di esperienza nella ricerca approfondita",
            llm=llama,
            verbose=False
        )
        
        agent_mixtral = Agent(
            role="Esperto Pratico",
            goal="Fornisci esempi concreti e applicazioni pratiche",
            backstory="Sei un professionista con vasta esperienza sul campo",
            llm=mixtral,
            verbose=False
        )
        
        agent_gemma = Agent(
            role="Pensatore Critico",
            goal="Analizza criticamente e offri prospettive alternative",
            backstory="Sei un esperto nel pensiero critico e nell'analisi multi-prospettiva",
            llm=gemma,
            verbose=False
        )
        
        agent_synth = Agent(
            role="Sintetizzatore",
            goal="Combina le risposte in una sintesi completa e bilanciata",
            backstory="Sei un esperto nel sintetizzare informazioni complesse",
            llm=llama,
            verbose=False
        )
        
        # Create tasks
        task1 = Task(
            description=user_question,
            agent=agent_llama,
            expected_output="Risposta tecnica dettagliata"
        )
        
        task2 = Task(
            description=user_question,
            agent=agent_mixtral,
            expected_output="Risposta pratica con esempi"
        )
        
        task3 = Task(
            description=user_question,
            agent=agent_gemma,
            expected_output="Risposta critica con prospettive alternative"
        )
        
        # Execute first crew
        crew1 = Crew(
            agents=[agent_llama, agent_mixtral, agent_gemma],
            tasks=[task1, task2, task3],
            process=Process.sequential,
            verbose=False
        )
        
        risultati = crew1.kickoff()
        
        # Synthesis task
        task_synth = Task(
            description=f"""Sintetizza queste tre risposte in una risposta finale completa e bilanciata:

Risposta Tecnica: {task1.output.raw}

Risposta Pratica: {task2.output.raw}

Risposta Critica: {task3.output.raw}

Crea una sintesi che integri i punti di forza di tutte e tre le prospettive.""",
            agent=agent_synth,
            expected_output="Sintesi finale completa"
        )
        
        crew2 = Crew(
            agents=[agent_synth],
            tasks=[task_synth],
            verbose=False
        )
        
        risultato_finale = crew2.kickoff()
        
        # Delete thinking message
        await thinking_msg.delete()
        
        # Send final response
        response_text = f"""✅ *Risposta Sintetizzata da 3 AI:*

{risultato_finale.raw}

---
📊 *Dettagli:*
🔵 Analista Tecnico: Analisi approfondita
🟠 Esperto Pratico: Esempi concreti
🟢 Pensatore Critico: Prospettive alternative

⏱️ Tempo elaborazione: ~{datetime.now().strftime('%H:%M')}
💰 Costo: $0.00 (free tier)
        """
        
        # Telegram message limit is 4096 characters
        if len(response_text) > 4000:
            # Split into multiple messages
            parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(response_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(
            "❌ *Errore durante l'elaborazione*\n\n"
            f"Si è verificato un problema: {str(e)}\n\n"
            "Riprova tra qualche secondo o contatta il supporto se il problema persiste.",
            parse_mode='Markdown'
        )

# Handle voice messages
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages by informing user to use Telegram's voice-to-text."""
    await update.message.reply_text(
        "🎤 *Messaggio Vocale Ricevuto*\n\n"
        "💡 Consiglio: Usa la funzione di Telegram per convertire il vocale in testo "
        "(tieni premuto sul vocale → 'Trascrivi') e poi inviami il testo.\n\n"
        "Questo mi permette di elaborare la tua richiesta più accuratamente!",
        parse_mode='Markdown'
    )

# Handle photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages - for future Vision API integration."""
    await update.message.reply_text(
        "📸 *Foto Ricevuta*\n\n"
        "L'analisi di immagini sarà disponibile a breve!\n\n"
        "Per ora, puoi:\n"
        "• Descrivermi cosa vedi nella foto\n"
        "• Farmi domande su cosa ti interessa sapere\n\n"
        "Lavorerò con le informazioni testuali che mi dai! 😊",
        parse_mode='Markdown'
    )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
