#!/bin/bash

echo "Deactivating licenses..."
echo "This will remove all of the current licenses from Tableau."
read -p "Are you sure [y/N]? " -n 1 -r
echo    # new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting."
    exit 1
fi

LICENSE_UPDATE_APPLIED="Updated licensing details are being applied across server"
LICENSE_UPDATE_TO_BE_APPLIED="Restart server to apply updated licensing details"
RET=""
err=0

if [ ! -z $TAB_PRODUCT_KEY ] # Tableau Internal / External Deactivation
then
  tsm licenses deactivate --license-key "$TAB_PRODUCT_KEY"   --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  err=$((err + $?))
else  # Error logging if no Key found
  err=$((err + 1))
  echo "ERROR: No Product Key found - Please Investigate"
fi

# Check if any of the above failed
if (( $err > 0 ))
then
  echo "ERROR: At least one license deactivation failed - Please investigate"
  exit $err
fi

# Check if license changes were applied automatically or if we need to restart TSM
if [[ $RET =~ $LICENSE_UPDATE_APPLIED ]] # Did we get an indication that ATR is running and License was applied correctly?
then
  echo "INFO: License Deactivation succeeded."
elif [[ $RET =~ $LICENSE_UPDATE_TO_BE_APPLIED ]] # If we got here, ATR is not running. Did we get indication License was applied correctly?
then
  echo "WARNING: License details updated. Restarting TSM..."
  tsm restart --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
else
  echo "ERROR: Unexpected outcome - Please investigate"
fi
