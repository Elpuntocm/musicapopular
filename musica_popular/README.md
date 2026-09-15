# Musicbox

Sistema de información musical construido con Flask, MySQL y HTML/CSS/JS.

## Ejecutar en AMMPS

1. Inicia Apache y MySQL desde el panel de AMMPS.
2. En phpMyAdmin importa `sql/schema.sql` y después `sql/seed.sql`.
3. Crea tu entorno e instala dependencias:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Copia `.env.example` a `.env` y ajusta `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
5. Ejecuta `python app.py` y abre `http://127.0.0.1:5000`.

Si las variables de MySQL no están completas, la app crea `musicbox.sqlite3` como modo local para que puedas probarla sin bloquear la interfaz.

## Funciones

- Portada con intro musical y selección editorial.
- Biblioteca con búsqueda, filtro por género y reproductor.
- Alta de canciones mediante formulario conectado a la tabla `songs`.
- API JSON disponible en `/api/canciones`.
- Entrada WSGI en `wsgi.py` para despliegues compatibles con Flask.

## Despliegue

Configura en el hosting las mismas variables de `.env.example`, instala `requirements.txt` y apunta el servidor WSGI a `wsgi:application`. Nunca subas un archivo `.env` con credenciales reales.
