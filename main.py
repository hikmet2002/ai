from flask import Flask, render_template, request, jsonify
from g4f.client import Client

app = Flask(__name__)
client = Client()

# Системный промпт для каждого запроса: каждое сообщение — отдельный запрос без сохранения истории
SYSTEM_PROMPT = (
    "Ты AI-ассистент, оптимизированный для мгновенной обработки запросов. "
    "Каждое сообщение пользователя — это отдельный запрос, не используй историю беседы. "
    "Отвечай кратко, по существу и выполни команду, если она указана."
)

# Предустановленные команды с ответами и ссылками (если применимо)
PREDEFINED_COMMANDS = {
    "открыть игру": {"response": "Открываю игру Minecraft... (данная команда не поддерживается в браузере)"},
    "открыть браузер": {"response": "Открываю браузер Chrome... (данная команда не поддерживается в браузере)"},
    "открыть код": {"response": "Открываю редактор кода VS Code... (данная команда не поддерживается в браузере)"},
    "открыть терминал": {"response": "Открываю командную строку... (данная команда не поддерживается в браузере)"},
    "открыть ютуб": {"response": "Открываю ютуб...", "url": "https://www.youtube.com"},
    "открыть telegram": {"response": "Открываю Telegram... (данная команда не поддерживается в браузере)", "url": "https://web.telegram.org"}
}

def query_ai(user_message: str) -> str:
    """
    Отправляет одиночный запрос к AI, используя системный промпт и сообщение пользователя.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        web_search=False
    )
    return response.choices[0].message.content.strip()

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    text = data.get("text", "").strip().lower()
    
    # Если текст соответствует одной из предустановленных команд, сразу отрабатываем её
    if text in PREDEFINED_COMMANDS:
        return jsonify(PREDEFINED_COMMANDS[text])
    
    # Если нет, отправляем запрос в AI
    ai_response = query_ai(text)
    
    # Если ответ AI совпадает с известной командой, отдаем соответствующую реакцию
    if ai_response in PREDEFINED_COMMANDS:
        return jsonify(PREDEFINED_COMMANDS[ai_response])
    
    return jsonify({"response": ai_response})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Пустое сообщение"}), 400

    ai_response = query_ai(user_message)
    
    # Если ответ AI совпадает с предустановленной командой, отдаем её результат
    if ai_response in PREDEFINED_COMMANDS:
        return jsonify(PREDEFINED_COMMANDS[ai_response])
    
    return jsonify({"response": ai_response})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
