#!/usr/bin/env bash
# Script to generate Tableau server backup and upload to amazon S3 - intended to be run as the tableau_srv user

# Start logging
exec > >(tee /var/log/last-tab-backup-to-s3.log | logger -t tab-backup-to-s3) 2>&1
echo "==========================="
date
echo "==========================="
echo "== Log file: /var/log/last-tab-backup-to-s3.log"

# Login to TSM
echo "== Authenticating with TSM"
tsm login -u $TAB_SRV_USER -p $TAB_SRV_PASSWORD

# Create backup file - saved to: /var/opt/tableau/tableau_server/data/tabsvc/files/backups/
echo "== Generating Tableau Server backup"
tsm maintenance backup --file ts_backup --append-date

# Export env_var for newly created backup
export NEWEST_BACKUP_FOR_S3=`find /var/opt/tableau/tableau_server/data/tabsvc/files/backups/ -type f -name '*.tsbak' -mmin -1`

# Upload backup to S3
echo "== Uploading backup to S3"
if aws s3 cp $NEWEST_BACKUP_FOR_S3 $DATA_ARCHIVE_TAB_INT_BACKUP_URL; then
  echo "== Upload successful"
  # If successful: cleanup - delete local backups older than 24 hours (ish)
  echo "== Removing old backup files"
  find /var/opt/tableau/tableau_server/data/tabsvc/files/backups/ -type f -name '*.tsbak' -mmin +1439 | xargs -I {} rm {} && echo "== Complete!"
else
  echo "== Upload failed"
fi
