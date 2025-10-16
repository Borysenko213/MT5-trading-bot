# Sistema de Trading Automatizado Pain/Gain

**Versión:** 1.0.0
**Plataforma:** MetaTrader 5
**Broker:** Weltrade
**Símbolos:** PainX/GainX 400, 600, 800, 999

---

## Descripción del Proyecto

Sistema de trading automatizado dual que implementa la estrategia Pain/Gain para índices sintéticos. El sistema consta de dos bots independientes:

- **PainBot** - Ejecuta señales de VENTA en símbolos PainX
- **GainBot** - Ejecuta señales de COMPRA en símbolos GainX

Ambos bots utilizan análisis multi-temporalidad (D1 → H4 → H1 → M30/M15 → M5 → M1) con indicadores personalizados.

---

## Características Principales

### Estrategia Multi-Temporalidad
- **Análisis D1:** Dirección de mecha determina sesgo diario
- **Confirmación H4:** Validación Fibonacci 50% en gráficos M15
- **Estructura H1:** Verificación de alineación de "shingle" (EMA)
- **Filtro M30/M15:** Confirmación de color de "snake"
- **Entrada M5/M1:** Patrón de ruptura-retesteo de línea morada

### Gestión de Riesgo
- Límite de pérdida diaria ($40 USD por defecto)
- Objetivo de ganancia diaria ($100 USD por defecto)
- Máximo 3 órdenes consecutivas por símbolo
- Control de spread y slippage
- Ventana de sesión de trading (19:00-06:00 COL)
- Condición de parada al 50% de mecha

### Gestión de Órdenes
- Retención mínima de 5 minutos
- Espera 1 vela M5 después del cierre
- Reentrada permitida en inicio de 3era vela M5
- Control de posición por línea morada
- Stop loss automático en ruptura de línea morada

### Sistema de Logs y Alertas
- Logs de operaciones detallados
- Seguimiento de errores y conexión
- Notificaciones Telegram (opcional)
- Alertas por email (opcional)
- Métricas de rendimiento

---

## Instalación

### 1. Requisitos Previos

- **Python 3.11+** instalado
- **MetaTrader 5** terminal
- Cuenta **Weltrade MT5** (Demo o Real)
- Windows OS (requisito de MT5)

### 2. Instalar Paquetes Python

```bash
cd C:\Users\Administrator\Documents\trading
pip install -r requirements_bot.txt
```

O usa el instalador automático:
```bash
install_dependencies.bat
```

### 3. Configurar Cuentas

Edita `config.json`:

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "TU_PASSWORD_AQUI",
    "use_demo": true
  }
}
```

⚠️ **IMPORTANTE:** Reemplaza las contraseñas con tus credenciales reales!

---

## Uso

### Ejecutar Ambos Bots (Recomendado)

```bash
python -m pain_gain_bot.main --bot both --demo
```

O doble clic en: `run_demo.bat`

### Ejecutar Solo PainBot

```bash
python -m pain_gain_bot.main --bot pain --demo
```

### Ejecutar Solo GainBot

```bash
python -m pain_gain_bot.main --bot gain --demo
```

### Usar Configuración Personalizada

```bash
python -m pain_gain_bot.main --config mi_config.json --bot both
```

### ⚠️ Trading en Vivo (Dinero Real)

```bash
python -m pain_gain_bot.main --bot both --live
```

---

## Detalles de Estrategia

### PainBot (Estrategia de VENTA)

1. **Sesgo D1:** Día anterior tiene cuerpo pequeño con mecha **hacia abajo**
2. **Parada Diaria:** Detener trading cuando el día actual llena 50% de esa mecha
3. **Verificación H4:** Vela H4 previa cubre ≥50% de Fibonacci M15 (alto→bajo)
4. **Filtro H1:** Precio debajo de **shingle rojo** grueso
5. **M30/M15:** Snake debe ser **ROJO** en ambos
6. **Entrada M1:**
   - Precio debajo de snake rojo
   - Romper línea morada hacia abajo
   - Retestear línea morada desde abajo → **VENDER**

### GainBot (Estrategia de COMPRA)

1. **Sesgo D1:** Día anterior tiene cuerpo pequeño con mecha **hacia arriba**
2. **Parada Diaria:** Detener trading cuando el día actual llena 50% de esa mecha
3. **Verificación H4:** Vela H4 previa cubre ≥50% de Fibonacci M15 (bajo→alto)
4. **Filtro H1:** Precio encima de **shingle verde** grueso
5. **M30/M15:** Snake debe ser **VERDE** en ambos
6. **Entrada M1:**
   - Precio encima de snake verde
   - Romper línea morada hacia arriba
   - Retestear línea morada desde arriba → **COMPRAR**

### Reglas de Salida

- **Take Profit:** Mantener 5 minutos, cerrar al cierre de vela
- **Reentrada:** Esperar 1 vela M5 más, puede entrar en inicio de 3era vela M5
- **Stop Loss:** Ruptura de línea morada M5 contra la operación
- **Parada Diaria:** 50% de mecha D1 llenada O límite de pérdida alcanzado

---

## Parámetros de Configuración

### Configuración de Broker
- `server`: Nombre del servidor broker
- `demo_account` / `live_account`: Números de cuenta
- `use_demo`: True para demo, False para real

### Gestión de Riesgo
- `lot_size`: Tamaño de posición (0.10 por defecto)
- `daily_stop_usd`: Pérdida máxima diaria
- `daily_target_usd`: Objetivo de ganancia diaria
- `max_consecutive_orders`: Límite de órdenes por símbolo
- `max_spread_pips`: Spread máximo permitido
- `max_slippage_pips`: Tolerancia de slippage

### Configuración de Sesión
- `session_start`: Hora de inicio de trading (19:00 COL)
- `session_end`: Hora de fin de trading (06:00 COL)
- `daily_close_time`: Cierre de vela D1 (16:00 COL)

### Indicadores de Estrategia
- `snake_fast_ema`: EMA rápida para Snake (8)
- `snake_slow_ema`: EMA lenta para Snake (21)
- `shingle_ema`: Período EMA para Shingle (50)
- `purple_line_ema`: Línea morada EMA (34)
- `squid_period`: Período indicador Squid (13)

---

## Monitoreo y Logs

### Archivos de Log (en carpeta `logs/`)

- `trading_YYYYMMDD.log` - Toda la actividad
- `errors_YYYYMMDD.log` - Solo errores
- `trades_YYYYMMDD.log` - Ejecución de operaciones

### Salida en Consola

El bot muestra estado cada ~10 minutos:

```
============================================================
PainBot Estado (Iteración 20)
============================================================
Balance: $500.00 | P/L Diario: $5.50 (1.10%)
Operaciones Hoy: 3 | Posiciones Activas: 1
Pérdida Diaria: $0.00 / $40.00 | Ganancia: $5.50 / $100.00
En Sesión: True | Detenido: False
============================================================
```

---

## Solución de Problemas

### Fallo de Conexión MT5

1. Asegúrate de que MetaTrader 5 esté corriendo
2. Verifica credenciales de cuenta
3. Confirma que "Permitir trading automatizado" está habilitado en MT5

### No Se Generan Señales

1. Verifica estar dentro del horario de sesión de trading
2. Asegúrate de que el sesgo diario esté establecido (revisar mecha D1)
3. Confirma que todas las confirmaciones de temporalidad estén alineadas

### Órdenes No Se Ejecutan

1. Verifica tamaño de lote dentro de límites del símbolo
2. Verifica que spread esté bajo el umbral máximo
3. Asegúrate de no exceder el límite de órdenes consecutivas

---

## Soporte

**Soporte Incluido:** 30 días post-entrega
- Corrección de bugs
- Ajuste de parámetros
- Ayuda con instalación
- Asistencia con backtesting

**Tiempo de Respuesta:** 24-48 horas hábiles

---

## ⚠️ Aviso Legal

**ADVERTENCIA DE RIESGO:** El trading de índices sintéticos y forex involucra riesgo sustancial de pérdida. Este software se proporciona para fines educativos y de investigación. Siempre prueba exhaustivamente en cuentas demo antes de trading en vivo. El rendimiento pasado no garantiza resultados futuros. Solo opera con capital que puedas permitirte perder.

---

## Licencia

Software propietario desarrollado para Leonel Rosso (Gestiones Latam).
Todos los derechos reservados.

**Desarrollador:** Borysenko
**Versión:** 1.0.0
**Fecha:** Octubre 2025
