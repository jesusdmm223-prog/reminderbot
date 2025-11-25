#!/usr/bin/env python3
"""
Bot de Recordatorios Multiplataforma
Funciona en WhatsApp y con interfaz web responsive
"""

import os
import json
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from threading import Thread

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio (opcional)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '')
YOUR_WHATSAPP_NUMBER = os.getenv('YOUR_WHATSAPP_NUMBER', '')

# Inicializar cliente de Twilio solo si está configurado
client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio configurado correctamente")
    except:
        print("⚠️  Twilio no disponible (opcional)")

# Archivo de tareas
TASKS_FILE = 'tasks.json'

# Configuración de Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

class TaskManager:
    """Gestor de tareas pendientes"""

    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Carga las tareas desde el archivo JSON"""
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_tasks(self):
        """Guarda las tareas en el archivo JSON"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, description, interval_minutes=30):
        """Agrega una nueva tarea"""
        # Obtener el ID más alto y sumar 1
        max_id = max([t['id'] for t in self.tasks], default=0)
        task = {
            'id': max_id + 1,
            'description': description,
            'completed': False,
            'interval_minutes': interval_minutes,
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def complete_task(self, task_id):
        """Marca una tarea como completada"""
        for task in self.tasks:
            if task['id'] == task_id and not task['completed']:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None

    def delete_task(self, task_id):
        """Elimina una tarea"""
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.save_tasks()
            return True
        return False

    def get_pending_tasks(self):
        """Obtiene todas las tareas pendientes"""
        return [t for t in self.tasks if not t['completed']]

    def get_all_tasks(self):
        """Obtiene todas las tareas"""
        return self.tasks

# Inicializar gestor de tareas
task_manager = TaskManager()

# ========== RUTAS WEB ==========

@app.route('/')
def index():
    """Página principal de la aplicación web"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Obtiene todas las tareas"""
    return jsonify({
        'success': True,
        'tasks': task_manager.get_all_tasks(),
        'pending_count': len(task_manager.get_pending_tasks())
    })

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Agrega una nueva tarea"""
    data = request.get_json()
    description = data.get('description', '').strip()

    if not description:
        return jsonify({'success': False, 'error': 'Descripción requerida'}), 400

    task = task_manager.add_task(description)
    return jsonify({'success': True, 'task': task})

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Completa una tarea"""
    task = task_manager.complete_task(task_id)
    if task:
        return jsonify({'success': True, 'task': task})
    return jsonify({'success': False, 'error': 'Tarea no encontrada'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Elimina una tarea"""
    if task_manager.delete_task(task_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Tarea no encontrada'}), 404

# ========== WHATSAPP WEBHOOK ==========

def enviar_mensaje_whatsapp(mensaje):
    """Envía un mensaje por WhatsApp usando Twilio"""
    if not client:
        print("⚠️  WhatsApp no configurado")
        return False

    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=mensaje,
            to=YOUR_WHATSAPP_NUMBER
        )
        print(f"✅ Mensaje WhatsApp enviado: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar mensaje WhatsApp: {str(e)}")
        return False

def enviar_recordatorios():
    """Envía recordatorios de tareas pendientes"""
    pending_tasks = task_manager.get_pending_tasks()

    if not pending_tasks:
        return

    timestamp = datetime.now().strftime("%H:%M")
    mensaje = f"⏰ [{timestamp}] RECORDATORIO DE TAREAS\n\n"
    mensaje += "📋 Tareas pendientes:\n\n"

    for task in pending_tasks:
        mensaje += f"#{task['id']} - {task['description']}\n"

    mensaje += f"\n📊 Total: {len(pending_tasks)} tarea(s) pendiente(s)"

    # Enviar por WhatsApp si está configurado
    if client:
        enviar_mensaje_whatsapp(mensaje)

    # Log en consola
    print(f"\n{mensaje}\n")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para recibir mensajes de WhatsApp"""
    try:
        mensaje_entrante = request.form.get('Body', '').strip()
        numero_remitente = request.form.get('From', '')

        print(f"📨 Mensaje recibido de {numero_remitente}: {mensaje_entrante}")

        if numero_remitente == YOUR_WHATSAPP_NUMBER:
            respuesta = procesar_comando_whatsapp(mensaje_entrante)
            enviar_mensaje_whatsapp(respuesta)

        return '', 200
    except Exception as e:
        print(f"❌ Error en webhook: {str(e)}")
        return '', 500

def procesar_comando_whatsapp(mensaje_recibido):
    """Procesa comandos recibidos por WhatsApp"""
    comando = mensaje_recibido.strip().lower()

    if comando == 'lista':
        tasks = task_manager.get_all_tasks()
        if not tasks:
            return "📋 No tienes tareas registradas.\n\n💡 Usa 'agregar [descripción]' para crear una."

        respuesta = "📋 TODAS TUS TAREAS:\n\n"
        pendientes = [t for t in tasks if not t['completed']]
        completadas = [t for t in tasks if t['completed']]

        if pendientes:
            respuesta += "⏳ Pendientes:\n"
            for task in pendientes:
                respuesta += f"  #{task['id']} - {task['description']}\n"

        if completadas:
            respuesta += f"\n✅ Completadas ({len(completadas)}):\n"
            for task in completadas[:5]:
                respuesta += f"  #{task['id']} - {task['description']}\n"

        return respuesta

    if comando.startswith('hecho #'):
        try:
            task_id = int(comando.split('#')[1].strip())
            task = task_manager.complete_task(task_id)
            if task:
                return f"✅ ¡Tarea completada!\n\n#{task_id} - {task['description']}\n\n🎉 ¡Bien hecho!"
            else:
                return f"❌ No se encontró la tarea #{task_id} o ya está completada."
        except:
            return "❌ Formato incorrecto. Usa: hecho #N"

    if comando.startswith('eliminar #') or comando.startswith('borrar #'):
        try:
            task_id = int(comando.split('#')[1].strip())
            if task_manager.delete_task(task_id):
                return f"🗑️ Tarea #{task_id} eliminada correctamente."
            else:
                return f"❌ No se encontró la tarea #{task_id}."
        except:
            return "❌ Formato incorrecto. Usa: eliminar #N"

    if comando.startswith('agregar '):
        descripcion = mensaje_recibido[8:].strip()
        if descripcion:
            task = task_manager.add_task(descripcion)
            return f"✅ Tarea agregada:\n\n#{task['id']} - {descripcion}\n\n⏰ Te recordaré cada 30 minutos."
        else:
            return "❌ Debes proporcionar una descripción.\n\nEjemplo: agregar Llamar al doctor"

    if comando in ['ayuda', 'help', 'comandos']:
        return """🤖 COMANDOS DISPONIBLES:

📝 Gestión de tareas:
• agregar [descripción] - Crear nueva tarea
• lista - Ver todas las tareas
• hecho #N - Completar tarea #N
• eliminar #N - Borrar tarea #N

💡 También puedes usar la interfaz web en tu navegador."""

    return "❌ Comando no reconocido.\n\n💬 Escribe 'ayuda' para ver los comandos disponibles."

# ========== SCHEDULER ==========

def iniciar_servidor():
    """Inicia el servidor Flask"""
    port = int(os.getenv('PORT', 5000))
    print(f"\n🌐 Interfaz web disponible en: http://localhost:{port}")
    print(f"📱 Accede desde cualquier dispositivo en tu red local\n")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    """Función principal"""
    import sys
    import io

    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("🤖 BOT DE RECORDATORIOS MULTIPLATAFORMA")
    print("=" * 60)

    pending_count = len(task_manager.get_pending_tasks())
    print(f"\n📋 Tareas pendientes: {pending_count}")
    print(f"⏰ Frecuencia de recordatorios: Cada 30 minutos")

    if client:
        print(f"📱 WhatsApp: Configurado")
    else:
        print(f"📱 WhatsApp: No configurado (opcional)")

    print("\n🚀 Bot iniciado. Presiona Ctrl+C para detener.\n")

    # Iniciar servidor web en thread separado
    server_thread = Thread(target=iniciar_servidor, daemon=True)
    server_thread.start()

    # Esperar un poco para que el servidor inicie
    time.sleep(2)

    # Programar recordatorios cada 30 minutos
    schedule.every(30).minutes.do(enviar_recordatorios)

    # Bucle principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido. ¡Hasta luego!")

if __name__ == "__main__":
    main()
