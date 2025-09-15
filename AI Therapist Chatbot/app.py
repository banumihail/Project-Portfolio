from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime
from huggingface_hub import InferenceClient

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

HUGGING_FACE_API_KEY = "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"
client = InferenceClient(token=HUGGING_FACE_API_KEY)

# ---------------- Database ----------------


def init_db():
    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            therapist_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000)
    return salt + password_hash.hex()


def verify_password(stored_password, provided_password):
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', provided_password.encode(), salt.encode(), 100000)
    return password_hash.hex() == stored_hash

# ---------------- Helper functions ----------------


def safe_str(s):
    return str(s) if s else "..."


def get_user_conversations(user_id, limit=10):
    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_message, therapist_response, timestamp
        FROM conversations
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    conversations = cursor.fetchall()
    conn.close()
    return list(reversed(conversations))


def save_conversation(user_id, user_message, therapist_response):
    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (user_id, user_message, therapist_response)
        VALUES (?, ?, ?)
    ''', (user_id, user_message, therapist_response))
    conn.commit()
    conn.close()


def get_therapist_response(user_message, user_id):
    messages = [
        {"role": "system", "content": (
            "You are a compassionate, empathetic therapist named Dr. Emma. Your responses should be:\n"
            "- Warm and understanding, using phrases like 'I hear you' or 'That sounds really difficult'\n"
            "- Non-judgmental and validating of the user's feelings\n"
            "- Focused on active listening rather than giving advice\n"
            "- Brief and conversational (1-3 sentences maximum)\n"
            "- Encouraging self-reflection with gentle, open-ended questions\n"
            "- Supportive but never diagnostic or prescriptive\n\n"
            "Avoid:\n"
            "- Medical diagnoses or treatment recommendations\n"
            "- Overly clinical language\n"
            "- Long responses or lectures\n"
            "- Dismissing or minimizing feelings"
        )}]
    for conv in get_user_conversations(user_id, 5):
        messages.append({"role": "user", "content": safe_str(conv[0])})
        messages.append({"role": "assistant", "content": safe_str(conv[1])})
    messages.append({"role": "user", "content": safe_str(user_message)})

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        therapist_response = safe_str(response.choices[0].message.content)
    except:
        import random
        fallback = [
            "I'm here for you. Could you tell me more?",
            "I understand this might be difficult. Take your time.",
            "It sounds challenging. I'm listening."
        ]
        therapist_response = random.choice(fallback)

    save_conversation(user_id, user_message, therapist_response)
    return therapist_response

# ---------------- Routes ----------------


@app.route("/")
@app.route("/login")
def login_page():
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return render_template("logreg.html")  # Single login/register page


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username or email already exists'}), 400

    password_hash = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'success': True, 'redirect': url_for('chat_page')})
    except:
        conn.close()
        return jsonify({'error': 'Registration failed'}), 500


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'success': True, 'redirect': url_for('chat_page')})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route("/chat")
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template("chat.html", username=session.get('username'))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400
    response = get_therapist_response(user_message, session['user_id'])
    return jsonify({"response": response, "timestamp": datetime.now().isoformat()})


@app.route("/api/history")
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    convs = get_user_conversations(session['user_id'], 20)
    history = []
    for c in convs:
        history.extend([
            {'type': 'user', 'content': c[0], 'timestamp': c[2]},
            {'type': 'therapist', 'content': c[1], 'timestamp': c[2]}
        ])
    return jsonify({'history': history})


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conn = sqlite3.connect('therapist_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM conversations WHERE user_id = ?',
                   (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'status': 'cleared'})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ---------------- Run App ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
