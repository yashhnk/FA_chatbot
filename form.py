from flask import Flask, request, render_template_string, render_template
from app import setup_database, get_response

# Create a separate Flask app for the form interface
form_app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; border-radius: 5px; padding: 20px; }
        .user-query { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
        .bot-response { background-color: #e6f7ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        input[type="text"] { width: 70%; padding: 10px; margin-right: 10px; }
        input[type="submit"] { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; }
        .history-button {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 15px;
            background-color: #2196F3;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .history-button:hover {
            background-color: #0b7dda;
        }
    </style>
</head>
<body>
    <h1>Chatbot Web Interface</h1>
    <div class="chat-container">
        {% for q, a in history %}
            <div class="user-query"><strong>You:</strong> {{ q }}</div>
            <div class="bot-response"><strong>Bot:</strong> {{ a }}</div>
        {% endfor %}
        
        <form method="POST">
            <input type="text" name="user_input" placeholder="Ask me anything..." required>
            <input type="submit" value="Send">
        </form>

        <a href="/history" class="history-button">View History</a>
    </div>
</body>
</html>
"""


@form_app.route("/", methods=["GET", "POST"])
def chat_interface():
    query = response = ""
    history = []

    conn, cursor = setup_database()

    if request.method == "POST":
        query = request.form.get("user_input", "").strip()
        if query:
            response = get_response(query, cursor)
            cursor.execute("INSERT INTO chat_history (query, response) VALUES (%s, %s)", (query, response))
            conn.commit()

    # Fetch all previous chats
    cursor.execute("SELECT query, response FROM chat_history ORDER BY id ASC")
    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template_string(HTML_TEMPLATE, query=query, response=response, history=history)

@form_app.route("/history")
def chat_history():
    conn, cursor = setup_database()
    cursor.execute("SELECT query, response FROM chat_history ORDER BY id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("history.html", history=rows)
if __name__ == "__main__":
    form_app.run(port=5001)  # Runs on different port than app.py