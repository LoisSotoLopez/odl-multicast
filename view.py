from lxml import etree
import libxml2

def _print_tree(tree,n):
	text = " " if tree.text == None else "_"*(50 - len(tree.tag) - n) + tree.text
	print(" "*n + tree.tag + text)
	for elem in tree:
		_print_tree(elem,n+1)


# Converts controller xml to legible text 
def _to_pretty_text(xml):
	if xml != '':
		tree = etree.fromstring(xml)
		for t in tree:
			_print_tree(t,0)
			print()
		
def show_info(xml,mode):
	if mode == "bad":
		print("An error ocurred")
	else:
		print("Worked!")
	_to_pretty_text(xml)



