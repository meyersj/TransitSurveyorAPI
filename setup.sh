#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTDIR=`dirname $SCRIPT`

cd $SCRIPTDIR
rm -rf env
virtualenv env
env/bin/pip install -r requirements.txt

psql -f sql/onoff.sql
