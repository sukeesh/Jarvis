"""
Module containing utility functions for generating XML strings
"""

import xml.etree.ElementTree as ET


def create_DOM_node_from_dict(d, name, parent_node):
    """
    Dumps dict data to an ``xml.etree.ElementTree.SubElement`` DOM subtree
    object and attaches it to the specified DOM parent node. The created
    subtree object is named after the specified name. If the supplied dict is
    ``None`` no DOM node is created for it as well as no DOM subnodes are
    generated  for eventual ``None`` values found inside the dict

    :param d: the input dictionary
    :type d: dict
    :param name: the name for the DOM subtree to be created
    :type name: str
    :param parent_node: the parent DOM node the newly created subtree must be
        attached to
    :type parent_node: ``xml.etree.ElementTree.Element`` or derivative objects
    :returns: ``xml.etree.ElementTree.SubElementTree`` object

    """
    if d is not None:
        root_dict_node = ET.SubElement(parent_node, name)
        for key, value in d.items():
            if value is not None:
                node = ET.SubElement(root_dict_node, key)
                node.text = str(value)
        return root_dict_node


def DOM_node_to_XML(tree, xml_declaration=True):
    """
    Prints a DOM tree to its Unicode representation.

    :param tree: the input DOM tree
    :type tree: an ``xml.etree.ElementTree.Element`` object
    :param xml_declaration: if ``True`` (default) prints a leading XML
        declaration line
    :type xml_declaration: bool
    :returns: Unicode object

    """
    result = ET.tostring(tree, encoding='utf8', method='xml').decode('utf-8')
    if not xml_declaration:
        result = result.split("<?xml version='1.0' encoding='utf8'?>\n")[1]
    return result


def annotate_with_XMLNS(tree, prefix, URI):
    """
    Annotates the provided DOM tree with XMLNS attributes and adds XMLNS
    prefixes to the tags of the tree nodes.

    :param tree: the input DOM tree
    :type tree: an ``xml.etree.ElementTree.ElementTree`` or
        ``xml.etree.ElementTree.Element`` object
    :param prefix: XMLNS prefix for tree nodes' tags
    :type prefix: str
    :param URI: the URI for the XMLNS definition file
    :type URI: str

    """
    if not ET.iselement(tree):
        tree = tree.getroot()
    tree.attrib['xmlns:' + prefix] = URI
    iterator = tree.iter()
    next(iterator)  # Don't add XMLNS prefix to the root node
    for e in iterator:
        e.tag = prefix + ":" + e.tag
