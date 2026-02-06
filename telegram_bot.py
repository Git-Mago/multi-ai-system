import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import signal
import sys

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

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

*🎤 Messaggi Vocali:*
Tieni premuto microfono Telegram → parla
Il bot converte automaticamente in testo!

*📸 Foto (presto):*
Funzionalità analisi immagini in arrivo

⏱️ Tempi: Quick 10s | Standard 30s | Deep 60s | Expert 2min
💰 Costo: Sempre $0 (gratis)
🤖 Modelli: Llama, Mixtral, Gemma
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
        
        final_msg = f"🟢 *QUICK - Risposta:*\n\n{risposta}\n| 1 modello"
        
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
        final_msg += "📊 *Dettagli:*\n"
        for role, _ in responses:
            final_msg += f"• {role}\n"
        final_msg += "\n3 modelli"
        
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
            "llama-3.3-70b-versatile",
            "Crea sintesi completa e bilanciata da tutte le prospettive.",
            synthesis_prompt
        )
        
        await msg.delete()
        
        final_msg = f"🟠 *DEEP - Risposta da 5 Prospettive:*\n\n{finale}\n\n"
        final_msg += "📊 *Agenti Consultati:*\n"
        for role, _ in responses:
            final_msg += f"• {role}\n"
        final_msg += "\n5 modelli premium"
        
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
        synthesis_prompt += "\nCrea una risposta finale che integri TUTTE le prospettive, evidenzi consensi/disaccordi, e fornisca raccomandazione ponderata."
        
        finale = query_groq(
            "llama-3.3-70b-versatile",
            "Sei un Master Sintetizzatore con 20 anni di esperienza. Crea sintesi definitiva.",
            synthesis_prompt
        )
        
        await msg.delete()
        
        final_msg = f"🔴 *EXPERT - Risposta Master da 6 AI:*\n\n{finale}\n\n"
        final_msg += "📊 *Breakdown Esperti:*\n"
        for role, _ in responses:
            final_msg += f"• {role}\n"
        final_msg += "\n6 modelli top-tier"
        
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
    
    # Check for mode keywords
    lower_text = domanda.lower()
    
    if any(kw in lower_text for kw in ['[quick]', 'veloce', 'rapido']):
        # Extract question without keyword
        for kw in ['[quick]', 'veloce', 'rapido']:
            domanda = domanda.replace(kw, '').replace(kw.upper(), '').strip()
        context.args = domanda.split()
        await quick_command(update, context)
        return
    
    elif any(kw in lower_text for kw in ['[deep]', 'approfondita', 'complessa']):
        for kw in ['[deep]', 'approfondita', 'complessa']:
            domanda = domanda.replace(kw, '').replace(kw.upper(), '').strip()
        context.args = domanda.split()
        await deep_command(update, context)
        return
    
    elif any(kw in lower_text for kw in ['[expert]', 'critica', 'importante']):
        for kw in ['[expert]', 'critica', 'importante']:
            domanda = domanda.replace(kw, '').replace(kw.upper(), '').strip()
        context.args = domanda.split()
        await expert_command(update, context)
        return
    
    # Default: STANDARD mode
    context.args = domanda.split()
    await standard_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Error: {context.error}")

def main():
    """Start bot"""
    global application
    
    logger.info("Starting Multi-AI Bot with all modes...")
    
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
