'''
This script used to extract out the possible (parameters, symbolattrs and connection) details from
the xml file passed. Resultant value will be json dict type, where we can find the entire details according
to the block wise sections.
'''

import xml.etree.ElementTree as ET
import json
import os


# --------- Helper: Remove namespace ---------
def strip_ns(tag):
    return tag.split("}")[-1]


# --------- Extract Parameters ---------
def extract_params(node):
    params = []
    for p in node:
        if strip_ns(p.tag) == "Parameter":
            param = {}
            for c in p:
                param[strip_ns(c.tag)] = c.text
            params.append(param)
    return params


# --------- Extract SymbolAttrs ---------
def extract_attrs(node):
    attrs = []
    for a in node:
        if strip_ns(a.tag) == "SymbolAttr":
            attr = {}
            for c in a:
                attr[strip_ns(c.tag)] = c.text
            attrs.append(attr)
    return attrs


# --------- Extract Connections ---------
def extract_connections(node):
    conns = []
    for c in node:
        if strip_ns(c.tag) == "Connection":
            conn = {}
            for x in c:
                conn[strip_ns(x.tag)] = x.text
            conns.append(conn)
    return conns


# --------- Parse Block (Recursive) ---------
def parse_block(block, parent_path=""):
    data = {
        "blockName": None,
        "fullPath": None,
        "parameters": [],
        "symbolAttrs": [],
        "connections": [],
        "embeddedBlocks": []
    }

    # --------- Extract BlockName safely ---------
    for elem in block.iter():
        if strip_ns(elem.tag) == "BlockName":
            data["blockName"] = elem.text
            break

    full_path = f"{parent_path}.{data['blockName']}" if parent_path else data["blockName"]
    data["fullPath"] = full_path

    # --------- Iterate direct children only ---------
    for child in block:
        tag = strip_ns(child.tag)

        if tag == "Parameters":
            data["parameters"] = extract_params(child)

        elif tag == "SymbolAttrs":
            data["symbolAttrs"] = extract_attrs(child)

        elif tag == "Connections":
            data["connections"] = extract_connections(child)

        elif tag == "EmbBlocks":
            for sub in child:
                if strip_ns(sub.tag) == "Block":
                    data["embeddedBlocks"].append(parse_block(sub, full_path))

    return data


# --------- MAIN EXECUTION ---------
def main():
    xml_file = "single_file/new/250LIC4032.cnf.xml"

    if not os.path.exists(xml_file):
        print("File not found")
        return

    print("File exists")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    if strip_ns(root.tag) != "Block":
        # find first Block
        for elem in root.iter():
            if strip_ns(elem.tag) == "Block":
                root = elem
                break

    result = parse_block(root)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()