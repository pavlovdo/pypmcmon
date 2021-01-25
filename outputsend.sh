#!/bin/bash

readonly PROJECT=pypmcmon
readonly OUTPUTFILE=/etc/zabbix/externalscripts/$PROJECT/data/output

if [ -f $OUTPUTFILE ]
then
    cat $OUTPUTFILE
    rm $OUTPUTFILE
fi
