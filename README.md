# 🤖 Bot de Recordatorios Multiplataforma

Aplicación completa de gestión de tareas con recordatorios automáticos. **Funciona en cualquier dispositivo, navegador y marca** (iPhone, Android, tablets, PC). También incluye integración opcional con WhatsApp.

## ✨ Características

### 📱 Interfaz Web Universal
- ✅ **Compatible con todos los dispositivos**: iPhone, Android, tablets, PC
- ✅ **Funciona en todos los navegadores**: Chrome, Safari, Firefox, Edge, etc.
- ✅ **Diseño responsive**: Se adapta automáticamente a cualquier pantalla
- ✅ **PWA (Instalable)**: Instálala como una app nativa en tu dispositivo
- ✅ **Notificaciones del navegador**: Recibe alertas incluso con la app cerrada
- ✅ **Funciona offline**: Cache local para uso sin conexión

### 🎯 Gestión de Tareas
- 📝 Agregar, completar y eliminar tareas
- ⏰ Recordatorios automáticos cada 30 minutos
- ✅ Solo te recuerda las tareas pendientes
- 📊 Estadísticas en tiempo real
- 🔄 Sincronización automática

### 💬 WhatsApp (Opcional)
- Integración con Twilio para enviar recordatorios por WhatsApp
- Control de tareas por comandos de texto

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Crear los Iconos (Opcional)

```bash
cd static
python create_icons.py
```

### 3. Configurar Variables de Entorno (Opcional para WhatsApp)

Crea un archivo `.env` (puedes copiar desde `.env.example`):

```env
PORT=5000

# Opcional: Solo si quieres integración con WhatsApp
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+tu_numero
```

**Nota**: WhatsApp es completamente opcional. La app funciona perfectamente sin Twilio.

### 4. Ejecutar la Aplicación

```bash
python reminder_bot.py
```

Verás algo como:
```
============================================================
🤖 BOT DE RECORDATORIOS MULTIPLATAFORMA
============================================================

📋 Tareas pendientes: 0
⏰ Frecuencia de recordatorios: Cada 30 minutos
📱 WhatsApp: No configurado (opcional)

🚀 Bot iniciado. Presiona Ctrl+C para detener.

🌐 Interfaz web disponible en: http://localhost:5000
📱 Accede desde cualquier dispositivo en tu red local
```

## 📱 Acceder desde Cualquier Dispositivo

### Desde tu PC
Abre tu navegador y ve a: `http://localhost:5000`

### Desde tu celular o tablet (misma red WiFi)

1. En la PC, averigua tu IP local:
   ```bash
   # Windows
   ipconfig
   # Mac/Linux
   ifconfig
   ```

2. Busca tu dirección IP (ej: `192.168.1.100`)

3. En tu celular/tablet, abre el navegador y ve a:
   ```
   http://192.168.1.100:5000
   ```

### Instalar como App (PWA)

#### En Android (Chrome, Edge, Samsung Internet):
1. Abre la web en el navegador
2. Toca el menú (⋮) → "Agregar a pantalla de inicio" o "Instalar app"
3. La app aparecerá en tu pantalla de inicio como cualquier otra app

#### En iPhone/iPad (Safari):
1. Abre la web en Safari
2. Toca el botón de compartir (□↑)
3. Desplázate y selecciona "Añadir a inicio"
4. La app aparecerá en tu pantalla de inicio

#### En PC (Chrome, Edge):
1. Abre la web en el navegador
2. Verás un botón de "Instalar" en la barra de direcciones
3. Haz clic y confirma la instalación

## 💡 Cómo Usar

### Agregar una Tarea
1. Escribe la tarea en el campo de texto
2. Presiona "➕ Agregar" o la tecla Enter
3. La tarea se agrega a la lista de pendientes

### Completar una Tarea
1. Haz clic en el círculo ⭕ junto a la tarea
2. La tarea se marca como completada ✅
3. **Ya no recibirás recordatorios de esa tarea**

### Ver Diferentes Vistas
- **⏳ Pendientes**: Solo tareas sin completar
- **📋 Todas**: Todas las tareas (pendientes y completadas)
- **✅ Completadas**: Solo tareas finalizadas

### Eliminar una Tarea
1. Haz clic en el botón 🗑️ de basura
2. Confirma la eliminación
3. La tarea se elimina permanentemente

### Recordatorios Automáticos
- Cada 30 minutos recibirás una notificación del navegador
- Solo te recordará las tareas **pendientes**
- Las tareas completadas no aparecen en los recordatorios

## 🎨 Capturas de Pantalla

La interfaz incluye:
- 📊 **Estadísticas**: Contador de tareas pendientes y completadas
- 🎯 **Lista visual**: Diseño limpio y fácil de usar
- 🌈 **Colores modernos**: Diseño atractivo con gradientes
- 📱 **Botones grandes**: Fáciles de tocar en móvil

## ⚙️ Configuración Avanzada

### Cambiar la Frecuencia de Recordatorios

Edita [reminder_bot.py:314](reminder_bot.py#L314):

```python
# Cada 15 minutos
schedule.every(15).minutes.do(enviar_recordatorios)

# Cada hora
schedule.every(1).hours.do(enviar_recordatorios)

# Cada 2 horas
schedule.every(2).hours.do(enviar_recordatorios)

# Diario a las 9 AM
schedule.every().day.at("09:00").do(enviar_recordatorios)
```

### Cambiar el Puerto

Edita el archivo `.env`:
```env
PORT=8080
```

O usa variable de entorno:
```bash
PORT=8080 python reminder_bot.py
```

### Acceso desde Internet (Avanzado)

Para acceder desde cualquier lugar (no solo tu red local):

1. **Opción 1: ngrok (Gratis)**
   ```bash
   ngrok http 5000
   ```
   Te da una URL pública temporal

2. **Opción 2: Deploy en la nube**
   - Heroku (gratis con limitaciones)
   - Railway
   - Render
   - Google Cloud Run

## 📂 Estructura del Proyecto

```
REMINDERBOT/
├── reminder_bot.py           # Servidor principal
├── tasks.json               # Base de datos de tareas
├── requirements.txt         # Dependencias de Python
├── .env                     # Configuración (crear desde .env.example)
├── .env.example            # Plantilla de configuración
├── templates/
│   └── index.html          # Interfaz web
├── static/
│   ├── manifest.json       # Configuración PWA
│   ├── service-worker.js   # Cache offline
│   ├── icon-192.png        # Icono app (pequeño)
│   ├── icon-512.png        # Icono app (grande)
│   └── create_icons.py     # Script para crear iconos
└── README.md               # Esta documentación
```

## 🔧 Solución de Problemas

### No puedo acceder desde mi celular
1. Verifica que ambos dispositivos estén en la misma red WiFi
2. Desactiva temporalmente el firewall en la PC
3. Asegúrate de usar la IP correcta (no `localhost`)
4. El puerto debe estar abierto (por defecto 5000)

### Las notificaciones no funcionan
1. Asegúrate de haber dado permisos de notificación
2. En el navegador, ve a Configuración → Notificaciones
3. Permite notificaciones para tu sitio
4. En iPhone, las notificaciones solo funcionan con la PWA instalada

### La app no se puede instalar
1. **HTTPS requerido**: La PWA solo se instala en HTTPS (excepto localhost)
2. Para producción, necesitas un certificado SSL
3. O usa servicios como ngrok que proveen HTTPS

### Error al crear iconos
```bash
pip install pillow
cd static
python create_icons.py
```

Si Pillow falla, puedes usar cualquier imagen PNG de 192x192 y 512x512 píxeles.

## 💻 Compatibilidad

### Navegadores
| Navegador | Desktop | Mobile |
|-----------|---------|--------|
| Chrome    | ✅      | ✅     |
| Firefox   | ✅      | ✅     |
| Safari    | ✅      | ✅     |
| Edge      | ✅      | ✅     |
| Opera     | ✅      | ✅     |
| Samsung Internet | ❌ | ✅   |

### Sistemas Operativos
- ✅ Windows 10/11
- ✅ macOS
- ✅ Linux
- ✅ Android 5.0+
- ✅ iOS 11.3+ (Safari)

### Dispositivos Probados
- ✅ iPhone (todos los modelos recientes)
- ✅ iPad
- ✅ Samsung Galaxy
- ✅ Xiaomi
- ✅ Huawei
- ✅ OnePlus
- ✅ Google Pixel
- ✅ Tablets Android
- ✅ Laptops y PCs

## 🌟 Características Técnicas

- **Backend**: Python + Flask
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Base de datos**: JSON (sin dependencias externas)
- **PWA**: Service Workers + Web Manifest
- **Notificaciones**: Web Notification API
- **Responsive**: CSS Flexbox + Media Queries
- **Compatible**: Todos los navegadores modernos

## 🎯 Casos de Uso

### Para Estudiantes
```
✓ Estudiar matemáticas
✓ Hacer tarea de inglés
✓ Leer capítulo 5
```

### Para el Trabajo
```
✓ Responder emails
✓ Llamar a cliente
✓ Preparar presentación
```

### Para la Salud
```
✓ Beber agua
✓ Hacer ejercicio
✓ Tomar medicamento
```

### Para el Hogar
```
✓ Lavar ropa
✓ Comprar despensa
✓ Pagar servicios
```

## 📊 Ventajas vs Otras Apps

| Característica | Esta App | Otras Apps |
|----------------|----------|------------|
| Gratis | ✅ | ❌ (muchas con pago) |
| Sin registro | ✅ | ❌ |
| Sin anuncios | ✅ | ❌ |
| Offline | ✅ | ❌ |
| Open source | ✅ | ❌ |
| Tus datos son tuyos | ✅ | ❌ |
| Funciona en cualquier dispositivo | ✅ | ⚠️ |
| Personalizable | ✅ | ❌ |

## 🔐 Privacidad y Seguridad

- ✅ **Sin tracking**: No recopilamos datos
- ✅ **Local first**: Tus datos están en tu dispositivo
- ✅ **Sin cuentas**: No requiere registro ni login
- ✅ **Open source**: Puedes revisar todo el código
- ✅ **Sin conexión a servicios externos** (excepto Twilio opcional)

## 💰 Costos

### Uso Local (Recomendado)
- **100% GRATIS**: Sin costos de ningún tipo
- Funciona en tu red local sin servicios externos

### Uso con WhatsApp (Opcional)
- **Twilio Trial**: Gratuito con crédito limitado
- **Producción**: ~$0.005 por mensaje de WhatsApp

### Deploy en Internet (Opcional)
- **Heroku Free Tier**: Gratis (con limitaciones)
- **Railway**: $5/mes aprox
- **Render**: Plan gratuito disponible

## 🤝 Contribuciones

Este proyecto es de código abierto. Siéntete libre de:
- Reportar bugs
- Sugerir nuevas características
- Hacer fork y modificar a tu gusto
- Compartir con otros

## 📄 Licencia

Este proyecto es de uso libre para fines personales y educativos.

## 💡 Tips y Trucos

### Tip 1: Instalar en Múltiples Dispositivos
Instala la PWA en todos tus dispositivos y comparte el archivo `tasks.json` usando Dropbox, Google Drive o sincronización de archivos.

### Tip 2: Backup Automático
Copia `tasks.json` regularmente para no perder tus tareas.

### Tip 3: Múltiples Usuarios
Cada usuario puede tener su propia copia del bot corriendo en diferente puerto.

### Tip 4: Usar con Cronjo (Ejecutar al iniciar el sistema)

**Windows**: Crear acceso directo en Inicio automático
**Mac/Linux**: Agregar al crontab con `@reboot`

## 📞 Soporte

Si tienes problemas:
1. Revisa la sección "Solución de Problemas"
2. Verifica que todas las dependencias estén instaladas
3. Comprueba los logs en la consola

## ⚠️ Notas Importantes

- La interfaz web funciona **sin necesidad de Twilio/WhatsApp**
- Los recordatorios se muestran como **notificaciones del navegador**
- Mantén el bot corriendo en tu PC para recibir recordatorios
- Para uso 24/7, considera un deploy en la nube

## 🎉 ¡Disfruta tu App de Recordatorios!

Ahora tienes una aplicación completa que funciona en **cualquier dispositivo, cualquier navegador, cualquier marca**. Sin complicaciones, sin pagos, sin publicidad.

¡Que tengas un día productivo! 📋✨
