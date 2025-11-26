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
    """Página principal - landing page de WhatsApp"""
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

            # Enviar por WhatsApp
            if user.get('whatsapp_number'):
                enviar_whatsapp(user['whatsapp_number'], mensaje_whatsapp)

def enviar_whatsapp(numero, mensaje):
    """Envía un mensaje por WhatsApp usando Evolution API"""
    import requests

    # Configuración Evolution API
    EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'https://devevoapi.tuagenteia.click')
    EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', 'e50bdaf76404943a4e2d13d7ff7a49a2')
    EVOLUTION_INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'reminderbot')

    if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
        print("⚠️  Evolution API no configurado")
        return False

    try:
        # Limpiar número (quitar + y espacios)
        numero_limpio = numero.replace('+', '').replace(' ', '').replace('-', '')

        # Agregar @s.whatsapp.net si no lo tiene
        if '@' not in numero_limpio:
            numero_limpio = f"{numero_limpio}@s.whatsapp.net"

        # Preparar el payload
        payload = {
            "number": numero_limpio,
            "text": mensaje
        }

        # Headers con API key
        headers = {
            'Content-Type': 'application/json',
            'apikey': EVOLUTION_API_KEY
        }

        # URL del endpoint
        url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"

        # Enviar mensaje
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 201 or response.status_code == 200:
            print(f"✅ WhatsApp enviado a {numero}: {response.json().get('key', {}).get('id', 'OK')}")
            return True
        else:
            print(f"❌ Error al enviar WhatsApp a {numero}: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error al enviar WhatsApp a {numero}: {str(e)}")
        return False

# ========== PROCESAMIENTO DE MENSAJES DE WHATSAPP ==========

def procesar_con_ia(mensaje, tareas_usuario=[]):
    """Usa Claude AI para interpretar el mensaje del usuario de forma natural"""
    try:
        import anthropic
        import json
        from datetime import datetime

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None

        client = anthropic.Anthropic(api_key=api_key)

        # Contexto de tareas existentes
        tareas_context = ""
        if tareas_usuario:
            tareas_context = "\n\nTareas actuales del usuario:\n"
            for i, t in enumerate(tareas_usuario, 1):
                tareas_context += f"{i}. {t['description']}"
                if t.get('due_time'):
                    tareas_context += f" - {t['due_time']}"
                tareas_context += "\n"

        prompt = f"""Eres un asistente de recordatorios por WhatsApp. Analiza el siguiente mensaje del usuario y extrae la información.

Mensaje: "{mensaje}"
Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M')}{tareas_context}

Responde SOLO con un JSON con este formato:
{{
  "accion": "crear_tarea" | "ver_lista" | "completar_tarea" | "ayuda" | "desconocido",
  "descripcion": "descripción de la tarea (sin la hora)",
  "fecha": "YYYY-MM-DD o null",
  "hora": "HH:MM o null",
  "numero_tarea": número o null
}}

Ejemplos:
- "Comprar pan a las 8:17" -> {{"accion": "crear_tarea", "descripcion": "Comprar pan", "fecha": "2025-11-26", "hora": "20:17", "numero_tarea": null}}
- "llamar al doctor mañana 3pm" -> {{"accion": "crear_tarea", "descripcion": "llamar al doctor", "fecha": "2025-11-27", "hora": "15:00", "numero_tarea": null}}
- "lista" -> {{"accion": "ver_lista", "descripcion": null, "fecha": null, "hora": null, "numero_tarea": null}}
- "completar 1" -> {{"accion": "completar_tarea", "descripcion": null, "fecha": null, "hora": null, "numero_tarea": 1}}
- "ayuda" -> {{"accion": "ayuda", "descripcion": null, "fecha": null, "hora": null, "numero_tarea": null}}

Responde SOLO el JSON, nada más."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        respuesta = message.content[0].text.strip()
        # Limpiar markdown si lo tiene
        if respuesta.startswith('```'):
            respuesta = respuesta.split('\n', 1)[1]
            respuesta = respuesta.rsplit('\n```', 1)[0]

        return json.loads(respuesta)

    except Exception as e:
        print(f"⚠️ Error en IA: {str(e)}")
        return None

def extraer_hora_fecha(texto):
    """Extrae hora y fecha de un texto usando expresiones regulares y dateparser"""
    import re
    from dateutil import parser as date_parser
    import dateparser

    # Patrones de hora comunes
    patrones_hora = [
        r'(\d{1,2}):(\d{2})\s*(am|pm)?',  # 3:00pm, 15:30
        r'(\d{1,2})\s*(am|pm)',            # 3pm, 3 pm
        r'a las (\d{1,2})',                # a las 3
        r'(\d{1,2})h',                     # 15h
    ]

    hora_encontrada = None
    fecha_encontrada = None

    # Buscar hora en el texto
    for patron in patrones_hora:
        match = re.search(patron, texto.lower())
        if match:
            try:
                hora_str = match.group(0)
                # Intentar parsear la hora
                fecha_hora = dateparser.parse(hora_str, settings={'PREFER_DATES_FROM': 'future'})
                if fecha_hora:
                    hora_encontrada = fecha_hora.strftime('%H:%M')
                    fecha_encontrada = fecha_hora.strftime('%Y-%m-%d')
                    break
            except:
                continue

    # Si no encontró hora, intentar con dateparser en todo el texto
    if not hora_encontrada:
        try:
            fecha_hora = dateparser.parse(texto, settings={'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'current'})
            if fecha_hora:
                hora_encontrada = fecha_hora.strftime('%H:%M')
                fecha_encontrada = fecha_hora.strftime('%Y-%m-%d')
        except:
            pass

    return fecha_encontrada, hora_encontrada

def procesar_mensaje_whatsapp(numero_remitente, mensaje):
    """Procesa mensajes entrantes de WhatsApp"""
    # Limpiar número
    numero_limpio = numero_remitente.replace('@s.whatsapp.net', '').replace('@c.us', '')

    # Buscar usuario por número de WhatsApp
    user = None
    for u in user_manager.users:
        user_number = u.get('whatsapp_number', '').replace('+', '').replace(' ', '').replace('-', '')
        if numero_limpio in user_number or user_number in numero_limpio:
            user = u
            break

    # Si no existe el usuario, crear uno automáticamente
    if not user:
        # Crear usuario automáticamente con el número de WhatsApp
        user, error = user_manager.register(
            username=numero_limpio,
            password=secrets.token_hex(16),  # Password aleatorio
            whatsapp_number=numero_limpio
        )

        if error:
            # Si ya existe (no debería pasar), buscar por número
            for u in user_manager.users:
                if u.get('username') == numero_limpio:
                    user = u
                    break

        # Enviar mensaje de bienvenida
        enviar_whatsapp(numero_remitente, """👋 ¡Bienvenido al bot de recordatorios!

Tu cuenta ha sido creada automáticamente.

💡 *Cómo usar el bot:*

📝 Crear tarea:
Comprar pan a las 3pm listo

📋 Ver tareas:
lista

✅ Completar tarea:
completar 1

Escribe "ayuda" para más comandos.""")

        # Continuar procesando el mensaje
        pass

    # ===== INTENTAR PROCESAR CON IA PRIMERO =====
    tareas_usuario = task_manager.get_pending_tasks(user['id'])
    ia_response = procesar_con_ia(mensaje, tareas_usuario)

    if ia_response:
        print(f"🤖 IA procesó: {ia_response}")

        # Crear tarea
        if ia_response['accion'] == 'crear_tarea' and ia_response['descripcion']:
            if not ia_response['hora']:
                return enviar_whatsapp(numero_remitente, "❌ No pude detectar la hora. Por favor incluye una hora clara.\nEjemplo: Comprar pan a las 3pm")

            task = task_manager.add_task(user['id'], ia_response['descripcion'], ia_response['fecha'], ia_response['hora'])

            respuesta = f"✅ *Tarea creada:*\n\n"
            respuesta += f"📝 {ia_response['descripcion']}\n"
            respuesta += f"🕐 {ia_response['hora']}"
            if ia_response['fecha']:
                respuesta += f" - {ia_response['fecha']}"
            respuesta += f"\n\n💡 Te recordaré a la hora indicada."

            return enviar_whatsapp(numero_remitente, respuesta)

        # Ver lista
        elif ia_response['accion'] == 'ver_lista':
            if not tareas_usuario:
                return enviar_whatsapp(numero_remitente, "📋 No tienes tareas pendientes.")

            respuesta = "📋 *Tus tareas pendientes:*\n\n"
            for i, tarea in enumerate(tareas_usuario, 1):
                respuesta += f"{i}. {tarea['description']}"
                if tarea.get('due_date') and tarea.get('due_time'):
                    respuesta += f" - {tarea['due_time']}"
                respuesta += "\n"

            respuesta += f"\n📊 Total: {len(tareas_usuario)} tarea(s)"
            respuesta += "\n\n💡 Para completar una tarea escribe: completar 1"

            return enviar_whatsapp(numero_remitente, respuesta)

        # Completar tarea
        elif ia_response['accion'] == 'completar_tarea' and ia_response['numero_tarea']:
            numero_tarea = ia_response['numero_tarea']

            if numero_tarea < 1 or numero_tarea > len(tareas_usuario):
                return enviar_whatsapp(numero_remitente, f"❌ Número de tarea inválido. Tienes {len(tareas_usuario)} tareas pendientes.")

            tarea = tareas_usuario[numero_tarea - 1]
            task_manager.complete_task(user['id'], tarea['id'])

            return enviar_whatsapp(numero_remitente, f"✅ Tarea completada: {tarea['description']}")

        # Ayuda
        elif ia_response['accion'] == 'ayuda':
            respuesta = """🤖 *Cómo usar el bot:*

📝 Crear tarea:
Simplemente escribe lo que quieres hacer y la hora
Ejemplo: Comprar pan a las 3pm

📋 Ver tareas:
Escribe: lista

✅ Completar tarea:
Escribe: completar 1"""
            return enviar_whatsapp(numero_remitente, respuesta)

    # ===== SI IA NO FUNCIONÓ, USAR COMANDOS CLÁSICOS =====
    mensaje_lower = mensaje.lower().strip()

    # Comando: Ver lista de tareas
    if mensaje_lower in ['lista', 'tareas', 'ver tareas', 'mis tareas']:
        tareas = task_manager.get_pending_tasks(user['id'])

        if not tareas:
            return enviar_whatsapp(numero_remitente, "📋 No tienes tareas pendientes.")

        respuesta = "📋 *Tus tareas pendientes:*\n\n"
        for i, tarea in enumerate(tareas, 1):
            respuesta += f"{i}. {tarea['description']}"
            if tarea.get('due_date') and tarea.get('due_time'):
                respuesta += f" - {tarea['due_time']}"
            respuesta += "\n"

        respuesta += f"\n📊 Total: {len(tareas)} tarea(s)"
        respuesta += "\n\n💡 Para completar una tarea escribe: completar 1"

        return enviar_whatsapp(numero_remitente, respuesta)

    # Comando: Completar tarea
    if mensaje_lower.startswith('completar') or mensaje_lower.startswith('✓'):
        # Extraer número de tarea
        import re
        match = re.search(r'(\d+)', mensaje)
        if not match:
            return enviar_whatsapp(numero_remitente, "❌ Por favor especifica el número de tarea. Ejemplo: completar 1")

        numero_tarea = int(match.group(1))
        tareas_pendientes = task_manager.get_pending_tasks(user['id'])

        if numero_tarea < 1 or numero_tarea > len(tareas_pendientes):
            return enviar_whatsapp(numero_remitente, f"❌ Número de tarea inválido. Tienes {len(tareas_pendientes)} tareas pendientes.")

        tarea = tareas_pendientes[numero_tarea - 1]
        task_manager.complete_task(user['id'], tarea['id'])

        return enviar_whatsapp(numero_remitente, f"✅ Tarea completada: {tarea['description']}")

    # Comando: Ayuda
    if mensaje_lower in ['ayuda', 'help', 'comandos', '?']:
        respuesta = """🤖 *Comandos disponibles:*

📝 Para crear una tarea:
Escribe la tarea y termina con "listo"
Ejemplo: Comprar pan a las 3pm listo

📋 Ver tus tareas:
Escribe: lista

✅ Completar una tarea:
Escribe: completar 1

❓ Ver esta ayuda:
Escribe: ayuda"""
        return enviar_whatsapp(numero_remitente, respuesta)

    # Crear tarea si termina con "listo"
    if mensaje_lower.endswith('listo'):
        # Quitar la palabra "listo" del mensaje
        texto_tarea = mensaje[:-5].strip()

        # Extraer fecha y hora
        fecha, hora = extraer_hora_fecha(texto_tarea)

        if not hora:
            return enviar_whatsapp(numero_remitente, "❌ No pude detectar la hora. Por favor incluye una hora clara.\nEjemplo: Comprar pan a las 3pm listo")

        # Crear la tarea sin la hora en la descripción
        descripcion_limpia = texto_tarea
        # Intentar limpiar la descripción eliminando patrones de hora
        import re
        descripcion_limpia = re.sub(r'\s*(a las|a la|al|en)\s*\d{1,2}(:\d{2})?\s*(am|pm|h)?\s*', ' ', descripcion_limpia, flags=re.IGNORECASE)
        descripcion_limpia = re.sub(r'\d{1,2}:\d{2}', '', descripcion_limpia)
        descripcion_limpia = descripcion_limpia.strip()

        # Crear la tarea
        task = task_manager.add_task(user['id'], descripcion_limpia, fecha, hora)

        respuesta = f"✅ *Tarea creada:*\n\n"
        respuesta += f"📝 {descripcion_limpia}\n"
        respuesta += f"🕐 {hora}"
        if fecha:
            respuesta += f" - {fecha}"
        respuesta += f"\n\n💡 Te recordaré a la hora indicada."

        return enviar_whatsapp(numero_remitente, respuesta)

    # Si no reconoce el comando
    respuesta = """🤔 No entendí tu mensaje.

💡 *Cómo usar el bot:*

📝 Crear tarea:
Comprar pan a las 3pm listo

📋 Ver tareas:
lista

✅ Completar tarea:
completar 1

Escribe "ayuda" para más info."""
    return enviar_whatsapp(numero_remitente, respuesta)

@app.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():
    """Webhook para recibir mensajes de WhatsApp desde Evolution API"""
    try:
        data = request.get_json()
        print(f"\n📨 Webhook recibido: {data}")

        # Verificar que sea un mensaje de texto
        if data.get('event') != 'messages.upsert':
            return jsonify({'success': True, 'message': 'Event ignored'}), 200

        # Obtener datos del mensaje
        message_data = data.get('data', {})
        key = message_data.get('key', {})
        message = message_data.get('message', {})

        # Ignorar mensajes propios
        if key.get('fromMe'):
            return jsonify({'success': True, 'message': 'Own message ignored'}), 200

        # Obtener número del remitente y texto del mensaje
        numero_remitente = key.get('remoteJid', '')
        texto_mensaje = message.get('conversation') or message.get('extendedTextMessage', {}).get('text', '')

        if not texto_mensaje or not numero_remitente:
            return jsonify({'success': True, 'message': 'No text or sender'}), 200

        print(f"📱 Mensaje de {numero_remitente}: {texto_mensaje}")

        # Procesar el mensaje en un thread separado para no bloquear el webhook
        from threading import Thread
        thread = Thread(target=procesar_mensaje_whatsapp, args=(numero_remitente, texto_mensaje))
        thread.start()

        return jsonify({'success': True, 'message': 'Processing'}), 200

    except Exception as e:
        print(f"❌ Error en webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

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
