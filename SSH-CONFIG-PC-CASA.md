# Configuración SSH - PC Casa

**Fecha de creación:** 2025-11-24
**PC:** PC Casa
**Status:** ✅ ACTIVO

---

## 🔑 Información de la Clave SSH

### Clave Generada
- **Tipo:** RSA 4096-bit
- **Nombre:** `id_rsa_contabo_pc_casa`
- **Ubicación:** `~/.ssh/id_rsa_contabo_pc_casa` (privada)
- **Ubicación pública:** `~/.ssh/id_rsa_contabo_pc_casa.pub`
- **Fingerprint:** `SHA256:r71T7tjd2n934eXL1mt37agykRotvNbA5M/ViCB/Hpg`
- **Comentario:** `pc-casa-contabo`

### Servidor
- **IP:** 213.199.42.218
- **Usuario:** root
- **Hostname:** cristianco
- **Ubicación de claves:** `/root/.ssh/authorized_keys`

---

## 📝 Configuración SSH (~/.ssh/config)

```bash
# ============================================
# Agente Financiero - Contabo Server
# ============================================

# PC Casa - Conexión al servidor Contabo
Host contabo
    HostName 213.199.42.218
    User root
    IdentityFile ~/.ssh/id_rsa_contabo_pc_casa
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Alias alternativo
Host agente-financiero
    HostName 213.199.42.218
    User root
    IdentityFile ~/.ssh/id_rsa_contabo_pc_casa
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

---

## ✅ Comandos de Uso

### Conexión Básica
```bash
# Usando alias principal
ssh contabo

# Usando alias alternativo
ssh agente-financiero

# Conexión directa (sin alias)
ssh -i ~/.ssh/id_rsa_contabo_pc_casa root@213.199.42.218
```

### Comandos Remotos
```bash
# Ver servicios Docker
ssh contabo "docker service ls"

# Ver logs del agente financiero
ssh contabo "docker service logs agente-financiero_api-whatsapp --tail 50"

# Ver estado del servicio
ssh contabo "docker service ps agente-financiero_api-whatsapp"

# Listar archivos en /root
ssh contabo "ls -la /root/"
```

### Transferencia de Archivos
```bash
# Copiar archivo local al servidor
scp archivo.txt contabo:/root/

# Copiar archivo del servidor a local
scp contabo:/root/archivo.txt .

# Copiar directorio completo
scp -r directorio/ contabo:/root/
```

### Deployment
```bash
# Build y deploy completo
ssh contabo "cd /root && docker build --no-cache -t agente-financiero-backend:latest . && docker service update --force agente-financiero_api-whatsapp"

# Solo update del servicio
ssh contabo "docker service update --force agente-financiero_api-whatsapp"
```

---

## 🔒 Seguridad

### Permisos Correctos
```bash
# Local (en este PC)
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa_contabo_pc_casa
chmod 644 ~/.ssh/id_rsa_contabo_pc_casa.pub
chmod 600 ~/.ssh/config

# Servidor (ya configurados)
chmod 700 /root
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

### Múltiples PCs
Esta configuración NO afecta otros PCs. El servidor tiene múltiples claves públicas en `/root/.ssh/authorized_keys`:
- Una línea por cada PC autorizado
- Ambos PCs (casa y trabajo) pueden conectarse simultáneamente sin problemas
- Cada PC usa su propia clave privada

---

## 🧪 Verificación

### Test Básico
```bash
# Debe conectar SIN pedir password
ssh contabo "echo 'Conexión exitosa'"
```

**Resultado esperado:**
```
Conexión exitosa
```

### Test Completo
```bash
# Test de Docker, hostname y fecha
ssh contabo "echo '✅ SSH OK' && hostname && docker service ls | head -3"
```

**Resultado esperado:**
```
✅ SSH OK
cristianco
ID             NAME                             MODE         REPLICAS   IMAGE
mf8wn2crj6ab   agente-financiero_api-whatsapp   replicated   1/1        agente-financiero-api:latest
a0ruq47kvcc6   bolt_bolt                        replicated   1/1        hipnologo/bolt.diy:latest
```

---

## 🚨 Troubleshooting

### Si pide password
```bash
# 1. Verificar que la clave está en el servidor
ssh -o PasswordAuthentication=yes root@213.199.42.218 "cat ~/.ssh/authorized_keys | grep pc-casa"

# 2. Verificar permisos locales
ls -la ~/.ssh/id_rsa_contabo_pc_casa

# 3. Verificar configuración SSH
cat ~/.ssh/config | grep -A 10 "Host contabo"

# 4. Probar con verbose para ver el error
ssh -v contabo
```

### Regenerar clave si es necesario
```bash
# 1. Generar nueva clave
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_contabo_pc_casa_new -C "pc-casa-contabo-new"

# 2. Copiar al servidor
cat ~/.ssh/id_rsa_contabo_pc_casa_new.pub | ssh root@213.199.42.218 "cat >> ~/.ssh/authorized_keys"

# 3. Actualizar ~/.ssh/config con el nuevo nombre
```

---

## 📊 Información del Servidor

### Servicios Principales
- **Backend:** agente-financiero_api-whatsapp (replica 1/1)
- **Bolt:** bolt_bolt
- **Evolution API:** evolution_evolution_api
- **Supabase:** supabase_db (PostgreSQL 15.8)
- **Traefik:** traefik_traefik (reverse proxy)

### Dominios
- Backend: https://devbackend.tuagenteia.click
- Evolution API: https://devevoapi.tuagenteia.click
- Supabase: https://devsupabase.tuagenteia.click

### Rutas Importantes
- Backend: `/root/backend/`
- Archivos raíz: `/root/`
- Logs Docker: `docker service logs <service-name>`

---

## 📌 Notas Importantes

1. **No compartir la clave privada** (`id_rsa_contabo_pc_casa`)
2. **Hacer backup** de la clave privada en USB encriptada
3. **Nunca commitear** la clave privada a Git
4. **Archivo `.ssh/config`** NO debe commitearse (información sensible)
5. **La clave del PC de trabajo** NO se ve afectada por esta configuración
6. **Ambos PCs** pueden conectarse simultáneamente sin problemas

---

## ✅ Checklist de Configuración

- [x] Clave SSH generada (RSA 4096-bit)
- [x] Clave pública agregada al servidor
- [x] Archivo ~/.ssh/config configurado
- [x] Permisos correctos en archivos SSH
- [x] Permisos correctos en servidor (/root)
- [x] Conexión passwordless verificada
- [x] Comandos Docker funcionando
- [x] Documentación actualizada

---

**Última actualización:** 2025-11-24
**Responsable:** jesusdmm223
**PC:** PC Casa
**Status:** ✅ Operacional
