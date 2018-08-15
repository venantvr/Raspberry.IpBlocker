import os
import time
import pycurl
import gzip
from netaddr import IPNetwork

directory = '/tmp/'
target = directory + 'ranges.txt'
ipblocker = directory + 'france.' + time.strftime('%Y%m%d') + '.p2p'
archive = ipblocker + '.gz'

url = 'http://www.ipdeny.com/ipblocks/data/aggregated/fr-aggregated.zone'

c = pycurl.Curl()
c.setopt(c.URL, url)

with open(target, 'w') as f:
        c.setopt(c.WRITEFUNCTION, f.write)
        c.perform()
	f.close()

with open(ipblocker, 'w') as t:
	with open(target) as f:
	        for line in f:
        	        item = line.strip()
			ip = IPNetwork(item)
			first = str(ip[0])
			last = str(ip[-1])
			t.write('France:' + first + '-' + last + '\n')
		f.close()
	t.close()

f = open(ipblocker)
t = gzip.open(archive, 'wb')
t.writelines(f)
t.close()
f.close()
