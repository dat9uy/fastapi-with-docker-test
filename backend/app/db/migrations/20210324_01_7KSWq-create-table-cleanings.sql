-- CREATE_TABLE_cleanings

CREATE TABLE cleanings
(
    id            SERIAL PRIMARY KEY,
    name          TEXT           NOT NULL,
    description   TEXT,
    cleaning_type VARCHAR(30)    NOT NULL DEFAULT 'spot_clean',
    price         NUMERIC(10, 2) NOT NULL
);

CREATE INDEX idx_name ON cleanings (name);
