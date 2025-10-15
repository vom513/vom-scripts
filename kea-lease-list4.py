#!/usr/bin/env python3
#

import requests
import json
import datetime
import mac_vendor_lookup
import os
import time
from colorama import Style, Fore, Back

# --- Configure these variables ---
host="192.168.64.1"
port="8000"
# ---------------------------------

# Deal with local OUI cache

# 90 days in seconds
NOW=int(time.time())
MAXAGE=(NOW - 7776000)

# Test for file existence
mac_vendors_file = os.path.expanduser("~/.cache/mac-vendors.txt")

if not os.path.exists(mac_vendors_file):
    print ("mac-vendors.txt not found.  Downloading...")
    mac = mac_vendor_lookup.MacLookup()
    mac.update_vendors()
else:
    pass

# Test for file age
CURAGE = int(os.path.getmtime(mac_vendors_file))

if (CURAGE < MAXAGE):
    print("mac-vendors.txt is older than 90 days.  Downloading...")
    mac = mac_vendor_lookup.MacLookup()
    mac.update_vendors()

url=("http://" + host + ":" + port + "/json/v1")

r = requests.post(url, json={"command": "lease4-get-all", "service": [ "dhcp4" ]})

jlist = r.json()

for item in jlist:
    leaselist=(item['arguments'])

leasedict=(dict(leaselist))

# Print header
print ('%-17s %-14s %-29s %-17s %-50s' % ("MAC Address", "IP Address", "Hostname", "Expires", "Vendor"))
print ("="*132)

for lease in (leasedict['leases']):

    # Get + calculate timers - all in unix ts
    start  = (lease['cltt'])
    valid  = (lease['valid-lft'])
    expire = (start + valid)

    uexpire = datetime.datetime.fromtimestamp(expire, datetime.UTC)

    datefmt = "%Y%m%d %H:%M:%S"

    fexpire = uexpire.strftime(datefmt)

    # Get hostname / empty.  Also truncate ridiculuous hostname lengths.
    if (lease['hostname']):
        hostname = (lease['hostname'][:27] + '..') if len(lease['hostname']) > 29 else lease['hostname']
    else:
        hostname = "."

    # Get OUI vendor
    try:
        vendor = (mac_vendor_lookup.MacLookup().lookup(lease['hw-address']))
        vendor = (vendor[:48] + '..') if len(vendor) > 50 else vendor
        cvendor     = Fore.CYAN    + vendor              + Style.RESET_ALL
    except:
        vendor = "// PRIVATE OR UNKNOWN //"
        cvendor     = Fore.RED    + vendor              + Style.RESET_ALL

    # Print columns
    chwaddr     = Fore.YELLOW        + lease['hw-address'] + Style.RESET_ALL
    chostname   = Fore.MAGENTA       + hostname            + Style.RESET_ALL
    cexpire     = Fore.LIGHTBLACK_EX + fexpire             + Style.RESET_ALL
    print ('%-18s %-14s %-38s %-17s %-50s' % (chwaddr, lease['ip-address'], chostname, cexpire, cvendor))

print ()
total = (str(len(leasedict['leases'])))
print (total + " total leases.")
