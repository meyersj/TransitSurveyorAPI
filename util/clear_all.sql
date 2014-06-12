--drops all records from every table
--used for clearing dev database

BEGIN;
DELETE FROM on_temp;
DELETE FROM off_temp;
DELETE FROM on_off_pairs__scans;
DELETE FROM on_off_pairs__stops;
COMMIT;
