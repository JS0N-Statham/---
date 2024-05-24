DROP DATABASE IF EXISTS consumable_db;
CREATE DATABASE IF NOT EXISTS consumable_db;
USE consumable_db;

-- Создание таблицы consumables
CREATE TABLE IF NOT EXISTS consumables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data JSON NOT NULL,
    name_consumables VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables'))) UNIQUE
);

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data JSON NOT NULL,
    name_users VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users'))) UNIQUE
);

-- Создание таблицы tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data JSON NOT NULL,
    name_users VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')))
);

-- Создание таблицы history
CREATE TABLE IF NOT EXISTS history_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data JSON NOT NULL,
    name_users VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users'))),
    name_consumables VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')))
);



--  Добавления данных

INSERT INTO consumables (data) VALUES ('{"name_consumables": "Бумага Снежинка А4 (500 стр.)", "quantity": 80}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Ручка ErichKrause", "quantity": 950}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Элитная ручка ErichKrause", "quantity": 950}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Люкс вода (5 литров)", "quantity": 50}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Люкс вода (19 литров)", "quantity": 30}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Вода демидовъ минеральная негазированная (0,5 л)", "quantity": 400}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Вода демидовъ минеральная газированная (0,5 л)", "quantity": 200}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Вода Нижнесергиенская минеральная газированная (1,5 л)", "quantity": 100}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Картридж лазерный Cactus CS-C728S для Canon i-Sensys", "quantity": 23}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Лазерный картридж NV Print MLT-D111S для принтеров Samsung", "quantity": 23}');
INSERT INTO consumables (data) VALUES ('{"name_consumables": "Пельмени Уральские (Упаковка 500 гр.)", "quantity": 25}');

INSERT INTO users (data) VALUES ('{"name_users": "Manager", "password": "1111"}');
INSERT INTO users (data) VALUES ('{"name_users": "Александр Маркетинг", "password": "1234"}');
INSERT INTO users (data) VALUES ('{"name_users": "Николай Сисадмин", "password": "4321"}');
INSERT INTO users (data) VALUES ('{"name_users": "Василий Реклама", "password": "2222"}');

INSERT INTO tasks (data) VALUES ('{"name_users": "Александр Маркетинг", "task": "Разработайте новую маркетинговую стратегию для компании"}');
INSERT INTO tasks (data) VALUES ('{"name_users": "Василий Реклама", "task": "Займитесь рекламой"}');
INSERT INTO tasks (data) VALUES ('{"name_users": "Николай Сисадмин", "task": "Решите проблему с принтером в бухгалтерии"}');

INSERT INTO history_user (data) VALUES ('{"name_users": "Николай Сисадмин", "name_consumables": "Картридж лазерный Cactus CS-C728S для Canon i-Sensys", "quantity": 1, "time": "2024-05-24 12:34"}');
INSERT INTO history_user (data) VALUES ('{"name_users": "Василий Реклама", "name_consumables": "Люкс вода (19 литров)", "quantity": 3, "time": "2024-05-25 14:22"}');