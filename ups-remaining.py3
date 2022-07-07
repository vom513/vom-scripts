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
			charge = 0

			mfr_command = 'upsc ' + ups + ' device.mfr 2>/dev/null'
			driver_command = 'upsc ' + ups + ' driver.name 2>/dev/null'
			runtime_command	= 'upsc ' + ups + ' battery.runtime 2>/dev/null'
			charge_command 	= 'upsc ' + ups + ' battery.charge 2>/dev/null'

			try:
				mfr = subprocess.check_output(mfr_command, shell=True, timeout=2)
				driver = subprocess.check_output(driver_command, shell=True, timeout=2)
				remaining_seconds = subprocess.check_output(runtime_command, shell=True, timeout=2)

				mfr = mfr.decode("utf-8")
				driver = driver.decode("utf-8")
				remaining_seconds = remaining_seconds.decode("utf-8")

				mfr = str(mfr)
				driver = str(driver)

				mfr = mfr.strip()
				driver = driver.strip()
				remaining_seconds = remaining_seconds.strip()

				remaining_seconds = remaining_seconds.split('.')
				remaining_seconds = remaining_seconds[0]
				remaining_seconds = str(remaining_seconds)

				# RMCARD doesn't have charge %
				if (mfr != 'CYBERPOWER' and driver != 'snmp-ups'):
					charge = subprocess.check_output(charge_command, shell=True, timeout=2)

			except subprocess.CalledProcessError as e:
				print ("Error with ups", ups)
				continue
			except subprocess.TimeoutExpired as te:
				print ("Error with ups", ups)
				continue

			remaining_seconds = int(remaining_seconds, 10)

			# RMCARD gives remaining seconds in 1/60th second counter
			if (mfr == "CYBERPOWER" and driver == "snmp-ups"):
				remaining_seconds = remaining_seconds/60

			hms = str(datetime.timedelta(seconds=remaining_seconds))
			charge = int(charge)

			if (charge == 0):
				charge = "N/A"

			print (('%s::' % ups), "Remain:", colored(hms, 'cyan'), "Charge:", colored(charge, 'yellow'))
			print ()

		time.sleep(refresh)
		os.system('clear')

except KeyboardInterrupt:
	sys.exit(0) # or 1, or whatever
