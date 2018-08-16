import re
import os
import time
import pycurl
import gzip
import socket
import struct
import sys
import pprint
from netaddr import IPNetwork

def merge_overlapping(initialranges):
	i = sorted(set([tuple(sorted(x)) for x in initialranges]))
	# initialize final ranges to [(a,b)]
	f = [i[0]]
	for c, d in i[1:]:
		a, b = f[-1]
		if c<=b<d:
			f[-1] = a, d
		elif b<c<d:
			f.append((c,d))
		else:
			# else case included for clarity. Since
			# we already sorted the tuples and the list
			# only remaining possibility is c<d<b
			# in which case we can silently pass
			pass
	return f

def gz_file(file):
	f = open(file)
	t = gzip.open(file + '.gz', 'wb')
	t.writelines(f)
	t.close()
	f.close()
	return

def ip2long(ip):
	'''IP to integer'''
	packed = socket.inet_aton(ip)
	return struct.unpack("!L", packed)[0]

def long2ip(n):
	'''integer to IP'''
	unpacked = struct.pack('!L', n)
	return socket.inet_ntoa(unpacked)

directory = '/tmp/'
target = directory + 'ranges.txt'
ipblocker = directory + 'france.' + time.strftime('%Y%m%d') + '.p2p'
optimized = directory + 'france.optimized.' + time.strftime('%Y%m%d') + '.p2p'
# archive = ipblocker + '.gz'

i = 0
lines = []
files = []

url = 'https://www.hack-my-domain.fr/wp-content/uploads/free-tools/p2p.sources'

c = pycurl.Curl()
c.setopt(c.URL, url)
target = directory + 'p2p.sources'

with open(target, 'w') as f:
	c.setopt(c.WRITEFUNCTION, f.write)
	c.perform()

with open(target) as f:
	for line in f:
		item = line.strip()
		match = len(item) > 0 and item.startswith('http')
		if match:
			files.append(item)

for file in files:
	c = pycurl.Curl()
	c.setopt(c.URL, file)
	target = directory + str(i) + '.txt'
	
	with open(target, 'w') as f:
		c.setopt(c.WRITEFUNCTION, f.write)
		c.perform()
	
	with open(target) as f:
		for line in f:
			item = line.strip()
			lines.append(item)
			
	i = i + 1

filtered = dict.fromkeys(lines).keys()

url = 'http://www.ipdeny.com/ipblocks/data/aggregated/fr-aggregated.zone'

c = pycurl.Curl()
c.setopt(c.URL, url)

with open(target, 'w') as f:
	c.setopt(c.WRITEFUNCTION, f.write)
	c.perform()
	f.close()

with open(ipblocker, 'w') as t:
	for item in filtered:
		match = re.match(r'^(.*):\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', item)
		if match:
			t.write(item + '\n')
	with open(target) as f:
		for line in f:
			item = line.strip()
		ip = IPNetwork(item)
		first = str(ip[0])
		last = str(ip[-1])
		t.write('France:' + first + '-' + last + '\n')
		f.close()
	t.close()

consolidated = []

with open(ipblocker) as f:
	for line in f:
		item = line.strip()
		match = re.match(r'^(.*):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})-(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', item)
		ipfrom = match.group(2)
		ipto = match.group(3);
		consolidated.append((ip2long(ipfrom), ip2long(ipto)))
	f.close()

merged = merge_overlapping(consolidated)

with open(optimized, 'w') as t:
	for item in merged:
		t.write('Consolidated:' + long2ip(item[0]) + '-' + long2ip(item[1]) + '\n')
	t.close()

gz_file(ipblocker)
gz_file(optimized)
