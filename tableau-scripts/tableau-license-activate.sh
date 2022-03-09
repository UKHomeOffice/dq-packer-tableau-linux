#!/bin/bash

echo "Activating licenses..."
echo "This will activate all of the current licenses for Tableau."
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

if [ ! -z $TAB_PRODUCT_KEY ] # Tableau External
then
  RET1="$(tsm licenses activate --license-key $TAB_PRODUCT_KEY   --username $TAB_SRV_USER --password $TAB_SRV_PASSWORD)"
  err=$((err + $?))
  RET1=${RET1//$'\n'/} # Remove newlines
  RET="${RET} ${RET1}"
  # re-run license activation so that we get $LICENSE_UPDATE_APPLIED returned - if ATR running
  RET2="$(tsm licenses activate --license-key $TAB_PRODUCT_KEY   --username $TAB_SRV_USER --password $TAB_SRV_PASSWORD)"
  err=$((err + $?))
  RET2=${RET2//$'\n'/} # Remove newlines
  RET="${RET} ${RET2}"
else # Tableau Internal
  RET1="$(tsm licenses activate --license-key $TAB_PRODUCT_KEY_1 --username $TAB_SRV_USER --password $TAB_SRV_PASSWORD)"
  err=$((err + $?))
  echo "$RET1"
  RET1=${RET1//$'\n'/} # Remove newlines
  RET="${RET} ${RET1}"
  RET2="$(tsm licenses activate --license-key $TAB_PRODUCT_KEY_2 --username $TAB_SRV_USER --password $TAB_SRV_PASSWORD)"
  err=$((err + $?))
  echo "$RET2"
  RET2=${RET2//$'\n'/} # Remove newlines
  RET="${RET} ${RET2}"
  RET3="$(tsm licenses activate --license-key $TAB_PRODUCT_KEY_3 --username $TAB_SRV_USER --password $TAB_SRV_PASSWORD)"
  err=$((err + $?))
  echo "$RET3"
  RET3=${RET3//$'\n'/} # Remove newlines
  RET="${RET} ${RET3}"
fi

# Check if any of the above failed
if (( $err > 0 ))
then
  echo "ERROR: At least one license activation failed - Please investigate"
  exit $err
fi

# Check if license changes were applied automatically or if we need to restart TSM
if [[ $RET =~ $LICENSE_UPDATE_APPLIED ]] # Did we get an indication that ATR is running and License was applied correctly?
then
  echo "INFO: License Activation succeeded."
elif [[ $RET =~ $LICENSE_UPDATE_TO_BE_APPLIED ]] # If we got here, ATR is not running. Did we get indication License was applied correctly?
then
  echo "WARNING: License details updated. Restarting TSM..."
  tsm restart --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
else
  echo "ERROR: Unexpected outcome - Please investigate"
fi
