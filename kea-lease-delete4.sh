#!/bin/sh

# Set kea servers here, seperated by space
#
# SERVERS="server1.lan server2.lan 192.168.0.100"

SERVERS="server1.lan server2.lan 192.168.0.100"

if [ $# -eq 0 ]
then
	echo "Usage: $0 <ip address>"
	exit 1
fi

IP=$1

read -r -p "Going to delete $IP lease.  Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
	for i in $SERVERS
	do
		printf "$i:\t"
		curl -H "Content-Type: application/json" -d '{ "command": "lease4-del", "service": [ "dhcp4" ], "arguments": { "ip-address": "'$IP'" } }' http://$i:8000/
		echo
	done
	exit 0
        ;;
    *)
        echo "Cancelled."
	exit 0
        ;;
esac

exit 0

