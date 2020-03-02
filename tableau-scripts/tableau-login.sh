#!/bin/bash
if [ "$#" -ne 1 ]
then
  echo "Usage: $0 [SITE]"
  exit 1
fi

SITE=$1

err = tabcmd login -s localhost --username "$TAB_ADMIN_USER" --password "$TAB_ADMIN_PASSWORD" --site "$SITE"

return err
