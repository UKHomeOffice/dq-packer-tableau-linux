#!/usr/bin/env bash
# Script to generate Tableau server backup and upload to amazon S3 - intended to be run as the tableau_srv user

# Add location of aws to PATH
PATH=${PATH}:/usr/local/bin

# log variables - set up in Packer Playbook
log_dir=/var/log/
log_file=tableau-backup-to-s3.log
old_logs=${log_dir}/tableau-backup-logs/
old_log_file=tableau-backup-to-s3-$(date +%Y-%m-%d).log

# keep old log_file, if exists
if [ -f ${log_dir}${log_file} ]
then
  cp ${log_dir}${log_file} ${old_logs}${old_log_file}
fi

# Start logging
exec > >(tee ${log_dir}${log_file} | logger -t tableau-backup-to-s3) 2>&1
echo "==========================="
date
echo "==========================="
echo "== Log file: ${log_dir}${log_file}"

# Login to TSM
echo "== Authenticating with TSM"
tsm login -u $TAB_SRV_USER -p $TAB_SRV_PASSWORD

# Check if backup file already exists: 
backup_dir=/var/opt/tableau/tableau_server/data/tabsvc/files/backups/
backup_file=ts_backup-$(date +%Y-%m-%d).tsbak
backup_file_2=ts_backup-$(date +%Y-%m-%d_%H:%M:%S).tsbak
if [ -f ${backup_dir}${backup_file} ]
then
  mv ${backup_dir}${backup_file} ${backup_dir}${backup_file_2}
fi

# Create backup file - saved to: /var/opt/tableau/tableau_server/data/tabsvc/files/backups/
echo "== Generating Tableau Server backup"
if tsm maintenance backup --file ts_backup --append-date; then
  echo "== Backup successfully created."
else 
  echo "== Error creating backup. Exiting..."
  exit 1
fi

# Lookup Green/Blue from S3
STAGING=0
if [ $TABLEAU_ENVIRONMENT == "internal" ]; then
  export GREEN_IP=$(aws s3 cp s3://$S3_HTTPD_CONFIG_BUCKET/ssl.conf - | grep -m 1 ProxyPass | awk -F // '{ print $2 }' | tr -d '/')
elif [ $TABLEAU_ENVIRONMENT == "external" ]; then
  export GREEN_IP=$(aws s3 cp s3://$S3_HAPROXY_CONFIG_BUCKET/haproxy.cfg - | grep "server tableau_ext" | awk '{ print $3 }' | awk -F : '{ print $1 }')
elif [ $TABLEAU_ENVIRONMENT == "staging" ]; then
  echo "Environment is Staging"
  STAGING=1
else
  echo "Unknown Tableau Server type, not backing up. Exiting..."
  exit 2
fi

echo "== Reading Tableau Server IP address"
export CURRENT_IP=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)


if [ $GREEN_IP == $CURRENT_IP ]; then
  echo "== Set destination as Green instance"
  export BACKUP_LOCATION="${DATA_ARCHIVE_TAB_BACKUP_URL}/green/"
elif [ $STAGING -eq 1 ]; then
  echo "== Set destination as Staging instance"
  export BACKUP_LOCATION="${DATA_ARCHIVE_TAB_BACKUP_URL}/staging/"
else
  echo "== Set destination as Blue instance"
  export BACKUP_LOCATION="${DATA_ARCHIVE_TAB_BACKUP_URL}/blue/${CURRENT_IP}/"
fi


# Export env_var for newly created backup (created in the past 1 minute)
export NEWEST_BACKUP_FILE_COUNT=`find ${backup_dir} -type f -name '*.tsbak' -mmin -1 | wc -l`
export NEWEST_BACKUP_FOR_S3=`find ${backup_dir} -type f -name '*.tsbak' -mmin -1`
if [ ${NEWEST_BACKUP_FILE_COUNT} -ne 1 ];
then
  echo "== ERROR: Found ${NEWEST_BACKUP_FILE_COUNT} backup files in ${backup_dir}."
  echo "== Exiting..."
  exit 3
fi


# Upload backup to S3
echo "== Uploading backup to S3"
if aws s3 cp ${NEWEST_BACKUP_FOR_S3} ${BACKUP_LOCATION} --no-progress; then
  echo "== Upload successful"
  # If successful: cleanup - delete local backups older than 24 hours (ish)
  echo "== Removing old backup files"
  find ${backup_dir} -type f -name '*.tsbak' -mmin +1439 | xargs -I {} rm {} && echo "== Complete!"
else
  echo "== Upload failed"
fi
echo "==========================="
date
echo "==========================="
echo "We're done here."
