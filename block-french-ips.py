import gzip
import re
import socket
import struct
import time

import pycurl
from netaddr import IPNetwork


def merge_overlapping(initialranges):
    i = sorted(set([tuple(sorted(x)) for x in initialranges]))
    # initialize final ranges to [(a,b)]
    f = [i[0]]
    for c, d in i[1:]:
        a, b = f[-1]
        if c <= b < d:
            f[-1] = a, d
        elif b < c < d:
            f.append((c, d))
        else:
            # else case included for clarity. Since
            # we already sorted the tuples and the list
            # only remaining possibility is c<d<b
            # in which case we can silently pass
            pass
    return f


def gz_file(file: str):
    with open(file) as f:
        with gzip.open(file + '.gz', 'wb') as t:
            t.writelines(f)
    return


def ip2long(ip):
    """IP to integer"""
    packed = socket.inet_aton(ip)
    return struct.unpack("!L", packed)[0]


def long2ip(n):
    """integer to IP"""
    unpacked = struct.pack('!L', n)
    return socket.inet_ntoa(unpacked)


def curl2file(url: str, file: str):
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    with open(file, 'w') as f:
        c.setopt(c.WRITEFUNCTION, f.write)
        c.perform()
        f.close()
    print('Written {0} in {1}'.format(url, file))
    return


directory = '/tmp/'
sources = '{0}p2p.sources'.format(directory)
france = '{0}fr-aggregated.zone'.format(directory)
ipblocker = '{0}france.scratch.{1}.p2p'.format(directory, time.strftime('%Y%m%d'))
optimized = '{0}france.optimized.{1}.p2p'.format(directory, time.strftime('%Y%m%d'))

i = 0
lines = []
files = []

curl2file('https://www.hack-my-domain.fr/wp-content/uploads/free-tools/p2p.sources', sources)

with open(sources) as f:
    for line in f:
        item = line.strip()
        match = len(item) > 0 and item.startswith('http')
        if match:
            files.append(item)

for file in files:
    tmp = '{0}{1}.txt'.format(directory, str(i))
    curl2file(file, tmp)

    with open(tmp) as f:
        for line in f:
            item = line.strip()
            lines.append(item)

    i = i + 1

filtered = dict.fromkeys(lines).keys()

curl2file('http://www.ipdeny.com/ipblocks/data/aggregated/fr-aggregated.zone', france)

with open(ipblocker, 'w') as t:
    for item in filtered:
        match = re.match(r'^(.*):\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', item)
        if match:
            t.write(item + '\n')
    with open(france) as f:
        for line in f:
            item = line.strip()
            ip = IPNetwork(item)
            first = str(ip[0])
            last = str(ip[-1])
            t.write('France:{0}-{1}\n'.format(first, last))
        f.close()
    t.close()

# sys.exit()

consolidated = []

with open(ipblocker) as f:
    for line in f:
        item = line.strip()
        match = re.match(r'^(.*):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})-(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', item)
        ipfrom = match.group(2)
        ipto = match.group(3)
        consolidated.append((ip2long(ipfrom), ip2long(ipto)))
    f.close()

merged = merge_overlapping(consolidated)

with open(optimized, 'w') as t:
    for item in merged:
        t.write('Optimized:{0}-{1}\n'.format(long2ip(item[0]), long2ip(item[1])))
    t.close()

gz_file(ipblocker)
gz_file(optimized)
