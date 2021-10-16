CREATE TABLE expense_categories (
    id SERIAL PRIMARY KEY,
    cat_name VARCHAR
);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    creation_timestamp TIMESTAMP DEFAULT NOW(),
    amount FLOAT,
    cat_id INT DEFAULT 1,
    exp_description VARCHAR DEFAULT '',
    CONSTRAINT fk_expense_categories
        FOREIGN KEY(cat_id)
            REFERENCES expense_categories(id)
            ON DELETE CASCADE
);


INSERT INTO expense_categories (cat_name) VALUES ('Unknown');
INSERT INTO expense_categories (cat_name) VALUES ('Shop');
INSERT INTO expense_categories (cat_name) VALUES ('Entertainment');
INSERT INTO expense_categories (cat_name) VALUES ('Restaurant');
