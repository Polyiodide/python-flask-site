DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS post CASCADE;

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE item (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
);
