import os
import random
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

try:
    import pymysql
except ImportError:
    pymysql = None

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "musicbox.sqlite3"
PROFILE_UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "profiles"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "musicbox-local-secret")
app.config["PERMANENT_SESSION_LIFETIME"] = 86400


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view

DEMO_SONGS = [
    {
        "title": "Aventurero", "artist": "Jeison Jimenez", "genre": "Popular", "year": 2024,
        "duration": "4:03", "cover": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900&q=85",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/9a/9f/4b/9a9f4bef-9f53-28dc-b53a-eb74ff7e3359/mzaf_3396137437711124774.plus.aac.p.m4a", "featured": 1,
    },
    {
        "title": "Maldita Traicion", "artist": "Alzate", "genre": "Popular", "year": 2023,
        "duration": "3:49", "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=900&q=85",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/c4/56/53/c4565372-ea67-1166-ee2f-a1f5bf5850c9/mzaf_12504108257691712081.plus.aac.p.m4a", "featured": 1,
    },
    {
        "title": "El Precio de Tu Error", "artist": "Luis Alberto Posada", "genre": "Despecho", "year": 1998,
        "duration": "3:29", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/56/6e/a2/566ea280-25bd-d48e-4e04-4d031bd7e20c/0889176989452_cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/02/bb/9b/02bb9b26-29de-e838-ea24-f4dcd92ca783/mzaf_306921825045736626.plus.aac.p.m4a", "featured": 1,
    },
    {
        "title": "Por Que la Envidia", "artist": "Yeison Jimenez", "genre": "Popular", "year": 2015,
        "duration": "2:58", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/ff/f1/8e/fff18ef3-37f9-a426-b7f9-65b74a24e398/cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/45/a7/60/45a76060-6b07-8d5a-e512-d578357d17d8/mzaf_9284720271253322973.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Devuelveme La Vida", "artist": "Alzate", "genre": "Despecho", "year": 2015,
        "duration": "3:42", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/e9/af/0d/e9af0d35-9fca-7867-7828-062ff784f079/8445281036034.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/9e/3c/2f/9e3c2fbb-5987-5365-4cbb-83b226cc02a0/mzaf_16175914597899748262.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Dulce Pecado", "artist": "Jessi Uribe", "genre": "Popular", "year": 2022,
        "duration": "3:18", "cover": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=900&q=85",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/5c/06/a6/5c06a6e8-ba25-ef5d-478b-63207a62d768/mzaf_15541167010748030239.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "No Voy a Morir", "artist": "Pipe Bueno", "genre": "Popular", "year": 2008,
        "duration": "3:32", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/f0/ff/b5/f0ffb555-95e3-4b9e-2cf1-ac5d11729764/0672985001435_Cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/18/b8/24/18b824cc-354f-8405-b325-cd47c8e04baf/mzaf_5531644700183181023.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Aunque Me Duela el Alma", "artist": "Luis Alberto Posada", "genre": "Despecho", "year": 2008,
        "duration": "2:23", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music/75/d7/32/mzi.wnrlqzof.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/89/e1/59/89e1593d-171d-363b-82ac-3225dc5e48db/mzaf_10667960304155882211.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Mi Venganza", "artist": "Alzate & Yeison Jimenez", "genre": "Despecho", "year": 2015,
        "duration": "3:12", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/9a/dc/3c/9adc3cec-f9b2-c873-adfb-99c8b22f4280/810082230567.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/e1/42/61/e1426169-c4c4-6d33-2fd5-9aedf3173f9e/mzaf_2616257922749041227.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Si Me Ven Llorando", "artist": "Jessi Uribe", "genre": "Despecho", "year": 2021,
        "duration": "2:44", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/0d/9c/10/0d9c5980-fa5f-6024-6491-c33c06a94101/641094337681_cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/fe/6f/90/fe6f9055-41b4-7ca5-b959-f1e994f640d7/mzaf_14116886629007395684.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "La Ultima Farra", "artist": "Yeison Jimenez", "genre": "Popular", "year": 2017,
        "duration": "2:51", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/6c/f9/e0/6cf9e025-308d-c192-7b9a-33f3de895b5f/cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/c6/fb/61/c6fb6182-8cc2-d8e5-ef34-5e4cd13d3eb5/mzaf_3609552741043404196.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Mis Borracheras", "artist": "Alzate", "genre": "Despecho", "year": 2015,
        "duration": "2:45", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/02/09/64/02096445-af2e-e1e8-23f2-8c970d488985/810121091258.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/84/58/6d/84586dc1-af65-7dd2-8edd-7d8b9ce3a34c/mzaf_5590927582154612832.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Me Tomas y Me Dejas", "artist": "Luis Alberto Posada", "genre": "Despecho", "year": 2001,
        "duration": "3:22", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/e8/e9/ca/e8e9caf4-8c2c-2c67-eb2b-53b87ce177c1/0.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/21/7d/e7/217de710-f311-0ab7-2b8c-2cf9c490c751/mzaf_10361718279722397161.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "La Culpa", "artist": "Jessi Uribe", "genre": "Despecho", "year": 2020,
        "duration": "2:37", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/b4/6d/f7/b46df7c1-c9d7-13c4-a490-0d8958feecd9/650414730873_cover.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/d2/37/cc/d237cc84-1164-8679-fc34-a71782edecee/mzaf_11993829992078742302.plus.aac.p.m4a", "featured": 0,
    },
    {
        "title": "Cupido Fallo", "artist": "Pipe Bueno", "genre": "Popular", "year": 2019,
        "duration": "3:17", "cover": "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/c9/32/0a/c9320a4a-d5a7-b1b2-5890-43209cb260d3/199066104125.jpg/600x600bb.jpg",
        "audio_url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/94/3c/1d/943c1dbe-e2cd-105c-8eb6-3c211e2813bd/mzaf_18078986314407974051.plus.aac.p.m4a", "featured": 0,
    },
]


def mysql_configured():
    return bool(os.getenv("DB_HOST") and os.getenv("DB_NAME") and os.getenv("DB_USER") and pymysql)


def get_mysql_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "musicbox"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_sqlite_connection():
    connection = sqlite3.connect(SQLITE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    legacy_titles = (
        "Por Que Te Vas", "No Estoy Bien", "Borracho de Amor",
        "Me Gaste la Vida", "Devuelveme la Vida", "Te Hubieras Ido Antes",
    )
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(190) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    avatar_path VARCHAR(255) DEFAULT NULL,
                    reset_code VARCHAR(10) DEFAULT NULL,
                    reset_expires DATETIME DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_rewards (
                    user_id INT PRIMARY KEY,
                    points INT NOT NULL DEFAULT 0,
                    best_score INT NOT NULL DEFAULT 0,
                    current_streak INT NOT NULL DEFAULT 0,
                    surprise_unlocked TINYINT(1) NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            try:
                cursor.execute("ALTER TABLE user_rewards ADD COLUMN current_streak INT NOT NULL DEFAULT 0")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN avatar_path VARCHAR(255) DEFAULT NULL")
            except Exception:
                pass
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(140) NOT NULL,
                    artist VARCHAR(140) NOT NULL,
                    genre VARCHAR(60) NOT NULL,
                    year INT NOT NULL,
                    duration VARCHAR(10) NOT NULL,
                    cover TEXT NOT NULL,
                    audio_url TEXT NOT NULL,
                    featured TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT COUNT(*) AS total FROM songs WHERE title IN ('Midnight City', 'Electric Feel', 'Afterglow')")
            if cursor.fetchone()["total"]:
                cursor.execute("DELETE FROM songs")
            cursor.execute("DELETE FROM songs WHERE title IN (%s, %s, %s, %s, %s, %s)", legacy_titles)
            cursor.execute("SELECT COUNT(*) AS total FROM songs")
            if cursor.fetchone()["total"] == 0:
                cursor.executemany(
                    "INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    [(song["title"], song["artist"], song["genre"], song["year"], song["duration"], song["cover"], song["audio_url"], song["featured"]) for song in DEMO_SONGS],
                )
            for song in DEMO_SONGS:
                cursor.execute("UPDATE songs SET cover = %s, audio_url = %s WHERE title = %s AND artist = %s", (song["cover"], song["audio_url"], song["title"], song["artist"]))
                cursor.execute("SELECT COUNT(*) AS total FROM songs WHERE title = %s AND artist = %s", (song["title"], song["artist"]))
                if cursor.fetchone()["total"] == 0:
                    cursor.execute("INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (song["title"], song["artist"], song["genre"], song["year"], song["duration"], song["cover"], song["audio_url"], song["featured"]))
        connection.close()
        return

    connection = get_sqlite_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            avatar_path TEXT,
            reset_code TEXT,
            reset_expires TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS user_rewards (
            user_id INTEGER PRIMARY KEY,
            points INTEGER NOT NULL DEFAULT 0,
            best_score INTEGER NOT NULL DEFAULT 0,
            current_streak INTEGER NOT NULL DEFAULT 0,
            surprise_unlocked INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    reward_columns = [column[1] for column in connection.execute("PRAGMA table_info(user_rewards)").fetchall()]
    if "current_streak" not in reward_columns:
        connection.execute("ALTER TABLE user_rewards ADD COLUMN current_streak INTEGER NOT NULL DEFAULT 0")
    user_columns = [column[1] for column in connection.execute("PRAGMA table_info(users)").fetchall()]
    if "avatar_path" not in user_columns:
        connection.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, artist TEXT NOT NULL, genre TEXT NOT NULL,
            year INTEGER NOT NULL, duration TEXT NOT NULL, cover TEXT NOT NULL,
            audio_url TEXT NOT NULL, featured INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    legacy_demo = connection.execute("SELECT COUNT(*) FROM songs WHERE title IN ('Midnight City', 'Electric Feel', 'Afterglow')").fetchone()[0]
    if legacy_demo:
        connection.execute("DELETE FROM songs")
    connection.executemany("DELETE FROM songs WHERE title = ?", [(title,) for title in legacy_titles])
    if connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(song["title"], song["artist"], song["genre"], song["year"], song["duration"], song["cover"], song["audio_url"], song["featured"]) for song in DEMO_SONGS],
        )
    for song in DEMO_SONGS:
        connection.execute("UPDATE songs SET cover = ?, audio_url = ? WHERE title = ? AND artist = ?", (song["cover"], song["audio_url"], song["title"], song["artist"]))
        exists = connection.execute("SELECT COUNT(*) FROM songs WHERE title = ? AND artist = ?", (song["title"], song["artist"])).fetchone()[0]
        if not exists:
            connection.execute("INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (song["title"], song["artist"], song["genre"], song["year"], song["duration"], song["cover"], song["audio_url"], song["featured"]))
    connection.commit()
    connection.close()


def find_user_by_email(email):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
            user = cursor.fetchone()
        connection.close()
        return user
    connection = get_sqlite_connection()
    user = connection.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    connection.close()
    return dict(user) if user else None


def find_user_by_id(user_id):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        connection.close()
        return user
    connection = get_sqlite_connection()
    user = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    connection.close()
    return dict(user) if user else None


def change_user_password(user_id, password):
    password_hash = generate_password_hash(password)
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    connection.commit()
    connection.close()


def get_user_profile(user_id):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT u.id, u.name, u.email, u.avatar_path, u.created_at, COALESCE(r.points, 0) AS points, COALESCE(r.best_score, 0) AS best_score, COALESCE(r.current_streak, 0) AS current_streak, COALESCE(r.surprise_unlocked, 0) AS surprise_unlocked FROM users u LEFT JOIN user_rewards r ON r.user_id = u.id WHERE u.id = %s", (user_id,))
            profile = cursor.fetchone()
        connection.close()
        return profile
    connection = get_sqlite_connection()
    profile = connection.execute("SELECT u.id, u.name, u.email, u.avatar_path, u.created_at, COALESCE(r.points, 0) AS points, COALESCE(r.best_score, 0) AS best_score, COALESCE(r.current_streak, 0) AS current_streak, COALESCE(r.surprise_unlocked, 0) AS surprise_unlocked FROM users u LEFT JOIN user_rewards r ON r.user_id = u.id WHERE u.id = ?", (user_id,)).fetchone()
    connection.close()
    return dict(profile) if profile else None


def save_avatar(user_id, file_storage):
    filename = secure_filename(file_storage.filename or "")
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return False
    PROFILE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"user-{user_id}.{extension}"
    file_storage.save(PROFILE_UPLOAD_DIR / stored_name)
    avatar_path = f"uploads/profiles/{stored_name}"
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET avatar_path = %s WHERE id = %s", (avatar_path, user_id))
        connection.close()
    else:
        connection = get_sqlite_connection()
        connection.execute("UPDATE users SET avatar_path = ? WHERE id = ?", (avatar_path, user_id))
        connection.commit()
        connection.close()
    return True


def record_game_result(user_id, score, correct):
    profile = get_user_profile(user_id)
    if not profile:
        return
    points = profile["points"] + (1 if correct else 0)
    best_score = max(profile["best_score"], score)
    current_streak = profile["current_streak"] + 1 if correct else max(0, profile["current_streak"] - 1)
    surprise = 1 if points >= 10 else profile["surprise_unlocked"]
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO user_rewards (user_id, points, best_score, current_streak, surprise_unlocked) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE points = %s, best_score = %s, current_streak = %s, surprise_unlocked = %s", (user_id, points, best_score, current_streak, surprise, points, best_score, current_streak, surprise))
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("INSERT INTO user_rewards (user_id, points, best_score, current_streak, surprise_unlocked) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET points = excluded.points, best_score = excluded.best_score, current_streak = excluded.current_streak, surprise_unlocked = excluded.surprise_unlocked", (user_id, points, best_score, current_streak, surprise))
    connection.commit()
    connection.close()


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name.strip(), email.lower(), password_hash))
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", (name.strip(), email.lower(), password_hash))
    connection.commit()
    connection.close()


def save_reset_code(email, code):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET reset_code = %s, reset_expires = DATE_ADD(NOW(), INTERVAL 15 MINUTE) WHERE email = %s", (code, email.lower()))
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("UPDATE users SET reset_code = ?, reset_expires = datetime('now', '+15 minutes') WHERE email = ?", (code, email.lower()))
    connection.commit()
    connection.close()


def reset_password(email, code, password):
    user = find_user_by_email(email)
    if not user or user["reset_code"] != code:
        return False
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET password_hash = %s, reset_code = NULL, reset_expires = NULL WHERE email = %s AND reset_code = %s AND reset_expires > NOW()", (generate_password_hash(password), email.lower(), code))
            updated = cursor.rowcount
        connection.close()
        return bool(updated)
    connection = get_sqlite_connection()
    updated = connection.execute("UPDATE users SET password_hash = ?, reset_code = NULL, reset_expires = NULL WHERE email = ? AND reset_code = ? AND reset_expires > datetime('now')", (generate_password_hash(password), email.lower(), code)).rowcount
    connection.commit()
    connection.close()
    return bool(updated)


def fetch_songs(search="", genre="", featured_only=False):
    search = f"%{search.strip()}%"
    if mysql_configured():
        connection = get_mysql_connection()
        query = "SELECT * FROM songs WHERE (title LIKE %s OR artist LIKE %s)"
        params = [search, search]
        if genre:
            query += " AND genre = %s"
            params.append(genre)
        if featured_only:
            query += " AND featured = 1"
        query += " ORDER BY featured DESC, year DESC, id DESC"
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            songs = cursor.fetchall()
        connection.close()
        return songs

    connection = get_sqlite_connection()
    query = "SELECT * FROM songs WHERE (title LIKE ? OR artist LIKE ?)"
    params = [search, search]
    if genre:
        query += " AND genre = ?"
        params.append(genre)
    if featured_only:
        query += " AND featured = 1"
    query += " ORDER BY featured DESC, year DESC, id DESC"
    songs = [dict(song) for song in connection.execute(query, params).fetchall()]
    connection.close()
    return songs


def create_song(data):
    values = (data["title"].strip(), data["artist"].strip(), data["genre"].strip(), int(data["year"]), data["duration"].strip(), data["cover"].strip(), data["audio_url"].strip(), int(data.get("featured", 0)))
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", values)
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)
    connection.commit()
    connection.close()


def delete_song(song_id):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM songs WHERE id = %s", (song_id,))
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    connection.commit()
    connection.close()


def find_song(song_id):
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM songs WHERE id = %s", (song_id,))
            song = cursor.fetchone()
        connection.close()
        return song
    connection = get_sqlite_connection()
    song = connection.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
    connection.close()
    return dict(song) if song else None


def update_song(song_id, data):
    values = (data["title"].strip(), data["artist"].strip(), data["genre"].strip(), int(data["year"]), data["duration"].strip(), data["cover"].strip(), data["audio_url"].strip(), int(data.get("featured", 0)), song_id)
    if mysql_configured():
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE songs SET title = %s, artist = %s, genre = %s, year = %s, duration = %s, cover = %s, audio_url = %s, featured = %s WHERE id = %s", values)
        connection.close()
        return
    connection = get_sqlite_connection()
    connection.execute("UPDATE songs SET title = ?, artist = ?, genre = ?, year = ?, duration = ?, cover = ?, audio_url = ?, featured = ? WHERE id = ?", values)
    connection.commit()
    connection.close()


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year, "using_mysql": mysql_configured(), "current_user": session.get("user_name")}


@app.route("/iniciar-sesion", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = find_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], request.form.get("password", "")):
            error = "El correo o la contraseña no son correctos."
        else:
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            next_url = request.args.get("next", "")
            return redirect(next_url if next_url.startswith("/") and not next_url.startswith("//") else url_for("home"))
    return render_template("auth.html", mode="login", error=error)


@app.route("/crear-usuario", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")
        if not name or not email or len(password) < 8:
            error = "Completa los campos y usa una contraseña de mínimo 8 caracteres."
        elif password != confirmation:
            error = "Las contraseñas no coinciden."
        elif find_user_by_email(email):
            error = "Ya existe un usuario con ese correo."
        else:
            create_user(name, email, password)
            return redirect(url_for("login", created="1"))
    return render_template("auth.html", mode="register", error=error)


@app.route("/recuperar-contrasena", methods=["GET", "POST"])
def forgot_password():
    error = None
    recovery_code = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if find_user_by_email(email):
            recovery_code = f"{secrets.randbelow(1000000):06d}"
            save_reset_code(email, recovery_code)
            session["recovery_email"] = email
        else:
            error = "No encontramos un usuario con ese correo."
    return render_template("auth.html", mode="forgot", error=error, recovery_code=recovery_code)


@app.route("/restablecer-contrasena", methods=["GET", "POST"])
def reset_password_route():
    error = None
    email = session.get("recovery_email", "")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")
        if len(password) < 8:
            error = "La nueva contraseña debe tener mínimo 8 caracteres."
        elif password != confirmation:
            error = "Las contraseñas no coinciden."
        elif not reset_password(email, code, password):
            error = "El código es incorrecto o ya expiró."
        else:
            session.pop("recovery_email", None)
            return redirect(url_for("login", reset="1"))
    return render_template("auth.html", mode="reset", error=error, recovery_email=email)


@app.get("/cerrar-sesion")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    featured = fetch_songs(featured_only=True)[:3] if session.get("user_id") else []
    return render_template("index.html", featured=featured)


@app.route("/biblioteca")
@login_required
def library():
    search = request.args.get("q", "")
    genre = request.args.get("genre", "")
    songs = fetch_songs(search, genre)
    genres = sorted({song["genre"] for song in fetch_songs()})
    return render_template("library.html", songs=songs, genres=genres, search=search, selected_genre=genre)


@app.route("/juego", methods=["GET", "POST"])
@login_required
def game():
    songs = fetch_songs()
    if not songs:
        return render_template("game.html", question=None, score=0, streak=0, feedback=None)
    if "game_streak" not in session:
        session["game_streak"] = get_user_profile(session["user_id"])["current_streak"]
    if request.args.get("nuevo"):
        session["game_score"] = 0
        session.pop("game_artist", None)
    feedback = None
    feedback_artist = None
    if request.method == "POST":
        selected = request.form.get("artist", "")
        correct = session.get("game_artist")
        feedback_artist = correct
        if selected == correct:
            session["game_score"] = session.get("game_score", 0) + 1
            session["game_streak"] = session.get("game_streak", 0) + 1
            record_game_result(session["user_id"], session["game_score"], True)
            feedback = "correct"
        else:
            session["game_streak"] = max(0, session.get("game_streak", 0) - 1)
            record_game_result(session["user_id"], session.get("game_score", 0), False)
            feedback = "wrong"
    question = random.choice(songs)
    artists = list({song["artist"] for song in songs})
    choices = [question["artist"]]
    choices.extend(random.sample([artist for artist in artists if artist != question["artist"]], min(3, len(artists) - 1)))
    random.shuffle(choices)
    session["game_artist"] = question["artist"]
    return render_template("game.html", question=question, choices=choices, score=session.get("game_score", 0), streak=session.get("game_streak", 0), feedback=feedback, feedback_artist=feedback_artist)


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        avatar = request.files.get("avatar")
        if not avatar or not avatar.filename:
            return redirect(url_for("profile", avatar_error="Selecciona una imagen."))
        if not save_avatar(session["user_id"], avatar):
            return redirect(url_for("profile", avatar_error="Usa una imagen JPG, PNG, WEBP o GIF."))
        return redirect(url_for("profile", avatar_updated="1"))
    profile_data = get_user_profile(session["user_id"])
    streak = profile_data["current_streak"]
    levels = [
        ("Novato", "comienza tu recorrido", "level-rookie.svg"),
        ("Explorador", "10 aciertos consecutivos", "level-explorer.svg"),
        ("Coleccionista", "20 aciertos consecutivos", "level-collector.svg"),
        ("Headliner", "30 aciertos consecutivos", "level-headliner.svg"),
        ("Icono", "40 aciertos consecutivos", "level-icon.svg"),
        ("Leyenda", "50 aciertos consecutivos", "level-legend.svg"),
    ]
    level_index = min(streak // 10, len(levels) - 1)
    level_name, level_subtitle, level_image = levels[level_index]
    next_level = (level_index + 1) * 10 - streak if level_index < len(levels) - 1 else None
    level = {"name": level_name, "subtitle": level_subtitle, "image": level_image, "next": next_level}
    return render_template("profile.html", profile=profile_data, level=level)


@app.post("/perfil/cambiar-contrasena")
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirmation = request.form.get("confirmation", "")
    user = find_user_by_id(session["user_id"])
    if not user or not check_password_hash(user["password_hash"], current_password):
        return redirect(url_for("profile", password_error="La contraseña actual no es correcta."))
    if len(new_password) < 8:
        return redirect(url_for("profile", password_error="La nueva contraseña debe tener mínimo 8 caracteres."))
    if new_password != confirmation:
        return redirect(url_for("profile", password_error="Las contraseñas nuevas no coinciden."))
    change_user_password(session["user_id"], new_password)
    return redirect(url_for("profile", password_updated="1"))


@app.route("/canciones/<int:song_id>/editar", methods=["GET", "POST"])
@login_required
def edit_song(song_id):
    song = find_song(song_id)
    if not song:
        return redirect(url_for("library", error="La canción no existe."))
    if request.method == "POST":
        required = ["title", "artist", "genre", "year", "duration", "cover", "audio_url"]
        if any(not request.form.get(field, "").strip() for field in required):
            return render_template("edit_song.html", song=song, error="Completa todos los campos de la canción.")
        try:
            update_song(song_id, request.form)
        except (ValueError, TypeError):
            return render_template("edit_song.html", song=song, error="El año debe ser un número válido.")
        return redirect(url_for("library", updated="1"))
    return render_template("edit_song.html", song=song)


@app.post("/canciones")
@login_required
def add_song():
    required = ["title", "artist", "genre", "year", "duration", "cover", "audio_url"]
    if any(not request.form.get(field, "").strip() for field in required):
        return redirect(url_for("library", error="Completa todos los campos de la canción."))
    try:
        create_song(request.form)
    except (ValueError, TypeError):
        return redirect(url_for("library", error="El año debe ser un número válido."))
    return redirect(url_for("library", created="1"))


@app.post("/canciones/<int:song_id>/eliminar")
@login_required
def remove_song(song_id):
    delete_song(song_id)
    return redirect(url_for("library", deleted="1"))


@app.get("/api/canciones")
@login_required
def songs_api():
    return jsonify(fetch_songs(request.args.get("q", ""), request.args.get("genre", "")))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=int(os.getenv("PORT", "5000")))
