#!/bin/bash
err=0
if [ ! -z $TAB_PRODUCT_KEY ] # Tableau External
then
  tsm licenses activate --license-key "$TAB_PRODUCT_KEY"   --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  err=$((err + $?))
else # Tableau Internal
  tsm licenses activate --license-key "$TAB_PRODUCT_KEY_1" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  err=$((err + $?))
  tsm licenses activate --license-key "$TAB_PRODUCT_KEY_2" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  err=$((err + $?))
  tsm licenses activate --license-key "$TAB_PRODUCT_KEY_3" --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
  err=$((err + $?))
fi
if (( $err > 0 ))
then
  echo "At least one license activation failed - NOT restarting TSM"
else
  tsm restart --username "$TAB_SRV_USER" --password "$TAB_SRV_PASSWORD"
fi
