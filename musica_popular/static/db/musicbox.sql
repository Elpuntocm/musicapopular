CREATE DATABASE IF NOT EXISTS musicbox
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE musicbox;

CREATE TABLE IF NOT EXISTS users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  avatar_path VARCHAR(255) DEFAULT NULL,
  reset_code VARCHAR(10) DEFAULT NULL,
  reset_expires DATETIME DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_rewards (
  user_id INT UNSIGNED NOT NULL,
  points INT NOT NULL DEFAULT 0,
  best_score INT NOT NULL DEFAULT 0,
  current_streak INT NOT NULL DEFAULT 0,
  surprise_unlocked TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_musicbox_rewards_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS songs (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  title VARCHAR(140) NOT NULL,
  artist VARCHAR(140) NOT NULL,
  genre VARCHAR(60) NOT NULL,
  year SMALLINT UNSIGNED NOT NULL,
  duration VARCHAR(10) NOT NULL,
  cover TEXT NOT NULL,
  audio_url TEXT NOT NULL,
  featured TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_songs_genre (genre),
  INDEX idx_songs_artist (artist),
  INDEX idx_songs_featured (featured)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO songs (title, artist, genre, year, duration, cover, audio_url, featured)
SELECT * FROM (
  SELECT 'Aventurero', 'Jeison Jimenez', 'Popular', 2024, '4:03', 'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900&q=85', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/9a/9f/4b/9a9f4bef-9f53-28dc-b53a-eb74ff7e3359/mzaf_3396137437711124774.plus.aac.p.m4a', 1
  UNION ALL SELECT 'Maldita Traicion', 'Alzate', 'Popular', 2023, '3:49', 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=900&q=85', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/c4/56/53/c4565372-ea67-1166-ee2f-a1f5bf5850c9/mzaf_12504108257691712081.plus.aac.p.m4a', 1
  UNION ALL SELECT 'El Precio de Tu Error', 'Luis Alberto Posada', 'Despecho', 1998, '3:29', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/56/6e/a2/566ea280-25bd-d48e-4e04-4d031bd7e20c/0889176989452_cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/02/bb/9b/02bb9b26-29de-e838-ea24-f4dcd92ca783/mzaf_306921825045736626.plus.aac.p.m4a', 1
  UNION ALL SELECT 'Por Que la Envidia', 'Yeison Jimenez', 'Popular', 2015, '2:58', 'https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/ff/f1/8e/fff18ef3-37f9-a426-b7f9-65b74a24e398/cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/45/a7/60/45a76060-6b07-8d5a-e512-d578357d17d8/mzaf_9284720271253322973.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Devuelveme La Vida', 'Alzate', 'Despecho', 2015, '3:42', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/e9/af/0d/e9af0d35-9fca-7867-7828-062ff784f079/8445281036034.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/9e/3c/2f/9e3c2fbb-5987-5365-4cbb-83b226cc02a0/mzaf_16175914597899748262.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Dulce Pecado', 'Jessi Uribe', 'Popular', 2022, '3:18', 'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=900&q=85', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/5c/06/a6/5c06a6e8-ba25-ef5d-478b-63207a62d768/mzaf_15541167010748030239.plus.aac.p.m4a', 0
  UNION ALL SELECT 'No Voy a Morir', 'Pipe Bueno', 'Popular', 2008, '3:32', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/f0/ff/b5/f0ffb555-95e3-4b9e-2cf1-ac5d11729764/0672985001435_Cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/18/b8/24/18b824cc-354f-8405-b325-cd47c8e04baf/mzaf_5531644700183181023.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Aunque Me Duela el Alma', 'Luis Alberto Posada', 'Despecho', 2008, '2:23', 'https://is1-ssl.mzstatic.com/image/thumb/Music/75/d7/32/mzi.wnrlqzof.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125/v4/89/e1/59/89e1593d-171d-363b-82ac-3225dc5e48db/mzaf_10667960304155882211.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Mi Venganza', 'Alzate & Yeison Jimenez', 'Despecho', 2015, '3:12', 'https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/9a/dc/3c/9adc3cec-f9b2-c873-adfb-99c8b22f4280/810082230567.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/e1/42/61/e1426169-c4c4-6d33-2fd5-9aedf3173f9e/mzaf_2616257922749041227.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Si Me Ven Llorando', 'Jessi Uribe', 'Despecho', 2021, '2:44', 'https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/0d/9c/10/0d9c5980-fa5f-6024-6491-c33c06a94101/641094337681_cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/fe/6f/90/fe6f9055-41b4-7ca5-b959-f1e994f640d7/mzaf_14116886629007395684.plus.aac.p.m4a', 0
  UNION ALL SELECT 'La Ultima Farra', 'Yeison Jimenez', 'Popular', 2017, '2:51', 'https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/6c/f9/e0/6cf9e025-308d-c192-7b9a-33f3de895b5f/cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/c6/fb/61/c6fb6182-8cc2-d8e5-ef34-5e4cd13d3eb5/mzaf_3609552741043404196.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Mis Borracheras', 'Alzate', 'Despecho', 2015, '2:45', 'https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/02/09/64/02096445-af2e-e1e8-23f2-8c970d488985/810121091258.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/84/58/6d/84586dc1-af65-7dd2-8edd-7d8b9ce3a34c/mzaf_5590927582154612832.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Me Tomas y Me Dejas', 'Luis Alberto Posada', 'Despecho', 2001, '3:22', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/e8/e9/ca/e8e9caf4-8c2c-2c67-eb2b-53b87ce177c1/0.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/21/7d/e7/217de710-f311-0ab7-2b8c-2cf9c490c751/mzaf_10361718279722397161.plus.aac.p.m4a', 0
  UNION ALL SELECT 'La Culpa', 'Jessi Uribe', 'Despecho', 2020, '2:37', 'https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/b4/6d/f7/b46df7c1-c9d7-13c4-a490-0d8958feecd9/650414730873_cover.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview221/v4/d2/37/cc/d237cc84-1164-8679-fc34-a71782edecee/mzaf_11993829992078742302.plus.aac.p.m4a', 0
  UNION ALL SELECT 'Cupido Fallo', 'Pipe Bueno', 'Popular', 2019, '3:17', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/c9/32/0a/c9320a4a-d5a7-b1b2-5890-43209cb260d3/199066104125.jpg/600x600bb.jpg', 'https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview211/v4/94/3c/1d/943c1dbe-e2cd-105c-8eb6-3c211e2813bd/mzaf_18078986314407974051.plus.aac.p.m4a', 0
) AS initial_songs
WHERE NOT EXISTS (SELECT 1 FROM songs LIMIT 1);
