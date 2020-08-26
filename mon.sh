#!/bin/sh
#
#
#

if [ -z $1 ];then
	echo "Usage: $0 <interface>"
	exit 1
fi

IFACE=$1
IFACEMON=$1mon

GREEN='\033[0;32m'
LCYAN='\033[1;36m'
LPURPLE='\033[1;35m'
LBLUE='\033[1;34m'
NC='\033[0m'

echo
echo "$GREEN+$NC Stopping network-manager..."

#service network-manager stop 2>&1 >/dev/null
systemctl stop NetworkManager

echo "$GREEN+$NC Manually killing off dhclient, wpa_supplicant, avahi-daemon..."

killall -q -15 dhclient wpa_supplicant 2>&1 >/dev/null

service avahi-daemon stop 2>&1 >/dev/null

echo -n "$GREEN+$NC airmon check says..."
echo
echo $LCYAN
echo "----"
airmon-ng check
echo "----"
echo -n $NC
echo

echo "$GREEN+$NC Changing $IFACE MAC address, preparing for monitoring..."

ifconfig $IFACE up 2>&1 >/dev/null
ifconfig $IFACE down 2>&1 >/dev/null
macchanger -A $IFACE 2>&1 >/dev/null
NEWMAC=`macchanger --show $IFACE | grep ^Current | awk '{print $3}'`
iw dev $IFACE interface add $IFACEMON type monitor 2>/dev/null
ifconfig $IFACEMON down 2>&1 >/dev/null
macchanger -m $NEWMAC $IFACEMON 2>&1 >/dev/null
ifconfig $IFACEMON up 2>&1 >/dev/null
ifconfig $IFACE up 2>&1 >/dev/null
ifconfig $IFACE down 2>&1 >/dev/null

echo "$GREEN+$NC Interface$LPURPLE $IFACEMON$NC created..."
echo $LCYAN
macchanger --show $IFACEMON
echo $NC
echo
