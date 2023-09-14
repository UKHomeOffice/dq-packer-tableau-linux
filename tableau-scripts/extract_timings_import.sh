#!/usr/bin/bash

export PGPASSWORD=$RDS_POSTGRES_SERVICE_PASSWORD

#log into RDS and run the SQL file
psql -v tableau_repo_environment=$TABLEAU_REPO_ENVIRONMENT postgresql://$RDS_POSTGRES_SERVICE_USER:$RDS_POSTGRES_SERVICE_PASSWORD@$RDS_POSTGRES_ENDPOINT/internal_tableau < /home/tableau_srv/scripts/import_repo.sql
