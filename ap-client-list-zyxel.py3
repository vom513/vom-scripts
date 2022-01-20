#!/usr/bin/env python3
#
# I tried this with paramiko and it was a disaster.
# I think the Zyxel ssh daemon has some issues.
# Other things (ex: Cisco IOS AP) worked fine.
# I gave up and did SNMP once I managed to find the magical OIDs.
#
# Tested on NWA210AX APs

aps = ["ap-upstairs", "ap-downstairs"]
snmpcomm = "public"
macfile = "/usr/local/etc/internal-macs.txt"

#================================================================

import time
import datetime
from colorama import Style, Fore, Back
from pysnmp.hlapi import *

# Read in internal mac file
hostdb = {}
try:
	with open(macfile) as macs:
		for line in macs:
			(key, val) = line.split()
			hostdb[key] = val

except EnvironmentError:
	print ('Problem reading file', macfile, "!")

# Start with a blank line
print ()

# iterate aps
for host in aps:

	location = ""
	ticks = 0

	# Location
	errorIndication, errorStatus, errorIndex, varBinds = next(
    		getCmd(SnmpEngine(),
           	CommunityData(snmpcomm),
           	UdpTransportTarget((host, 161)),
           	ContextData(),
           	ObjectType(ObjectIdentity('1.3.6.1.2.1.1.6.0')))
	)

	# If this fails already, we will consider the host down
	if errorIndication:
		print(errorIndication)
		print('AP', host, 'seems to be down, skipping...')
		continue
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),
		errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
		print('AP', host, 'seems to be down, skipping...')
		continue
	else:
		location = varBinds[0][1]

	# Uptime
	errorIndication, errorStatus, errorIndex, varBinds = next(
    		getCmd(SnmpEngine(),
           	CommunityData(snmpcomm),
           	UdpTransportTarget((host, 161)),
           	ContextData(),
           	ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0')))
	)

	if errorIndication:
    		print(errorIndication)
	elif errorStatus:
    		print('%s at %s' % (errorStatus.prettyPrint(),
		errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
	else:
		ticks = varBinds[0][1]

	ticks = int(ticks)
	upseconds = ticks/100
	uptime = datetime.timedelta(seconds=upseconds)
	# Strip microseconds
	uptime = str(uptime).split(".")[0]

	# Print current host, location, uptime
	print ('%-20s (%s) Uptime: %s' % (host, location, uptime))
	print ("====================================================================")

	# Station list
	clients = []
	for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
		CommunityData(snmpcomm),
		UdpTransportTarget((host, 161)),
		ContextData(),
		ObjectType(ObjectIdentity('iso.3.6.1.4.1.890.1.15.3.5.2.1.2.2')), lexicographicMode=False
		):

			if not errorIndication and not errorStatus:
				for varBind in varBinds:
					mac = varBind[1].prettyPrint()
					mac = mac[2:]
					mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
					clients.append(mac)

	# RSSIs
	rssis = []
	for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
		CommunityData(snmpcomm),
		UdpTransportTarget((host, 161)),
		ContextData(),
		ObjectType(ObjectIdentity('iso.3.6.1.4.1.890.1.15.3.5.2.1.5.2')), lexicographicMode=False
		):

			if not errorIndication and not errorStatus:
				for varBind in varBinds:
					rssi = varBind[1]
					rssis.append(rssi)

	# Radio channels
	channels = []
	for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
		CommunityData(snmpcomm),
		UdpTransportTarget((host, 161)),
		ContextData(),
		ObjectType(ObjectIdentity('iso.3.6.1.4.1.890.1.15.3.5.1.1.6')), lexicographicMode=False
		):

			if not errorIndication and not errorStatus:
				for varBind in varBinds:
					channel = varBind[1]
					channels.append(channel)


	# Print channels, more header misc.
	# Current frequencies: Chan. X Chan. 5
	(channel2g, channel5g) = channels
	print ("Current frequencies: " + Fore.CYAN + "Chan. %s Chan. %s" % (channel2g, channel5g), end = '')
	print (Style.RESET_ALL)
	print ("--------------------------------------------------------------------")
	print ("Client                  MAC                 RSSI")
	print ("--------------------------------------------------------------------")

	# Kind of sloppy, but if a client connected/disconnected in between collection of these
	# we will be out of whack...
	if len(clients) != len(rssis):
		print ("A client seems to have connected/disconnected while collecting data.  Please rerun.")
		continue

	# Process clients
	index = 0
	for mac in clients:
		cmac = Fore.YELLOW + mac + Style.RESET_ALL

		rssi = rssis[index]
		rssi = str(rssi)
		rssi = rssi.lstrip('-')
		rssi = int(rssi)
		rssi = (100 - rssi)
		rssi = str(rssi)
		crssi = Fore.BLUE + rssi + Style.RESET_ALL

		if mac in hostdb.keys():
			client = hostdb[mac]
			cclient = Fore.MAGENTA + client + Style.RESET_ALL
		else:
			client = "UNKNOWN"
			cclient = Fore.RED + client + Style.RESET_ALL

		print ('%-32s %-28s %-4s' % (cclient, cmac, crssi))

		index  += 1

	# No clients connected...
	if (index == 0):
		print ("NO CLIENTS")

	# Blank seperator line
	print ()

