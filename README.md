# TransitSurveyor API

**author:** Jeffrey Meyers (jeffrey.alan.meyers@gmail.com)

See https://github.com/TransitSurveyor/Deploy for a vagrant project to build the database and run the api

## Description

Data is received as either a SCAN or STOP. SCAN records occur when collection is done using the **QR Code Scanner** mode while STOP records occur when collection is done using the **Map-Based** mode.

##### SCAN

A scan received consists of the following data

- unique identifier from QR code
- route
- direction
- surveyor id
- timestamp
- mode (ON or OFF)
- latitude and longitude of scan

Based on *mode* the data is handled differently. For **ON** records the data is inserted into a temporary table. Handling **OFF** records requires a few more steps.

1. Query temporary table looking for unmatched ON scan by comparing unique identifier, route and direction.
2. If no match is found nothing happens. The temporary table gets cleared during downtime.
3. If a match is found
    - The record in the temporary table is flagged to avoid future matches
    - A spatial lookup is done using the lat-lon coordinates for the nearest bus stop for given route and direction
    - New ON-OFF record is saved

##### STOP

A stop received consists of the data below. Lookups are done in a stops table to find the corresponding keys
for boarding and alighting stops and then all the data is written to a postgres database.

- route
- direction
- surveyor id
- timestamp
- boarding stop ID
- alighting stop ID
