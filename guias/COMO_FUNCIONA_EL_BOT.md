# Cómo Funciona el Bot - Explicación Paso a Paso

Entendiendo qué hace el bot desde que lo ejecutas hasta que coloca una operación.

---

## 🚀 1. Inicio del Bot (Primeros 5 Segundos)

### Paso 1.1: Carga de Configuración
```
18:04:42 | INFO | Configuration Summary:
18:04:42 | INFO |   Mode: DEMO
18:04:42 | INFO |   Broker: Weltrade
```

**¿Qué hace?**
- Lee el archivo `config.json`
- Carga todos los parámetros (símbolos, lotes, stops, etc.)
- Muestra un resumen en pantalla

**Archivos involucrados:**
- `config.json` (tu configuración)
- `pain_gain_bot/config.py` (código que lee el JSON)

---

### Paso 1.2: Conexión a MT5
```
18:05:00 | INFO | [OK] Connected to MT5
18:05:00 | INFO | [OK] Account: 19498321
18:05:00 | INFO | [OK] Balance: $500.00
```

**¿Qué hace?**
1. Busca MetaTrader 5 en tu computadora
2. Se conecta usando la API de Python
3. Verifica que la cuenta esté activa
4. Obtiene información de balance
5. Verifica la conexión con el servidor

**Si falla aquí:**
- MT5 no está abierto → Error "IPC timeout"
- Credenciales incorrectas → Error "Login failed"
- Sin internet → Error "Connection failed"

**Archivo involucrado:**
- `pain_gain_bot/data/mt5_connector.py`

---

### Paso 1.3: Verificación de Símbolos
```
18:05:01 | INFO | [OK] Symbol PainX 400 verified
```

**¿Qué hace?**
1. Para cada símbolo en config (PainX 400, PainX 600, etc.)
2. Verifica que existe en MT5
3. Lo activa en Market Watch si no está
4. Obtiene información (spread, tick size, etc.)

**Si falla aquí:**
- Símbolo no existe → Error "Symbol not found"
- Broker no ofrece ese símbolo → Agrégalo manualmente en MT5

**Archivo involucrado:**
- `pain_gain_bot/data/mt5_connector.py` (función `verify_symbols`)

---

### Paso 1.4: Inicialización de Gestión de Riesgo
```
18:05:02 | INFO | Risk Manager initialized
18:05:02 | INFO | Daily P/L: $0.00
18:05:02 | INFO | Can trade: YES
```

**¿Qué hace?**
1. Inicia el contador de pérdidas/ganancias del día
2. Verifica si está en horario de trading (19:00-06:00 COL)
3. Revisa si no se alcanzaron límites diarios
4. Prepara controles de riesgo

**Archivo involucrado:**
- `pain_gain_bot/strategy/risk_manager.py`

---

## 🔄 2. Loop Principal (Se Repite Cada 30 Segundos)

Una vez iniciado, el bot entra en un **loop infinito** que se ejecuta cada 30 segundos:

```
18:06:15 | INFO | [Iteration 1] Scanning symbols...
```

### Paso 2.1: Verificación de Límites Diarios

**¿Qué hace?**
```python
# El bot pregunta:
¿Ya perdimos $5 hoy? → Si SÍ: DETENER trading
¿Ya ganamos $10 hoy? → Si SÍ: DETENER trading
¿Estamos en horario? → Si NO: Esperar
```

**Mensajes posibles:**
```
18:06:15 | WARNING | Daily stop reached: -$5.00 (limit: $5.00)
18:06:15 | INFO | Trading halted for the day
```

O si todo OK:
```
18:06:15 | INFO | Daily P/L: +$2.50 | Can trade: YES
```

**Archivo involucrado:**
- `pain_gain_bot/strategy/risk_manager.py` (función `check_daily_limits`)

---

### Paso 2.2: Gestión de Posiciones Abiertas

**¿Qué hace?**
Si ya tienes operaciones abiertas, las gestiona:

```python
# Para cada posición abierta:
1. ¿Ya pasaron 5 minutos? → Cerrar
2. ¿La línea morada se rompió? → Stop Loss, cerrar
3. ¿El precio se movió a favor? → Monitorear
```

**Mensajes:**
```
18:07:00 | INFO | Managing position #12345678
18:07:00 | INFO |   Symbol: PainX 400
18:07:00 | INFO |   Type: SELL
18:07:00 | INFO |   Entry: 145.234
18:07:00 | INFO |   Current: 145.180
18:07:00 | INFO |   Profit: +$0.54
18:07:00 | INFO |   Hold time: 3/5 minutes
```

Si es momento de cerrar:
```
18:12:00 | INFO | [OK] 5 minutes elapsed - closing position
18:12:01 | INFO | Position #12345678 closed at 145.150
18:12:01 | INFO | Profit: +$0.84
```

**Archivo involucrado:**
- `pain_gain_bot/strategy/order_manager.py` (función `manage_positions`)

---

### Paso 2.3: Escaneo de Símbolos para Nuevas Señales

Si no hay posiciones abiertas (o ya pasó el tiempo de espera), busca nuevas señales:

```
18:06:15 | INFO | PainX 400: Scanning for SELL signals...
```

**Aquí empieza el análisis multi-temporalidad:**

---

## 📊 3. Análisis Multi-Temporalidad (El Corazón del Bot)

### Paso 3.1: Análisis D1 (Daily)
```
18:06:16 | INFO | PainX 400: D1 - Checking wick direction...
18:06:16 | INFO | PainX 400: D1 wick = DOWN (lower wick larger)
```

**¿Qué hace?**
```python
# Mira la vela ANTERIOR (ya cerrada) del gráfico D1
1. Compara mecha superior vs mecha inferior
2. Si mecha inferior > mecha superior → Sesgo DOWN (SELL)
3. Si mecha superior > mecha inferior → Sesgo UP (BUY)
4. Calcula el 50% de la mecha para stop loss futuro
```

**Archivo involucrado:**
- `pain_gain_bot/indicators/technical.py` (función `check_wick_direction`)

**Para PainBot (SELL):**
- Necesita mecha inferior larga → Sesgo DOWN
- Si no → Rechaza la señal inmediatamente

**Mensajes posibles:**
```
18:06:16 | INFO | D1: PASS - Lower wick detected (sesgo DOWN)
```
O:
```
18:06:16 | INFO | D1: FAIL - Upper wick (necesitamos lower wick para SELL)
18:06:16 | INFO | PainX 400: No signal
```

---

### Paso 3.2: Análisis H4 (4 Horas)
```
18:06:17 | INFO | PainX 400: H4 - Checking Fibonacci 50%...
```

**¿Qué hace?**
```python
# Busca el último swing en M15 (high-low)
# Calcula Fibonacci 50%
# Verifica si vela H4 previa cubrió ≥50% del swing

1. Obtiene datos M15 (últimas 100 velas)
2. Encuentra punto más alto (swing high)
3. Encuentra punto más bajo (swing low)
4. Calcula 50% entre ellos
5. Verifica si H4 tocó ese nivel
```

**Archivo involucrado:**
- `pain_gain_bot/indicators/technical.py` (función `calculate_fibonacci`)
- `pain_gain_bot/strategy/signals.py` (verifica H4)

**Mensajes:**
```
18:06:17 | INFO | M15 Swing: High=145.890 Low=145.120
18:06:17 | INFO | Fib 50%: 145.505
18:06:17 | INFO | H4 previous: High=145.620 Low=145.380
18:06:17 | INFO | H4: PASS - Covered 50% level
```

O si falla:
```
18:06:17 | INFO | H4: FAIL - Did not reach 50% Fibonacci
18:06:17 | INFO | PainX 400: No signal
```

---

### Paso 3.3: Análisis H1 (1 Hora)
```
18:06:18 | INFO | PainX 400: H1 - Checking Shingle position...
```

**¿Qué hace?**
```python
# Calcula el indicador Shingle (EMA de 50 períodos)
# Verifica posición del precio respecto al Shingle

1. Obtiene datos H1
2. Calcula EMA(50) = Shingle
3. Obtiene precio actual
4. Para SELL: Precio debe estar DEBAJO del Shingle rojo
5. Para BUY: Precio debe estar ARRIBA del Shingle verde
```

**Archivo involucrado:**
- `pain_gain_bot/indicators/technical.py` (función `calculate_shingle`)

**Mensajes:**
```
18:06:18 | INFO | H1 Shingle: 145.678 (RED)
18:06:18 | INFO | Current price: 145.234
18:06:18 | INFO | H1: PASS - Price below red shingle
```

---

### Paso 3.4: Análisis M30 y M15 (Snake)
```
18:06:19 | INFO | PainX 400: M30/M15 - Checking Snake color...
```

**¿Qué hace?**
```python
# Calcula el indicador Snake (cruce de EMAs)
# Verifica que AMBOS (M30 Y M15) tengan el color correcto

1. M30: Calcula EMA(8) y EMA(21)
2. Si EMA(8) < EMA(21) → Snake ROJO (bajista)
3. Si EMA(8) > EMA(21) → Snake VERDE (alcista)
4. Repite lo mismo para M15
5. Para SELL: Ambos deben ser ROJOS
6. Para BUY: Ambos deben ser VERDES
```

**Archivo involucrado:**
- `pain_gain_bot/indicators/technical.py` (función `calculate_snake`)

**Mensajes:**
```
18:06:19 | INFO | M30 Snake: RED (EMA8=145.345 < EMA21=145.456)
18:06:19 | INFO | M15 Snake: RED (EMA8=145.289 < EMA21=145.378)
18:06:19 | INFO | M30/M15: PASS - Both snakes are RED
```

Si uno falla:
```
18:06:19 | INFO | M30 Snake: RED
18:06:19 | INFO | M15 Snake: GREEN ← PROBLEMA
18:06:19 | INFO | M30/M15: FAIL - Colors don't match
18:06:19 | INFO | PainX 400: No signal
```

---

### Paso 3.5: Análisis M5 y M1 (Purple Line Break-Retest)
```
18:06:20 | INFO | PainX 400: M5/M1 - Checking purple line pattern...
```

**¿Qué hace?**
```python
# Esta es la confirmación FINAL para entrar

1. Calcula Purple Line en M5 (EMA de 34 períodos)
2. Verifica M1 para patrón break-retest:

   Para SELL:
   a) Precio debe estar DEBAJO del Snake rojo en M1
   b) Precio debe haber ROTO la Purple Line hacia abajo
   c) Precio debe haber RETESTEADO (vuelto a tocar) la Purple Line
   d) Precio está volviendo a bajar

   Para BUY:
   a) Precio debe estar ARRIBA del Snake verde en M1
   b) Precio debe haber ROTO la Purple Line hacia arriba
   c) Precio debe haber RETESTEADO la Purple Line
   d) Precio está volviendo a subir
```

**Archivo involucrado:**
- `pain_gain_bot/indicators/technical.py` (función `calculate_purple_line`)
- `pain_gain_bot/strategy/signals.py` (verifica patrón break-retest)

**Mensajes si TODO pasa:**
```
18:06:20 | INFO | M1 Snake: RED
18:06:20 | INFO | Price below snake: YES
18:06:20 | INFO | Purple line: 145.245
18:06:20 | INFO | Break detected: YES (price crossed 145.245)
18:06:20 | INFO | Retest detected: YES (price touched 145.245 again)
18:06:20 | INFO | M5/M1: PASS - Break-retest pattern confirmed
```

---

## 🎯 4. Generación de Señal

Si **TODAS** las confirmaciones pasaron:

```
18:06:21 | INFO | ========================================
18:06:21 | INFO | [*] SIGNAL DETECTED: PainX 400
18:06:21 | INFO | ========================================
18:06:21 | INFO | Action: SELL
18:06:21 | INFO | Price: 145.234
18:06:21 | INFO |
18:06:21 | INFO | Confirmations:
18:06:21 | INFO |   D1 Wick: PASS (DOWN)
18:06:21 | INFO |   H4 Fib50%: PASS
18:06:21 | INFO |   H1 Shingle: PASS (below red)
18:06:21 | INFO |   M30 Snake: PASS (red)
18:06:21 | INFO |   M15 Snake: PASS (red)
18:06:21 | INFO |   M1 Position: PASS (below red snake)
18:06:21 | INFO |   Purple Break: PASS
18:06:21 | INFO |   Purple Retest: PASS
18:06:21 | INFO | ========================================
```

**Archivo involucrado:**
- `pain_gain_bot/strategy/signals.py` (función `generate_signal`)

---

## 💰 5. Ejecución de Orden

Ahora el bot verifica si **puede** abrir la orden:

### Paso 5.1: Verificaciones de Seguridad
```python
1. ¿Pasó el tiempo de espera? (5 min hold + 1 vela M5)
2. ¿No llegamos a máximo de órdenes consecutivas? (máx 3)
3. ¿El precio sigue más allá de la Purple Line?
```

**Mensajes:**
```
18:06:22 | INFO | Checking if can open order...
18:06:22 | INFO | Wait period: OK (last order was 15 min ago)
18:06:22 | INFO | Consecutive orders: 1/3
18:06:22 | INFO | Purple line position: OK
18:06:22 | INFO | Can open order: YES
```

---

### Paso 5.2: Cálculo de Volumen
```python
# Del config.json:
lot_size = 0.01  # Lo que configuraste
```

**Verifica:**
- Lote no es menor al mínimo del broker (0.01)
- Lote no es mayor al máximo permitido
- Balance es suficiente

---

### Paso 5.3: Envío de Orden a MT5
```
18:06:23 | INFO | Sending SELL order for PainX 400...
18:06:23 | INFO |   Volume: 0.01 lots
18:06:23 | INFO |   Price: 145.234
```

**¿Qué hace internamente?**
```python
# Llama a MT5 API:
mt5.order_send({
    'action': mt5.TRADE_ACTION_DEAL,
    'symbol': 'PainX 400',
    'volume': 0.01,
    'type': mt5.ORDER_TYPE_SELL,
    'price': 145.234,
    'magic': 100001,  # Número mágico del PainBot
    'comment': 'PainBot-SELL'
})
```

**Archivo involucrado:**
- `pain_gain_bot/data/mt5_connector.py` (función `send_order`)

---

### Paso 5.4: Confirmación
```
18:06:24 | INFO | ========================================
18:06:24 | INFO | [OK] ORDER EXECUTED
18:06:24 | INFO | ========================================
18:06:24 | INFO | Ticket: #12345678
18:06:24 | INFO | Symbol: PainX 400
18:06:24 | INFO | Type: SELL
18:06:24 | INFO | Volume: 0.01 lots
18:06:24 | INFO | Entry Price: 145.234
18:06:24 | INFO | Entry Time: 2025-10-15 18:06:24
18:06:24 | INFO | Hold until: 2025-10-15 18:11:24 (5 min)
18:06:24 | INFO | ========================================
```

**También se guarda en:**
- Log principal: `logs/trading_YYYYMMDD.log`
- Log de trades: `logs/trades_YYYYMMDD.log`
- Terminal MT5 (pestaña "Trade")

---

## ⏱️ 6. Gestión de Posición Abierta

Ahora el bot monitorea la posición cada 30 segundos:

```
18:06:54 | INFO | Managing position #12345678
18:06:54 | INFO | Time elapsed: 0.5/5.0 minutes
18:06:54 | INFO | Current price: 145.198
18:06:54 | INFO | Floating P/L: +$0.36
```

```
18:07:24 | INFO | Time elapsed: 1.0/5.0 minutes
18:07:24 | INFO | Current price: 145.156
18:07:24 | INFO | Floating P/L: +$0.78
```

### Verifica Dos Cosas:

**1. ¿Ya pasaron 5 minutos?**
```python
if tiempo >= 5 minutos:
    Cerrar posición con ganancia/pérdida actual
```

**2. ¿La Purple Line se rompió en contra?**
```python
# Para SELL:
if precio > purple_line:  # Subió y rompió la línea
    STOP LOSS - cerrar inmediatamente

# Para BUY:
if precio < purple_line:  # Bajó y rompió la línea
    STOP LOSS - cerrar inmediatamente
```

---

## 🔚 7. Cierre de Posición

### Escenario 1: Cierre Normal (5 minutos)
```
18:11:24 | INFO | ========================================
18:11:24 | INFO | [OK] 5 MINUTES ELAPSED - CLOSING
18:11:24 | INFO | ========================================
18:11:25 | INFO | Closing position #12345678...
18:11:26 | INFO | Position closed successfully
18:11:26 | INFO | Entry: 145.234
18:11:26 | INFO | Exit: 145.120
18:11:26 | INFO | Profit: +$1.14
18:11:26 | INFO | ========================================
```

### Escenario 2: Stop Loss (Purple Line)
```
18:08:15 | INFO | [!] PURPLE LINE BREAK DETECTED
18:08:15 | INFO | Price: 145.289 > Purple: 145.245
18:08:15 | INFO | STOP LOSS triggered - closing position
18:08:16 | INFO | Position closed
18:08:16 | INFO | Entry: 145.234
18:08:16 | INFO | Exit: 145.289
18:08:16 | INFO | Loss: -$0.55
```

---

## 🔄 8. Período de Espera (Re-entry Rules)

Después de cerrar, el bot espera:

```
18:11:27 | INFO | Position closed. Entering wait period...
18:11:27 | INFO | Must wait 1 M5 candle (5 minutes)
18:11:27 | INFO | Next entry allowed after: 18:16:27
```

Durante este tiempo:
- Sigue analizando el mercado
- NO abre nuevas órdenes
- Cuenta el tiempo de espera

```
18:12:00 | INFO | Wait period: 0.5/1.0 candles (2.5 min remaining)
18:13:00 | INFO | Wait period: 0.8/1.0 candles (1 min remaining)
18:16:27 | INFO | [OK] Wait period complete - can trade again
```

---

## 📊 9. Re-entrada (3ra vela M5)

Si detecta señal nuevamente:

```
18:16:30 | INFO | Signal detected again on PainX 400
18:16:30 | INFO | Wait period: OK
18:16:30 | INFO | This would be entry #2 (max 3 consecutive)
18:16:30 | INFO | Purple line position: OK
18:16:31 | INFO | [OK] Opening order...
```

Si ya hubo 3 operaciones consecutivas:
```
18:21:30 | INFO | Signal detected but...
18:21:30 | INFO | [!] Max consecutive orders reached (3/3)
18:21:30 | INFO | Cannot open new order - waiting for different symbol
```

---

## 🌙 10. Fin del Día

Al final de la sesión:

```
06:00:00 | INFO | ========================================
06:00:00 | INFO | SESSION END - 06:00:00
06:00:00 | INFO | ========================================
06:00:00 | INFO | Daily Summary:
06:00:00 | INFO |   Total Trades: 8
06:00:00 | INFO |   Wins: 5
06:00:00 | INFO |   Losses: 3
06:00:00 | INFO |   Win Rate: 62.5%
06:00:00 | INFO |   Total P/L: +$3.45
06:00:00 | INFO | ========================================
06:00:00 | INFO | Trading halted until 19:00:00
```

El bot sigue corriendo pero no opera hasta las 19:00 nuevamente.

---

## 📝 Resumen del Flujo Completo

```
1. INICIO
   ↓
2. CONEXIÓN MT5
   ↓
3. LOOP cada 30 seg:
   ↓
   ├─ Verificar límites diarios
   ├─ Gestionar posiciones abiertas
   └─ Buscar nuevas señales:
      │
      ├─ D1: Wick direction ✓
      ├─ H4: Fibonacci 50% ✓
      ├─ H1: Shingle position ✓
      ├─ M30/M15: Snake color ✓
      └─ M5/M1: Purple break-retest ✓
         │
         └─ SEÑAL COMPLETA
            ↓
         Verificar puede operar
            ↓
         ABRIR ORDEN
            ↓
         GESTIONAR 5 min
            ↓
         CERRAR
            ↓
         ESPERAR 1 vela M5
            ↓
         Volver al LOOP
```

---

## 🎓 Conceptos Clave

### Multi-Timeframe = Filtro en Cascada
Cada temporalidad es un **filtro**. Si falla uno, rechaza la señal inmediatamente.

### Purple Line = Gatillo de Entrada
Es el indicador más importante. Determina el momento exacto de entrada.

### Hold 5 Min = Disciplina
No importa si sube o baja, cierra a los 5 minutos (excepto stop loss).

### Wait 1 Candle = Evitar Overtrading
Fuerza al bot a esperar, evita demasiadas operaciones seguidas.

### Max 3 Consecutive = Protección
Si un símbolo da 3 señales malas seguidas, para de operarlo temporalmente.

---

**¿Entiendes ahora cómo funciona cada parte?**

Si quieres que profundice en alguna sección específica (indicadores, gestión de riesgo, etc.), dime cuál te interesa.
