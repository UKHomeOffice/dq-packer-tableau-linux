#!/bin/bash
if [ "$#" -ne 2 ]
then
  echo "Usage: $0 [PROJECT] [WORKBOOK_FILENAME]"
  exit 1
fi

PROJECT=$1
WORKBOOK_FILENAME=$2
if [ ! -f "$WORKBOOK_FILENAME" ]
then
  echo "DataSource file ($WORKBOOK_FILENAME) does not exist"
  exit 2
fi

tabcmd publish "$WORKBOOK_FILENAME" --project "$PROJECT" --tabbed --overwrite
