PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS Peoples(
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `Name`	TEXT NOT NULL,
            `Age`	INTEGER,
            `Gender`	TEXT );
COMMIT;