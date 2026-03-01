'''
This script will read the list of given xml files, then create adjacency matrix for those master blocks.
Master Blocks - main block of the individual xml file.

'''
import os
import xml.etree.ElementTree as ET
import pandas as pd


def extract_inout(source, xmls):
    # xml_file = f"{tag}.cnf.xml"
    consolidated_resp = []
    MasterBlocks = set()
    for xml_file in xmls:
        ind_xml_resp = []
        xml_tag = xml_file.split(".cnf.xml")[0]
        MasterBlocks.add(xml_tag)
        filepath = os.path.join(source, xml_file)

        if not os.path.exists(filepath):
            print(f"File not found: {xml_file}")
            return

        tree = ET.parse(filepath)
        root = tree.getroot()

        inputs, outputs = [], []

        for elem in root.iter():
            tagname = elem.tag.split("}")[-1]  # remove namespace if any
            if tagname == "InputEnd" and elem.text:
                inputs.append(elem.text.strip())
            elif tagname == "OutputEnd" and elem.text:
                outputs.append(elem.text.strip())

        # print(f"\nExtracting <InputEnd> and <OutputEnd> for {xml_tag}:")
        for i, inp in enumerate(inputs):
            ind_xml_resp.append((inp, outputs[i]))
            # print(f"{inp} --> {outputs[i]}")

        consolidated_resp.append(ind_xml_resp)

    return consolidated_resp, list(MasterBlocks)


def separate_prime_tags(tag_list, Masters):
    ''' Function used to take the primary tag value from the given set of long tag value (Acutal one without stripe)'''
    prime_tags_cons = set()
    NodeLoc = set()
    if tag_list:
        for inner_tag in tag_list:
            if len(inner_tag) >0:
                for tg in inner_tag:
                    ip_tag = tg[0].split('.')[0]
                    op_tag = tg[1].split('.')[0]
                    if ip_tag != op_tag:         # Avoiding self loops
                        if ip_tag in Masters and op_tag in Masters:
                            prime_tags_cons.add((op_tag, ip_tag)) # Direction alignment here
                            NodeLoc.add(op_tag)
                            NodeLoc.add(ip_tag)

    return list(prime_tags_cons), list(NodeLoc)




if __name__ == "__main__":
    folder = "./single_file/new"   # change this
    files = os.listdir(folder)
    xml_ext_files = []
    for file in files:
        if str(file).endswith('.cnf.xml'):
            xml_ext_files.append(file)

    # extracting all input and output tags from xml files (individually)
    # consolidated_tags -> which has all inbound/outbound connections for all xml's

    consolidated_tags, MasterBlocks = extract_inout(folder, xml_ext_files)

    Edges, Nodes = separate_prime_tags(consolidated_tags, MasterBlocks)

    # Initialize a square matrix of zeros later you can update with nodes and edges(2D matrix)
    adj_matrix = pd.DataFrame(0, index=Nodes, columns=Nodes)  # Unique tags --> Nodes/vertices

    # Directed graph ()
    for u, v in Edges:
        adj_matrix.loc[u, v] = 1     # direction u -> v
        adj_matrix.loc[v, u] = -1    # reverse direction v -> u

    print("Adjacency Matrix (Note: Self loop avoided) \n", adj_matrix)