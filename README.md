# 🚖 Sistema de Gestión de Taxis - Backend (Clean Architecture)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=for-the-badge&logo=docker)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)

**Universidad de las Fuerzas Armadas - ESPE** **Asignatura:** Arquitectura de Software  
**Período:** Octubre 2025 - Marzo 2026

---

## 📖 Descripción del Proyecto

Este es el Backend del Sistema de Gestión de Taxis, diseñado para manejar el registro de usuarios, conductores, geolocalización y asignación inteligente de viajes.

El proyecto se distingue por implementar una **Arquitectura Limpia (Clean Architecture)** estricta, desacoplando completamente la lógica de negocio (Dominio) del framework web (Django) y la base de datos.

### 🏗️ Arquitectura del Sistema

El código no sigue la estructura tradicional de Django. Se organiza en capas concéntricas respetando la regla de dependencia (las capas internas no conocen a las externas):

```text
src/
├── domain/            # 🧠 CAPA 1: LÓGICA PURA
│   ├── entities.py    # Entidades (Usuario, Viaje) - Dataclasses puros
│   ├── services.py    # Reglas de negocio (Strategy Pattern para asignación)
│   └── repositories.py # Interfaces (Contratos) para la DB
│
├── application/       # 🤝 CAPA 2: CASOS DE USO
│   └── (Orquestación de la lógica, ej: SolicitarTaxi)
│
├── infrastructure/    # 🔌 CAPA 3: ADAPTADORES & FRAMEWORKS
│   ├── django_conf/   # Configuración de Django (settings, wsgi)
│   ├── database/      # Modelos ORM y Migraciones
│   └── repositories/  # Implementación real de los repositorios
```

---

## 🚀 Guía de Inicio Rápido (Setup)

### Prerrequisitos
- **Docker Desktop** (instalado y corriendo).
- **Git**.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/FerQode/taxi-backend-thesis.git
cd backend-taxi-gestion
```

### 2. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz (basado en `.env.example`):
```bash
cp .env.example .env
```
*Asegúrate de que las credenciales de DB coincidan con las del `docker-compose.yml`.*

### 3. Levantar el Entorno (Docker)
Este comando descargará las imágenes de Python, Postgres y Redis, y levantará los servicios.
```bash
docker-compose up --build
```
> **Nota:** La primera vez puede tardar unos minutos. Si ves logs de Django indicando que el servidor corre en `0.0.0.0:8000`, ¡estás listo!

### 4. Aplicar Migraciones
Una vez levantado el contenedor, abre una **nueva terminal** y ejecuta:
```bash
docker-compose run --rm web python manage.py migrate
```

---

## 🛠️ Comandos de Desarrollo (Cheat Sheet)

Como usamos Docker, todos los comandos deben ejecutarse a través de `docker-compose`.

| Acción | Comando |
| :--- | :--- |
| **Crear Migraciones** | `docker-compose run --rm web python manage.py makemigrations database` |
| **Aplicar Migraciones** | `docker-compose run --rm web python manage.py migrate` |
| **Crear Superusuario** | `docker-compose run --rm web python manage.py createsuperuser` |
| **Correr Tests (Pytest)** | `docker-compose run --rm web pytest` |
| **Entrar a la Shell** | `docker-compose run --rm web /bin/bash` |

---

## 🧪 Testing y Calidad

El proyecto utiliza **Pytest** para pruebas unitarias.
- **Tests de Dominio:** Validan la lógica matemática (ej. asignación por cercanía) sin tocar la base de datos.
- **Ejecución:**
  ```bash
  docker-compose run --rm web pytest src/tests/domain
  ```

---

## 🌳 Flujo de Trabajo Git (Gitflow)

Para mantener el orden profesional, respetamos estrictamente las ramas:

1.  **`main`**: ⛔ **PROHIBIDO TOCAR DIRECTAMENTE**. Solo código listo para producción.
2.  **`develop`**: Rama de integración principal. Aquí se unen los cambios.
3.  **`feature/<nombre>`**: Crea una rama para cada nueva funcionalidad.
    * Ej: `feature/auth-login`, `feature/viajes-strategy`.

**Pasos para contribuir:**
1.  `git checkout develop`
2.  `git checkout -b feature/mi-nueva-funcionalidad`
3.  Desarrollar y hacer commits.
4.  Subir cambios: `git push origin feature/mi-nueva-funcionalidad`
5.  Crear un Pull Request hacia `develop`.

---

## 📚 Tecnologías Clave

* **Django REST Framework:** Para la API.
* **PostgreSQL + PostGIS:** Base de datos relacional y espacial.
* **Redis:** Caché y Broker de mensajes.
* **Celery:** Procesamiento de tareas asíncronas (asignación de choferes en background).
* **Gunicorn:** Servidor de aplicaciones WSGI para producción.

---
*Proyecto final de Arquitectura de Software - ESPE 2026*
