#!/bin/bash
source /opt/backend/bin/bin/activate
exec "$@"
set -e
export POSTGRES_SERVER=db
/tmp/wait_db_start.sh 