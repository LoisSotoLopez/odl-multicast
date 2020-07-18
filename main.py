#!/usr/bin/python3
import os, signal, sys

## Signal handler
def ctrl_c_handler(sig, frame):
    close()


## Main functionalities.

def show_topo():
	print("Doing show_topo")

def show_node_info():
	print("Doing show_node_info")

def show_node_flows():
	print("Doing show_node_flows")

def close():
	print("\nClosing application ...")
	sys.exit(0)

# Application menu
def menu():
	print("\n[0] Close application.")
	print("[1] Show network topology.")
	print("[2] Show information for node.")
	print("[3] Show flows for node.")
	return input("> ")

# Application loop
def main_loop():
	# Map used to implement switch case
	actions = {
		0: close,
		1: show_topo,
		2: show_node_info,
		3: show_node_flows
	}
	while True:
		try:
			val = menu()
			os.system("clear")
			actions[int(val)]()
		except Exception:
			os.system("clear")
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
