#!/bin/bash
#
# This script can be used to schedule long running zabbix_sender scripts via a normal external check.
# It allows you to work with long running script while still using polling intervals from within Zabbix
# as opposed to using cron.

#SCRIPTPATH=/usr/lib/zabbix/externalscripts
SCRIPTPATH=/opt/zabbix-current/share/zabbix/externalscripts

echo "$SCRIPTPATH/$@" | at -M now 2>&1 | grep -v "warning: commands will be executed using"
