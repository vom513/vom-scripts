* oui.pl
	* MAC (OUI) registration lookup (Company name).

* wepscii.pl
	* Convert ascii->hex, hex->ascii for WEP keys.

* revwalk.pl
	* Walk a CIDR (IPv4) and lookup PTRs.

* neighbor-list.pl
	* ARP/ND with gravy.  Print out all neighbors, MAC vendor, RDNS, etc.  (Linux)  

* nxos-rot.pl
	* Cisco NXOS "rotational" cipher.

* mon.sh
	* Recent linux kernels, wireless drivers, etc very persnickety about changing MAC

* smartreport.pl
	* Linux / FreeBSD - prints out misc. info about hard disks

* fourbyte.pl
	* Convert 32-bit ASN from ASPLAIN <-> ASDOT

* icecast-list-clients.py(3)
	* List connected clients and other info from an icecast streaming server

* ap-client-list.pl
	* List wireless client details on Cisco IOS Autonomous/WAP300 (possibly more) APs

* ups-remaining.py(3)
	* Connect to nut (Network UPS Tools), get UPS runtime and battery charge, display, refresh.

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
