from flask import Flask, request, jsonify, render_template
import pyperclip
import asyncio
from telegram import Bot
import threading

app = Flask(__name__)

TOKEN = '7423032401:AAHP3yAaGLSLCnXIY-uINVvG-tpog0ZGnoU'
CHAT_ID = '603004587'

is_running = False
loop = asyncio.new_event_loop()
monitor_thread = None

async def send_message_with_clickable_link(bot, chat_id, phone_number):
    text = f'Phone Number: <a href="tel:{phone_number}">+91{phone_number}</a>'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')

async def monitor_clipboard():
    last_clipboard_content = ""
    bot = Bot(token=TOKEN)
    while is_running:
        clipboard_content = pyperclip.paste()
        if clipboard_content != last_clipboard_content:
            last_clipboard_content = clipboard_content
            print(f"New clipboard content detected: {clipboard_content}")
            if clipboard_content.isdigit() and len(clipboard_content) >= 10 and len(clipboard_content) <= 15:
                await send_message_with_clickable_link(bot, CHAT_ID, clipboard_content)
        await asyncio.sleep(1)

def start_monitoring():
    global is_running, monitor_thread
    if not is_running:
        is_running = True

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_until_complete(monitor_clipboard())

        monitor_thread = threading.Thread(target=run_loop)
        monitor_thread.start()

def stop_monitoring():
    global is_running
    is_running = False
    if monitor_thread:
        monitor_thread.join()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.json
    action = data.get('action', 'start')

    if action == 'start':
        start_monitoring()
    elif action == 'stop':
        stop_monitoring()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
