#!/usr/bin/env bash
# Script to generate Tableau server backup and upload to amazon S3 - intended to be run as the tableau_srv user

# Start logging
exec > >(tee /var/log/last-tab-backup-to-s3.log | logger -t tab-backup-to-s3) 2>&1
echo "==========================="
date
echo "==========================="
echo "== Log file: /var/log/last-tab-backup-to-s3.log"

# Add /usr/local/bin to path
PATH=/usr/local/bin:$PATH

# Login to TSM
echo "== Authenticating with TSM"
tsm login -u $TAB_SRV_USER -p $TAB_SRV_PASSWORD

# Create backup file - saved to: /var/opt/tableau/tableau_server/data/tabsvc/files/backups/
echo "== Generating Tableau Server backup"
tsm maintenance backup --file ts_backup --append-date

# Lookup Green/Blue from S3
export IP=$(aws s3 cp s3://$S3_HTTPD_CONFIG_BUCKET/ssl.conf - | grep -m 1 ProxyPass | awk -F // '{ print $2 }' | tr -d '/')
export CURRENT_IP=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)


if [ $IP == $CURRENT_IP ]; then
  echo "== Set destination as Green instance"
  export BACKUP_LOCATION="${DATA_ARCHIVE_TAB_BACKUP_URL}/green/"
else
  echo "== Set destination as Blue instance"
  export BACKUP_LOCATION="${DATA_ARCHIVE_TAB_BACKUP_URL}/blue/"
fi

# Export env_var for newly created backup
export NEWEST_BACKUP_FOR_S3=`find /var/opt/tableau/tableau_server/data/tabsvc/files/backups/ -type f -name '*.tsbak' -mmin -1`

# Upload backup to S3
echo "== Uploading backup to S3"
if aws s3 cp $NEWEST_BACKUP_FOR_S3 $BACKUP_LOCATION --no-progress; then
  echo "== Upload successful"
  # If successful: cleanup - delete local backups older than 24 hours (ish)
  echo "== Removing old backup files"
  find /var/opt/tableau/tableau_server/data/tabsvc/files/backups/ -type f -name '*.tsbak' -mmin +1439 | xargs -I {} rm {} && echo "== Complete!"
else
  echo "== Upload failed"
fi
