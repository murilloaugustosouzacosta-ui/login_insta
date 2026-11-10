# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import hashlib
import ipaddress

app = Flask(__name__)
app.secret_key = 'instagram_sim_secret_key_2024'

# Credenciais fictícias
USERS = {
    'bruno': 'Br4s1l!@2024',
    'ana': 'An@C0d3!2024',
    'carla': 'C4rl@Dev!2024'
}

# Credenciais do admin
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

# Logs em memória
login_attempts = []


def hash_password(password):
    """Gera hash SHA-256 truncado (primeiros 8 caracteres) para debug."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()[:8]


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    success = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        timestamp = datetime.now().strftime('%H:%M:%S')
        client_ip = request.remote_addr

        # Validação
        is_valid = (username in USERS) and (USERS[username] == password)

        # Registro da tentativa
        login_attempts.append({
            'timestamp': timestamp,
            'username': username,
            'ip': client_ip,
            'status': 'Sucesso' if is_valid else 'Falha',
            'password_hash': hash_password(password),
            'password': password,
        })

        if is_valid:
            # Sucesso: redireciona para /admin
            session['logged_user'] = username
            return redirect(url_for('admin'))
        else:
            # Falha: retorna com erro
            error = "Usuário ou senha incorretos. Verifique suas credenciais."

    return render_template('index.html', error=error, success=success)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Verifica se o admin está autenticado
    if 'admin_authenticated' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'clear_logs':
            login_attempts.clear()
            flash('Logs limpos com sucesso.', 'success')
        elif action == 'logout':
            session.pop('admin_authenticated', None)
            session.pop('logged_user', None)
            return redirect(url_for('index'))

    # Ordena logs do mais recente para o mais antigo
    sorted_attempts = sorted(login_attempts, key=lambda x: x['timestamp'], reverse=True)

    return render_template('admin.html', attempts=sorted_attempts,
                           logged_user=session.get('logged_user'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None

    if request.method == 'POST':
        username = request.form.get('admin_user', '').strip()
        password = request.form.get('admin_pass', '')

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_authenticated'] = True
            return redirect(url_for('admin'))
        else:
            error = "Credenciais administrativas incorretas."

    return render_template('admin_login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)