#!/bin/bash

readonly PROJECT_DIR=$(dirname "$0")
readonly PROJECT=$(basename "$PROJECT_DIR")
readonly OUTPUTFILE=/etc/zabbix/externalscripts/$PROJECT/data/output

if [ -f "$OUTPUTFILE" ]
then
    cat "$OUTPUTFILE"
    rm "$OUTPUTFILE"
fi