import requests
from requests.auth import HTTPBasicAuth
BASEURL = 'http://localhost:8181/restconf/'
CREDENTIALS = HTTPBasicAuth('admin','admin')

def get_topo():
	url = BASEURL + 'operational/network-topology:network-topology'
	headers = {
		'Accept': 'application/xml'
	}

	try:
		resp = requests.get(url, headers = headers, auth= CREDENTIALS)
	except Exception as e:
		print(e)
		print("Error! " + type(e).__name__ )

	else:
		if (resp.status_code == requests.codes.ok ):
			return "ok",resp.text
		else:
			return "bad",resp.text

def get_flows_for(node_id):
	url = BASEURL + "config/opendaylight-inventory:nodes/node/" + node_id + "/table/0/"
	headers = {
		'Accept': 'application/xml'
	}

	try:
		resp = requests.get(url, headers = headers, auth= CREDENTIALS)
	except Exception as e:
		print("Error! " + type(e).__name__ )

	else:
		if (resp.status_code == requests.codes.ok ):
			return "ok",resp.text
		else:
			return "bad",resp.text
