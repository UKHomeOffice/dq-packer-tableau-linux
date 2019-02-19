#!/bin/bash
if [ "$#" -ne 2 ]
then
  echo "Usage: $0 [PROJECT] [DATASOURCE_FILENAME]"
  exit 1
fi

PROJECT=$1
DATASOURCE_FILENAME=$2
if [ ! -f "$DATASOURCE_FILENAME" ]
then
  echo "DataSource file ($DATASOURCE_FILENAME) does not exist"
  exit 2
fi

tabcmd publish "$DATASOURCE_FILENAME" --project "$PROJECT" --overwrite --db-username "$TAB_DB_USER" --db-password "$TAB_DB_PASSWORD" --save-db-password
#tabcmd publish \"$DATASOURCE_FILENAME\" --project \"$PROJECT\" --overwrite --db-username "$TAB_DB_USER" --db-password "$TAB_DB_PASSWORD" --save-db-password
