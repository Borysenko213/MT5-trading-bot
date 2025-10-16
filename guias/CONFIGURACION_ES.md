# Guía de Configuración - Sistema Pain/Gain

Guía completa para configurar tus bots de trading usando el archivo de configuración centralizado.

---

## 📋 Resumen

Todos los parámetros del bot se controlan a través de un solo archivo **config.json**. ¡No se requiere editar código!

---

## 🚀 Configuración Rápida

### Paso 1: Crear Tu Archivo de Configuración

Copia una de las plantillas proporcionadas:

```bash
# Opción 1: Configuración simple (recomendado para principiantes)
copy config_example.json config.json

# Opción 2: Configuración completa con explicaciones
copy config_template.json config.json
```

### Paso 2: Editar Tus Contraseñas

Abre `config.json` y reemplaza:
```json
"demo_password": "TU_CONTRASEÑA_AQUI"
```

Con tu contraseña real:
```json
"demo_password": "%6Qn4Er["
```

### Paso 3: Ejecutar el Bot

```bash
python -m pain_gain_bot.main --bot both --config config.json
```

**¡Eso es todo!** Todos los ajustes se cargan desde tu archivo de configuración.

---

## 🎛️ Secciones de Configuración

### 1. Configuración de Broker

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "TU_CONTRASEÑA",
    "live_account": 34279304,
    "live_password": "TU_CONTRASEÑA",
    "leverage": 10000,
    "use_demo": true
  }
}
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `server` | string | Nombre del servidor broker |
| `demo_account` | int | Número de cuenta demo |
| `demo_password` | string | Contraseña de cuenta demo |
| `live_account` | int | Número de cuenta real |
| `live_password` | string | Contraseña de cuenta real |
| `leverage` | int | Apalancamiento de cuenta (1:10000) |
| `use_demo` | bool | true = demo, false = real ⚠️ |

⚠️ **IMPORTANTE:** Siempre mantén `use_demo: true` hasta estar completamente probado!

---

### 2. Símbolos de Trading

```json
{
  "symbols": {
    "pain_symbols": [
      "PainX400",
      "PainX600",
      "PainX800",
      "PainX999"
    ],
    "gain_symbols": [
      "GainX400",
      "GainX600",
      "GainX800",
      "GainX999"
    ]
  }
}
```

**Ejemplos de Personalización:**

Operar solo PainX400 y GainX400:
```json
{
  "pain_symbols": ["PainX400"],
  "gain_symbols": ["GainX400"]
}
```

Operar solo símbolos de alta volatilidad:
```json
{
  "pain_symbols": ["PainX800", "PainX999"],
  "gain_symbols": ["GainX800", "GainX999"]
}
```

---

### 3. Gestión de Riesgo ⚠️ CRÍTICO

```json
{
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0,
    "max_consecutive_orders": 3,
    "max_spread_pips": 2.0,
    "max_slippage_pips": 2.0
  }
}
```

| Parámetro | Por Defecto | Descripción |
|-----------|-------------|-------------|
| `lot_size` | 0.10 | Tamaño de posición por operación |
| `daily_stop_usd` | 40.0 | Pérdida máx. por día - **LÍMITE DE SEGURIDAD** |
| `daily_target_usd` | 100.0 | Objetivo de ganancia por día |
| `max_consecutive_orders` | 3 | Máx. órdenes seguidas por símbolo |
| `max_spread_pips` | 2.0 | Spread máximo permitido |
| `max_slippage_pips` | 2.0 | Slippage máximo permitido |

#### Preajustes de Riesgo

**Conservador (Bajo Riesgo):**
```json
{
  "lot_size": 0.01,
  "daily_stop_usd": 10.0,
  "daily_target_usd": 20.0,
  "max_consecutive_orders": 2
}
```

**Moderado (Por Defecto):**
```json
{
  "lot_size": 0.10,
  "daily_stop_usd": 40.0,
  "daily_target_usd": 100.0,
  "max_consecutive_orders": 3
}
```

**Agresivo (Alto Riesgo):**
```json
{
  "lot_size": 0.25,
  "daily_stop_usd": 100.0,
  "daily_target_usd": 300.0,
  "max_consecutive_orders": 5
}
```

---

### 4. Sesión de Trading

```json
{
  "session": {
    "session_start": "19:00:00",
    "session_end": "06:00:00",
    "daily_close_time": "16:00:00"
  }
}
```

| Parámetro | Formato | Descripción |
|-----------|---------|-------------|
| `session_start` | "HH:MM:SS" | Hora de inicio de trading (Colombia) |
| `session_end` | "HH:MM:SS" | Hora de fin de trading (Colombia) |
| `daily_close_time` | "HH:MM:SS" | Hora de cierre de vela D1 |

#### Preajustes de Sesión

**Sesión Nocturna (Por Defecto):**
```json
{
  "session_start": "19:00:00",
  "session_end": "06:00:00"
}
```

**Noche Extendida:**
```json
{
  "session_start": "18:00:00",
  "session_end": "08:00:00"
}
```

**Sesión Diurna:**
```json
{
  "session_start": "08:00:00",
  "session_end": "17:00:00"
}
```

**Trading 24/7:**
```json
{
  "session_start": "00:00:00",
  "session_end": "23:59:59"
}
```

---

### 5. Parámetros de Estrategia

```json
{
  "strategy": {
    "hold_minutes": 5,
    "wait_candles": 1,
    "snake_fast_ema": 8,
    "snake_slow_ema": 21,
    "shingle_ema": 50,
    "purple_line_ema": 34,
    "squid_period": 13
  }
}
```

| Parámetro | Por Defecto | Descripción |
|-----------|-------------|-------------|
| `hold_minutes` | 5 | Tiempo mín. de retención por operación |
| `wait_candles` | 1 | Velas M5 a esperar antes de reentrada |
| `snake_fast_ema` | 8 | Período EMA rápida para Snake |
| `snake_slow_ema` | 21 | Período EMA lenta para Snake |
| `shingle_ema` | 50 | Período EMA para Shingle |
| `purple_line_ema` | 34 | Período EMA línea morada |
| `squid_period` | 13 | Período indicador Squid |

⚠️ **ADVERTENCIA:** Cambiar períodos de indicadores puede afectar significativamente el rendimiento de la estrategia. ¡Prueba en demo primero!

---

### 6. Alertas y Notificaciones

```json
{
  "alerts": {
    "enable_telegram": false,
    "telegram_token": "",
    "telegram_chat_id": "",
    "enable_email": false,
    "log_level": "INFO"
  }
}
```

#### Habilitar Notificaciones de Telegram

1. Crea un bot con [@BotFather](https://t.me/botfather)
2. Obtén tu chat ID con [@userinfobot](https://t.me/userinfobot)
3. Actualiza configuración:

```json
{
  "enable_telegram": true,
  "telegram_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "telegram_chat_id": "123456789"
}
```

#### Niveles de Log

- `"DEBUG"` - Todo (muy detallado)
- `"INFO"` - Operaciones normales (recomendado)
- `"WARNING"` - Solo advertencias importantes
- `"ERROR"` - Solo errores

---

## 🎯 Escenarios Comunes de Configuración

### Escenario 1: Primera Vez Probando (Demo)

```json
{
  "broker": {"use_demo": true},
  "symbols": {
    "pain_symbols": ["PainX400"],
    "gain_symbols": ["GainX400"]
  },
  "risk": {
    "lot_size": 0.01,
    "daily_stop_usd": 5.0,
    "daily_target_usd": 10.0
  }
}
```

**Por qué:** Riesgo mínimo, un símbolo por bot, fácil monitoreo.

---

### Escenario 2: Pruebas Estándar en Demo

```json
{
  "broker": {"use_demo": true},
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0
  }
}
```

**Por qué:** Estrategia completa como fue diseñada, pruebas seguras en demo.

---

### Escenario 3: Trading en Vivo Inicial (Precaución)

```json
{
  "broker": {"use_demo": false},
  "symbols": {
    "pain_symbols": ["PainX400", "PainX600"],
    "gain_symbols": ["GainX400", "GainX600"]
  },
  "risk": {
    "lot_size": 0.01,
    "daily_stop_usd": 10.0,
    "daily_target_usd": 25.0
  },
  "alerts": {
    "enable_telegram": true
  }
}
```

**Por qué:** Dinero real pero riesgo muy bajo, 2 símbolos, alertas de Telegram habilitadas.

---

## 🔄 Cargando Configuración

### Método 1: Automático (Recomendado)

Coloca `config.json` en la raíz del proyecto. El bot lo cargará automáticamente.

```bash
python -m pain_gain_bot.main --bot both
```

### Método 2: Especificar Ruta

```bash
python -m pain_gain_bot.main --bot both --config mi_config_personalizado.json
```

### Método 3: Sobrescribir con Línea de Comandos

```bash
python -m pain_gain_bot.main --bot both --demo  # Fuerza modo demo
python -m pain_gain_bot.main --bot both --live  # Fuerza modo real
```

---

## ✅ Validación de Configuración

El bot validará tu configuración al inicio y mostrará:

```
✓ Configuración cargada desde config.json
✓ Broker: Weltrade (Modo demo)
✓ Símbolos: 4 Pain, 4 Gain
✓ Riesgo: Lote 0.10, Parada diaria $40.00
✓ Sesión: 19:00 - 06:00 COL
```

Si hay errores, verás advertencias y se usarán valores por defecto.

---

## 🔧 Solución de Problemas

### Configuración no se carga

**Problema:** El bot usa valores por defecto en lugar de config
**Solución:**
- Verifica que el archivo se llame exactamente `config.json`
- Verifica que el archivo esté en el directorio correcto
- Verifica sintaxis JSON (usa [jsonlint.com](https://jsonlint.com))

### Formato JSON inválido

**Problema:** "Error al cargar config: ..."
**Solución:**
- Asegúrate de que todas las cadenas estén entre comillas
- Sin comas finales
- Coincidencia adecuada de corchetes
- Usa la plantilla como referencia

### Errores de formato de hora

**Problema:** Horas de sesión no funcionan
**Solución:** Usa formato "HH:MM:SS" exactamente
```json
"session_start": "19:00:00"  ✓ Correcto
"session_start": "19:00"     ✗ Incorrecto
"session_start": "7:00 PM"   ✗ Incorrecto
```

---

## 📝 Mejores Prácticas

1. **Empieza con plantilla** - Copia `config_example.json`
2. **Prueba en demo primero** - ¡Siempre!
3. **Mantén respaldos** - Guarda configuraciones funcionales
4. **Documenta cambios** - Anota qué cambiaste y por qué
5. **Versiona tus configs** - Nómbralas (config_v1.json, config_v2.json)
6. **Valida JSON** - Usa validador en línea antes de ejecutar
7. **Empieza conservador** - Aumenta riesgo gradualmente

---

## 💡 Consejos Avanzados

### Múltiples Configuraciones

Crea diferentes configs para diferentes escenarios:

```
config_demo.json              # Pruebas en demo
config_live_conservador.json  # Real con bajo riesgo
config_live_completo.json     # Real con estrategia completa
config_solo_noche.json        # Solo trading nocturno
config_un_simbolo.json        # Prueba con un símbolo
```

Cambia entre ellas:
```bash
python -m pain_gain_bot.main --config config_solo_noche.json
```

---

**¿Necesitas Ayuda?**

Si tienes preguntas sobre configuración:
1. Revisa los comentarios de la plantilla
2. Revisa esta guía
3. Prueba en demo primero
4. Contacta soporte durante período de 30 días

---

**Recuerda:** ¡Todos los parámetros son opcionales. Si no se especifican, se usan valores por defecto sensatos!

**¡Feliz Trading!** 🚀
