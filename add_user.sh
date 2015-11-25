#!/bin/bash

# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


# ./add_user.sh <username> <password>

db=$1
db_user=$2
username=$3
password=$4
pass_hash=$(echo -n ${password} | sha256sum | awk -F ' ' '{ print $1 }')

insert="INSERT INTO users (username, password_hash) VALUES"
insert="${insert} ('${username}', '${pass_hash}');"

echo ${username} ${password} ${pass_hash}
su -c "psql -c \"${insert}\" -d ${db}" ${db_user}
