--drops all records from temp tables
--used for cleaning up prod database nightly

BEGIN;
DELETE FROM on_temp;
DELETE FROM off_temp;
COMMIT;
