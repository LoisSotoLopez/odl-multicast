#!/usr/bin/python3
import os, re, signal, sys
import rest_service as service
import view
from exceptions import GoBack
from lxml import etree
import libxml2
import ipaddress
from dijkstar import Graph, find_path


## Signal handler
def ctrl_c_handler(sig, frame):
    close()

## Controller data transformations M->V
## Purge and modify data from the model to provide it to the view.
def _clean_namespaces(xml):
	xml = re.sub(' xmlns="[^"]+"', '', xml)
	xml = re.sub(' xmlns:a="[^"]+"', '', xml)
	return xml

def _get_topo_view_xml(xml):
	xml = _clean_namespaces(xml)
	
	view_tree = etree.Element("nodes")
	context = libxml2.parseDoc(xml)
	# Store representation of nodes and links received from model
	m_nodes = context.xpathEval("/network-topology/topology/node")
	m_links = context.xpathEval("/network-topology/topology/link")

	_clean_graph()

	for n in m_nodes:
		view_node = etree.SubElement(view_tree, "node")
		view_node_id = etree.SubElement(view_node, "node-id")
		view_node_id.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/node-id/text()')[0])
		if view_node_id.text[0:4] == "host":
			view_node_ip = etree.SubElement(view_node, "ip")
			view_node_ip.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/addresses/ip/text()')[0])
			_add_node(view_node_id.text, view_node_ip.text)

			view_node_mac = etree.SubElement(view_node, "mac")
			view_node_mac.text = str(libxml2.parseDoc(str(n)).xpathEval('/node/addresses/mac/text()')[0])
		else:
			_add_node(view_node_id.text, "")

		for l in m_links:
			# Append to node links which id is in irst half (source) of  link id
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

	for l in m_links:
		aux = str(libxml2.parseDoc(str(l)).xpathEval('/link/link-id/text()')[0])
		# A pair of port ids => for hosts matches with id, for switch it does not
		lsrc = str(libxml2.parseDoc(str(l)).xpathEval('/link/source/source-tp/text()')[0])
		ldst = str(libxml2.parseDoc(str(l)).xpathEval('/link/destination/dest-tp/text()')[0])
		src_ref, dst_ref = _get_node_pos(lsrc), _get_node_pos(ldst)
		_add_link(src_ref, dst_ref)

	_build_graph()
	

		
	return etree.tostring(view_tree)

def _get_node_flows_view_xml(xml):
	xml = _clean_namespaces(xml)
	return xml


####

## Controller logic
## Perform actions on controller variables
def _clean_graph():
	graph = Graph()
	nodes = []
	links = []

def _add_node(node_id, node_ip):
	nodes.append((node_id, node_ip))

def _get_node_pos(node_ref):
	# Get index i of next element i,v in nodes wich value v matches node_ref
	try:
		return nodes.index(next(i for i in nodes if node_ref.find(i[0]) != -1 or node_ref == i[1] ))
	except:
		pass

def _add_link(node1_ref, node2_ref):
	links.append((node1_ref, node2_ref))

def _build_graph():
	for l in links:
		graph.add_edge(l[0],l[1],1)

def _get_path(ref1, ref2):
	id1 = _get_node_pos(ref1)
	id2 = _get_node_pos(ref2)
	return find_path(graph, id1, id2)

####


## MVC communications
## Call service functions, model-view transformations and controller logic functions
def _is_ip(string):
	try:
		ipaddress.IPv4Address(string)
		print("IPv4 detected")
		True
	except ipaddress.AddressValueError:
		print("Node id detected")
		False

def _is_switch(identifier):
	return not identifier[:4] == "host"

def _is_error(func, *args, **kw):
    try:
        func(*args, **kw)
        return False
    except Exception:
        return True

def _get_flows_ids(xml):
	xml = _clean_namespaces(xml)

	context = libxml2.parseDoc(xml)
	# Store representation of nodes and links received from model
	ids = [str(i) for i in libxml2.parseDoc(str(xml)).xpathEval('/table/flow/id/text()')]
	return ids

def _get_ports_refs(xml):
	xml = _clean_namespaces(xml)

	context = libxml2.parseDoc(xml)
	# Store representation of ports received from model
	ids = [str(i).split(":")[-1] for i in libxml2.parseDoc(str(xml)).xpathEval('/node/node-connector/id/text()')]
	clean_ids = [i for i in ids if not _is_error(int,i)]
	return clean_ids

def _get_flow_id_for_port(xml, port_ref):
	xml = _clean_namespaces(xml)
	context = libxml2.parseDoc(xml)
	# Store representation of nodes and links received from model
	flows = context.xpathEval("/table/flow")
	for f in flows:
		if str(libxml2.parseDoc(str(f)).xpathEval('/flow/flow-name/text()')[0]) == ("block_port_"+ port_ref):
			return str(libxml2.parseDoc(str(f)).xpathEval('/flow/id/text()')[0])
	return -1

def _get_port_with(node_ref, neighbor_ref, xml):
	context = libxml2.parseDoc(xml)
	links = context.xpathEval("/network-topology/topology/link")

	for l in links:
		if str(libxml2.parseDoc(str(l)).xpathEval('/link/source/source-node/text()')[0]) == node_ref and str(libxml2.parseDoc(str(l)).xpathEval('/link/destination/dest-node/text()')[0]) == neighbor_ref:
			return str(libxml2.parseDoc(str(l)).xpathEval('/link/source/source-tp/text()')[0])


def show_topo():
	response = service.get_topo()
	xml = _get_topo_view_xml(response[1]).decode('UTF-8')
	view.show_info(xml, mode=response[0])

def show_node_flows():
	print("(Node id) ", end= '')
	node_id = input("> ")
	response = service.get_flows_for(node_id)
	xml = _get_node_flows_view_xml(response[1])
	view.show_info(xml, mode=response[0])

def clean_flows():
	if nodes==[]:
		print("No nodes detected. Have you 'shown network topology' ?")
		back()
	else:
		for n in (n for n in nodes if _is_switch(n[0])):
			node_ref = n[0]
			response = service.get_flows_for(node_ref)
			if response[0] == "ok":
				flow_ids = _get_flows_ids(response[1])
				for f in flow_ids:
					response = service.delete_flow(node_ref, f)
					view.show_info(response[1], mode=response[0])
			else:
				view.show_info(response[1],"error")

def block_all():
	if nodes==[]:
		print("No nodes detected. Have you 'shown network topology' ?")
		back()
	else:
		clean_flows()
		for n in (n for n in nodes if _is_switch(n[0])):
			node_ref = n[0]
			response = service.get_flows_for(node_ref)
			if response[0] == "ok":
				flow_ids = _get_flows_ids(response[1])
				if flow_ids == []:
					flow_id = 1
				else:
					flow_id = max([int(i) for i in flow_ids]) + 1
				response = service.get_all_for(node_ref)
				if response[0] == "ok":
					ports = _get_ports_refs(response[1])
					for p in ports:
						response = service.block_port(node_ref, p, flow_id)
						flow_id+=1
						view.show_info(response[1],response[0])
				else:
					view.show_info(response[1],response[0])
			else:
				view.show_info(response[1],response[0])

def enable_port(node_ref=None, port_ref=None):
	if nodes==[]:
		print("No nodes detected. Have you 'shown network topology' ?")
		back()
	else:
		if node_ref == None:
			print("(Node (switch) id) ", end='')
			node_ref = input("> ")

		flow_response = service.get_flows_for(node_ref)
		if flow_response[0] == "ok":
			flow_ids = _get_flows_ids(flow_response[1])
			if flow_ids == []:
				print("All ports are enabled.")
			else:
				ports_response = service.get_all_for(node_ref)
				if ports_response[0] == "ok":
					ports = _get_ports_refs(ports_response[1])
					if port_ref == None:
						print("(Port id) " + str(ports) , end='')
						port_ref = input(" > ")
					blocking_flow_id = _get_flow_id_for_port(flow_response[1], port_ref)
					if blocking_flow_id == -1:
						print("Port is already unlocked")
					else:
						response = service.delete_flow(node_ref, blocking_flow_id)
						view.show_info(response[1],response[0])
				else:
					view.show_info(ports_response[1],ports_response[0])
		else:
			view.show_info(flow_response[1],flow_response[0])

def block_port():
	if nodes==[]:
		print("No nodes detected. Have you 'shown network topology' ?")
		back()
	else:
		print("(Node (switch) id) ", end='')
		node_ref = input("> ")

		flow_response = service.get_flows_for(node_ref)
		if flow_response[0] == "ok":
			flow_ids = _get_flows_ids(flow_response[1])
			if flow_ids == []:
				flow_id = 1
			else:
				flow_id = max([int(i) for i in flow_ids]) + 1
			ports_response = service.get_all_for(node_ref)
			if ports_response[0] == "ok":
				ports = _get_ports_refs(ports_response[1])
				print("(Port id) " + str(ports) , end='')
				port_ref = input(" > ")
				blocking_flow_id = _get_flow_id_for_port(flow_response[1], port_ref)
				if blocking_flow_id == -1:
					response = service.block_port(node_ref, port_ref, flow_id)
					print("Port blocked: " + node_ref + ":" + port_ref)
				else:
					print("Port is already blocked")
			else:
				view.show_info(ports_response[1],ports_response[0])

def enable_path():
	if nodes==[]:
		print("No nodes detected. Have you 'shown network topology' ?")
		back()
	else:
		print("(Node 1 id | ip ) ", end='')
		node1_ref = input("> ")
		print("(Node 2 id | ip ) ", end='')
		node2_ref = input("> ")

		path = _get_path(node1_ref, node2_ref)
		response = service.get_topo()
		if response[0] == "ok":
			xml = _clean_namespaces(response[1])
			# Iterate over path.nodes (list of positions on nodes)
			for i in range(len(path.nodes)-1):
				# path.nodes[i] is the position in nodes of the i-th node of the path
				if _is_switch(nodes[path.nodes[i]][0]):
					port = _get_port_with(nodes[path.nodes[i]][0], nodes[path.nodes[i-1]][0], xml)
					enable_port(nodes[path.nodes[i]][0], port.split(":")[-1])
					port = _get_port_with(nodes[path.nodes[i]][0], nodes[path.nodes[i+1]][0], xml)
					enable_port(nodes[path.nodes[i]][0], port.split(":")[-1])

		else:
			print("Error! Could not retrieve needed topology.")
####
def back():
	raise GoBack()

def close():
	print("\nClosing application ...")
	sys.exit(0)

# Enable nodes menu
def enable_block_menu():
	print("\nEnable/Block nodes menu.")
	print("[0] Go back.")
	print("[1] Clean all flows.")
	print("[2] Block all.")
	print("[3] Enable a switch port.")
	print("[4] Block a switch port.")
	print("[5] Enable switch ports in a path.")
	return(input("> "))
	

# Enable nodes loop
def enable_block_loop():
	actions = {
		0: back,
		1: clean_flows,
		2: block_all,
		3: enable_port,
		4: block_port,
		5: enable_path
	}
	while True:
		try:
			val = enable_block_menu()
			#os.system("clear")
			actions[int(val)]()
		except KeyError as e:
			#os.system("clear")
			print("Error! Invalid option \"", val, "\"")
		except GoBack:
			break
# Application menu
def main_menu():
	print("\n Main menu.")
	print("[0] Close application.")
	print("[1] Show network topology.")
	print("[2] Show flows for node.")
	print("[3] Block/Enable nodes ...")
	return input("> ")

# Application loop
def main_loop():
	# Map used to implement switch case
	actions = {
		0: close,
		1: show_topo,
		2: show_node_flows,
		3: enable_block_loop,
	}
	while True:
		try:
			val = main_menu()
			#os.system("clear")
			actions[int(val)]()
		except KeyError as e:
			#os.system("clear")
			print("Error! Invalid option \"", val, "\"")


try:
	# Initialization
	signal.signal(signal.SIGINT, ctrl_c_handler) # Register handler

	graph = Graph()
	nodes = []
	links = []
	block_flows = []

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
