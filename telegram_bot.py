import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
APP_URL = os.getenv('APP_URL', '')
PORT = int(os.getenv('PORT', 8080))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

# Groq API helper
def query_groq(model, system_msg, user_msg):
    """Query Groq API"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
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
        logger.error(f"Groq API error: {e}")
        return f"Errore API: {str(e)}"

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    welcome = """
🤖 *Benvenuto nel Multi-AI Agent Bot!*

Consulto 3 modelli AI per darti risposte complete.

*Comandi:*
/start - Questo messaggio
/help - Guida
/quick [domanda] - 1 modello (veloce)
/standard [domanda] - 3 modelli (default)

*Esempio:*
`Quali sono i benefici della meditazione?`

Inizia facendo una domanda! 🚀
    """
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📚 *Guida Rapida*

*Modalità disponibili:*
🟢 QUICK - 1 modello (10 sec)
🟡 STANDARD - 3 modelli (30 sec)

*Come usare:*
1. Scrivi semplicemente la tua domanda
2. Il bot usa automaticamente modalità STANDARD
3. Per QUICK: /quick [domanda]

*Esempi:*
`Pro e contro del lavoro remoto?`
`/quick Cos'è Bitcoin?`

⏱️ Tempo medio: 20-30 secondi
💰 Costo: $0 (gratis)
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick mode command"""
    if not context.args:
        await update.message.reply_text("Uso: /quick [domanda]\nEsempio: /quick Cos'è l'AI?")
        return
    
    domanda = " ".join(context.args)
    
    await update.message.reply_text("🟢 *Modalità QUICK*\n⏳ Elaborazione...", parse_mode='Markdown')
    
    risposta = query_groq(
        "llama-3.3-70b-versatile",
        "Sei un esperto. Rispondi in modo completo e chiaro.",
        domanda
    )
    
    await update.message.reply_text(f"✅ *Risposta:*\n\n{risposta}\n\n💰 Costo: $0.00", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (STANDARD mode)"""
    domanda = update.message.text
    
    thinking_msg = await update.message.reply_text(
        "🟡 *Modalità STANDARD*\n⏳ 3 agenti stanno analizzando...\n\n_Attendi 20-30 secondi_",
        parse_mode='Markdown'
    )
    
    try:
        # Query 3 models
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico"),
            ("mixtral-8x7b-32768", "Esperto Pratico"),
            ("gemma-7b-it", "Pensatore Critico")
        ]
        
        responses = []
        for model, role in agents:
            r = query_groq(model, f"Sei un {role}.", domanda)
            responses.append(f"{role}: {r}")
        
        # Synthesize
        synthesis_prompt = "Sintetizza:\n\n" + "\n\n".join(responses)
        finale = query_groq(
            "llama-3.3-70b-versatile",
            "Crea sintesi coerente.",
            synthesis_prompt
        )
        
        # Delete thinking message
        await thinking_msg.delete()
        
        # Send final response
        response_text = f"✅ *Risposta Sintetizzata:*\n\n{finale}\n\n📊 3 modelli consultati\n💰 Costo: $0.00"
        
        # Telegram max 4096 chars
        if len(response_text) > 4000:
            parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(response_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(
            f"❌ Errore durante elaborazione:\n{str(e)}",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start bot with webhook"""
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quick", quick_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start webhook
    logger.info(f"Starting webhook on port {PORT}")
    
    # Run webhook (Render provides the URL)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://multi-ai-telegram-bot.onrender.com/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
