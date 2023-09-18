#!/usr/bin/bash

export PGPASSWORD=$RDS_POSTGRES_SERVICE_PASSWORD

#PSQL requires single quotes so as to avoid interpreting the environment variable as a column
export TAB_REPO_ENV="'$TABLEAU_REPO_ENVIRONMENT'"

#log into RDS and run the SQL file
psql -v tableau_repo_environment=$TAB_REPO_ENV postgresql://$RDS_POSTGRES_SERVICE_USER:$RDS_POSTGRES_SERVICE_PASSWORD@$RDS_POSTGRES_ENDPOINT/internal_tableau < /home/tableau_srv/scripts/import_repo.sql
