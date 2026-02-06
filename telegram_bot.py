import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import signal
import sys
from flask import Flask
import threading

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PORT = int(os.getenv('PORT', 10000))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

# Flask app for health check (required by Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "active"}

def run_flask():
    """Run Flask in background thread"""
    app.run(host='0.0.0.0', port=PORT)

# Global application reference
application = None

def signal_handler(signum, frame):
    """Handle shutdown gracefully"""
    logger.info("Shutdown signal received")
    if application:
        application.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

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
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"Errore API: {str(e)}"

def split_message(text, max_length=4000):
    """Split long messages"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    
    return parts

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    welcome = """
🤖 *Multi-AI Agent Bot - Tutte le Modalità*

Consulto da 1 a 6 modelli AI in base alla complessità!

*🎯 Comandi Disponibili:*

🟢 `/quick [domanda]` - 1 modello (10s)
   Esempio: `/quick Cos'è Bitcoin?`

🟡 `/standard [domanda]` - 3 modelli (30s)
   Esempio: `/standard Pro e contro lavoro remoto?`

🟠 `/deep [domanda]` - 5 modelli (60s)
   Esempio: `/deep Dovrei cambiare carriera?`

🔴 `/expert [domanda]` - 6 modelli (120s)
   Esempio: `/expert Analizza investimento startup`

*Oppure scrivi direttamente* (usa STANDARD)

/help - Guida dettagliata
    """
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📚 *Guida Completa Multi-AI Bot*

*🟢 QUICK (10 secondi)*
Un solo modello potente per risposte rapide
Usa per: definizioni, fatti veloci
Comando: `/quick [domanda]`

*🟡 STANDARD (30 secondi)*
3 modelli diversi + sintesi
Usa per: domande normali, confronti
Comando: `/standard [domanda]` o scrivi direttamente

*🟠 DEEP (60 secondi)*
5 modelli specializzati + sintesi avanzata
Usa per: analisi complesse, decisioni importanti
Comando: `/deep [domanda]`

*🔴 EXPERT (120 secondi)*
6 modelli premium + super-sintesi
Usa per: decisioni critiche, massima accuratezza
Comando: `/expert [domanda]`

*💡 Esempi:*
`/quick Definizione di blockchain`
`/standard Vantaggi intelligenza artificiale`
`/deep Dovrei accettare offerta lavoro all'estero?`
`/expert Valuta acquisizione azienda 2M€`

⏱️ Tempi: Quick 10s | Standard 30s | Deep 60s | Expert 2min
💰 Costo: Sempre $0 (gratis)
🤖 Modelli: Llama 3.3, OpenAI GPT-OSS, Qwen 3
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== QUICK MODE ==========
async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick mode - 1 model"""
    if not context.args:
        await update.message.reply_text(
            "🟢 *Modalità QUICK*\n\nUso: `/quick [domanda]`\nEsempio: `/quick Cos'è l'AI?`",
            parse_mode='Markdown'
        )
        return
    
    domanda = " ".join(context.args)
    
    msg = await update.message.reply_text(
        "🟢 *Modalità QUICK*\n⏳ 1 modello al lavoro...\n\n_~10 secondi_",
        parse_mode='Markdown'
    )
    
    try:
        risposta = query_groq(
            "llama-3.3-70b-versatile",
            "Sei un esperto generalista. Fornisci risposta completa e chiara.",
            domanda
        )
        
        await msg.delete()
        
        final_msg = f"🟢 *QUICK - Risposta:*\n\n{risposta}\n\n💰 1 modello"
        
        for part in split_message(final_msg):
            await update.message.reply_text(part, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Quick error: {e}")
        await msg.delete()
        await update.message.reply_text(f"❌ Errore: {str(e)}")

# ========== STANDARD MODE ==========
async def standard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standard mode - 3 models"""
    if not context.args:
        await update.message.reply_text(
            "🟡 *Modalità STANDARD*\n\nUso: `/standard [domanda]`\nEsempio: `/standard Pro e contro Bitcoin?`",
            parse_mode='Markdown'
        )
        return
    
    domanda = " ".join(context.args)
    
    msg = await update.message.reply_text(
        "🟡 *Modalità STANDARD*\n⏳ 3 agenti stanno analizzando...\n\n_~30 secondi_",
        parse_mode='Markdown'
    )
    
    try:
        agents = [
            ("llama-3.1-8b-instant", "Analista Tecnico", "Analisi dettagliata"),
            ("openai/gpt-oss-20b", "Esperto Pratico", "Esempi concreti e soluzioni pratiche"),
            ("qwen/qwen3-32b", "Pensatore Critico", "Analisi critica e prospettive alternative")
        ]
        
        responses = []
        for model, role, goal in agents:
            r = query_groq(model, f"Sei un {role}. {goal}.", domanda)
            responses.append((role, r))
        
        # Synthesis
        synthesis_prompt = "Sintetizza queste 3 analisi:\n\n"
        for role, resp in responses:
            synthesis_prompt += f"{role}: {resp}\n\n"
        
        finale = query_groq(
            "llama-3.3-70b-versatile",
            "Sintetizza le analisi in una risposta coerente e completa.",
            synthesis_prompt
        )
        
        await msg.delete()
        
        final_msg = f"🟡 *STANDARD - Risposta Sintetizzata:*\n\n{finale}\n\n"
        final_msg += "📊 *Dettagli:* 3 modelli consultati"
        
        for part in split_message(final_msg):
            await update.message.reply_text(part, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Standard error: {e}")
        await msg.delete()
        await update.message.reply_text(f"❌ Errore: {str(e)}")

# ========== DEEP MODE ==========
async def deep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deep mode - 5 models"""
    if not context.args:
        await update.message.reply_text(
            "🟠 *Modalità DEEP*\n\nUso: `/deep [domanda]`\nEsempio: `/deep Dovrei cambiare lavoro?`",
            parse_mode='Markdown'
        )
        return
    
    domanda = " ".join(context.args)
    
    msg = await update.message.reply_text(
        "🟠 *Modalità DEEP*\n⏳ 5 agenti esperti stanno analizzando...\n\n_~60 secondi - Attendi_",
        parse_mode='Markdown'
    )
    
    try:
        agents = [
            ("llama-3.1-8b-instant", "Analista Veloce"),
            ("llama-3.3-70b-versatile", "Stratega"),
            ("openai/gpt-oss-20b", "Esperto Pratico"),
            ("qwen/qwen3-32b", "Pensatore Alternativo"),
            ("meta-llama/llama-4-scout-17b-16e-instruct", "Verificatore Moderno")
        ]
        
        responses = []
        for i, (model, role) in enumerate(agents, 1):
            await msg.edit_text(
                f"🟠 *Modalità DEEP*\n⏳ Agente {i}/5: {role}...",
                parse_mode='Markdown'
            )
            r = query_groq(model, f"Sei un {role}.", domanda)
            responses.append((role, r))
        
        await msg.edit_text(
            "🟠 *Modalità DEEP*\n🎯 Sintetizzazione finale...",
            parse_mode='Markdown'
        )
        
        # Synthesis
        synthesis_prompt = "Crea sintesi definitiva da queste 5 analisi:\n\n"
        for role, resp in responses:
            synthesis_prompt += f"{role}: {resp}\n\n"
        
        finale = query_groq(
            "openai/gpt-oss-120b",
            "Crea sintesi completa e bilanciata da tutte le prospettive.",
            synthesis_prompt
        )
        
        await msg.delete()
        
        final_msg = f"🟠 *DEEP - Risposta da 5 Prospettive:*\n\n{finale}\n\n"
        final_msg += "📊 *5 modelli premium consultati*"
        
        for part in split_message(final_msg):
            await update.message.reply_text(part, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Deep error: {e}")
        await msg.delete()
        await update.message.reply_text(f"❌ Errore: {str(e)}")

# ========== EXPERT MODE ==========
async def expert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Expert mode - 6 models"""
    if not context.args:
        await update.message.reply_text(
            "🔴 *Modalità EXPERT*\n\nUso: `/expert [domanda]`\nEsempio: `/expert Analizza contratto acquisizione`",
            parse_mode='Markdown'
        )
        return
    
    domanda = " ".join(context.args)
    
    msg = await update.message.reply_text(
        "🔴 *Modalità EXPERT*\n⏳ 6 modelli premium stanno analizzando...\n\n_~2 minuti - Massima qualità_",
        parse_mode='Markdown'
    )
    
    try:
        agents = [
            ("llama-3.1-8b-instant", "Analista Veloce"),
            ("llama-3.3-70b-versatile", "Stratega Master"),
            ("openai/gpt-oss-120b", "Pensatore Profondo"),
            ("openai/gpt-oss-20b", "Esperto Pratico"),
            ("qwen/qwen3-32b", "Critico Costruttivo"),
            ("meta-llama/llama-guard-4-12b", "Verificatore Globale")
        ]
        
        responses = []
        for i, (model, role) in enumerate(agents, 1):
            await msg.edit_text(
                f"🔴 *Modalità EXPERT*\n⏳ Agente {i}/6: {role}...",
                parse_mode='Markdown'
            )
            r = query_groq(model, f"Sei un {role}.", domanda)
            responses.append((role, r))
        
        await msg.edit_text(
            "🔴 *Modalità EXPERT*\n🎯 Super-sintesi master in corso...",
            parse_mode='Markdown'
        )
        
        # Master synthesis
        synthesis_prompt = "Crea sintesi definitiva master da queste 6 analisi esperte:\n\n"
        for role, resp in responses:
            synthesis_prompt += f"{role}: {resp}\n\n"
        
        finale = query_groq(
            "openai/gpt-oss-120b",
            "Crea sintesi definitiva master integrando tutte le prospettive.",
            synthesis_prompt
        )
        
        await msg.delete()
        
        final_msg = f"🔴 *EXPERT - Risposta Master da 6 AI:*\n\n{finale}\n\n"
        final_msg += "📊 *6 modelli top-tier consultati*"
        
        for part in split_message(final_msg):
            await update.message.reply_text(part, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Expert error: {e}")
        await msg.delete()
        await update.message.reply_text(f"❌ Errore: {str(e)}")

# ========== DEFAULT MESSAGE HANDLER ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages - uses STANDARD mode by default"""
    domanda = update.message.text
    context.args = domanda.split()
    await standard_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Error: {context.error}")

def main():
    """Start bot"""
    global application
    
    logger.info("Starting Multi-AI Bot with Flask health check...")
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"Flask server started on port {PORT}")
    
    # Start Telegram bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quick", quick_command))
    application.add_handler(CommandHandler("standard", standard_command))
    application.add_handler(CommandHandler("deep", deep_command))
    application.add_handler(CommandHandler("expert", expert_command))
    
    # Default message handler (uses STANDARD)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Run polling
    logger.info("Bot started - All 4 modes active!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
