CREATE TABLE IF NOT EXISTS users (
    id              SERIAL                    PRIMARY KEY,
    name            VARCHAR(100)              NOT NULL,
    email           VARCHAR(255)              UNIQUE NOT NULL,
    password_hash   VARCHAR(255)              NOT NULL,
    start_month     DATE                      NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE  NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id              SERIAL                    PRIMARY KEY,
    user_id         BIGINT                    NOT NULL,
    name            VARCHAR(100)              NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    CONSTRAINT categories_user_id_fk
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS operations (
    id              SERIAL                    PRIMARY KEY,
    user_id         BIGINT                    NOT NULL,
    category_id     BIGINT                    NOT NULL,
    type            VARCHAR(20)               NOT NULL,
    amount          NUMERIC(12, 2)            NOT NULL,
    operation_date  DATE                      NOT NULL,
    comment         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    CONSTRAINT operations_user_id_fk
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT operations_category_id_fk
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT operations_type_check
        CHECK (type IN ('income', 'expense')),
    CONSTRAINT operations_amount_check
        CHECK (amount >= 0)
);

CREATE TABLE IF NOT EXISTS budget (
    id              SERIAL                    PRIMARY KEY,
    user_id         BIGINT                    NOT NULL,
    category_id     BIGINT                    NOT NULL,
    month           INTEGER                   NOT NULL,
    year            INTEGER                   NOT NULL,
    planned_amount  NUMERIC(12, 2)            NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE  NOT NULL,
    CONSTRAINT budget_user_id_fk
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT budget_category_id_fk
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT budget_month_check
        CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT budget_year_check
        CHECK (year >= 2000),
    CONSTRAINT budget_planned_amount_check
        CHECK (planned_amount >= 0),
    CONSTRAINT budget_unique_user_category_period
        UNIQUE (user_id, category_id, month, year)
);

CREATE INDEX IF NOT EXISTS idx_categories_user_id
    ON categories(user_id);

CREATE INDEX IF NOT EXISTS idx_operations_user_id
    ON operations(user_id);

CREATE INDEX IF NOT EXISTS idx_operations_category_id
    ON operations(category_id);

CREATE INDEX IF NOT EXISTS idx_operations_operation_date
    ON operations(operation_date);

CREATE INDEX IF NOT EXISTS idx_budget_user_id
    ON budget(user_id);

CREATE INDEX IF NOT EXISTS idx_budget_category_id
    ON budget(category_id);

CREATE INDEX IF NOT EXISTS idx_budget_period
    ON budget(year, month);

CREATE OR REPLACE VIEW actual_expense_summary AS
SELECT
    o.user_id,
    o.category_id,
    EXTRACT(MONTH FROM o.operation_date)::INTEGER AS month,
    EXTRACT(YEAR FROM o.operation_date)::INTEGER AS year,
    SUM(o.amount) AS total_actual
FROM operations o
WHERE o.type = 'expense'
GROUP BY
    o.user_id,
    o.category_id,
    EXTRACT(YEAR FROM o.operation_date),
    EXTRACT(MONTH FROM o.operation_date);
