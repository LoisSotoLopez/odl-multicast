#!/usr/bin/python3
import os, re, signal, sys
import rest_service as service
import view
from lxml import etree
import libxml2

## Signal handler
def ctrl_c_handler(sig, frame):
    close()

## Controller data transformations
def _clean_namespaces(xml):
	xml = re.sub(' xmlns="[^"]+"', '', xml)
	xml = re.sub(' xmlns:a="[^"]+"', '', xml)
	return xml

def get_topo_view_xml(xml):
	xml = _clean_namespaces(xml)
	
	view_tree = etree.Element("nodes")

	context = libxml2.parseDoc(xml)
	nodes = context.xpathEval("/network-topology/topology/node")
	links = context.xpathEval("/network-topology/topology/link")

	for n in nodes:
		view_node = etree.SubElement(view_tree, "node")
		view_node_id = etree.SubElement(view_node, "node-id")
		view_node_id.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/node-id/text()')[0])

		if view_node_id.text[0:4] == "host":
			view_node_ip = etree.SubElement(view_node, "ip")
			view_node_ip.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/addresses/ip/text()')[0])

			view_node_mac = etree.SubElement(view_node, "mac")
			view_node_mac.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/addresses/mac/text()')[0])

		for l in links:
			print(view_node_id.text)
			print(str(libxml2.parseDoc(str(l)).xpathEval('/link/link-id/text()')[0]).split("/")[0])
			print((str(libxml2.parseDoc(str(l)).xpathEval('/link/link-id/text()')[0]).split("/")[0]).find(view_node_id.text))
			# Get first half of identifier (link source)
			if (str(libxml2.parseDoc(str(l)).xpathEval('/link/link-id/text()')[0]).split("/")[0]).find(view_node_id.text) != -1:
				link = etree.SubElement(view_node, "link")
				link_id = etree.SubElement(link, "link-id")
				link_id.text = str(libxml2.parseDoc(str(l)).xpathEval('/link/link-id/text()')[0])
				link_src = etree.SubElement(link, "source")
				link_src.text = str(libxml2.parseDoc(str(l)).xpathEval('/link/source/source-tp/text()')[0])
				link_dst = etree.SubElement(link, "destination")
				link_dst.text = str(libxml2.parseDoc(str(l)).xpathEval('/link/destination/dest-node/text()')[0])
				link_dst_port = etree.SubElement(link, "destination-port")
				link_dst_port.text = str(libxml2.parseDoc(str(l)).xpathEval('/link/destination/dest-tp/text()')[0])
	return etree.tostring(view_tree)

def get_node_flows_view_xml(xml):
	xml = _clean_namespaces(xml)
	return xml
####
	

## MVC communications

def show_topo():
	response = service.get_topo()
	xml = get_topo_view_xml(response[1]).decode('UTF-8')
	view.show_info(xml, mode=response[0])

def show_node_flows():
	print(" (Node id) ", end= '')
	node_id = input("> ")
	response = service.get_flows_for(node_id)
	xml = get_node_flows_view_xml(response[1])
	view.show_info(xml, mode=response[0])

####

def close():
	print("\nClosing application ...")
	sys.exit(0)

# Application menu
def menu():
	print("\n[0] Close application.")
	print("[1] Show network topology.")
	print("[2] Show flows for node.")
	return input("> ")

# Application loop
def main_loop():
	# Map used to implement switch case
	actions = {
		0: close,
		1: show_topo,
		2: show_node_flows
	}
	while True:
		try:
			val = menu()
			os.system("clear")
			actions[int(val)]()
		except Exception as e:
			os.system("clear")
			print(e)
			print("Error! Invalid option \"", val, "\"")


try:
	# Initialization
	signal.signal(signal.SIGINT, ctrl_c_handler) # Register handler


	# Display Wellcome
	os.system("clear")
	print("Wellcome to odl-multicast!")

	main_loop()
	
	close()
# Unhandled exceptions terminate application
except Exception as e:
	print(e)
	print("\nError!", e.__class__.__name__, "Exception occurred.")
	print("Terminating ...")
	sys.exit(1)
