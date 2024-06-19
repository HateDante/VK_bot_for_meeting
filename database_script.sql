CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE,
    age INT,
    gender VARCHAR,
    city VARCHAR
);

CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    url VARCHAR,
    likes INT
);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    favorite_user_id INT REFERENCES users(user_id)
);

CREATE TABLE blacklist (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    blacklisted_user_id INT REFERENCES users(user_id)
);
