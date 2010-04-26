"""Transform dict to xml dom object

values in 'attrs' are saved as attributes of node

"""
from xml.dom.minidom import getDOMImplementation

impl = getDOMImplementation()

def process(doc, tag, v):
    """Generate dom object for tag:v

    Return node or nodelist     # Becarefull here
    """
    if isinstance(v, dict) and v.keys() == ['value']:
        v = v['value']

    # Create a new node for simple values
    if isinstance(v, int) or isinstance(v, str):
        return process_simple(doc, tag, v)

    # Return a list of nodes with same tag
    if isinstance(v, list): 
        # Only care nodelist for list type, drop attrs
        return process_complex(doc, [(tag, x) for x in v])[0]

    # Create a new node, and insert all subnodes in dict to it
    if isinstance(v, dict):
        node = doc.createElement(tag) 
        nodelist, attrs = process_complex(doc, v.items())
        for child in nodelist:
            node.appendChild(child) 
        for attr in attrs:
            node.setAttributeNode(attr)
        return node

def process_complex(doc, children):
    """Generate multi nodes for list, dict
        @children    tuple of (tag, value)

    Return nodelist
    """
    nodelist = []
    attrs = []
    for tag, v in children:
        # If tag is attrs, all the nodes should be added to attrs
        # FIXME:Assume all values in attrs are simple values.
        if tag == 'attrs':
            for attr_name, attr_value in v.items():
                attr = doc.createAttribute(attr_name)
                attr.nodeValue = attr_value
                #attr.appendChild(doc.createTextNode(str(attr_value)))
                attrs.append(attr)
            continue

        nodes = process(doc, tag, v)
        if not isinstance(nodes, list):
            nodes = [nodes]
        nodelist += nodes
    return nodelist, attrs

def process_simple(doc, tag, v):
    """For int, str
    Return node
    """
    node = doc.createElement(tag) 
    node.appendChild(doc.createTextNode(str(v)))
    return node

def dict2xml(d):
    """Generate a xml string from dict"""
    doc = impl.createDocument(None, None, None)
    if len(d) > 1:
        print 'Only one root node allowed'
        return None
    root, _ = process_complex(doc, d.items())
    doc.appendChild(root[0])
    return doc.toprettyxml(encoding = 'utf-8', indent = '  ')

if __name__ == '__main__':
    import xml2dict
    x = xml2dict.XML2Dict()
    d = x.parse('t5')
    print d
    print dict2xml(d)

