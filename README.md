# 🔥 BruteDose - Herramienta Avanzada de Fuerza Bruta

<div align="center">

![BruteDose Banner](https://img.shields.io/badge/BruteDose-v2.0-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Mac-orange)
![Status](https://img.shields.io/badge/Status-Activo-brightgreen)

**Herramienta profesional de fuerza bruta multiservicio creada por doseuser**

[✨ Características](#-características) • [🚀 Instalación Rápida](#-instalación-rápida) • [📖 Uso](#-uso) • [⚡ Modos de Ataque](#-modos-de-ataque) • [🔧 Instalación Avanzada](#-instalación-avanzada) • [📊 Ejemplos](#-ejemplos) • [🤝 Contribuir](#-contribuir) • [⚠️ Aviso Legal](#️-aviso-legal)

</div>

---

## 📋 Descripción

**BruteDose** es una herramienta de fuerza bruta profesional y altamente configurable diseñada para pruebas de penetración y auditorías de seguridad. Con soporte para múltiples protocolos y un motor multihilo potente, BruteDose es la herramienta definitiva para profesionales de ciberseguridad.

**Creado por:** doseuser  
**Repositorio:** [github.com/doseuser/brutedose](https://github.com/doseuser/brutedose)

---

## ✨ Características

### 🚀 **Rendimiento Superior**
- **Multihilo avanzado** (hasta 100+ hilos concurrentes)
- **Timeout configurable** por conexión
- **Reintentos inteligentes** automáticos
- **Velocidad optimizada** para cada protocolo

### 🛡️ **Multiprotocolo**
- ✅ **SSH** - Ataques a servidores Secure Shell
- ✅ **FTP** - Fuerza bruta a servidores FTP/FTPS
- ✅ **Telnet** - Conexiones Telnet legacy
- ✅ **Modo Connect** - Escaneo básico de puertos
- ✅ **Modo Custom** - Protocolos personalizados

### 📊 **Estadísticas en Tiempo Real**
- Monitorización de intentos por segundo
- Tiempo total de ejecución
- Credenciales encontradas en vivo
- Progreso detallado con porcentajes

### 🎯 **Funciones Avanzadas**
- Guardado automático de resultados
- Modo verboso para debugging
- Banner personalizado
- Continuación de ataques interrumpidos
- Exportación en múltiples formatos

---

## 🚀 Instalación Rápida

### Requisitos Previos
```bash
# Python 3.8 o superior
python3 --version

# Instalar dependencias básicas
pip install paramiko
