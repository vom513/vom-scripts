#!/usr/bin/env python3
#
# Tested on IAP Virtual Cluster running 8.6.x.x, 8.10.x.x
#
# This version uses the net-snmp package (snmpget, snmpwalk).  Lots of awk/sed/etc.
# I modified this when I was frustrated and it shows, it's fast and loose...
#
#================================================================

import os
import argparse
import getpass
import time
import datetime
from colorama import Style, Fore, Back

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

# Convert xx:xx:xx:xx:xx:xx to OID
def mac2oid(mac):

	bytes = mac.split(':')

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

	return macdec

# Convert ASCII MAC to OID
def smac2oid(mac):

	bytes = []

	for char in mac:
		bytes.append(char)

	b0 = (ord(bytes[0]))
	b1 = (ord(bytes[1]))
	b2 = (ord(bytes[2]))
	b3 = (ord(bytes[3]))
	b4 = (ord(bytes[4]))
	b5 = (ord(bytes[5]))

	b0=str(b0)
	b1=str(b1)
	b2=str(b2)
	b3=str(b3)
	b4=str(b4)
	b5=str(b5)

	macdec = b0 + '.' + b1 + '.' + b2 + '.' + b3 + '.' + b4 + '.' + b5

	return macdec

# Convert ASCII MAC to xx:xx:xx:xx:xx:xx MAC
def smac2mac(mac):

	bytes = []

	for char in mac:
		bytes.append(char)

	b0 = format(ord(bytes[0]), "x")
	b1 = format(ord(bytes[1]), "x")
	b2 = format(ord(bytes[2]), "x")
	b3 = format(ord(bytes[3]), "x")
	b4 = format(ord(bytes[4]), "x")
	b5 = format(ord(bytes[5]), "x")

	b0=str(b0)
	b1=str(b1)
	b2=str(b2)
	b3=str(b3)
	b4=str(b4)
	b5=str(b5)

	mac = b0 + ':' + b1 + ':' + b2 + ':' + b3 + ':' + b4 + ':' + b5

	return mac

# Start with a blank line
print ()

# iterate vcs
for vc in vclist:

	print ('Connecting to VC:', vc) 
	print ()
	print ('Gathering data...')
	print ()

	# Get AP MACs
	snmpcmd = "snmpwalk -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.1.1.1 | cut -f 2 -d : | tr -d ' '"
	x = os.popen(snmpcmd).read()
	apmacs = x.splitlines()

	# Station list
	clients = []
	snmpcmd = "snmpwalk -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.4.1.1 | cut -f 2 -d : | tr -d ' '"
	x = os.popen(snmpcmd).read()
	for mac in x.splitlines():
		if (len(mac) == 8):
			mac = (mac[1 : -1])
			coid = smac2oid(mac)
		else:
			mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
			mac = mac.lower()
			coid = mac2oid(mac)

		# client to BSSID association
		snmpcmd = "snmpget -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.4.1.2" + "." + coid + " | cut -f 2 -d : | tr -d ' '"
		bssid = os.popen(snmpcmd).read()
		bssid = bssid.strip()

		# Client uptimes
		snmpcmd = "snmpget -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.4.1.16" + "." + coid + " | cut -f 2 -d '(' | cut -f 1 -d ')'"
		cuptime = os.popen(snmpcmd).read()
		cuptime = cuptime.strip()

		# SNRs
		snmpcmd = "snmpget -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.4.1.7" + "." + coid + " | awk '{print $2}' |tr -d ' '"
		snr = os.popen(snmpcmd).read()
		snr = snr.strip()

		clients.append([mac,bssid,cuptime,snr])

	# Uncomment to short circuit
	#continue

	for apmac in apmacs:

		apmacdec = ':'.join(apmac[i:i+2] for i in range(0, len(apmac), 2))
		apmacdec = mac2oid(apmacdec)

		ticks = 0

		# AP name
		snmpcmd = "snmpget -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.1.1.2" + "." + apmacdec + " | awk '{print $2}' | tr -d ' ' | sed 's/\"//g'"
		ap = os.popen(snmpcmd).read()
		ap = ap.strip()

		# Uptime
		snmpcmd = "snmpget -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.1.1.9" + "." + apmacdec + " | awk '{print $2}' | cut -f 2 -d '(' | cut -f 1 -d ')'"
		ticks = os.popen(snmpcmd).read()
		ticks = ticks.strip()

		ticks = int(ticks)
		upseconds = ticks/100
		uptime = datetime.timedelta(seconds=upseconds)
		# Strip microseconds
		uptime = str(uptime).split(".")[0]

		# Print current host, uptime
		print ('%-20s Uptime: %s' % (ap, uptime))
		print ("=============================================================================")

		# Radio channels
		snmpcmd = "snmpwalk -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.2.1.4" + "." + apmacdec + " | awk '{print $2}' | tr -d ' ' | sed 's/\"//g'"
		x = os.popen(snmpcmd).read()
		channels = x.splitlines()

		# BSSIDs on this AP
		snmpcmd = "snmpwalk -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.3.1.4" + "." + apmacdec + " | cut -f 2 -d : | tr -d ' '"
		x = os.popen(snmpcmd).read()
		apbssids = x.splitlines()

		# ESSIDs on this AP
		snmpcmd = "snmpwalk -v 2c -Ov -c " + snmpcomm + " " + vc + " 1.3.6.1.4.1.14823.2.3.3.1.2.3.1.3" + "." + apmacdec + " | awk '{print $2}' | tr -d ' ' | sed 's/\"//g'"
		x = os.popen(snmpcmd).read()
		essids = x.splitlines()

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

					arubabug = 0

					mac = row[0]

					# Sometimes we get client macs as ASCII strings.  Aruba says this is normal.  Agree to disagree...
					if (len(mac) == 6):
						mac  = smac2mac(mac)
						arubabug = 1

					cuptime = row[2]
					cuptime = int(cuptime)
					cupseconds = cuptime/100
					cuptime = datetime.timedelta(seconds=cupseconds)
					# Strip microseconds
					cuptime = str(cuptime).split(".")[0]

					snr = row[3]

					cmac = Fore.YELLOW + mac + Style.RESET_ALL

					snr = str(snr).zfill(2)
					csnr = Fore.BLUE + snr + Style.RESET_ALL

					if mac in hostdb.keys():
						client = hostdb[mac]
						cclient = Fore.MAGENTA + client + Style.RESET_ALL
					else:
						client = "UNKNOWN"
						cclient = Fore.RED + client + Style.RESET_ALL

					if (arubabug == 1):
						cmac = cmac + "*"

					# Print out each entry
					print ('%-32s %-28s %-20s %-6s %18s' % (cclient, cmac, cssid, csnr, cuptime))

					index += 1


		# No clients connected...
		if (index == 0):
			print ("NO CLIENTS")

		print ()

	# Blank seperator line
	#print ()

