#!/usr/bin/bash

export PGPASSWORD=$TAB_TABSVR_REPO_PASSWORD

#log into Tableau Repo and run the SQL file
psql -h localhost -p 8060 -d workgroup --username=$TAB_TABSVR_REPO_USER < /home/tableau_srv/scripts/export_repo.sql
