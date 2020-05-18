import sys
import re
import urllib3
import functools
from concurrent.futures import ThreadPoolExecutor

# PARAMS - could be changed to be CLI arguments
TIMEOUT = 15                      # Connect/read timeout
RETRIES = 1                       # Connect/read retries that are permitted
REDIRECTS = 0                     # How many redirects to follow
OUTPUT_STATUS_CODES = [200, 403]  # Status codes to track in results
ASSUME_SCHEME = 'https://'        # Scheme to assume when none is provided
# The following controls:
# Connection pool #
# Max simultaneous connections
# Number of Python threads
# Essentially, how many requests can be active at once
# Be careful when tuning this
THREADS = 10

# usage and arg validation
if len(sys.argv) != 3:
    print('-- Usage:')
    print('pywebscan.py [https://example.com | 192.168.1.1 | hosts.txt] paths.txt')
    print('-- Notes:')
    print('Protocol must be provided when targeting a single hostname')
    exit()

# turn off output buffering so we see progressive updates
print = functools.partial(print, flush=True)


# add trailing slash and protocol where needed
def formatHost(host):
    if not re.search('^https?:\\/\\/', host): # add scheme if needed
        host = ASSUME_SCHEME + host
    if host[-1] != '/': # add trailing slash if needed
        host += '/'
    return host


# request a url and return a (url, status code) tuple
def request(url):
    try:
        response = http.request('GET', url)
        print(url, response.status)
        return (url, response.status)
    except Exception: # SSL error, timeout, host is down, firewall block, etc.
        print(url, 'ERROR')
        return (url, None)


# parse hosts
hosts = []
# hosts as an argument (IP or hostname)
if re.search('^([0-9]{1,3}\\.){3}[0-9]{1,3}$', sys.argv[1]) \
        or re.search('^https?:\\/\\/', sys.argv[1]):
    hosts.append(formatHost(sys.argv[1]))
else: # hosts from a file
    fp = open(sys.argv[1], 'r')
    hosts = [formatHost(line.strip()) for line in fp if len(line.strip()) > 0]
    fp.close()

# parse paths
fp = open(sys.argv[2], 'r')
paths = [line.strip().lstrip('/') for line in fp if len(line.strip()) > 0] # strip leading slash
fp.close()

# initialize our http object
timeout = urllib3.util.Timeout(connect=TIMEOUT, read=TIMEOUT)
retries = urllib3.util.Retry(connect=RETRIES, read=RETRIES, redirect=REDIRECTS)
http = urllib3.PoolManager(
    retries=retries,
    timeout=timeout,
    num_pools=THREADS,
    maxsize=THREADS,
    block=True
)

# thread and execute the scan
print(f'Scanning {len(hosts)} host(s) for {len(paths)} path(s) - {len(hosts) * len(paths)} requests total...\n')
print('------ REQUESTS ------\n')

urls = [host + path for host in hosts for path in paths]
with ThreadPoolExecutor(max_workers=THREADS) as executor:
    results = executor.map(request, urls)
executor.shutdown(wait=True)

# print our results
print('\n------ RESULTS ------\n')

results = list(results) # convert from generator
pathNum = len(paths)
for i, host in enumerate(hosts):
    # group our results by host by slicing since order is preserved
    group = results[(i * pathNum):(i * pathNum + pathNum)]
    # filter for desired status codes
    filtered = [result for result in group if result[1] in OUTPUT_STATUS_CODES]

    # output
    print(host)
    print('---')
    for url, status in filtered:
        print(url, status)
    if not filtered:
        print('no results')
    print()

print("------ SCAN COMPLETE ------\n")
