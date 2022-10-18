#!/usr/bin/env python3
#

from datetime import date
import calendar
import random
import os
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

today = date.today()

dateformatted = calendar.day_name[today.weekday()] + " " + str(today.month) + "/" + str(today.day) + "/" + str(today.year)

dict_adj="/usr/share/dict/guest-adjective.txt";
dict_noun="/usr/share/dict/guest-noun.txt";

adjs = []
nouns = []

# Read adjectives
with open(dict_adj) as a:
	for line in a:
		line = line.rstrip()
		if (5 <= len(line) <= 8):
			adjs.append(line)
a.close()

# Read nouns
with open(dict_noun) as a:
	for line in a:
		line = line.rstrip()
		if (5 <= len(line) <= 8):
			nouns.append(line)
a.close()

# Get random values
adj = random.choice(adjs)
adj = adj.capitalize()
noun = random.choice(nouns)
noun = noun.capitalize()
digits = random.randrange(0, 9999, 1)
digits = "{:04d}".format(digits)

# Assemble key
key = adj + noun + digits
qrstring = "WIFI:S:GUEST;T:WPA2;P:" + key + ";;"

# Write out qrcode
command = ("echo \'" + qrstring + "\' | qrencode -s 10 -o /var/www/html/guest.png")
os.system(command)

# Write out html
html = """<html>
        <head>
                <title>Guest WIFI Password</title>
                <meta http-equiv="refresh" content="900">
        </head>
        <body>
                <center>
                        <h3>Guest WIFI Password for {htmldate}</h3>
                        <table border="1" style="font-size:22;" cellpadding="5" width="30%">
                                <tr>
                                        <th>SSID</th>
                                        <td align="center"><font face="Courier New">GUEST</font></td>
                                </tr>
                                <tr>
                                        <th>Key</th>
                                        <td align="center"><font face="Courier New"><b>{htmlkey}</b></font></td>
                                </tr>
                        </table>
                        <img src=guest.png width=300>
                        <br>
                        <b>Note: key is changed daily @ 3:15 am.</b>
                        <br>
                </center>
        </body>
</html>
""".format(htmldate=dateformatted, htmlkey=key)

with open("/var/www/html/guest.html","w+") as f:
        f.writelines(html)
f.close()

txt = (dateformatted + "," + key)

with open("/var/www/html/guest.txt", "w+") as f:
	f.writelines(txt)
f.close

# Login and get sid
params = {"user": "admin", "passwd": "password"}

response = requests.post("https://ap-vc:4343/rest/login", json=params, verify=False,
	headers={
   		"Content-Type": "application/json"
 	}
)

json_data = response.json()
sid = (json.dumps(json_data["sid"]).strip('"'))

# Change PSK
ssid_json = {
	"ssid-profile": {
		"action": "create",
		"ssid-profile": "GUEST",
		"wpa-passphrase": key
	}
}

params = {"sid": sid}

response = requests.post("https://ap-vc:4343/rest/ssid", params=params, json=ssid_json, verify=False,
	headers={
   		"Content-Type": "application/json"
 	}
)

# Logout
params = {"sid": sid}

response = requests.post("https://ap-vc:4343/rest/logout", json=params, verify=False,
	headers={
   		"Content-Type": "application/json"
 	}
)
