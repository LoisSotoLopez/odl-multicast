import requests
from requests.auth import HTTPBasicAuth

BASEURL = 'http://localhost:8181/restconf/'
CREDENTIALS = HTTPBasicAuth('admin','admin')
BLOCK_XML_PATH = 'static/rest/block_all.xml'

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

def delete_flow(node_id, flow_id):
	url = BASEURL + 'config/opendaylight-inventory:nodes/node/' + node_id + '/table/0/flow/' + str(flow_id)
	headers = {
		'Accept': 'application/xml'
	}

	try:
		resp = requests.delete(url, headers = headers, auth= CREDENTIALS)
	except Exception as e:
		print(e)
		print("Error! " + type(e).__name__ )

	else:
		if (resp.status_code == requests.codes.ok ):
			return "ok",resp.text
		else:
			return "bad",resp.text

def get_all_for(node_ref):
	url = BASEURL + "operational/opendaylight-inventory:nodes/node/"+ node_ref +"/"
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

def block_port(node_ref, node_port, flow_id):
	url = BASEURL + "config/opendaylight-inventory:nodes/node/"+ node_ref +"/table/0/flow/" + str(flow_id)
	headers = {
		'Content-Type': 'application/xml'
	}

	data = "<?xml version='1.0' encoding='UTF-8' standalone='no'?><flow xmlns='urn:opendaylight:flow:inventory'>"
	data += "<strict>false</strict><instructions><instruction><order>0</order><apply-actions><action><order>1</order>"
	data += "<drop-action/></action></apply-actions></instruction></instructions><table_id>0</table_id><id>"+ str(flow_id)
	data += "</id><cookie_mask>255</cookie_mask><match><in-port>"+ str(node_port) + "</in-port></match>"
	data += "<flow-name>block_port_" + str(node_port) + "</flow-name><priority>20</priority></flow>"

	try:
		resp = requests.put(url, data = data, headers = headers, auth= CREDENTIALS)
	except Exception as e:
		print(e)
		print("Error! " + type(e).__name__ )

	else:
		if (resp.status_code == requests.codes.ok ):
			return "ok",resp.text
		else:
			return "bad",resp.text

