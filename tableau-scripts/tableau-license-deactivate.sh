#!/bin/bash

echo "Deactivating licenses..."
echo "This will removed all of the current licenses from Tableau."
read -p "Are you sure [y/N]? " -n 1 -r
echo    # new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting."
    exit 1
fi

if [ ! -z $TAB_PRODUCT_KEY ] # Tableau External
then
  tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY"   --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
else # Tableau Internal
  tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_1" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_2" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY_3" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
fi
tsm licenses activate --trial --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
tsm restart                   --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
