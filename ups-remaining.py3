#!/usr/bin/env python3

import subprocess
import time
import datetime
import os
import sys
from termcolor import colored

# List of UPSes to monitor.  <ups_name>@<hostname> format. Or just <ups_name> is for a locally connected unit.
upses = ('ups', 'ups@fileserver1', 'ups@testbox')

os.system('clear')

try:
	refresh = 15

	while True:
		print ()
		print ("Refreshing every", refresh, "seconds")
		print ("===============================")

		now = datetime.datetime.now().strftime("%a %B %d %Y %H:%M:%S")

		print (now)
		print ()

		for ups in upses:
			runtime_command	= 'upsc ' + ups + ' battery.runtime 2>/dev/null'
			charge_command 	= 'upsc ' + ups + ' battery.charge 2>/dev/null'

			try:
				remaining_seconds = subprocess.check_output(runtime_command, shell=True, timeout=2)
				charge = subprocess.check_output(charge_command, shell=True, timeout=2)
			except subprocess.CalledProcessError as e:
				print ("Error with ups", ups)
				continue

			remaining_seconds = int(remaining_seconds, 10)
			hms = str(datetime.timedelta(seconds=remaining_seconds))
			charge=int(charge)

			print (('%s::' % ups), "Remain:", colored(hms, 'cyan'), "Charge:", colored(charge, 'yellow'))
			print ()

		time.sleep(refresh)
		os.system('clear')

except KeyboardInterrupt:
	sys.exit(0) # or 1, or whatever
