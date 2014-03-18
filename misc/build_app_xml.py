"""
Copyright Jeffrey Meyers @ 2014
meyersj@trimet.org
created 3/17/18

1.
    reads in route name, route codes, direction and direction name
    from csv
2.
    builds xml for string-array resources for use in
    drop down selection for onandoff app
3.
    builds space delimited list of identifier for route/route direction
    along with code to access that row in database
"""

import csv, re
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring


rtes = []
dirs = []
dirs_dict = {}

with open("routes.csv", 'r') as routes:
    r = csv.reader(routes)
    for route in r:
        rtes.append((route[0], route[2]))
        dirs.append((route[0], route[1], route[3]))
        
        if route[0] not in dirs_dict:
            dirs_dict[route[0]] = {}
        
        dirs_dict[route[0]][route[1]] = route[3]

rtes = sorted(list(set(rtes)), key=lambda x: int(x[0]))

root = Element('resources')
spinner = SubElement(root, "string-array")
spinner.set("name","lines")

for r, n in rtes:
    item = SubElement(spinner, "item")
    item.text = n
    dir_spinner = SubElement(root, "string-array")
    dir_spinner.set("name", re.sub("[^A-Za-z]", "", n))
    zero = SubElement(dir_spinner, "item")
    zero.text = dirs_dict[r]["0"]
    one = SubElement(dir_spinner, "item")
    one.text = dirs_dict[r]["1"]

ElementTree(root).write("routes.xml", xml_declaration=True, encoding="utf-8", method="xml")

with open("line_ids.txt", 'w') as ids:
    line = "{0} {1}\n"
    for r, n in rtes:
        ids.write(line.format(re.sub("[^A-Za-z]", "", n),r)) 
    for r, d, n in dirs:
        ids.write(line.format(re.sub("[^A-Za-z]", "", n)+r,d)) 

     
