# Guía de Inicio Rápido - Sistema Pain/Gain

Guía rápida para poner en marcha en 15 minutos.

---

## 🚀 3 Pasos Simples

### Paso 1: Instalar Dependencias (2 minutos)

Doble clic en: `install_dependencies.bat`

Espera a que la instalación se complete.

---

### Paso 2: Configurar Cuenta (3 minutos)

Crea un archivo llamado `config.json`:

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

⚠️ Reemplaza `TU_PASSWORD_AQUI` con tu contraseña real de demo!

---

### Paso 3: Ejecutar (1 clic)

Doble clic en: `run_demo.bat`

Deberías ver:
```
============================================================
 Sistema de Trading Automatizado Pain/Gain v1.0
============================================================
✓ Conectado a MT5 - Cuenta: 19498321 (Demo)
✓ PainBot inicializado correctamente
✓ GainBot inicializado correctamente
🚀 Iniciando bots...
```

Déjalo correr por 5 minutos, luego presiona `Ctrl+C` para detener.

---

## ✅ ¡Listo!

### Ejecutar Ambos Bots
```bash
python -m pain_gain_bot.main --bot both --demo
```

### Ejecutar Solo PainBot
```bash
python -m pain_gain_bot.main --bot pain --demo
```

### Ejecutar Solo GainBot
```bash
python -m pain_gain_bot.main --bot gain --demo
```

---

## 📊 Qué Esperar

### Primera Hora
- Los bots analizarán mercados
- Puede que no coloquen operaciones inmediatamente (esperando condiciones)
- La consola se actualiza cada ~10 minutos

### Primer Día
- Espera 0-5 operaciones (dependiendo de condiciones del mercado)
- Todas las operaciones seguirán la estrategia multi-temporalidad
- Revisa logs para análisis de señales

### Primera Semana
- Deberías ver comportamiento consistente
- Aparecerá el patrón de ganar/perder
- Puedes empezar a ajustar parámetros

---

## ⚙️ Cambios Rápidos de Configuración

### Cambiar Tamaño de Lote
Edita `config.json`:
```json
{
  "risk": {
    "lot_size": 0.05
  }
}
```

### Cambiar Límites Diarios
```json
{
  "risk": {
    "daily_stop_usd": 20.0,
    "daily_target_usd": 50.0
  }
}
```

### Cambiar Horario de Trading
```json
{
  "session": {
    "session_start": "18:00:00",
    "session_end": "07:00:00"
  }
}
```

---

## 🔍 Comandos de Monitoreo

### Ver Estado Actual
Mira la salida de la consola - se actualiza cada 20 iteraciones (~10 min)

### Ver Operaciones de Hoy
Abre: `logs/trades_YYYYMMDD.log`

### Revisar Errores
Abre: `logs/errors_YYYYMMDD.log`

---

## 🛑 Cómo Detener

Presiona `Ctrl+C` en la ventana de comandos

El bot:
1. Cerrará todas las posiciones abiertas
2. Guardará estadísticas finales
3. Se desconectará de MT5
4. Saldrá de forma elegante

---

## ❓ Solución Rápida de Problemas

### "Fallo de inicialización de MT5"
→ Asegúrate de que MetaTrader 5 esté corriendo

### "Símbolo no encontrado"
→ Agrega símbolos a Market Watch en MT5

### "Fallo de login"
→ Verifica contraseña en config.json

### "Sin señales"
→ ¡Normal! Espera las condiciones adecuadas del mercado

---

## 📚 ¿Necesitas Más Detalles?

- **Configuración Completa:** Lee CONFIGURACION_ES.md
- **Detalles de Estrategia:** Lee README_ES.md
- **Pruebas:** Lee PRUEBAS_ES.md
- **Todas las Características:** Lee RESUMEN_PROYECTO_ES.md

---

## 🎯 Cronograma de Pruebas Recomendado

### Semana 1: Pruebas en Demo
- Ejecutar 8 horas/día mínimo
- Monitorear de cerca
- Revisar logs diariamente

### Semana 2: Demo Extendida
- Ejecutar 24/7 si es posible
- Seguir todas las métricas
- Ajustar parámetros

### Semana 3+: Considerar en Vivo
- Solo si demo exitosa
- Empezar con riesgo mínimo
- Aumentar gradualmente

---

## ⚠️ Recordatorios Importantes

1. **SIEMPRE prueba en demo primero** - ¡Sin excepciones!
2. **Monitorear diariamente** - Especialmente las primeras 2 semanas
3. **Empezar pequeño** - Aumentar tamaño de lote gradualmente
4. **Gestión de riesgo** - Nunca arriesgues más de lo que puedas perder
5. **Ser paciente** - La estrategia necesita condiciones adecuadas del mercado

---

## 🎉 ¡Listo para Operar!

Ahora tienes un sistema de trading completamente automatizado.

**Próximos pasos:**
1. ✅ Ejecutar en demo por 1-2 semanas
2. ✅ Analizar rendimiento
3. ✅ Ajustar parámetros
4. ✅ Cuando esté confiado → considerar en vivo (con precaución!)

**¡Buena suerte y feliz trading!** 📈

---

**Desarrollador:** Borysenko
**Soporte:** Disponible por 30 días post-entrega
**Versión:** 1.0.0
