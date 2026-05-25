-- ============================================================
-- Cloud POS System — Full Database Schema
-- Based on: SRS ChromisPOS Stage 1 (Group 1, UGM 2026)
--
-- Run locally:
--   mysql -h localhost -u root -p < schema.sql
--
-- Run on AWS RDS:
--   mysql -h <rds-endpoint> -u admin -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS cloud_pos
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cloud_pos;

-- ============================================================
-- ROLES — user permission levels
-- ============================================================
CREATE TABLE IF NOT EXISTS ROLES (
    ID          VARCHAR(50)   NOT NULL PRIMARY KEY,
    NAME        VARCHAR(100)  NOT NULL,
    PERMISSIONS LONGTEXT
);

-- ============================================================
-- PEOPLE — staff / user accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS PEOPLE (
    ID          VARCHAR(50)   NOT NULL PRIMARY KEY,
    NAME        VARCHAR(255)  NOT NULL,
    ROLE        VARCHAR(50),
    PASS        VARCHAR(255),
    VISIBLE     TINYINT(1)    NOT NULL DEFAULT 1,
    -- Cloud sync fields
    branch_id            VARCHAR(50)   NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_people_role FOREIGN KEY (ROLE) REFERENCES ROLES(ID)
);

-- ============================================================
-- CATEGORIES — product category groupings
-- ============================================================
CREATE TABLE IF NOT EXISTS CATEGORIES (
    ID        VARCHAR(50)  NOT NULL PRIMARY KEY,
    NAME      VARCHAR(255) NOT NULL,
    PARENTID  VARCHAR(50),
    IMAGE     LONGBLOB,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100)
);

-- ============================================================
-- TAXES — tax rates and rules
-- ============================================================
CREATE TABLE IF NOT EXISTS TAXES (
    ID          VARCHAR(50)    NOT NULL PRIMARY KEY,
    NAME        VARCHAR(255)   NOT NULL,
    RATE        DECIMAL(10, 4) NOT NULL DEFAULT 0.0000,
    RATECASCADE TINYINT(1)     NOT NULL DEFAULT 0
);

-- ============================================================
-- LOCATIONS — stock locations / branches
-- ============================================================
CREATE TABLE IF NOT EXISTS LOCATIONS (
    ID      VARCHAR(50)  NOT NULL PRIMARY KEY,
    NAME    VARCHAR(255) NOT NULL,
    ADDRESS VARCHAR(500)
);

-- ============================================================
-- SUPPLIERS — supplier / vendor records
-- ============================================================
CREATE TABLE IF NOT EXISTS SUPPLIERS (
    ID      VARCHAR(50)  NOT NULL PRIMARY KEY,
    NAME    VARCHAR(255) NOT NULL,
    PHONE   VARCHAR(50),
    EMAIL   VARCHAR(255),
    ADDRESS VARCHAR(500),
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100)
);

-- ============================================================
-- PRODUCTS — product / menu items
-- ============================================================
CREATE TABLE IF NOT EXISTS PRODUCTS (
    ID           VARCHAR(50)    NOT NULL PRIMARY KEY,
    NAME         VARCHAR(255)   NOT NULL,
    PRICESELL    DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    CATEGORY     VARCHAR(50),
    TAXCAT       VARCHAR(50),
    BARCODE      VARCHAR(255),
    STOCKCURRENT DECIMAL(12, 3) NOT NULL DEFAULT 0.000,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_products_category FOREIGN KEY (CATEGORY) REFERENCES CATEGORIES(ID),
    CONSTRAINT fk_products_tax      FOREIGN KEY (TAXCAT)   REFERENCES TAXES(ID)
);

-- ============================================================
-- CUSTOMERS — customer records
-- ============================================================
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    ID            VARCHAR(50)  NOT NULL PRIMARY KEY,
    SEARCHKEY     VARCHAR(255),
    NAME          VARCHAR(255) NOT NULL,
    EMAIL         VARCHAR(255),
    PHONE         VARCHAR(50),
    LOYALTYPOINTS INT          NOT NULL DEFAULT 0,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100)
);

-- ============================================================
-- TICKETS — sales transaction headers
-- ============================================================
CREATE TABLE IF NOT EXISTS TICKETS (
    ID          VARCHAR(50)    NOT NULL PRIMARY KEY,
    TICKETTYPE  TINYINT(1)     NOT NULL DEFAULT 0,
    DATENEW     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CUSTOMER    VARCHAR(50),
    PERSON      VARCHAR(50),
    TOTAL       DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_tickets_customer FOREIGN KEY (CUSTOMER) REFERENCES CUSTOMERS(ID),
    CONSTRAINT fk_tickets_person   FOREIGN KEY (PERSON)   REFERENCES PEOPLE(ID)
);

-- ============================================================
-- TICKETLINES — individual line items within a sale
-- ============================================================
CREATE TABLE IF NOT EXISTS TICKETLINES (
    TICKET   VARCHAR(50)    NOT NULL,
    LINE     INT            NOT NULL,
    PRODUCT  VARCHAR(50),
    UNITS    DECIMAL(12, 3) NOT NULL DEFAULT 1.000,
    PRICE    DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    TAXID    VARCHAR(50),
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    PRIMARY KEY (TICKET, LINE),
    CONSTRAINT fk_ticketlines_ticket  FOREIGN KEY (TICKET)  REFERENCES TICKETS(ID),
    CONSTRAINT fk_ticketlines_product FOREIGN KEY (PRODUCT) REFERENCES PRODUCTS(ID),
    CONSTRAINT fk_ticketlines_tax     FOREIGN KEY (TAXID)   REFERENCES TAXES(ID)
);

-- ============================================================
-- STOCKCURRENT — current inventory levels per location
-- ============================================================
CREATE TABLE IF NOT EXISTS STOCKCURRENT (
    LOCATION  VARCHAR(50)    NOT NULL,
    PRODUCT   VARCHAR(50)    NOT NULL,
    UNITS     DECIMAL(12, 3) NOT NULL DEFAULT 0.000,
    PRIMARY KEY (LOCATION, PRODUCT),
    CONSTRAINT fk_stock_location FOREIGN KEY (LOCATION) REFERENCES LOCATIONS(ID),
    CONSTRAINT fk_stock_product  FOREIGN KEY (PRODUCT)  REFERENCES PRODUCTS(ID)
);

-- ============================================================
-- STOCKDIARY — inventory movement log
-- ============================================================
CREATE TABLE IF NOT EXISTS STOCKDIARY (
    ID       VARCHAR(50)    NOT NULL PRIMARY KEY,
    DATENEW  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LOCATION VARCHAR(50)    NOT NULL,
    PRODUCT  VARCHAR(50)    NOT NULL,
    UNITS    DECIMAL(12, 3) NOT NULL,
    REASON   VARCHAR(255),
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_diary_location FOREIGN KEY (LOCATION) REFERENCES LOCATIONS(ID),
    CONSTRAINT fk_diary_product  FOREIGN KEY (PRODUCT)  REFERENCES PRODUCTS(ID)
);

-- ============================================================
-- ORDERS — supplier purchase orders
-- ============================================================
CREATE TABLE IF NOT EXISTS ORDERS (
    ID       VARCHAR(50)    NOT NULL PRIMARY KEY,
    DATENEW  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    SUPPLIER VARCHAR(50),
    STATUS   VARCHAR(50)    NOT NULL DEFAULT 'PENDING',
    TOTAL    DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_orders_supplier FOREIGN KEY (SUPPLIER) REFERENCES SUPPLIERS(ID)
);

-- ============================================================
-- GIFTCARDS — gift card records
-- ============================================================
CREATE TABLE IF NOT EXISTS GIFTCARDS (
    ID      VARCHAR(50)    NOT NULL PRIMARY KEY,
    CODE    VARCHAR(100)   NOT NULL UNIQUE,
    BALANCE DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    EXPIRY  DATE,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100)
);

-- ============================================================
-- LOYALTY — loyalty program transactions
-- ============================================================
CREATE TABLE IF NOT EXISTS LOYALTY (
    ID       VARCHAR(50) NOT NULL PRIMARY KEY,
    CUSTOMER VARCHAR(50) NOT NULL,
    POINTS   INT         NOT NULL DEFAULT 0,
    DATENEW  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Cloud sync fields
    branch_id            VARCHAR(50)  NOT NULL DEFAULT 'branch_1',
    sync_status          ENUM('PENDING','SYNCED','CONFLICT') NOT NULL DEFAULT 'SYNCED',
    last_sync_timestamp  DATETIME,
    cloud_record_id      VARCHAR(100),
    CONSTRAINT fk_loyalty_customer FOREIGN KEY (CUSTOMER) REFERENCES CUSTOMERS(ID)
);

-- ============================================================
-- SEED DATA — sample records for local testing
-- ============================================================

INSERT IGNORE INTO ROLES (ID, NAME, PERMISSIONS) VALUES
    ('role_admin',    'Administrator', 'ALL'),
    ('role_cashier',  'Cashier',       'SALES,CUSTOMERS'),
    ('role_manager',  'Manager',       'SALES,CUSTOMERS,REPORTS,INVENTORY');

INSERT IGNORE INTO TAXES (ID, NAME, RATE, RATECASCADE) VALUES
    ('tax_ppn',  'PPN 11%', 0.1100, 0),
    ('tax_none', 'No Tax',  0.0000, 0);

INSERT IGNORE INTO LOCATIONS (ID, NAME, ADDRESS) VALUES
    ('loc_branch1', 'Branch 1 - Yogyakarta', 'Jl. Malioboro No. 1, Yogyakarta'),
    ('loc_branch2', 'Branch 2 - Sleman',     'Jl. Kaliurang No. 5, Sleman');

INSERT IGNORE INTO CATEGORIES (ID, NAME, branch_id, sync_status) VALUES
    ('cat_food',      'Food',      'branch_1', 'SYNCED'),
    ('cat_beverage',  'Beverage',  'branch_1', 'SYNCED'),
    ('cat_snack',     'Snacks',    'branch_1', 'SYNCED');

INSERT IGNORE INTO PRODUCTS (ID, NAME, PRICESELL, CATEGORY, TAXCAT, BARCODE, STOCKCURRENT, branch_id, sync_status) VALUES
    ('prod_001', 'Coffee',        25000.00, 'cat_beverage', 'tax_ppn',  '8991234560001', 50.000, 'branch_1', 'SYNCED'),
    ('prod_002', 'Milk Tea',      18000.00, 'cat_beverage', 'tax_ppn',  '8991234560002', 35.000, 'branch_1', 'SYNCED'),
    ('prod_003', 'Nasi Goreng',   35000.00, 'cat_food',     'tax_ppn',  '8991234560003', 20.000, 'branch_1', 'SYNCED'),
    ('prod_004', 'French Fries',  22000.00, 'cat_snack',    'tax_ppn',  '8991234560004', 40.000, 'branch_1', 'SYNCED'),
    ('prod_005', 'Mineral Water',  5000.00, 'cat_beverage', 'tax_none', '8991234560005', 100.000,'branch_1', 'SYNCED');

INSERT IGNORE INTO CUSTOMERS (ID, SEARCHKEY, NAME, EMAIL, PHONE, LOYALTYPOINTS, branch_id, sync_status) VALUES
    ('cust_001', 'JOHN001',  'John Doe',      'john@example.com',  '081234567890', 150, 'branch_1', 'SYNCED'),
    ('cust_002', 'JANE001',  'Jane Smith',    'jane@example.com',  '081234567891', 80,  'branch_1', 'SYNCED'),
    ('cust_003', 'BUDI001',  'Budi Santoso',  'budi@example.com',  '081234567892', 200, 'branch_1', 'SYNCED');

INSERT IGNORE INTO PEOPLE (ID, NAME, ROLE, PASS, VISIBLE, branch_id, sync_status) VALUES
    ('person_admin',   'Admin User',    'role_admin',   '1234', 1, 'branch_1', 'SYNCED'),
    ('person_cashier', 'Cashier One',   'role_cashier', '1234', 1, 'branch_1', 'SYNCED'),
    ('person_manager', 'Store Manager', 'role_manager', '1234', 1, 'branch_1', 'SYNCED');

INSERT IGNORE INTO STOCKCURRENT (LOCATION, PRODUCT, UNITS) VALUES
    ('loc_branch1', 'prod_001', 50.000),
    ('loc_branch1', 'prod_002', 35.000),
    ('loc_branch1', 'prod_003', 20.000),
    ('loc_branch1', 'prod_004', 40.000),
    ('loc_branch1', 'prod_005', 100.000);

INSERT IGNORE INTO TICKETS (ID, TICKETTYPE, DATENEW, CUSTOMER, PERSON, TOTAL, branch_id, sync_status) VALUES
    ('ticket_001', 0, '2026-05-01 10:30:00', 'cust_001', 'person_cashier', 43000.00, 'branch_1', 'SYNCED'),
    ('ticket_002', 0, '2026-05-01 11:15:00', 'cust_002', 'person_cashier', 35000.00, 'branch_1', 'SYNCED'),
    ('ticket_003', 0, '2026-05-02 09:00:00', 'cust_003', 'person_cashier', 80000.00, 'branch_1', 'SYNCED');

INSERT IGNORE INTO TICKETLINES (TICKET, LINE, PRODUCT, UNITS, PRICE, TAXID, branch_id, sync_status) VALUES
    ('ticket_001', 1, 'prod_001', 1.000, 25000.00, 'tax_ppn',  'branch_1', 'SYNCED'),
    ('ticket_001', 2, 'prod_002', 1.000, 18000.00, 'tax_ppn',  'branch_1', 'SYNCED'),
    ('ticket_002', 1, 'prod_003', 1.000, 35000.00, 'tax_ppn',  'branch_1', 'SYNCED'),
    ('ticket_003', 1, 'prod_001', 2.000, 25000.00, 'tax_ppn',  'branch_1', 'SYNCED'),
    ('ticket_003', 2, 'prod_003', 1.000, 35000.00, 'tax_ppn',  'branch_1', 'SYNCED');
