* ap-client-list.pl
	* List wireless client details on Cisco IOS Autonomous/WAP300 (possibly more) APs

* ap-client-list-engenius.py(3)
	* List wireless client details on Engenius APs (tested on EWS377AP)
	* Needs colorama, paramiko, pysnmp

* ap-client-list-zyxel.py3
	* List wireless client details on Zyxel APs (tested on NMA210AX)
	* Needs colorama, pysnmp

* ap-client-list-aruba-*.py3
	* List wireless client details on Aruba IAP VC APs (tested on AP515, 8.6.x.x, 8.10.x.x)
	* Needs colorama, [net-snmp package|pysnmp4|easysnmp] depending on version
	* Multiple versions here.  net-snmp, pysnmp4, easysnmp.  pysnmp6 deprecated the simple/synchronous interface so it's now too complex for what I'm trying to do.

* ap-guest-psk/
	* Generate random PSK for guest wifi.  <adjective + noun + 4 digit>  Push to Aruba IAP via REST.
	* You will need to edit the script to change your SSID, password etc.  This was for internal use, so it wasn't made to be "friendly".
	* Needs qrencode on system.

* bgp-comm-format.py
	* Convert BGP raw decimal community to "new format" and vice-versa.

* fail2ban-report.py
	* Pulls from systemd journal to make a nicely formatted report for the last day of all f2b ban/unbans. Having tons of issues with logwatch and systemd-journal (ex: Debian >= 12) - hence writing this.

* fail2ban-report
	* Simple shell wrapper for the above report script.  Mails to root.  I put mine in cron daily.

* fourbyte.pl
	* Convert 32-bit ASN from ASPLAIN <-> ASDOT

* generate-parental-agents/
	* Script to create BIND file with parental agents (upstream NS's) for given zone

* icecast-list-clients.py(3)
	* List connected clients and other info from an icecast streaming server

* isis-net.pl
	* Convert IS-IS NET IP address and vice versa
	* Example:

```
vom@onosendai 💀 vom-scripts % ./isis-net.pl 123.45.67.89
1230.4506.7089
vom@onosendai 💀 vom-scripts % ./isis-net.pl 49.0001.1230.4506.7089.00
123.45.67.89
vom@onosendai 💀 vom-scripts % ./isis-net.pl 1230.4506.7089           
123.45.67.89
```

* kea-lease-list4.py
	* Retrieve all DHCP (v4) leases from Kea via management API.  Needs a few extra modules (mac_vendor_lookup, colorama, etc).

* kea-lease-delete4.sh
	* Delete an IPv4 lease from kea server(s).  Needs curl.  Assumes no authentication.

* mon.sh
	* Recent linux kernels, wireless drivers, etc very persnickety about changing MAC

* neighbor-list.pl
	* ARP/ND with gravy.  Print out all neighbors, MAC vendor, RDNS, etc.  (Linux)

* nxos-rot.pl
	* Cisco NXOS "rotational" cipher.

* oui.pl
	* MAC (OUI) registration lookup (Company name).

* revwalk.pl
	* Walk a CIDR (IPv4) and lookup PTRs.

* smartreport.pl
	* Linux / FreeBSD - prints out misc. info about hard disks

* ups-remaining.py(3)
	* Connect to nut (Network UPS Tools), get UPS runtime and battery charge, display, refresh.

* wepscii.pl
	* Convert ascii->hex, hex->ascii for WEP keys.

* Testing VSCode whatnots - ignore !
