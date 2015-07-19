#!/bin/bash

user=survey
db=${user}
db_user=${db}
db_pass=${db}

# create linux users and passwords before running

# useradd -d /home/survey -s /bin/bash -m survey
# passwd survey

# install libraries
apt-get update
apt-get install -y git postgis postgresql-9.3-postgis-2.1 \
postgresql-server-dev-9.3 python-pip python-dev nginx

pip install virtualenv

# create postgres user and geo-enabled database
su - postgres # switch to postgres user
psql -c "CREATE USER ${db_user} WITH PASSWORD '${db_password}'"
createdb -O ${db_user} ${db}
psql -c "CREATE EXTENSION postgis;" ${db}
exit # switch back to root user

# clone API repo and build database tables
su - ${user} # switch to survey user
git clone https://github.com/TransitSurveyor/API
cd API
psql -f db/schema.sql -d ${db}
psql -f db/stops.sql -d ${db}

virtualenv env
env/bin/pip install -r requirements.txt
exit

cd /home/survey/API

# !!! open nginx_site_config and correct server_name !!!
cp nginx_site_config /etc/nginx/sites-available/api
cp upstart_init_conf /etc/init/api.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api

# open up nginx and upstart configs and verify the paths and server_name ...
#   vim /etc/nginx/sites-available/api
#   vim /etc/init/api.conf

reboot
