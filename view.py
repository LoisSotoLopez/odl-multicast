from lxml import etree
import libxml2
import os, sys

def _host_abbreviation(hostname):
	return hostname[:2] + hostname[-2:]

# Slight modification on @israel-unterman solution for printing by console python3 lists (see link below)
# https://stackoverflow.com/questions/39032720/formatting-lists-into-columns-of-a-table-output-python-3
# Sort by @stephen and @martin-thoma (see link below)
# https://stackoverflow.com/questions/3121979/how-to-sort-a-list-tuple-of-lists-tuples-by-the-element-at-a-given-index
def show_hosts(hosts):
	hosts_sort = [ (hosts.index(h),h[0]) for h in hosts]
	hosts_sort.sort(key=lambda tup: tup[1])
	host_names = [hosts[h[0]][0] for h in hosts_sort]
	known_ips = [hosts[h[0]][1] for h in hosts_sort]
	abbreviations = [_host_abbreviation(hosts[h[0]][0]) for h in hosts_sort]

	titles = ['host_names', 'known_ips', 'abbreviations']
	data = [titles] + list(zip(host_names, known_ips, abbreviations))

	for i, d in enumerate(data):
		line = '|'.join(str(x).ljust(30) for x in d)
		print(line)
		if i == 0:
			print('-' * len(line))

def show_links(links, hosts):
	print("\nLinks")
	n=0
	links.sort(key=lambda tup: _host_abbreviation(hosts[tup[0]]))
	for l in links:
		n+=1
		print(_host_abbreviation(hosts[l[0]][0]), "-",_host_abbreviation(hosts[l[1]][0]), end='\t')
		if n % 5 == 0:
			print()

def clean():
	os.system("clear")
