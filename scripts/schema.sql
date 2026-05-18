-- Cloud POS — database schema and seed data.
-- Run this once against the target database (local MySQL or Amazon RDS).
--   mysql -h <host> -u <user> -p < scripts/schema.sql

CREATE DATABASE IF NOT EXISTS cloud_pos
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cloud_pos;

CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255)   NOT NULL,
    price       DECIMAL(12, 2) NOT NULL,
    stock       INT            NOT NULL DEFAULT 0,
    branch_id   VARCHAR(50)    NOT NULL DEFAULT 'branch_1',
    sync_status VARCHAR(20)    NOT NULL DEFAULT 'PENDING'
);

CREATE TABLE IF NOT EXISTS customers (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

-- Seed data (matches the records used in the Week 3 report).
INSERT INTO products (name, price, stock, branch_id, sync_status) VALUES
    ('Coffee',   25000, 50, 'branch_1', 'SYNCED'),
    ('Milk Tea', 18000, 35, 'branch_1', 'SYNCED');

INSERT INTO customers (name, email) VALUES
    ('John Doe', 'john@example.com');
