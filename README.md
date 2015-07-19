# TransitSurveyor API

## Setup

Here are instructions for how to get a server/database up and running for the [API](https://github.com/TransitSurveyor/API) to recieve and store data collected using [MobileSurveyor](https://github.com/TransitSurveyor/MobileSurveyor).

+ *OS:* Ubuntu
+ *Database:* PostgreSQL
+ *Framework:* Python/Flask
+ *Server:* NginX/uWSGI

#### Create a (virtual private) server
If needed signup with [DigitalOcean](https://www.digitalocean.com/), then create a droplet. This will cost you $5 dollar a month to run. You can take a snapshot then destroy to avoid being charged when not using it. [Tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-your-first-digitalocean-droplet-virtual-server)
+ choose Ubuntu 14.04 with 512MB RAM

#### Build and Configure
```shell
# connect to server
ssh root@new_ip_address

# create new user
useradd -d /home/survey -s /bin/bash -m survey
passwd survey

# if you change the user from `survey` to something else
# you need to make that change in `setup.sh` also

# download and execute setup script
curl https://raw.githubusercontent.com/TransitSurveyor/API/master/setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh

# -------------- update config files ------------------
# open up nginx and upstart config files to verify the paths and server_name ...
#   vim /etc/nginx/sites-available/api
#   vim /etc/init/api.conf
# -----------------------------------------------------
```

## Description

Data is received as either a SCAN or STOP. SCAN records occur when collection is done using the **QR Code Scanner** mode while STOP records occur when collection is done using the **Map-Based** mode.

##### SCAN

A scan recieved consists of the following data

- unique identifier from QR code
- route
- direction
- surveyor id
- timestamp
- mode (ON or OFF)
- latitude and longitude of scan

Based on *mode* the data is handled differently. For **ON** records the data is inserted into a temporary table. Handling **OFF** records requires a few more steps.

1. Query temporary table looking for unmatched ON scan by comparing unique identifer, route and direction.
2. If no match is found nothin happends. The temporary table gets cleared during downtime.
3. If a match is found
    - The record in the temporary table is flagged to avoid future matches
    - A spatial lookup is done using the lat-lon coordinates for the nearest bus stop for given route and direction
    - New ON-OFF record is saved

##### STOP

A stop recieved consists of the data below. Lookups are done in a stops table to find the corresponding keys
for boarding and alighting stops and then all the data is written to a postgres database.

- route
- direction
- surveyor id
- timestamp
- boarding stop ID
- alighting stop ID
