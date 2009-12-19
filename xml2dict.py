"""xml2dict: Convert bewteen xml file and python dict """

from oodict import OODict
import re

try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET # for 2.4

class XML2Dict:

    def __init__(self):
        pass

    def _parse_node(self, node):
        tree = OODict()
        # Save value
        value = node.text
        if isinstance(value, str):
            value = value.strip() # Only strip strings 
        tree.value = value
        # Save attributes
        for k,v in node.attrib.items():
            tree.update(self._make_dict(k, v))
        #Save childrens
        for child in node.getchildren():
            ctag = child.tag
            ctree = self._parse_node(child)
            cdict = self._make_dict(ctag, ctree)

            if ctag not in tree: # First time found
                tree.update(cdict)
                continue

            old = tree[ctag]
            if not isinstance(old, list):
                tree[ctag] = [old] # Multi entries, change to list       
            tree[ctag].append(ctree) # Add new entry

        return  tree

    def _make_dict(self, tag, value):
        """Generate a new dict with tag and value
        
        If tag is like '{http://cs.sfsu.edu/csc867/myscheduler}patients',
        split it first to: http://cs.sfsu.edu/csc867/myscheduler, patients
        """
        tmp = value
        result = re.compile("\{(.*)\}(.*)").search(tag)
        if result:
            tmp = OODict()
            tmp.xmlns, tag = result.groups() # We have a namespace!
            tmp.value = value
        return OODict({tag: tmp})

    def parse(self, file):
        """Parse xml file to dict"""
        f = open(file, 'r')
        return self.fromstring(f.read())

    def fromstring(self, s):
        """Parse xml string to dict"""
        tmp = ET.fromstring(s)
        return self._make_dict(tmp.tag, self._parse_node(tmp))

if __name__ == '__main__':
    s = """<?xml version="1.0" encoding="utf-8" ?>
    <result>
        <count n="1">10</count>
        <data><id>491691</id><name>test</name></data>
        <data><id>491692</id><name>test2</name></data>
        <data><id>503938</id><name>hello, world</name></data>
    </result>"""

    xml = XML2Dict()
    r = xml.fromstring(s)
    from pprint import pprint
    pprint(r)
    print r.result.count.value
    print r.result.count.n
    for data in r.result.data:
        print data.id, data.name

    ns = """<myscheduler:patients
    xmlns:myscheduler="http://cs.sfsu.edu/csc867/myscheduler"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://cs.sfsu.edu/csc867/myscheduler myscheduler.xsd">
    <myscheduler:user id="12444223" username="msales" password="utn29oad">
        <myscheduler:firstName>Marcello</myscheduler:firstName>
        <myscheduler:lastName>Sales</myscheduler:lastName>
        <myscheduler:email>msales@sfsu.edu</myscheduler:email>
    </myscheduler:user>
    </myscheduler:patients>
    """
    pprint(xml.fromstring(ns))
