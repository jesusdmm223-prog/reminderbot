# 🤖 Guía de Uso - Bot de Recordatorios por WhatsApp

## 📱 Cómo usar el bot

### 1. Crear una tarea
Escribe tu tarea y termina con la palabra "listo"

**Ejemplos:**
```
Comprar pan a las 3pm listo
Llamar al doctor 18:30 listo
Reunión mañana 10am listo
Pagar recibo de luz a las 5 de la tarde listo
```

El bot responderá:
```
✅ Tarea creada:

📝 Comprar pan
🕐 15:00 - 2025-11-26

💡 Te recordaré a la hora indicada.
```

### 2. Ver tu lista de tareas
Escribe: `lista`

Recibirás:
```
📋 Tus tareas pendientes:

1. Comprar pan - 15:00
2. Llamar al doctor - 18:30
3. Reunión - 10:00

📊 Total: 3 tarea(s)

💡 Para completar una tarea escribe: completar 1
```

### 3. Completar una tarea (marcar como "chuleada")
Escribe: `completar 1` o `✓1`

El bot responderá:
```
✅ Tarea completada: Comprar pan
```

**IMPORTANTE:** Una vez que completas una tarea, el bot **DEJA de enviar recordatorios** de esa tarea.

### 4. Ver ayuda
Escribe: `ayuda`

Recibirás la lista completa de comandos.

---

## ⏰ Sistema de Recordatorios

### Cómo funcionan los recordatorios

1. **A la hora indicada** recibes el primer recordatorio
2. Si **NO completas** la tarea, el bot seguirá enviando recordatorios **cada 5 minutos**
3. La urgencia va aumentando:
   - 🟡 **IMPORTANTE** (después de 2 recordatorios)
   - 🟠 **URGENTE** (después de 4 recordatorios)
   - 🔴 **MUY URGENTE** (después de 6 recordatorios)

### Ejemplo de recordatorio

```
⏰ RECORDATORIOS - jesusdmm223@gmail.com

🟡 IMPORTANTE IMPORTANTE
#1: Comprar pan
📅 2025-11-26 ⏰ 15:00
(Recordatorio #3)

📊 Total: 1 tarea(s) pendiente(s)

💡 Completa las tareas en la app para dejar de recibir recordatorios.
```

---

## 📋 Formatos de Hora Aceptados

El bot entiende múltiples formatos:

- `3pm`, `3 pm`, `15:00`
- `a las 3`, `a las 15:30`
- `18:30`, `6:30pm`
- `mañana 10am`

---

## ❓ Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `[tarea] listo` | Crear tarea nueva | `Comprar pan a las 3pm listo` |
| `lista` | Ver tareas pendientes | `lista` |
| `completar X` | Completar tarea número X | `completar 1` |
| `✓X` | Completar tarea (atajo) | `✓1` |
| `ayuda` | Ver comandos | `ayuda` |

---

## 🔧 Configuración Técnica

### Variables de Entorno (Render)

```
EVOLUTION_API_URL=https://devevoapi.tuagenteia.click
EVOLUTION_API_KEY=e50bdaf76404943a4e2d13d7ff7a49a2
EVOLUTION_INSTANCE=reminderbot
SECRET_KEY=mi_clave_super_secreta_12345
PORT=5000
```

### Webhook Evolution API

```json
{
  "url": "https://reminderbot-qsvy.onrender.com/webhook/whatsapp",
  "enabled": true,
  "events": ["MESSAGES_UPSERT"],
  "webhookByEvents": false
}
```

---

## 🧪 Pruebas

### Test 1: Crear tarea
```
Tú: Comprar pan a las 3pm listo
Bot: ✅ Tarea creada: Comprar pan - 15:00
```

### Test 2: Ver lista
```
Tú: lista
Bot: 📋 Tus tareas pendientes:
     1. Comprar pan - 15:00
```

### Test 3: Completar
```
Tú: completar 1
Bot: ✅ Tarea completada: Comprar pan
```

---

## 🚨 Solución de Problemas

### El bot no responde
1. Verifica que el servicio esté "Live" en Render
2. Verifica las variables de entorno
3. Revisa los logs de Render

### No detecta la hora
Asegúrate de incluir una hora clara:
- ✅ "Comprar pan a las 3pm listo"
- ✅ "Comprar pan 15:00 listo"
- ❌ "Comprar pan listo" (sin hora)

### No recibo recordatorios
1. Verifica que WhatsApp esté conectado (Evolution API)
2. Verifica que la tarea NO esté completada
3. Espera hasta la hora programada

---

**Última actualización:** 2025-11-26
**Status:** ✅ Bot funcionando
**WhatsApp:** Conectado
**Webhook:** Configurado
