import xml.etree.ElementTree as ET
import json
import os


# --------- Helper: Remove namespace ---------
def strip_ns(tag):
    return tag.split("}")[-1]


# --------- Extract text safely ---------
def get_text(element, tag_name):
    for child in element:
        if strip_ns(child.tag) == tag_name:
            return child.text
    return None


# --------- Parse Parameters ---------
def parse_parameters(block):
    params = []

    for elem in block.iter():
        if strip_ns(elem.tag) == "Parameter":
            param = {}
            for child in elem:
                param[strip_ns(child.tag)] = child.text
            params.append(param)

    return params


# --------- Parse SymbolAttr ---------
def parse_symbol_attrs(block):
    attrs = []

    for elem in block.iter():
        if strip_ns(elem.tag) == "SymbolAttr":
            attr = {}
            for child in elem:
                attr[strip_ns(child.tag)] = child.text
            attrs.append(attr)

    return attrs


# --------- Parse Connections ---------
def parse_connections(block):
    conns = []

    for elem in block.iter():
        if strip_ns(elem.tag) == "Connection":
            conn = {}
            for child in elem:
                conn[strip_ns(child.tag)] = child.text
            conns.append(conn)

    return conns


# --------- Parse Block (Recursive) ---------
def parse_block(block, parent_path=""):
    data = {}

    # Get BlockName
    block_name = None
    for elem in block.iter():
        if strip_ns(elem.tag) == "BlockName":
            block_name = elem.text
            break

    # Full hierarchical path
    full_path = f"{parent_path}.{block_name}" if parent_path else block_name

    data["blockName"] = block_name
    data["fullPath"] = full_path

    # Extract elements
    data["parameters"] = parse_parameters(block)
    data["symbolAttrs"] = parse_symbol_attrs(block)
    data["connections"] = parse_connections(block)

    # Parse Embedded Blocks
    embedded_blocks = []

    for child in block:
        if strip_ns(child.tag) == "EmbBlocks":
            for sub in child:
                if strip_ns(sub.tag) == "Block":
                    embedded_blocks.append(parse_block(sub, full_path))

    data["embeddedBlocks"] = embedded_blocks

    return data


# --------- MAIN EXECUTION ---------
def main():
    xml_file = "single_file/new/250LIC4032.cnf.xml"  # change your file name

    if os.path.exists(xml_file):
        print("file exisits")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    result = parse_block(root)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()




# Note: currently the above script can exract (Blockdef, Paramters, Symbolattrs) of Main block
# Let's devide the program into two sections, first let the program to look for only main bloc (Block)
# secondly let the program to find the components (Blockdef, param, symattrs) of EmbBlocks

