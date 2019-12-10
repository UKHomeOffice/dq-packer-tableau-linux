#!/bin/bash
# Script to restore from backup from night before (from Green server).

echo "Restoring from most recent (Green) backup."
echo "This will cause existing WorkBooks and DataSources to be removed from Tableau."
read -p "Are you sure [y/N]? " -n 1 -r
echo    # new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting."
    exit 1
fi

# Restore from Green
export BACKUP_LOCATION="$DATA_ARCHIVE_TAB_BACKUP_URL/green/"

echo "Get most recent Tableau backup from S3"
export LATEST_BACKUP_NAME=`aws s3 ls $BACKUP_LOCATION | tail -1 | awk '{print $4}'`
aws s3 cp $BACKUP_LOCATION$LATEST_BACKUP_NAME /var/opt/tableau/tableau_server/data/tabsvc/files/backups/$LATEST_BACKUP_NAME

echo "Restore latest backup to Tableau Server"
tsm stop --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD" && tsm maintenance restore --file $LATEST_BACKUP_NAME --username "$TAB_SRV_USER" --password "$TAB_SRV
_PASSWORD" && tsm start --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
