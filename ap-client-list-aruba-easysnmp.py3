#!/usr/bin/env python3
#
# Tested on IAP Virtual Cluster running 8.6.x.x, 8.10.x.x
#
#================================================================

import argparse
import getpass
import time
import datetime
from colorama import Style, Fore, Back
from easysnmp import Session, EasySNMPConnectionError, EasySNMPTimeoutError

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

	b0 = "{:02x}".format(ord(bytes[0]), "x")
	b1 = "{:02x}".format(ord(bytes[1]), "x")
	b2 = "{:02x}".format(ord(bytes[2]), "x")
	b3 = "{:02x}".format(ord(bytes[3]), "x")
	b4 = "{:02x}".format(ord(bytes[4]), "x")
	b5 = "{:02x}".format(ord(bytes[5]), "x")

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

	# Get mac addresses of ap's from vc
	try:
		session = Session(hostname=vc, community=snmpcomm, version=2)

	# Connection timed out in some fashion
	except EasySNMPConnectionError:
		print('VC', vc, 'seems to be down, skipping...')
		continue

	results = []
	apmacs = []
	oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.1'

	try:
		results = session.walk(oid)

	except EasySNMPTimeoutError:
		print('Bad SNMP community for VC', vc, '(or down) ?  Skipping...')
		print()
		continue

	for apmac in results:
		apmac = smac2mac(apmac.value)
		apmacs.append(apmac)

	# Station list
	results = []
	clients = []
	oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.1'

	results = session.walk(oid)

	for mac in results:

		mac = mac.value
		coid = smac2oid(mac)

		# client to BSSID association
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.2' + '.' + coid
		bssid = smac2mac((session.get(oid).value))

		# Client uptimes
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.16' + '.' + coid
		cuptime = (session.get(oid).value)

		# SNRs
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.4.1.7' + '.' + coid
		snr = (session.get(oid).value)

		clients.append([smac2mac(mac),bssid,cuptime,snr])

	# Uncomment to short circuit
	#continue

	for apmac in apmacs:

		apmacdec = mac2oid(apmac)

		ticks = 0

		# AP name
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.2' + '.' + apmacdec
		ap = (session.get(oid).value)

		# Uptime
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.1.1.9' + '.' + apmacdec
		ticks = session.get(oid).value

		ticks = int(ticks)
		upseconds = ticks/100
		uptime = datetime.timedelta(seconds=upseconds)
		# Strip microseconds
		uptime = str(uptime).split(".")[0]

		# Print current host, uptime
		print ('%-20s Uptime: %s' % (ap, uptime))
		print ("=============================================================================")

		# Radio channels
		results = []
		channels = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.2.1.4' + '.' + apmacdec

		results = session.walk(oid)

		for channel in results:
			channel = channel.value
			channels.append(channel)

		# BSSIDs on this AP
		results = []
		apbssids = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.3.1.4' + '.' + apmacdec

		results = session.walk(oid)

		for apbssid in results:
			apbssid = smac2mac(apbssid.value)
			apbssids.append(apbssid)

		# ESSIDs on this AP
		results = []
		essids = []
		oid = '1.3.6.1.4.1.14823.2.3.3.1.2.3.1.3' + '.' + apmacdec

		results = session.walk(oid)

		for essid in results:
			essid = essid.value
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

		print ()

	# Blank seperator line
	#print ()

