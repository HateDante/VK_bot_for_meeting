CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    age INTEGER,
    gender VARCHAR,
    city VARCHAR
);

CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    url VARCHAR,
    likes INTEGER
);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    favorite_user_id INTEGER REFERENCES users(id)
);

CREATE TABLE blacklist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    blacklisted_user_id INTEGER REFERENCES users(id)
);

-- Получение трех самых популярных фотографий для всех пользователей
WITH RankedPhotos AS (
    SELECT *,
           RANK() OVER (PARTITION BY user_id ORDER BY likes DESC) as rank
    FROM photos
)
SELECT user_id, id, url, likes
FROM RankedPhotos
WHERE rank <= 3;