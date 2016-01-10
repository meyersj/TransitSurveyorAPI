#!/bin/bash
set -e

SCRIPT=$(readlink -f $0)
SCRIPTDIR=`dirname $SCRIPT`

# create virtual environment
cd $SCRIPTDIR
rm -rf env
virtualenv env
env/bin/pip install -r requirements.txt

# build test database (must have postgis installed)
psql -f sql/test_db.sql -d postgres

# run tests
./env/bin/python tests.py
