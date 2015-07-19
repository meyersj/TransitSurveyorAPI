#!/bin/bash

server=$1
user=survey
db=${user}
db_user=${db}
db_pass=${db}
proj=/home/${user}/API

# you must run these commands before running this script
# to create a ew linux user with password
#     useradd -d /home/survey -s /bin/bash -m survey
#     passwd survey

# install libraries
apt-get update
apt-get install -y git postgis postgresql-9.3-postgis-2.1 \
postgresql-server-dev-9.3 python-pip python-dev nginx

pip install virtualenv

# create postgres user and geo-enabled database
su - postgres -c "psql -c \"CREATE USER ${db_user} WITH PASSWORD '${db_pass}';\""
su - postgres -c "createdb -O ${db_user} ${db}"
su - postgres -c "psql -c \"CREATE EXTENSION postgis;\" ${db}"

# clone API repo, build database tables and setup environment
su - ${user} -c "git clone https://github.com/TransitSurveyor/API"
su - ${user} -c "psql -f ${proj}/db/schema.sql -d ${db}"
su - ${user} -c "psql -f ${proj}/db/stops.sql -d ${db}"
su - ${user} -c "virtualenv ${proj}/env"
su - ${user} -c "${proj}/env/bin/pip install -r ${proj}/requirements.txt"



cp ${proj}/nginx_site_config /etc/nginx/sites-available/api
cp ${proj}/upstart_init_conf /etc/init/api.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api

if [ "${server}" -gt "-1" ]
  then sed -i 's/host_name_or_ip/${server}/' /etc/nginx/sites-available/api
fi

# open up nginx and upstart configs and verify the paths and server_name ...
#   vim /etc/nginx/sites-available/api
#   vim /etc/init/api.conf
