#!/usr/bin/env python3
#
# Tested on IAP Virtual Cluster running 8.6.x.x
#
#================================================================

import argparse
import getpass
import time
import datetime
from colorama import Style, Fore, Back
from pysnmp.hlapi import *

parser = argparse.ArgumentParser(description = 'Connects to Aruba IAP VC(s), enumerates APs, and connected client info.  SNMP community will be read via prompt.')
parser.add_argument('-vcs', type=str, required=True, help='Comma seperated list of VCs')
parser.add_argument('-m', type=str, metavar='MACFILE', default='/usr/local/etc/internal-macs.txt', help='Location of MAC address file (optional), defaults to /usr/local/etc/internal-macs.txt.  Format is simply mac <tab> short_hostname.  MAC format is xx:xx:xx:xx:xx:xx')

args = parser.parse_args()

vclist		= args.vcs.split(",")

snmpcomm = getpass.getpass(prompt='SNMP community: ')
macfile = args.m

# Read in internal mac file
hostdb = {}
try:
	with open(macfile) as macs:
		for line in macs:
			(key, val) = line.split()
			hostdb[key] = val

except EnvironmentError:
	print ('Problem reading file', macfile, "!")
	exit(1)

def mac2oid(mac):

	bytes = mac.split(':')

	try:
		b0 = int(bytes[0], 16)
		b1 = int(bytes[1], 16)
		b2 = int(bytes[2], 16)
		b3 = int(bytes[3], 16)
		b4 = int(bytes[4], 16)
		b5 = int(bytes[5], 16)

		b0=str(b0)
		b1=str(b1)
		b2=str(b2)
		b3=str(b3)
		b4=str(b4)
		b5=str(b5)

		macdec = b0 + '.' + b1 + '.' + b2 + '.' + b3 + '.' + b4 + '.' + b5

	except:
		macdec = "0.0.0.0.0.0"

	return macdec

# Start with a blank line
print ()

# iterate vcs
for vc in vclist:

	print ('Connecting to VC:', vc) 
	print ()
	print ('Gathering data...')
	print ()

	# Get mac addresses of ap's from vc
	apmacs = []
	oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.1'
	for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
		CommunityData(snmpcomm),
		UdpTransportTarget((vc, 161)),
		ContextData(),
		ObjectType(ObjectIdentity(oid)), lexicographicMode=False
		):

		# If this fails already, we will consider the host down
		if errorIndication:
			print(errorIndication)
			print('VC', vc, 'seems to be down, skipping...')
			continue
		elif errorStatus:
			print('%s at %s' % (errorStatus.prettyPrint(),
			errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
			print('VC', vc, 'seems to be down, skipping...')
			continue
		else:
			for varBind in varBinds:
				apmac = varBind[1].prettyPrint()
				apmac = apmac[2:]
				apmac = ':'.join(apmac[i:i+2] for i in range(0, len(apmac), 2))
				apmacs.append(apmac)

	# Station list
	clients = []
	oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.1'
	for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
		CommunityData(snmpcomm),
		UdpTransportTarget((vc, 161)),
		ContextData(),
		ObjectType(ObjectIdentity(oid)), lexicographicMode=False
		):

			if not errorIndication and not errorStatus:
				for varBind in varBinds:
					mac = varBind[1].prettyPrint()
					mac = mac[2:]
					mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
					# print (mac)
					coid = mac2oid(mac)

					# client to BSSID association
					oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.2' + '.' + coid
					for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(SnmpEngine(),
						CommunityData(snmpcomm),
						UdpTransportTarget((vc, 161)),
						ContextData(),
						ObjectType(ObjectIdentity(oid)), lexicographicMode=False
					):

						if not errorIndication and not errorStatus:
							for varBind in varBinds:
								bssid = varBind[1]

					# Client uptimes
					oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.16' + '.' + coid
					for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(SnmpEngine(),
						CommunityData(snmpcomm),
						UdpTransportTarget((vc, 161)),
						ContextData(),
						ObjectType(ObjectIdentity(oid)), lexicographicMode=False
					):

						if not errorIndication and not errorStatus:
							for varBind in varBinds:
								cuptime = varBind[1]

					# SNRs
					oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.7' + '.' + coid
					for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(SnmpEngine(),
						CommunityData(snmpcomm),
						UdpTransportTarget((vc, 161)),
						ContextData(),
						ObjectType(ObjectIdentity(oid)), lexicographicMode=False
					):

						if not errorIndication and not errorStatus:
							for varBind in varBinds:
								snr = varBind[1]

					clients.append([mac,bssid,cuptime,snr])

	# Uncomment to short circuit
	#continue

	for apmac in apmacs:

		apmacdec = mac2oid(apmac)

		ticks = 0

		# AP name
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.2' + '.' + apmacdec
		for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(SnmpEngine(),
			CommunityData(snmpcomm),
			UdpTransportTarget((vc, 161)),
			ContextData(),
			ObjectType(ObjectIdentity(oid)), lexicographicMode=False
			):

			if not errorIndication and not errorStatus:
				for varBind in varBinds:
					ap = varBind[1]
					ap = str(ap)

		# Uptime
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.9' + '.' + apmacdec
		oid = str(oid)
		errorIndication, errorStatus, errorIndex, varBinds = next(
    			getCmd(SnmpEngine(),
           		CommunityData(snmpcomm),
           		UdpTransportTarget((vc, 161)),
           		ContextData(),
           		ObjectType(ObjectIdentity(oid)))
		)

		if not errorIndication and not errorStatus:
			for varBind in varBinds:
				ticks = varBinds[0][1]

		ticks = int(ticks)
		upseconds = ticks/100
		uptime = datetime.timedelta(seconds=upseconds)
		# Strip microseconds
		uptime = str(uptime).split(".")[0]

		# Print current host, uptime
		print ('%-20s Uptime: %s' % (ap, uptime))
		print ("=============================================================================")

		# Radio channels
		channels = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.2.1.4' + '.' + apmacdec
		for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
			CommunityData(snmpcomm),
			UdpTransportTarget((vc, 161)),
			ContextData(),
			ObjectType(ObjectIdentity(oid)), lexicographicMode=False
			):

				if not errorIndication and not errorStatus:
					for varBind in varBinds:
						channel = varBind[1]
						channels.append(channel)

		# BSSIDs on this AP
		apbssids = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.3.1.4' + '.' + apmacdec
		for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
			CommunityData(snmpcomm),
			UdpTransportTarget((vc, 161)),
			ContextData(),
			ObjectType(ObjectIdentity(oid)), lexicographicMode=False
			):

				if not errorIndication and not errorStatus:
					for varBind in varBinds:
						apbssid = varBind[1]
						apbssids.append(apbssid)


		# ESSIDs on this AP
		essids = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.3.1.3' + '.' + apmacdec
		for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
			CommunityData(snmpcomm),
			UdpTransportTarget((vc, 161)),
			ContextData(),
			ObjectType(ObjectIdentity(oid)), lexicographicMode=False
			):

				if not errorIndication and not errorStatus:
					for varBind in varBinds:
						essid = varBind[1]
						essids.append(essid)


		# Print channels, more header misc.
		chanstr = ""
		for i in channels:
			chanstr = (chanstr + " " + i)

		print ("Current frequencies: " + Fore.CYAN + "Channels:%s" % (chanstr), end = '')
		print (Style.RESET_ALL)
		print ("-----------------------------------------------------------------------------")
		print ("Client                  MAC                 SSID        SNR            Uptime")
		print ("-----------------------------------------------------------------------------")

		index = 0
		ssidindex = 0
		for apbssid in apbssids:
			ssid = essids[ssidindex]
			cssid = Fore.CYAN + ssid + Style.RESET_ALL

			ssidindex += 1

			for row in clients:
				if (apbssid == row[1]):

					mac = row[0]

					cuptime = row[2]
					cuptime = int(cuptime)
					cupseconds = cuptime/100
					cuptime = datetime.timedelta(seconds=cupseconds)
					# Strip microseconds
					cuptime = str(cuptime).split(".")[0]

					snr = row[3]

					cmac = Fore.YELLOW + mac + Style.RESET_ALL

					snr = str(snr).zfill(2)
					#rssi = rssi.lstrip('-')
					#rssi = int(rssi)
					#rssi = (100 - rssi)
					#rssi = str(rssi)
					csnr = Fore.BLUE + snr + Style.RESET_ALL

					if mac in hostdb.keys():
						client = hostdb[mac]
						cclient = Fore.MAGENTA + client + Style.RESET_ALL
					else:
						client = "UNKNOWN"
						cclient = Fore.RED + client + Style.RESET_ALL

					# Print out each entry
					print ('%-32s %-28s %-20s %-6s %18s' % (cclient, cmac, cssid, csnr, cuptime))

					index += 1


		# No clients connected...
		if (index == 0):
			print ("NO CLIENTS")

		# Blank seperator line
		print ()

