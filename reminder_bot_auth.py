#!/usr/bin/env python3
"""
Bot de Recordatorios con Autenticación
Sistema multi-usuario con login
"""

import os
import json
import time
import schedule
import hashlib
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from threading import Thread
from functools import wraps

# Cargar variables de entorno
load_dotenv()

# Archivos de datos
USERS_FILE = 'users.json'
TASKS_FILE = 'tasks_auth.json'

# Configuración de Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.permanent_session_lifetime = timedelta(days=7)
CORS(app)

class UserManager:
    """Gestor de usuarios"""

    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        """Carga usuarios desde archivo"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_users(self):
        """Guarda usuarios en archivo"""
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def hash_password(self, password):
        """Hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, whatsapp_number):
        """Registra un nuevo usuario"""
        if self.get_user(username):
            return None, "El usuario ya existe"

        user = {
            'id': len(self.users) + 1,
            'username': username,
            'password': self.hash_password(password),
            'whatsapp_number': whatsapp_number,
            'created_at': datetime.now().isoformat()
        }

        self.users.append(user)
        self.save_users()
        return user, None

    def login(self, username, password):
        """Valida credenciales de usuario"""
        user = self.get_user(username)
        if user and user['password'] == self.hash_password(password):
            return user
        return None

    def get_user(self, username):
        """Obtiene un usuario por nombre"""
        for user in self.users:
            if user['username'] == username:
                return user
        return None

class TaskManager:
    """Gestor de tareas por usuario"""

    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Carga tareas desde archivo"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_tasks(self):
        """Guarda tareas en archivo"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def get_user_tasks(self, user_id):
        """Obtiene tareas de un usuario"""
        return self.tasks.get(str(user_id), [])

    def add_task(self, user_id, description, due_date=None, due_time=None):
        """Agrega una tarea para un usuario con fecha/hora programada"""
        user_id = str(user_id)
        if user_id not in self.tasks:
            self.tasks[user_id] = []

        user_tasks = self.tasks[user_id]
        max_id = max([t['id'] for t in user_tasks], default=0)

        task = {
            'id': max_id + 1,
            'description': description,
            'completed': False,
            'due_date': due_date,  # Formato: YYYY-MM-DD
            'due_time': due_time,  # Formato: HH:MM
            'reminder_count': 0,   # Contador de recordatorios enviados
            'created_at': datetime.now().isoformat()
        }

        self.tasks[user_id].append(task)
        self.save_tasks()
        return task

    def complete_task(self, user_id, task_id):
        """Marca una tarea como completada"""
        user_tasks = self.get_user_tasks(user_id)
        for task in user_tasks:
            if task['id'] == task_id and not task['completed']:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None

    def delete_task(self, user_id, task_id):
        """Elimina una tarea"""
        user_id = str(user_id)
        if user_id in self.tasks:
            self.tasks[user_id] = [t for t in self.tasks[user_id] if t['id'] != task_id]
            self.save_tasks()
            return True
        return False

    def get_pending_tasks(self, user_id):
        """Obtiene tareas pendientes de un usuario"""
        return [t for t in self.get_user_tasks(user_id) if not t['completed']]

# Inicializar gestores
user_manager = UserManager()
task_manager = TaskManager()

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ========== RUTAS DE AUTENTICACIÓN ==========

@app.route('/')
def index():
    """Página principal - redirige según estado de sesión"""
    if 'user_id' in session:
        return render_template('app.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400

    user = user_manager.login(username, password)
    if user:
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username']}})

    return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

@app.route('/register', methods=['POST'])
def register():
    """Endpoint de registro"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    whatsapp = data.get('whatsapp', '').strip()

    if not username or not password or not whatsapp:
        return jsonify({'success': False, 'error': 'Todos los campos son requeridos'}), 400

    if len(username) < 3:
        return jsonify({'success': False, 'error': 'El usuario debe tener al menos 3 caracteres'}), 400

    if len(password) < 4:
        return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 4 caracteres'}), 400

    # Validar formato de WhatsApp
    if not whatsapp.startswith('+'):
        return jsonify({'success': False, 'error': 'El número de WhatsApp debe incluir código de país (ej: +52...)'}), 400

    user, error = user_manager.register(username, password, whatsapp)
    if error:
        return jsonify({'success': False, 'error': error}), 400

    session.permanent = True
    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username']}})

@app.route('/logout', methods=['POST'])
def logout():
    """Endpoint de logout"""
    session.clear()
    return jsonify({'success': True})

# ========== RUTAS DE TAREAS (PROTEGIDAS) ==========

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Obtiene tareas del usuario actual"""
    user_id = session['user_id']
    tasks = task_manager.get_user_tasks(user_id)
    pending = task_manager.get_pending_tasks(user_id)

    return jsonify({
        'success': True,
        'tasks': tasks,
        'pending_count': len(pending)
    })

@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    """Agrega una tarea para el usuario actual"""
    user_id = session['user_id']
    data = request.get_json()
    description = data.get('description', '').strip()
    due_date = data.get('due_date')
    due_time = data.get('due_time')

    if not description:
        return jsonify({'success': False, 'error': 'Descripción requerida'}), 400

    task = task_manager.add_task(user_id, description, due_date, due_time)
    return jsonify({'success': True, 'task': task})

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Completa una tarea del usuario actual"""
    user_id = session['user_id']
    task = task_manager.complete_task(user_id, task_id)

    if task:
        return jsonify({'success': True, 'task': task})
    return jsonify({'success': False, 'error': 'Tarea no encontrada'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Elimina una tarea del usuario actual"""
    user_id = session['user_id']
    if task_manager.delete_task(user_id, task_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Tarea no encontrada'}), 404

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    """Obtiene información del usuario actual"""
    return jsonify({
        'success': True,
        'user': {
            'id': session['user_id'],
            'username': session['username']
        }
    })

# ========== RECORDATORIOS ==========

def enviar_recordatorios():
    """Envía recordatorios para todos los usuarios con tareas vencidas o próximas"""
    now = datetime.now()
    print(f"\n⏰ [{now.strftime('%H:%M')}] Verificando recordatorios...")

    for user_id in task_manager.tasks.keys():
        user_tasks = task_manager.get_user_tasks(user_id)
        user = next((u for u in user_manager.users if u['id'] == int(user_id)), None)

        if not user:
            continue

        tasks_to_remind = []

        for task in user_tasks:
            if task['completed']:
                continue

            # Si la tarea tiene fecha/hora programada
            if task.get('due_date') and task.get('due_time'):
                try:
                    due_datetime_str = f"{task['due_date']} {task['due_time']}"
                    due_datetime = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M')

                    # Si ya pasó la fecha/hora y no se ha completado
                    if now >= due_datetime:
                        tasks_to_remind.append(task)
                        task['reminder_count'] = task.get('reminder_count', 0) + 1

                except:
                    pass

            # Si solo tiene fecha (sin hora)
            elif task.get('due_date'):
                try:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    if now.date() >= due_date:
                        tasks_to_remind.append(task)
                        task['reminder_count'] = task.get('reminder_count', 0) + 1
                except:
                    pass

        if tasks_to_remind:
            task_manager.save_tasks()
            print(f"📋 Usuario '{user['username']}': {len(tasks_to_remind)} recordatorio(s) enviado(s)")

            # Preparar mensaje de WhatsApp
            mensaje_whatsapp = f"⏰ *RECORDATORIOS - {user['username']}*\n\n"

            for task in tasks_to_remind:
                urgency = ""
                urgency_text = ""
                count = task.get('reminder_count', 1)

                if count > 5:
                    urgency = "🔴 MUY URGENTE "
                    urgency_text = "MUY URGENTE"
                elif count > 3:
                    urgency = "🟠 URGENTE "
                    urgency_text = "URGENTE"
                elif count > 1:
                    urgency = "🟡 IMPORTANTE "
                    urgency_text = "IMPORTANTE"

                print(f"  {urgency}#{task['id']}: {task['description']} (recordatorio #{count})")

                # Agregar al mensaje de WhatsApp
                if urgency_text:
                    mensaje_whatsapp += f"{urgency}*{urgency_text}*\n"
                mensaje_whatsapp += f"#{task['id']}: {task['description']}\n"

                if task.get('due_date'):
                    mensaje_whatsapp += f"📅 {task['due_date']}"
                    if task.get('due_time'):
                        mensaje_whatsapp += f" ⏰ {task['due_time']}"
                    mensaje_whatsapp += "\n"

                mensaje_whatsapp += f"(Recordatorio #{count})\n\n"

            mensaje_whatsapp += f"📊 Total: {len(tasks_to_remind)} tarea(s) pendiente(s)\n\n"
            mensaje_whatsapp += "💡 Completa las tareas en la app para dejar de recibir recordatorios."

            # Enviar por WhatsApp si está configurado
            if client and user.get('whatsapp_number'):
                enviar_whatsapp(user['whatsapp_number'], mensaje_whatsapp)

def enviar_whatsapp(numero, mensaje):
    """Envía un mensaje por WhatsApp usando Twilio"""
    if not client:
        print("⚠️  Twilio no configurado")
        return False

    try:
        # Formatear número con prefijo whatsapp:
        whatsapp_to = f"whatsapp:{numero}" if not numero.startswith('whatsapp:') else numero

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=mensaje,
            to=whatsapp_to
        )
        print(f"✅ WhatsApp enviado a {numero}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp a {numero}: {str(e)}")
        return False

# ========== SERVIDOR ==========

def iniciar_servidor():
    """Inicia el servidor Flask"""
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    """Función principal"""
    import sys
    import io

    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("🔐 BOT DE RECORDATORIOS CON AUTENTICACIÓN")
    print("=" * 60)

    print(f"\n👥 Usuarios registrados: {len(user_manager.users)}")
    print(f"⏰ Frecuencia de recordatorios: Cada 30 minutos")
    print("\n🚀 Servidor iniciado. Presiona Ctrl+C para detener.\n")

    # Iniciar servidor en thread separado
    server_thread = Thread(target=iniciar_servidor, daemon=True)
    server_thread.start()

    time.sleep(2)

    # Programar recordatorios cada 5 minutos (para pruebas rápidas)
    # Puedes cambiar a 30 minutos con: schedule.every(30).minutes.do(enviar_recordatorios)
    schedule.every(5).minutes.do(enviar_recordatorios)

    # Enviar recordatorio inicial después de 30 segundos
    schedule.every(30).seconds.do(enviar_recordatorios)

    # Bucle principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido. ¡Hasta luego!")

if __name__ == "__main__":
    main()
