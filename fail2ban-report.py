#!/usr/bin/env python3

from systemd import journal
from datetime import datetime, timedelta
from collections import Counter

def get_unique_items(list):
    unique_items_list = []
    unique_items = set(list)

    for item in unique_items:
        unique_items_list.append(item)

    return unique_items_list

j = journal.Reader()
j.add_match(_SYSTEMD_UNIT="fail2ban.service")

# Get last 1 day of logs.  This is intended to be ran daily via cron
j.seek_realtime(datetime.now() - timedelta(days=1))

lines = []

for entry in j:
    if ("Ban" in entry["MESSAGE"] or "Unban" in entry["MESSAGE"]):
        #print(entry["MESSAGE"])
        lines.append(entry["MESSAGE"])

print ()

# Get uique services
services = []

for line in lines:
    service = line.split("]", 1)[0]
    service = service.split("[", 1)[1]
    services.append(service)

unique_services = (get_unique_items(services))

# Get bans/unbans per unique service
for service in unique_services:

    allips = []
    unique_ips = []
    bans = []
    unique_bans = []
    counter_bans = {}
    unbans = []
    unique_unbans = []
    counter_unbans = {}

    # Unique IPs
    for line in lines:
        if (service in line and ("Ban" in line or "Unban" in line)):
            if ("Restore" in line):
                ip = line.split()[3]
            else:
                ip = line.split()[2]
            allips.append(ip)

    unique_ips = (get_unique_items(allips))

    #print ("Bans for service", service)

    # Bans
    for line in lines:
        if (service in line and "Ban" in line):
            if ("Restore" in line):
                ip = line.split()[3]
            else:
                ip = line.split()[2]
            bans.append(ip)

    unique_bans = (get_unique_items(bans))
    #print ("Unique bans:", unique_bans)
    counter_bans=(Counter(bans))

    #for ip in unique_bans:
    #    print (ip, counter_bans[ip])

    #print ("Unbans for service", service)

    # Unbans
    for line in lines:
        if (service in line and "Unban" in line):
            ip = line.split()[2]
            unbans.append(ip)

    unique_unbans = (get_unique_items(unbans))
    #print ("Unique unbans:", unique_unbans)
    counter_unbans=(Counter(unbans))

    #for ip in unique_unbans:
    #    print (ip, counter_unbans[ip])

    print (service + ":")
    print (53 * "=")
    #print (len(service)*"=" + "=")
    print ('%-40s %-5s %-5s' % ("IP", "Bans", "Unbans"))
    print (26 * "- " + "-")
    for ip in unique_ips:
        print ('%-40s %-5s %-5s' % (ip, counter_bans[ip], counter_unbans[ip]))

    print ()
