#!/bin/bash
if [ "$#" -ne 0 ]
then
  echo "Usage: $0"
  exit 1
fi

tabcmd listsites -s localhost --username "$TAB_ADMIN_USER" --password "$TAB_ADMIN_PASSWORD"
