# Configurar Variables de Entorno en Render

## 📋 Pasos para agregar las variables de entorno

1. **Ve a tu dashboard de Render:** https://dashboard.render.com/
2. **Selecciona tu servicio:** `reminderbot`
3. **Ve a la pestaña "Environment"** (en el menú lateral izquierdo)
4. **Haz clic en "Add Environment Variable"**
5. **Agrega las siguientes variables:**

### Variables requeridas:

| Key | Value |
|-----|-------|
| `EVOLUTION_API_URL` | `https://devevoapi.tuagenteia.click` |
| `EVOLUTION_API_KEY` | `e50bdaf76404943a4e2d13d7ff7a49a2` |
| `EVOLUTION_INSTANCE` | `reminderbot` |
| `SECRET_KEY` | `mi_clave_super_secreta_12345` |
| `PORT` | `5000` |

## 🔄 Después de agregar las variables:

1. Render **automáticamente reiniciará** el servicio
2. Espera a que el servicio se vuelva a desplegar (puede tardar 1-2 minutos)
3. Una vez que el servicio esté "Live", los recordatorios se enviarán por WhatsApp

## 📱 Verificar que WhatsApp está conectado:

1. Abre el archivo [qr-whatsapp.html](qr-whatsapp.html) en tu navegador
2. Escanea el código QR con tu WhatsApp
3. Una vez conectado, el bot podrá enviar mensajes

## 🧪 Probar el bot:

1. Crea una tarea con fecha/hora vencida en https://reminderbot-qsvy.onrender.com
2. Espera 5 minutos (el bot verifica cada 5 minutos)
3. Deberías recibir un mensaje de WhatsApp con el recordatorio

## ❓ Solución de problemas:

**Si no recibes mensajes de WhatsApp:**

1. Verifica que las variables de entorno estén configuradas correctamente
2. Verifica que WhatsApp esté conectado (escanear QR de nuevo si es necesario)
3. Revisa los logs de Render para ver si hay errores:
   - Ve a tu servicio en Render
   - Haz clic en "Logs"
   - Busca mensajes como "✅ WhatsApp enviado a..." o "❌ Error al enviar WhatsApp..."

**Si el QR code expira:**

1. Ejecuta este comando para obtener un nuevo QR:
```bash
curl -s -X GET "https://devevoapi.tuagenteia.click/instance/connect/reminderbot" -H "apikey: e50bdaf76404943a4e2d13d7ff7a49a2"
```

2. Copia el campo `base64` y pégalo en qr-whatsapp.html reemplazando el src de la imagen

---

**Última actualización:** 2025-11-24
**Status:** ✅ Configuración completa
