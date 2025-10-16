# Guía de Instalación - Sistema Pain/Gain

Instrucciones completas paso a paso para instalar los bots de trading.

---

## Requisitos del Sistema

### Sistema Operativo
- **Windows 10/11** (requerido para MetaTrader 5)

### Software
- **Python 3.11 o superior**
- **MetaTrader 5** terminal
- Cuenta **Weltrade MT5**

### Hardware (Recomendado)
- **CPU:** Dual-core 2.0 GHz o mejor
- **RAM:** 4GB mínimo, 8GB recomendado
- **Almacenamiento:** 2GB espacio libre
- **Internet:** Conexión de banda ancha estable

### Opcional (Para Operación 24/7)
- **VPS:** VPS Windows con soporte MT5
- Recomendado: 2GB RAM, 20GB SSD, 99.9% uptime

---

## Paso 1: Instalar Python

### 1.1 Descargar Python

Visita [python.org](https://www.python.org/downloads/) y descarga Python 3.11 o superior.

### 1.2 Instalar Python

1. Ejecuta el instalador
2. ✅ **IMPORTANTE:** Marca "Add Python to PATH"
3. Clic en "Install Now"
4. Espera a que la instalación se complete

### 1.3 Verificar Instalación

Abre Command Prompt y ejecuta:

```bash
python --version
```

Debería mostrar: `Python 3.11.x`

```bash
pip --version
```

Debería mostrar información de versión de pip.

---

## Paso 2: Instalar MetaTrader 5

### 2.1 Descargar MT5

1. Visita [sitio web de Weltrade](https://weltrade.com)
2. Descarga MetaTrader 5 para Windows
3. Ejecuta el instalador y sigue las instrucciones

### 2.2 Configurar MT5

1. Abre MetaTrader 5
2. Ve a **Tools → Options → Expert Advisors**
3. ✅ Habilita "Allow automated trading"
4. ✅ Habilita "Allow DLL imports"
5. Clic en OK

### 2.3 Iniciar Sesión en la Cuenta

**Cuenta Demo:**
- Servidor: **Weltrade**
- Login: **19498321**
- Contraseña: **TU_CONTRASEÑA**

**Cuenta Real:**
- Servidor: **Weltrade**
- Login: **34279304**
- Contraseña: **TU_CONTRASEÑA**

### 2.4 Agregar Símbolos a Market Watch

1. Clic derecho en Market Watch
2. Selecciona "Symbols"
3. Busca y agrega:
   - PainX400, PainX600, PainX800, PainX999
   - GainX400, GainX600, GainX800, GainX999

---

## Paso 3: Instalar Indicadores Personalizados JannerTrading

### 3.1 Ubicar Archivos de Indicadores

En la carpeta del proyecto, encuentra:
```
JannerTrading-Caza-Spike-2024/
  Esto va en Indicators-JannerTrading/
    - JannerTrading1.ex5
    - JannerTrading2.ex5
    - JannerTrading3.ex5
    - JannerTrading4.ex5
    - JannerTrading5.ex5
```

### 3.2 Copiar a MT5

1. En MT5, clic en **File → Open Data Folder**
2. Navega a **MQL5 → Indicators**
3. Copia los 5 archivos `.ex5` aquí
4. Reinicia MetaTrader 5

### 3.3 Instalar Plantillas (Opcional)

1. De la carpeta del proyecto: `Esto va en Templates-JannerTrading/`
2. Copia todos los archivos `.tpl`
3. Pega en **Carpeta de Datos MT5 → templates**
4. Reinicia MT5

---

## Paso 4: Instalar Bot de Trading

### 4.1 Extraer Archivos del Proyecto

Asegúrate de que la estructura de tu proyecto se vea así:

```
C:\Users\Administrator\Documents\trading\
├── pain_gain_bot\           # Paquete principal del bot
├── requirements_bot.txt     # Dependencias de Python
├── README.md                # Documentación
└── INSTALACION_ES.md        # Este archivo
```

### 4.2 Abrir Command Prompt en Carpeta del Proyecto

1. Navega a la carpeta de trading:
```bash
cd C:\Users\Administrator\Documents\trading
```

### 4.3 Instalar Dependencias de Python

```bash
pip install -r requirements_bot.txt
```

O usa el instalador automático:
```bash
install_dependencies.bat
```

Espera a que todos los paquetes se instalen. Puede tomar 5-10 minutos.

### 4.4 Verificar Instalación

Verifica que el paquete MetaTrader5 se instaló correctamente:

```bash
python -c "import MetaTrader5 as mt5; print(mt5.__version__)"
```

Debería imprimir el número de versión de MT5.

---

## Paso 5: Configurar los Bots

### 5.1 Opción A: Editar config.py Directamente

Abre `pain_gain_bot/config.py` en un editor de texto y modifica:

```python
@dataclass
class BrokerConfig:
    server: str = "Weltrade"
    demo_account: int = TU_CUENTA_DEMO
    demo_password: str = "TU_CONTRASEÑA_DEMO"
    live_account: int = TU_CUENTA_REAL
    live_password: str = "TU_CONTRASEÑA_REAL"
    use_demo: bool = True  # True para demo, False para real
```

### 5.2 Opción B: Crear config.json

Crea un archivo llamado `config.json` en la carpeta trading:

```json
{
  "broker": {
    "server": "Weltrade",
    "demo_account": 19498321,
    "demo_password": "TU_CONTRASEÑA_AQUI",
    "use_demo": true
  },
  "symbols": {
    "pain_symbols": ["PainX400", "PainX600", "PainX800", "PainX999"],
    "gain_symbols": ["GainX400", "GainX600", "GainX800", "GainX999"]
  },
  "risk": {
    "lot_size": 0.10,
    "daily_stop_usd": 40.0,
    "daily_target_usd": 100.0,
    "max_consecutive_orders": 3
  }
}
```

⚠️ **SEGURIDAD:** ¡Nunca subas contraseñas a control de versiones!

---

## Paso 6: Probar Instalación

### 6.1 Probar Conexión MT5

```bash
python -c "import MetaTrader5 as mt5; mt5.initialize(); print('MT5 OK' if mt5.terminal_info() else 'MT5 FALLO')"
```

Debería imprimir: `MT5 OK`

### 6.2 Ejecutar Primera Prueba (Ejecución en Seco)

```bash
python -m pain_gain_bot.main --bot pain --demo
```

Deberías ver:
```
==============================================
 Sistema de Trading Automatizado Pain/Gain v1.0
==============================================
✓ Conectado a MT5 - Cuenta: 19498321 (Demo)
✓ PainBot inicializado correctamente
🚀 Iniciando PainBot...
```

Presiona `Ctrl+C` para detener.

---

## Paso 7: Ejecutar los Bots

### 7.1 Modo Demo (Recomendado para Pruebas)

**Ejecutar ambos bots:**
```bash
python -m pain_gain_bot.main --bot both --demo
```

**Ejecutar solo PainBot:**
```bash
python -m pain_gain_bot.main --bot pain --demo
```

**Ejecutar solo GainBot:**
```bash
python -m pain_gain_bot.main --bot gain --demo
```

### 7.2 Modo Real (Dinero Real - ¡Usar con Precaución!)

```bash
python -m pain_gain_bot.main --bot both --live
```

⚠️ **ADVERTENCIA:** Esto operará con dinero real. ¡Asegúrate de haber probado exhaustivamente en demo primero!

---

## Paso 8: Monitorear Operación

### 8.1 Verificar Logs

Los logs se crean en la carpeta `logs/`:

```
logs/
├── trading_20251014.log   # Toda la actividad
├── errors_20251014.log    # Solo errores
└── trades_20251014.log    # Ejecución de operaciones
```

### 8.2 Salida de Consola

El bot muestra estado cada ~10 minutos:

```
============================================================
PainBot Estado (Iteración 20)
============================================================
Balance: $500.00 | P/L Diario: $5.50 (1.10%)
Operaciones Hoy: 3 | Posiciones Activas: 1
...
```

### 8.3 Verificar MT5

Abre MetaTrader 5 y verifica:
- **Terminal → Trade:** Posiciones abiertas
- **Terminal → History:** Operaciones cerradas
- **Charts:** Representación visual

---

## Paso 9: Configuraciones Opcionales

### 9.1 Habilitar Alertas de Telegram

1. Crea un bot mediante [@BotFather](https://t.me/botfather)
2. Obtén tu token de bot y chat ID
3. Edita `config.json`:

```json
"alerts": {
  "enable_telegram": true,
  "telegram_token": "TU_TOKEN_BOT",
  "telegram_chat_id": "TU_CHAT_ID"
}
```

### 9.2 Ejecutar en VPS para Operación 24/7

1. Renta VPS Windows (recomendado: Vultr, DigitalOcean, AWS)
2. Instala Python, MT5 y bot como se describe arriba
3. Usa Task Scheduler o nssm para ejecutar como servicio de Windows

### 9.3 Personalizar Parámetros de Riesgo

Edita `config.json` para ajustar:
- `lot_size`: Tamaño de posición
- `daily_stop_usd`: Pérdida máxima diaria
- `daily_target_usd`: Objetivo de ganancia diaria
- `max_consecutive_orders`: Límite de frecuencia de operaciones

---

## Solución de Problemas

### Problema: "Fallo de inicialización de MT5"

**Soluciones:**
1. Asegúrate de que MetaTrader 5 esté corriendo
2. Verifica credenciales de cuenta
3. Verifica que "Allow automated trading" esté habilitado
4. Intenta iniciar sesión en MT5 manualmente primero

### Problema: "Símbolo no encontrado"

**Soluciones:**
1. Agrega símbolos a Market Watch en MT5
2. Verifica que los nombres de símbolos coincidan exactamente (sensible a mayúsculas)
3. Verifica que el broker proporcione estos símbolos

### Problema: "Fallo de pip install"

**Soluciones:**
1. Ejecuta Command Prompt como Administrador
2. Actualiza pip: `python -m pip install --upgrade pip`
3. Instala paquetes uno por uno
4. Verifica conexión a internet

### Problema: "No se generan señales"

**Soluciones:**
1. Espera condiciones adecuadas del mercado
2. Verifica si está dentro del horario de sesión de trading
3. Verifica que todas las temporalidades tengan datos
4. Revisa archivos de log para errores

---

## Próximos Pasos

1. ✅ Prueba exhaustivamente en cuenta demo por al menos 1-2 semanas
2. ✅ Monitorea rendimiento y ajusta parámetros
3. ✅ Revisa logs diariamente
4. ✅ Solo cambia a real después de resultados consistentes en demo
5. ✅ Empieza con tamaño de lote mínimo en real

---

## Soporte

Para soporte técnico durante el período de 30 días:
- Contacta al desarrollador
- Tiempo de respuesta: 24-48 horas hábiles

---

## Recordatorios Importantes

⚠️ **NUNCA** compartas tus contraseñas de cuenta públicamente
⚠️ **SIEMPRE** prueba en demo antes de trading en vivo
⚠️ **SOLO** opera con dinero que puedas permitirte perder
⚠️ **MONITOREA** el bot regularmente - automatización ≠ ganancia garantizada

---

**¡Instalación Completa!** 🎉

Ya estás listo para ejecutar el sistema de trading Pain/Gain. Empieza en modo demo y gradualmente haz la transición a trading en vivo una vez que estés confiado en el rendimiento del sistema.
