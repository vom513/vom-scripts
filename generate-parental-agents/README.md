generate-parental-agents.sh
---------------------------

BIND supports "parental agents" which defines the upstream/parent NS'es for a given zone.

This can then be used in a zone clause for example, and in the case of DNSSEC, BIND will automatically check if the DS record is published.  This is extremely useful in the pursuit of fully automated key rollovers.

This script takes a single argument of [zone].  You should check the FILE variable near the top to make sure this gets written where you want it.  The name of the parental agents set is simply the zone.

The script will output the parental agents for [zone], and diff this against the last time it was ran so you can keep an eye on if the parents zone has changed NS'es and/or IPs.  The script emails root.

Personally I have this in cron to run weekly.  TLDs don't change their auth servers very often, so weekly is more than frequent enough.

I use a wrapper script to run this with a few zones, and at the end do an 'rndc reconfig'.  This is necessary to ensure BIND has the updated list. 

Once you have this writing these files out, you need to include them in your BIND config somewhere:

```
include "/etc/bind/parental-agents-com.include";
```

Then, within a zone clause you can tell BIND to use this set for one of your zones:

```
        zone "example.com" IN {
                type master;   
                file "example.com.zone";   
                parental-agents { "com"; };
        };
   
```

References:

* https://bind9.readthedocs.io/en/v9_18_8/reference.html?highlight=parental#parental-agents-block-grammar

