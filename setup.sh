#!/bin/bash

# Copyright © 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

# NOTE:
#
# you must run these commands before running this script
# to create new linux user with password

#     useradd -d /home/survey -s /bin/bash -m survey
#     passwd survey


set -e

server=$1
user=survey
db=${user}
db_user=${db}
db_pass=${db}
proj=/home/${user}/API


if [ -z "${server}" ]
then
    echo
    echo "Error: You must include server ip or hostname when running script"
    echo
    echo "Usage: setup.sh <ip or hostname>"
    echo
    exit 1
fi

if [ $(grep -c "^${user}:" /etc/passwd) -eq 0 ]; then
    echo
    echo "Error: user ${user} does not exist"
    echo
    echo "To fix: create a new user of that name"
    echo "  # useradd -d /home/${user} -s /bin/bash -m ${survey}"
    echo "  # passwd ${survey}"
    echo
    exit 2
fi


# install libraries
apt-get update
apt-get install -y git postgis postgresql-9.3-postgis-2.1 \
postgresql-server-dev-9.3 python-pip python-dev nginx
pip install virtualenv

# create postgres user and spatial-enabled database
su - postgres -c "psql -c \"CREATE USER ${db_user} WITH PASSWORD '${db_pass}';\""
su - postgres -c "createdb -O ${db_user} ${db}"
su - postgres -c "psql -c \"CREATE EXTENSION postgis;\" ${db}"

# clone API repo, build database tables and setup environment
su - ${user} -c "git clone https://github.com/TransitSurveyor/API"
su - ${user} -c "psql -f ${proj}/data_inputs/schema.sql -d ${db}"
su - ${user} -c "psql -f ${proj}/data_inputs/stops.sql -d ${db}"
su - ${user} -c "/home/survey/API/add_user.sh testuser 1234"
su - ${user} -c "virtualenv ${proj}/env"
su - ${user} -c "${proj}/env/bin/pip install -r ${proj}/requirements.txt"

cp ${proj}/server_config/nginx_site_config /etc/nginx/sites-available/api
cp ${proj}/server_config/upstart_init_conf /etc/init/api.conf
rm -f /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api

sed -i "s/host_name_or_ip/${server}/" /etc/nginx/sites-available/api
su - ${user} -c "echo >> ~/.bashrc"
su - ${user} -c "echo \"export API_ENDPOINT=${server}\" >> ~/.bashrc"


