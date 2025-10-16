# Guía de Pruebas - Sistema Pain/Gain

Procedimientos para validar el bot antes del despliegue en vivo.

---

## Fases de Prueba

### Fase 1: Validación de Instalación ✅
### Fase 2: Prueba de Conexión ✅
### Fase 3: Verificación de Indicadores ✅
### Fase 4: Prueba de Generación de Señales ✅
### Fase 5: Prueba de Ejecución de Órdenes ✅
### Fase 6: Prueba de Gestión de Riesgo ✅
### Fase 7: Trading Demo Extendido ✅
### Fase 8: Despliegue en Vivo (con riesgo mínimo) ✅

---

## Fase 1: Validación de Instalación

### 1.1 Verificar Instalación de Python

```bash
python --version
# Esperado: Python 3.11.0 o superior

pip --version
# Esperado: pip 22.3 o superior
```

### 1.2 Verificar Instalación de MT5

1. Abre MetaTrader 5
2. Revisa versión (Ayuda → Acerca de)
3. Verifica que el login funciona manualmente
4. Confirma que los símbolos estén visibles en Market Watch

### 1.3 Verificar Dependencias

```bash
cd C:\Users\Administrator\Documents\trading
pip install -r requirements_bot.txt
```

Todos los paquetes deben instalarse sin errores.

### 1.4 Verificar Estructura del Proyecto

Verifica que todos los archivos existan:

```
pain_gain_bot/
├── __init__.py ✓
├── config.py ✓
├── main.py ✓
├── bots/ ✓
├── data/ ✓
├── indicators/ ✓
├── strategy/ ✓
└── utils/ ✓
```

---

## Fase 2: Prueba de Conexión

### 2.1 Probar Integración Python-MT5

Crea archivo de prueba `test_connection.py`:

```python
import MetaTrader5 as mt5

# Inicializar MT5
if not mt5.initialize():
    print("❌ Fallo al inicializar MT5")
    quit()

print("✅ MT5 inicializado correctamente")

# Login a cuenta demo
account = 19498321
password = "TU_CONTRASEÑA"
server = "Weltrade"

if mt5.login(account, password=password, server=server):
    print(f"✅ Conectado a cuenta {account}")

    # Obtener info de cuenta
    account_info = mt5.account_info()
    print(f"  Balance: ${account_info.balance}")
    print(f"  Apalancamiento: 1:{account_info.leverage}")
else:
    print("❌ Login falló")

mt5.shutdown()
```

Ejecutar:
```bash
python test_connection.py
```

**Salida Esperada:**
```
✅ MT5 inicializado correctamente
✅ Conectado a cuenta 19498321
  Balance: $500.00
  Apalancamiento: 1:10000
```

### 2.2 Probar Acceso a Símbolos

```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(19498321, password="TU_CONTRASEÑA", server="Weltrade")

symbols = ["PainX 400", "PainX 600", "PainX 800", "PainX 999",
           "GainX 400", "GainX 600", "GainX 800", "GainX 999"]

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info:
        print(f"✅ {symbol}: Spread={info.spread} puntos")
    else:
        print(f"❌ {symbol}: No encontrado")

mt5.shutdown()
```

Todos los símbolos deben mostrar ✅

---

## Fase 3: Verificación de Indicadores

### 3.1 Probar Cálculo de Indicadores

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.indicators.technical import indicators

connector.initialize(use_demo=True)

symbol = "PainX 400"
df_h1 = connector.get_bars(symbol, 'H1', count=100)

# Probar indicador Snake
fast_ema, slow_ema, color = indicators.calculate_snake(df_h1)
print(f"Snake: {color}")
print(f"  Fast EMA: {fast_ema.iloc[-1]:.5f}")
print(f"  Slow EMA: {slow_ema.iloc[-1]:.5f}")

# Probar Shingle
shingle, shingle_color = indicators.calculate_shingle(df_h1)
print(f"\nShingle: {shingle_color}")
print(f"  Valor: {shingle.iloc[-1]:.5f}")

# Probar línea morada
purple = indicators.calculate_purple_line(df_h1)
print(f"\nLínea Morada: {purple.iloc[-1]:.5f}")

connector.shutdown()
```

**Esperado:** Todos los indicadores calculan sin errores y muestran valores razonables.

### 3.2 Probar Análisis de Mecha D1

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.indicators.technical import indicators

connector.initialize(use_demo=True)

symbol = "PainX 400"
df_d1 = connector.get_bars(symbol, 'D1', count=5)

direction, wick_size, wick_50 = indicators.check_wick_direction(df_d1)

print(f"Análisis D1:")
print(f"  Dirección: {direction}")
print(f"  Tamaño Mecha: {wick_size:.5f}")
print(f"  Nivel 50%: {wick_50:.5f}")

connector.shutdown()
```

**Esperado:** Dirección es 'UP' o 'DOWN', con valores válidos de mecha.

---

## Fase 4: Prueba de Generación de Señales

### 4.1 Probar Motor de Señales

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.signals import SignalEngine

connector.initialize(use_demo=True)

engine = SignalEngine()
symbol = "PainX 400"

signal = engine.generate_signal(symbol)

print(f"Señal para {symbol}:")
print(f"  Acción: {signal['action']}")
print(f"  Precio: {signal['price']}")
print(f"  Confirmaciones:")
for key, value in signal['confirmations'].items():
    print(f"    {key}: {value}")

connector.shutdown()
```

**Esperado:** Señal generada con todas las confirmaciones registradas.

### 4.2 Monitorear Señales en el Tiempo

Ejecutar por 30 minutos y observar señales:

```bash
python -c "
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.signals import SignalEngine
import time

connector.initialize(use_demo=True)
engine = SignalEngine()

for i in range(60):  # 60 iteraciones = 30 minutos
    signal = engine.generate_signal('PainX 400')
    if signal['action']:
        print(f'SEÑAL: {signal}')
    time.sleep(30)

connector.shutdown()
"
```

---

## Fase 5: Prueba de Ejecución de Órdenes

### 5.1 Probar Colocación de Orden (Lote Mínimo)

⚠️ ¡Esto colocará una orden real en cuenta demo!

```python
from pain_gain_bot.data.mt5_connector import connector

connector.initialize(use_demo=True)
connector.verify_symbols(["PainX 400"])

# Colocar orden de prueba mínima
result = connector.send_order(
    symbol="PainX 400",
    order_type="SELL",
    volume=0.01,  # Lote mínimo
    magic=999999,
    comment="Orden de prueba"
)

if result:
    print(f"✅ Orden colocada: Ticket {result['ticket']}")
    print(f"  Precio: {result['price']}")

    # Cerrar inmediatamente
    input("Presiona Enter para cerrar orden...")
    connector.close_position(result['ticket'])
    print("✅ Orden cerrada")
else:
    print("❌ Orden falló")

connector.shutdown()
```

**Esperado:** Orden se coloca y cierra exitosamente.

### 5.2 Probar Gestor de Órdenes

```python
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.strategy.order_manager import OrderManager
from pain_gain_bot.config import config

connector.initialize(use_demo=True)
config.risk.lot_size = 0.01  # Usar lote mínimo

order_mgr = OrderManager("PAIN", 100000)

# Probar ejecución de orden
result = order_mgr.execute_order(
    symbol="PainX 400",
    action="SELL",
    volume=0.01
)

if result:
    print(f"✅ Prueba de Order Manager pasó")
    print(f"  Posiciones activas: {len(order_mgr.active_positions)}")

    # Esperar y gestionar
    import time
    time.sleep(10)
    order_mgr.manage_positions()
else:
    print("❌ Prueba de Order Manager falló")

connector.shutdown()
```

---

## Fase 6: Prueba de Gestión de Riesgo

### 6.1 Probar Límites Diarios

```python
from pain_gain_bot.strategy.risk_manager import risk_manager
from pain_gain_bot.data.mt5_connector import connector
from pain_gain_bot.config import config

connector.initialize(use_demo=True)
risk_manager.initialize()

# Sobrescribir límites para prueba
config.risk.daily_stop_usd = 10.0
config.risk.daily_target_usd = 20.0

# Revisar estado actual
stats = risk_manager.get_risk_status()

print("Estado de Riesgo:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Probar verificación de límites
can_trade, reason = risk_manager.check_daily_limits()
print(f"\nPuede tradear: {can_trade}")
print(f"Razón: {reason}")

connector.shutdown()
```

### 6.2 Probar Tiempo de Sesión

```python
from pain_gain_bot.strategy.risk_manager import risk_manager
from datetime import datetime

# Verificar si está en sesión
in_session = risk_manager.is_trading_session()
print(f"Hora actual: {datetime.now().strftime('%H:%M:%S')}")
print(f"En sesión de trading: {in_session}")
```

---

## Fase 7: Trading Demo Extendido

### 7.1 Ejecutar Bot Completo en Demo (24-48 Horas)

```bash
python -m pain_gain_bot.main --bot both --demo
```

**Monitorear:**
- Logs en directorio `logs/`
- Terminal MT5 (posiciones e historial)
- Salida de consola cada 10 minutos

**Verificar:**
- ✅ Señales se generan correctamente
- ✅ Órdenes se ejecutan cuando se cumplen condiciones
- ✅ Posiciones cierran después de 5 minutos
- ✅ Re-entradas respetan reglas de tiempo
- ✅ Stops diarios se activan correctamente
- ✅ Lógica de línea morada funciona
- ✅ Sin crashes ni errores

### 7.2 Lista de Validación

Después de 24-48 horas de trading demo:

- [ ] Bot corrió sin crashes
- [ ] Al menos 5 operaciones ejecutadas
- [ ] Todas las operaciones siguieron reglas de estrategia
- [ ] Lógica de stop loss funcionó correctamente
- [ ] Lógica de take profit funcionó correctamente
- [ ] Límites diarios respetados
- [ ] Logs son detallados y precisos
- [ ] Sin comportamiento inesperado

---

## Fase 8: Despliegue en Vivo (Enfoque Cauteloso)

⚠️ **¡Solo proceder si pruebas demo fueron 100% exitosas!**

### 8.1 Checklist Pre-Vivo

- [ ] Pruebas demo completadas exitosamente (mínimo 1 semana)
- [ ] Todas las pruebas de validación pasaron
- [ ] Revisados todos los logs en busca de errores
- [ ] Entendidos todos los parámetros de estrategia
- [ ] Cómodo con cantidad de riesgo
- [ ] Fondos de respaldo disponibles
- [ ] Plan de monitoreo establecido

### 8.2 Prueba Inicial en Vivo (Riesgo Mínimo)

**Día 1-3: Un Solo Símbolo, Lote Mínimo**

```json
{
  "broker": {
    "use_demo": false  // ⚠️ MODO REAL
  },
  "symbols": {
    "pain_symbols": ["PainX 400"],  // Solo un símbolo
    "gain_symbols": ["GainX 400"]   // Solo un símbolo
  },
  "risk": {
    "lot_size": 0.01,  // LOTE MÍNIMO
    "daily_stop_usd": 5.0,  // Límite muy bajo
    "daily_target_usd": 10.0
  }
}
```

Ejecutar:
```bash
python -m pain_gain_bot.main --bot both --live
```

**Monitorear continuamente durante primeras 24 horas.**

### 8.3 Escalar Gradualmente

Si Día 1-3 es exitoso:

**Día 4-7:**
- Aumentar a 2 símbolos por bot
- Aumentar lote a 0.05
- Aumentar stop diario a 20

**Semana 2:**
- Agregar todos los símbolos
- Aumentar a tamaño de lote configurado (0.10)
- Usar límites diarios completos (40/100)

---

## Solución de Problemas en Pruebas

### No se Generan Señales

**Causas Posibles:**
1. Condiciones del mercado no cumplen todos los criterios
2. Fuera de sesión de trading
3. Stop diario ya alcanzado

**Soluciones:**
- Esperar configuración adecuada del mercado
- Revisar D1 para sesgo de mecha
- Revisar todas las confirmaciones de temporalidades

### Órdenes Fallan al Ejecutar

**Causas Posibles:**
1. Balance insuficiente
2. Spread demasiado alto
3. Símbolo no está operando
4. Tamaño de lote incorrecto

**Soluciones:**
- Revisar balance de cuenta
- Monitorear spread en MT5
- Verificar que símbolo esté activo
- Ajustar tamaño de lote en config

### Posiciones No Cierran

**Causas Posibles:**
1. Línea morada no está rompiendo
2. Tiempo de retención no alcanzado
3. Problema de conexión

**Soluciones:**
- Revisar línea morada M5 visualmente
- Esperar vela M5 completa
- Verificar conexión MT5

---

## Métricas de Rendimiento a Rastrear

### Métricas Diarias
- Total de operaciones
- Tasa de ganancia
- Ganancia promedio por operación
- Pérdida promedio por operación
- Drawdown máximo

### Métricas Semanales
- P/L total
- Factor de ganancia (ganancia bruta / pérdida bruta)
- Ratio de Sharpe
- Máximo de victorias/pérdidas consecutivas

### Métricas Mensuales
- Retorno sobre cuenta (%)
- Retorno ajustado por riesgo
- Tasa de adherencia a estrategia
- Conteo de errores/excepciones

---

## Criterios de Aceptación

Antes de considerar el bot listo para producción:

✅ **Estabilidad:**
- Corre continuamente por 7+ días sin crashes
- Cero errores críticos en logs

✅ **Cumplimiento de Estrategia:**
- Todas las operaciones siguen reglas documentadas
- Confirmaciones de entrada coinciden con estrategia
- Reglas de salida correctamente implementadas

✅ **Gestión de Riesgo:**
- Stops diarios funcionan 100% del tiempo
- Dimensionamiento de posición correcto
- Sin violaciones de límites de riesgo

✅ **Rendimiento:**
- Expectativa positiva (ganancia promedio > pérdida promedio × (1/tasa_ganancia - 1))
- Drawdown aceptable (<20% del stop diario)
- Rentable durante período de prueba

---

## Aprobación Final

Antes de trading en vivo con capital completo:

1. **Aprobación del Desarrollador:** Todas las pruebas pasaron ✅
2. **Revisión del Cliente:** Estrategia funciona como se esperaba ✅
3. **Reconocimiento de Riesgo:** Cliente entiende los riesgos ✅
4. **Plan de Monitoreo:** Horario de revisión diaria establecido ✅

---

**Recuerda:** Ningún sistema de trading es perfecto. ¡Siempre monitorea activamente, especialmente en las primeras semanas de operación en vivo!
