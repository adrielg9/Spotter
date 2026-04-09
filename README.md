# Spotter | Gym Management Engine 🏋️‍♂️

![Python](https://img.shields.io/badge/python-3.12-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flet](https://img.shields.io/badge/flet-%23005cf7.svg?style=for-the-badge&logo=flutter&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**Spotter** es un motor de gestión de escritorio de alto rendimiento diseñado para optimizar la operativa de centros de fitness. Desarrollado con **Python 3.12**, utiliza **Flet** para ofrecer una interfaz moderna, fluida y reactiva, apoyándose en **SQLite3** como motor de persistencia robusto.

---

## ⚡ Módulos Core

- **Auth & Access:** Control de membresías y validación de estados de socios en tiempo real.
- **Revenue Tracker:** Gestión integral de cobros, vencimientos y flujos de caja.
- **Member Analytics:** Persistencia de perfiles de usuario y registro de métricas de asistencia.
- **Architecture-First:** Diseño basado en el patrón **Repository** para un desacoplamiento total entre la lógica de negocio y la base de datos.

## 🏗️ Arquitectura Técnica

El sistema implementa una arquitectura por capas (N-Tier) diseñada bajo principios de ingeniería de software para maximizar la escalabilidad:

| Capa             | Responsabilidad                                              |
| :--------------- | :----------------------------------------------------------- |
| **Controllers**  | Orquestación del flujo de datos y manejo de eventos de Flet. |
| **Services**     | Lógica de negocio transaccional y validaciones técnicas.     |
| **Repositories** | Abstracción de acceso a datos y consultas SQL optimizadas.   |
| **Views**        | Interfaz UI/UX dinámica y reactiva basada en componentes.    |

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12
- **Frontend:** [Flet](https://flet.dev/) (Framework basado en el motor de Flutter)
- **Base de Datos:** SQLite3 (Motor relacional embebido)
- **Patrón de Diseño:** Repository Pattern & Layered Architecture

## 🚀 Instalación y Ejecución

1. **Clonar el repositorio:**

   ```bash
   git clone [https://github.com/adrielg9/Spotter.git](https://github.com/adrielg9/Spotter.git)
   cd Spotter

   ```

2. **Instalar dependencias**
   Bash
   pip install -r requirements.txt

3. **Iniciar la aplicación**

   Bash
   python main.py

👥 Equipo de Desarrollo
Este proyecto es una colaboración interdisciplinaria enfocada en soluciones de gestión:

    Adriel Fernando Gallego
        Arquitectura de Software, Backend & Gestión de Base de Datos
        https://github.com/adrielg9

    Facundo Torres
        Diseño de Interfaz Gráfica (UI/UX) & Estética Visual con Flet
        https://www.linkedin.com/in/facundosebastiantorres/

📜 Licencia
Este proyecto se distribuye bajo la licencia MIT.
