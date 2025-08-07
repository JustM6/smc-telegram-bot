
import ccxt
import pandas as pd
import os
import telegram
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)
exchange = ccxt.binance()

def detect_ob_fvg(df):
    last = df.iloc[-2]
    prev = df.iloc[-3]
    if last['low'] > prev['high']:
        return {
            "type": "long",
            "ob_level": round(prev['close'], 2),
            "fvg_range": (round(prev['high'], 2), round(last['low'], 2)),
            "sl": round(prev['low'], 2),
            "tp": round(last['high'] + 2 * (last['high'] - prev['low']), 2)
        }
    return None

def check_signal():
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=200)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    signal = detect_ob_fvg(df)
    if signal:
        msg = f"""
<b>Сигнал по BTC/USDT</b>
Тип: <b>{'Лонг' if signal['type']=='long' else 'Шорт'}</b>
Order Block: {signal['ob_level']}
FVG: {signal['fvg_range'][0]} – {signal['fvg_range'][1]}
SL: {signal['sl']}
TP: {signal['tp']}
⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.HTML)

keep_alive()
scheduler = BackgroundScheduler()
scheduler.add_job(check_signal, "interval", minutes=15)
scheduler.start()
