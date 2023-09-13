#!/usr/bin/bash

export PGPASSWORD=$TAB_TABSVR_REPO_PASSWORD

#log into Tableau Repo and run the SQL file
psql postgresql://$TAB_TABSVR_REPO_USER:$PGPASSWORD@localhost:8060/workgroup < /home/tableau_srv/scripts/export_repo.sql
