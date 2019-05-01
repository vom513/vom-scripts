#!/usr/bin/python

import xml.etree.ElementTree as ET
import urllib2
import base64
from termcolor import colored
from dns import resolver,reversename,exception
import sys

# print colored('hello', 'red'), colored('world', 'green')

listeners_url="http://FIXME:8000/admin/listclients?mount=/FIXME"
stats_url="http://FIXME:8000/admin/stats?mount=/FIXME"

username = "admin"
password = "FIXME"

base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

listeners_request = urllib2.Request(listeners_url)
listeners_request.add_header("Authorization", "Basic %s" % base64string) 

stats_request = urllib2.Request(stats_url)
stats_request.add_header("Authorization", "Basic %s" % base64string) 

try:
	listeners_result = urllib2.urlopen(listeners_request)
except urllib2.HTTPError as err:
	if err.code:
		error = "HTTP error " + str(err.code)
		print colored(error, 'red')
		sys.exit(1)

listeners_data = listeners_result.read()

try:
	stats_result = urllib2.urlopen(stats_request)
except urllib2.HTTPError as err:
	if err.code:
		error = "HTTP error " + str(err.code)
		print colored(error, 'red')
		sys.exit(1)

stats_data = stats_result.read()

listeners_root = ET.fromstring(listeners_data)

stats_root = ET.fromstring(stats_data)

# Init lists
ips=list()
ipv4=list()
ipv6=list()
uas=list()
connected=list()
title=list()
peak=list()

# Listeners
for child in listeners_root.iterfind('.//IP'):
	ips.append(child.text)
	if ":" in child.text:
		ipv6.append(child.text)
	else:
		ipv4.append(child.text)

listeners=len(ips)

ipv4s=len(ipv4)
ipv6s=len(ipv6)

for child in listeners_root.iterfind('.//UserAgent'):
	uas.append(child.text)

for child in listeners_root.iterfind('.//Connected'):
	connected.append(child.text)

# Stats
for child in stats_root.iterfind('.//title'):
        title.append(child.text)

for child in stats_root.iterfind('.//listener_peak'):
        peak.append(child.text)

print

ctitle = colored(title[0], 'magenta')
clisteners = colored(listeners, 'green')
cpeak = colored(peak[0], 'green')

print "Now playing:", ctitle
print
print "Current listeners: %-2s (%s ipv4, %s ipv6)" % (clisteners,ipv4s,ipv6s)
print "Peak listeners:    %-2s" % (cpeak)
print "-------------------------------------------------------------------------------------------------------------------------------"

for i in range(0, listeners):
	cips = colored(ips[i], 'cyan')
	cuas = colored(uas[i], 'yellow')
	cconnected = colored(connected[i], 'magenta')

	addr=reversename.from_address(ips[i])

	try:
		answer = str(resolver.query(addr,"PTR")[0])
		answer = answer.rstrip('.')
		rdns = colored(answer, 'blue')
	except resolver.NXDOMAIN:
		rdns = colored("NO RDNS", 'blue')
	except resolver.Timeout:
		rdns = colored("NO RDNS", 'blue')
	except exception.DNSException:
		rdns = colored("NO RDNS", 'blue')

	print 'IP: %-48s Connected for (seconds): %-6s' % (cips,cconnected)
	print 'RDNS: %-75s' % (rdns)
	print 'User agent: %-75s' % (cuas)
	print "-------------------------------------------------------------------------------------------------------------------------------"
print
