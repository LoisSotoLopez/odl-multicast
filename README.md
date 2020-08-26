
# odl-multicast

*odl-multicast* is a Python application that allows performing basic functions against the OpenFlow REST API.

The final purpose of *odl-multicast* is to serve as a tool for the study of multicast traffic management in a OpenDaylight environment, and by extension in any SDN, and therefore may not include many of the interactions the OpenFlow REST API provides.

## Functionalities
Accessible via a CLI menu, the following functionalities are provided:
 - Show network topology.
 - Show flows for a node to specify.
 - Enable/Block flows.
	 - Enable/block all flows in the topology.
	 - Enable/block flows in a switch port.
	 - Enable switch ports in a path between two end hosts.

## Installation
### Set up environment
The application has been developed under Ubuntu 20.04 LTS, which includes python3, to be used alongside [OpenDaylight Lithium Release](https://www.opendaylight.org/what-we-do/current-release/lithium) SDN controller.

Since no method for the user to configure the URL for the REST API to use is provided, users should either configure a similar scenario in which the OpenFlow controller is available at "http://localhost:8181/" or directly modify the controller URL to use on the [rest_service.py](rest_service.py) file.

The following dependencies are required for the application to run.
 - lxml
	 - `sudo apt-get install python3-lxml`
 - libxml2
	 - 	 `sudo apt-get install python3-libxml2`
 - Dijkstar
	 1. `sudo apt install python3-pip`
	 2. `pip3 install Dijkstar`
 

### Clone repository
Clone this project to the machine running your controller, preferably to the habitual user home directory

    git clone https://github.com/LoisSotoLopez/odl-multicast.git