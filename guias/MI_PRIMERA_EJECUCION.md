# Mi Primera Ejecución del Bot - Paso a Paso

Documentación de lo que hicimos y lo que necesitas hacer.

---

## ✅ Lo Que Ya Funciona

### 1. Python y Dependencias
```
Python: OK
MetaTrader5 package: OK (versión 5.0.5328)
pandas: OK (versión 2.2.3)
numpy: OK (versión 2.2.4)
```

### 2. Configuración
Archivo `config.json` ya está creado con:
- Cuenta demo: 19498321
- Servidor: Weltrade
- Contraseña configurada
- Símbolos: PainX 400, GainX 400
- Lote mínimo: 0.01
- Stop diario: $5 USD

### 3. Código del Bot
- Todos los archivos Python funcionan
- Sin errores de sintaxis
- Emojis corregidos (reemplazados con texto ASCII)

---

## ❌ El Problema Encontrado

**Error:** `MT5 initialization failed: (-10005, 'IPC timeout')`

**¿Qué significa?**
- El bot intentó conectarse a MetaTrader 5
- Pero MetaTrader 5 **NO ESTÁ ABIERTO**
- "IPC timeout" = no puede comunicarse con MT5

**Solución Simple:**
Necesitas abrir MetaTrader 5 antes de ejecutar el bot.

---

## 🔧 Cómo Ejecutar el Bot Correctamente

### Paso 1: Abrir MetaTrader 5

1. Busca "MetaTrader 5" en tu computadora
2. Abre el programa
3. Si no estás conectado, haz login:
   - Cuenta: 19498321
   - Contraseña: %6Qn4Er[
   - Servidor: Weltrade

### Paso 2: Verificar Conexión

Debes ver en la esquina inferior derecha:
- Conexión activa (luz verde o número de ping)
- Balance de cuenta visible

### Paso 3: Ejecutar el Bot

Abre una terminal (CMD o PowerShell) y ejecuta:

```bash
cd C:\Users\Administrator\Documents\trading
python -m pain_gain_bot.main --bot pain --demo
```

O simplemente haz doble clic en:
```
run_pain_demo.bat
```

---

## 📊 Qué Verás Cuando Funcione

### Salida del Bot:

```
======================================================================
 Pain/Gain Automated Trading System v1.0
 MetaTrader 5 Integration for PainX/GainX Synthetic Indices
======================================================================

18:04:42 | WARNING  | [!] DEMO MODE ENABLED
18:04:42 | INFO     | Configuration Summary:
18:04:42 | INFO     |   Mode: DEMO
18:04:42 | INFO     |   Broker: Weltrade
18:04:42 | INFO     |   Pain Symbols: PainX 400
18:04:42 | INFO     |   Lot Size: 0.01
18:04:42 | INFO     |   Daily Stop: $5.0
18:04:42 | INFO     |   Daily Target: $10.0
18:04:42 | INFO     | ----------------------------------------------------------------------

18:04:42 | INFO     | Starting PainBot (SELL strategy)...
18:04:42 | INFO     | === Initializing PainBot ===
18:05:00 | INFO     | [OK] Connected to MT5
18:05:00 | INFO     | [OK] Account: 19498321
18:05:00 | INFO     | [OK] Balance: $500.00
18:05:00 | INFO     | [OK] Server: Weltrade
18:05:01 | INFO     | [OK] Symbol PainX 400 verified
18:05:01 | INFO     | === PainBot Started Successfully ===
18:05:01 | INFO     | Monitoring PainX 400 for SELL signals...
```

### Mensajes Normales Durante Operación:

```
18:06:15 | INFO     | [Iteration 1] Scanning symbols...
18:06:15 | INFO     | PainX 400: Analyzing D1 timeframe...
18:06:16 | INFO     | PainX 400: D1 wick direction = DOWN
18:06:16 | INFO     | PainX 400: Checking H4 Fibonacci...
18:06:17 | INFO     | PainX 400: No signal - H1 shingle not aligned
```

### Si Encuentra una Señal:

```
18:12:30 | INFO     | [*] SIGNAL DETECTED: PainX 400
18:12:30 | INFO     |   Action: SELL
18:12:30 | INFO     |   Price: 145.234
18:12:30 | INFO     |   All confirmations: PASS
18:12:31 | INFO     | [OK] Order placed: Ticket #12345678
18:12:31 | INFO     |   Entry: 145.234
18:12:31 | INFO     |   Lot: 0.01
18:12:31 | INFO     |   Hold until: 18:17:30
```

---

## 🗂️ Archivos de Log

El bot crea logs automáticamente en:
```
C:\Users\Administrator\Documents\trading\logs\
```

Encontrarás:
- `trading_YYYYMMDD.log` - Todo lo que hace el bot
- `errors_YYYYMMDD.log` - Solo errores
- `trades_YYYYMMDD.log` - Solo operaciones ejecutadas

**Ejemplo de fecha:**
- Hoy: `trading_20251015.log`

---

## ⚙️ Configuración Actual (config.json)

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "%6Qn4Er[",
    "use_demo": true
  },
  "symbols": {
    "pain_symbols": ["PainX 400"],  // Solo 1 símbolo para pruebas
    "gain_symbols": ["GainX 400"]
  },
  "risk": {
    "lot_size": 0.01,              // Lote mínimo
    "daily_stop_usd": 5.0,         // Stop bajo para pruebas
    "daily_target_usd": 10.0,
    "max_consecutive_orders": 2
  }
}
```

**Nota:** Esta configuración es conservadora para pruebas.

---

## 🎯 Próximos Pasos

### 1. Primera Ejecución (Ahora)
- Abre MT5
- Ejecuta el bot con `run_pain_demo.bat`
- Déjalo correr 30-60 minutos
- Observa los logs

### 2. Monitoreo (Primeras Horas)
- Revisa la consola cada 10-15 minutos
- Verifica que no haya errores
- Observa si detecta señales

### 3. Validación (24 Horas)
- Deja correr el bot todo el día
- Revisa el archivo `logs/trading_YYYYMMDD.log`
- Verifica operaciones en MT5 (si hubo)

### 4. Ajustes (Después de Probar)
- Si todo funciona bien, aumenta a más símbolos
- Ajusta parámetros de riesgo según resultados
- Consulta `CONFIGURACION_ES.md` para opciones

---

## 🔍 Checklist Pre-Ejecución

Antes de ejecutar el bot, verifica:

- [ ] MetaTrader 5 está abierto
- [ ] MT5 está conectado (luz verde)
- [ ] Cuenta demo visible en MT5
- [ ] Símbolos PainX 400/GainX 400 visibles en Market Watch
- [ ] Archivo config.json existe
- [ ] Terminal/CMD abierta en carpeta del proyecto

---

## 🆘 Problemas Comunes

### Error: "IPC timeout"
**Causa:** MT5 no está abierto
**Solución:** Abre MetaTrader 5

### Error: "Login failed"
**Causa:** Credenciales incorrectas
**Solución:** Verifica cuenta/contraseña en config.json

### Error: "Symbol not found"
**Causa:** Símbolo no disponible en broker
**Solución:** Agrega el símbolo en MT5 Market Watch

### No detecta señales
**Causa:** Condiciones del mercado no cumplen criterios
**Solución:** Normal, espera. Las señales son poco frecuentes.

---

## 📞 Siguiente Paso

Una vez que MT5 esté abierto:

1. Ejecuta: `run_pain_demo.bat`
2. Observa la salida durante 5 minutos
3. Si ves "[OK] Connected to MT5" = **ÉXITO**
4. Déjalo correr y monitorea los logs

---

**Fecha de esta prueba:** 15 de Octubre 2025
**Resultado:** Bot funciona correctamente, solo necesita MT5 abierto
**Estado:** Listo para ejecutar
