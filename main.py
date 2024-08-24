
from flask import Flask, request, redirect, jsonify, render_template_string
import pyperclip
import asyncio
from telegram import _bot
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
    from telegram import Bot
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
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <h1 style="font-size: 100px ">COPY MAMA </h1>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Copymama</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                    text-align: center;
                }

                .btn-55 {
                    background: linear-gradient(90deg, blue, red);
                    border-radius: 999px;
                    color: #000;
                    display: inline-block;
                    font-weight: 900;
                    overflow: hidden;
                    padding: 1.8rem 5rem;
                    text-transform: uppercase;
                    text-decoration: none;
                    font-size: 1.2rem;
                    line-height: 1.5;
                    cursor: pointer;
                    position: relative;
                    margin: 20px;
                }

                .btn-55 span {
                    background: #1e293b;
                    border-radius: 999px;
                    color: #fff;
                    display: grid;
                    inset: 5px;
                    place-items: center;
                    position: absolute;
                    transition: background 0.3s;
                }

                .btn-55:hover span {
                    background: none;
                }

                .btn-55 svg {
                    display: block;
                    vertical-align: middle;
                }
            </style>
            <script>
                function toggleScript(action) {
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "/toggle", true);
                    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                    xhr.send(JSON.stringify({ action: action }));
                    xhr.onload = function() {
                        if (xhr.status === 200) {
                            var btnStart = document.getElementById('start-btn');
                            var btnStop = document.getElementById('stop-btn');
                            if (action === 'start') {
                                btnStart.style.display = 'none';
                                btnStop.style.display = 'inline-block';
                            } else {
                                btnStart.style.display = 'inline-block';
                                btnStop.style.display = 'none';
                            }
                        }
                    }
                }
            </script>
        </head>
        <body>
            <a href="javascript:void(0);" id="start-btn" class="btn-55" onclick="toggleScript('start')">
                <span>Start</span>
            </a>
            <a href="javascript:void(0);" id="stop-btn" class="btn-55" style="display:none;" onclick="toggleScript('stop')">
                <span>Stop</span>
            </a>
        </body>
        </html>
    ''')


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
