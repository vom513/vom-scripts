#!/usr/bin/python
#
# Dirty nasty python3 fixup :/
#

import time
import re
from colorama import Style, Fore, Back
import paramiko
from pysnmp.hlapi import *

aps = ["ap-downstairs", "ap-upstairs", "ap-test"]

username = "admin"
password = "FIXME"
snmpcomm = "FIXME"

macfile = "/usr/local/etc/internal-macs.txt"

def to_bytes(s):
	if type(s) is bytes:
		return s
	elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
		return codecs.encode(s, 'utf-8')
	else:
		raise TypeError("Expected bytes or string, but got %s." % type(s))

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

	# Initialize client counters
	count2g = 0
	count5g = 0

	# All this to get the SNMP location natively :(
	errorIndication, errorStatus, errorIndex, varBinds = next(
    		getCmd(SnmpEngine(),
           	CommunityData(snmpcomm),
           	UdpTransportTarget((host, 161)),
           	ContextData(),
           	ObjectType(ObjectIdentity('1.3.6.1.2.1.1.6.0')))
	)

	if errorIndication:
    		print(errorIndication)
	elif errorStatus:
    		print('%s at %s' % (errorStatus.prettyPrint(),
		errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
	else:
		location = varBinds[0][1]


	# Print current host, location
	print ('%-20s (%s)' % (host, location))
	print ("====================================================================")

	# Begin SSH portion
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(host, port=22, username=username, password=password, timeout=5)

	channel = client.get_transport().open_session()
	channel.invoke_shell()

	# Get 2ghz channels
	channel.send('stat info channel2\n')

	while not channel.recv_ready():
    		time.sleep(.5)
	chan2gout = channel.recv(9999)
	chan2lines = chan2gout.splitlines()

	# Get 5ghz channels
	channel.send('stat info channel5\n')

	while not channel.recv_ready():
    		time.sleep(.5)
	chan5gout = channel.recv(9999)
	chan5lines = chan5gout.splitlines()

	# Get 2ghz clients
	channel.send('stat client2 kickclient\n')

	while not channel.recv_ready():
    		time.sleep(.5)
	client2gout = channel.recv(9999)
	client2lines = client2gout.splitlines()

	# Get 5ghz clients
	channel.send('stat client5 kickclient\n')

	while not channel.recv_ready():
    		time.sleep(.5)
	client5gout = channel.recv(9999)
	client5lines = client5gout.splitlines()

	# Close session
	client.close()

	# Process 2g channels
	for line in chan2lines:
		line = to_bytes(line)
		if b"Current" in line:
			line = line.strip()
			words = line.split()
			channel2g = words[1]
			channel2g = channel2g.decode()

	# Process 5g channels
	for line in chan5lines:
		line = to_bytes(line)
		if b"Current" in line:
			line = line.strip()
			words = line.split()
			channel5g = words[1]
			channel5g = channel5g.decode()

	# Print channels, more header misc.
	# Current frequencies: Chan. X Chan. 5
	print ("Current frequencies: " + Fore.CYAN + "Chan. %s Chan. %s" % (channel2g, channel5g), end = '')
	print (Style.RESET_ALL)
	print ("--------------------------------------------------------------------")
	print ("Client                  MAC                 RSSI")
	print ("--------------------------------------------------------------------")

	# Process / print 2g clients
	for line in client2lines:
		line = to_bytes(line)
		if re.search(b"^SSID[0-9]+", line):
			line = line.strip()
			words = line.split()
			mac = words[1]
			mac = mac.decode()
			cmac = Fore.YELLOW + mac + Style.RESET_ALL

			# Have to futz with RSSI :(
			rssi = words[4]
			rssi = rssi.decode()
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

			count2g += 1

	# Process / print 5g clients
	for line in client5lines:
		line = to_bytes(line)
		if re.search(b"^SSID[0-9]+", line):
			line = line.strip()
			words = line.split()
			mac = words[1]
			mac = mac.decode()
			cmac = Fore.YELLOW + mac + Style.RESET_ALL

			# Have to futz with RSSI :(
			rssi = words[4]
			rssi = rssi.decode()
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

			count5g +=1

	# No clients connected...
	if ((count2g == 0) and (count5g == 0)):
		print ("NO CLIENTS")

	# Blank seperator line
	print ()
