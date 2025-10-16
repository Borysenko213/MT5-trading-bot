# Estructura Completa de Archivos - Sistema Pain/Gain

Listado comprensivo de todos los archivos del proyecto con descripciones.

---

## 📁 Directorio Raíz del Proyecto

```
C:\Users\Administrator\Documents\trading\
```

---

## 📄 Archivos de Documentación

| Archivo | Descripción | Líneas |
|---------|-------------|--------|
| **README.md** | Documentación principal y resumen del proyecto | ~400 |
| **INSTALLATION.md** | Guía de instalación paso a paso | ~600 |
| **QUICK_START.md** | Setup rápido de 15 minutos | ~200 |
| **TESTING_GUIDE.md** | Procedimientos comprensivos de prueba | ~700 |
| **PROJECT_SUMMARY.md** | Resumen completo del proyecto y entregables | ~800 |
| **FILE_STRUCTURE.md** | Este archivo - listado completo de archivos | ~150 |

---

## 🐍 Código Fuente Python

### Paquete Principal: `pain_gain_bot/`

#### Nivel Raíz
```
pain_gain_bot/
├── __init__.py              # Inicialización del paquete
├── config.py                # Gestión de configuración (350+ líneas)
└── main.py                  # Controlador principal y CLI (200+ líneas)
```

#### Módulo Bots: `pain_gain_bot/bots/`
```
bots/
├── __init__.py              # Exportaciones del módulo
├── pain_bot.py              # PainBot - Estrategia VENTA (250+ líneas)
└── gain_bot.py              # GainBot - Estrategia COMPRA (250+ líneas)
```

**Propósito:** Implementaciones de bots de trading con loops principales, reportes de estado, y gestión de ciclo de vida.

#### Módulo Data: `pain_gain_bot/data/`
```
data/
├── __init__.py              # Exportaciones del módulo
└── mt5_connector.py         # Integración MT5 (450+ líneas)
```

**Propósito:** Conexión MetaTrader 5, recuperación de datos, ejecución de órdenes, gestión de posiciones.

**Clases Clave:**
- `MT5Connector`: Interfaz principal a API MT5

**Funciones Clave:**
- `initialize()`: Conectar a MT5
- `get_bars()`: Recuperar datos OHLC
- `send_order()`: Ejecutar operaciones
- `close_position()`: Cerrar posiciones
- `get_positions()`: Consultar operaciones abiertas

#### Módulo Indicators: `pain_gain_bot/indicators/`
```
indicators/
├── __init__.py              # Exportaciones del módulo
└── technical.py             # Indicadores personalizados (450+ líneas)
```

**Propósito:** Análisis técnico e indicadores personalizados.

**Clases Clave:**
- `TechnicalIndicators`: Métodos estáticos para todos los cálculos
- `IndicatorCache`: Sistema de caché para rendimiento

**Indicadores Implementados:**
- Snake (cruce de EMAs)
- Shingle (EMA gruesa)
- Squid (confirmación de tendencia)
- Purple Line (referencia ruptura-retesteo)
- Fibonacci Retracement
- Análisis Mecha D1

#### Módulo Strategy: `pain_gain_bot/strategy/`
```
strategy/
├── __init__.py              # Exportaciones del módulo
├── signals.py               # Motor de señales multi-temporalidad (350+ líneas)
├── order_manager.py         # Gestión de ciclo de vida de órdenes (280+ líneas)
└── risk_manager.py          # Controles y límites de riesgo (250+ líneas)
```

**Propósito:** Implementación central de la estrategia de trading.

**Clases Clave:**
- `SignalEngine`: Análisis multi-temporalidad y generación de señales
- `OrderManager`: Ejecución de órdenes, períodos de retención, tiempo de re-entrada
- `RiskManager`: Stops diarios, dimensionamiento de posiciones, controles de sesión

#### Módulo Utils: `pain_gain_bot/utils/`
```
utils/
├── __init__.py              # Exportaciones del módulo
└── logger.py                # Logging y alertas (250+ líneas)
```

**Propósito:** Logging, alertas, y notificaciones.

**Clases Clave:**
- `TradingLogger`: Logging mejorado con múltiples salidas
- `AlertManager`: Notificaciones Telegram/Email

---

## 🔧 Archivos de Configuración

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| **requirements_bot.txt** | Dependencias | Requerimientos de paquetes Python |
| **config.json** | Config Usuario | Configuración de ejecución (creado por usuario) |

---

## 🪟 Scripts Batch de Windows

| Archivo | Propósito |
|---------|-----------|
| **install_dependencies.bat** | Instalación de dependencias en un clic |
| **run_demo.bat** | Ejecutar ambos bots en modo demo |
| **run_pain_demo.bat** | Ejecutar solo PainBot (demo) |
| **run_gain_demo.bat** | Ejecutar solo GainBot (demo) |

---

## 📊 Indicadores Personalizados MT5 (Pre-existentes)

```
JannerTrading-Caza-Spike-2024/
└── Esto va en Indicators-JannerTrading/
    ├── JannerTrading1.ex5       # Indicador personalizado 1
    ├── JannerTrading2.ex5       # Indicador personalizado 2
    ├── JannerTrading3.ex5       # Indicador personalizado 3
    ├── JannerTrading4.ex5       # Indicador personalizado 4
    └── JannerTrading5.ex5       # Indicador personalizado 5
```

**Nota:** Estos son indicadores compilados de MT5 (.ex5) que deben copiarse a la carpeta Indicators de MT5.

---

## 📝 Plantillas MT5 (Pre-existentes)

```
JannerTrading-Caza-Spike-2024/
└── Esto va en Templates-JannerTrading/
    ├── JannerTrading-BOOM.tpl
    ├── JannerTrading-CRASH.tpl
    ├── JannerTrading-CRASH300.tpl
    └── JannerTrading-Grafico Limpio.tpl
```

**Nota:** Plantillas de gráficos para setup visual de MT5.

---

## 📂 Directorios de Ejecución (Creados Automáticamente)

### Directorio Logs
```
logs/
├── trading_YYYYMMDD.log     # Toda la actividad de trading
├── errors_YYYYMMDD.log      # Solo errores
└── trades_YYYYMMDD.log      # Ejecuciones de operaciones
```

**Creado:** Automáticamente en primera ejecución
**Rotación:** Diaria (nuevos archivos cada día)
**Ubicación:** `C:\Users\Administrator\Documents\trading\logs\`

---

## 📊 Estadísticas del Proyecto

### Métricas de Código

| Métrica | Valor |
|---------|-------|
| Total Archivos Python | 16 |
| Total Líneas de Código | ~2,800+ |
| Total Clases | 12 |
| Total Funciones | 80+ |
| Archivos Documentación | 6 |
| Scripts Batch | 4 |

### Conteo de Archivos por Tipo

| Tipo | Conteo |
|------|--------|
| Python (.py) | 16 |
| Markdown (.md) | 6 |
| Batch (.bat) | 4 |
| Texto (.txt) | 1 (requirements) |
| Indicadores MT5 (.ex5) | 5 |
| Plantillas MT5 (.tpl) | 4 |
| **Total** | **36** |

---

## 🗂️ Árbol Completo de Archivos

```
trading/
│
├── 📄 Documentación
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── QUICK_START.md
│   ├── TESTING_GUIDE.md
│   ├── PROJECT_SUMMARY.md
│   └── FILE_STRUCTURE.md
│
├── 🔧 Configuración
│   ├── requirements_bot.txt
│   └── config.json (creado por usuario)
│
├── 🪟 Scripts
│   ├── install_dependencies.bat
│   ├── run_demo.bat
│   ├── run_pain_demo.bat
│   └── run_gain_demo.bat
│
├── 🐍 Código Fuente: pain_gain_bot/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   │
│   ├── bots/
│   │   ├── __init__.py
│   │   ├── pain_bot.py
│   │   └── gain_bot.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── mt5_connector.py
│   │
│   ├── indicators/
│   │   ├── __init__.py
│   │   └── technical.py
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── signals.py
│   │   ├── order_manager.py
│   │   └── risk_manager.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py
│
├── 📊 Assets MT5: JannerTrading-Caza-Spike-2024/
│   ├── Esto va en Indicators-JannerTrading/
│   │   ├── JannerTrading1.ex5
│   │   ├── JannerTrading2.ex5
│   │   ├── JannerTrading3.ex5
│   │   ├── JannerTrading4.ex5
│   │   └── JannerTrading5.ex5
│   │
│   └── Esto va en Templates-JannerTrading/
│       ├── JannerTrading-BOOM.tpl
│       ├── JannerTrading-CRASH.tpl
│       ├── JannerTrading-CRASH300.tpl
│       └── JannerTrading-Grafico Limpio.tpl
│
└── 📂 Ejecución (auto-generado)
    └── logs/
        ├── trading_YYYYMMDD.log
        ├── errors_YYYYMMDD.log
        └── trades_YYYYMMDD.log
```

---

## 🎯 Archivos Clave por Función

### Para Instalación
1. `install_dependencies.bat` - Instalar todos los requerimientos
2. `INSTALLATION.md` - Guía paso a paso
3. `requirements_bot.txt` - Dependencias de paquetes

### Para Configuración
1. `config.py` - Configuración por defecto
2. `config.json` - Configuración de usuario (crear este)
3. `QUICK_START.md` - Ejemplos rápidos de config

### Para Ejecutar
1. `run_demo.bat` - Lanzamiento rápido (ambos bots)
2. `main.py` - Punto de entrada Python
3. `pain_bot.py` / `gain_bot.py` - Implementaciones de bots

### Para Probar
1. `TESTING_GUIDE.md` - Procedimientos de prueba
2. Scripts de prueba (pueden crearse como se muestra en guía)

### Para Monitorear
1. `logs/trading_*.log` - Log principal de actividad
2. `logs/errors_*.log` - Seguimiento de errores
3. `logs/trades_*.log` - Registros de operaciones

---

## 📦 Paquete de Distribución

Al entregar al cliente, incluir:

```
PainGain_Trading_System_v1.0.zip
├── pain_gain_bot/              (paquete completo)
├── JannerTrading-Caza-Spike-2024/  (assets MT5)
├── README.md
├── INSTALLATION.md
├── QUICK_START.md
├── TESTING_GUIDE.md
├── PROJECT_SUMMARY.md
├── FILE_STRUCTURE.md
├── requirements_bot.txt
├── install_dependencies.bat
├── run_demo.bat
├── run_pain_demo.bat
└── run_gain_demo.bat
```

**Tamaño:** ~50MB (principalmente dependencia del paquete MT5 cuando se instala)

---

## 🔄 Control de Versiones

### Estructura Git (si se usa)
```
.gitignore debe incluir:
- config.json (¡contraseñas!)
- logs/
- __pycache__/
- *.pyc
- .env
```

---

## 📞 Archivos de Soporte

Contactar al desarrollador a través de Workana para:
- Archivos faltantes
- Problemas de instalación
- Solicitudes de personalización
- Reportes de bugs

---

**Última Actualización:** Octubre 14, 2025
**Versión:** 1.0.0
**Desarrollador:** Borysenko
