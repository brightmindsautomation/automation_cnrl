# This script will exract out all the available connection inside the xml file 
# This will be for a deeper analysis of single xml than handling larger one
import os
import xml.etree.ElementTree as ET
import pandas as pd
import pathlib

def extract_inout(filepath):
    if not os.path.exists(filepath):
        print(f"File not found")
        return
    ind_xml_resp = []
    tree = ET.parse(filepath)
    root = tree.getroot()

    inputs, outputs = [], []    # storing both tags in diff lists

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

    return ind_xml_resp

def find_foreign(cons_tags, current_tag):
    '''This function will separate the foreign tags from the cons tags WRT current tag'''
    tag_unique = set()
    for block in cons_tags:
        sender_block = block[1].split('.')[0]
        receiver_block = block[0].split('.')[0]
         # Condition for avoiding current xml block (random one)
        if sender_block != current_tag or receiver_block != current_tag:
            if sender_block == receiver_block:
                tag_unique.add(sender_block)
            else:
                tag_unique.add(sender_block)
                tag_unique.add(receiver_block)

    return tag_unique

def display_out(list_data):
    if len(list_data) >0:
        for trf in list_data:
            receiver = trf[0]
            sender = trf[1]

            print(" {} is receiving the input from {}".format(receiver, sender))
    
# xml_path = "./single_file/250DIC4545.cnf.xml"
random_xml_tag = "250FIC4521"
xml_path = "./xml_files"
files = os.listdir(xml_path)
random_filename = random_xml_tag + ".cnf.xml"
# Scenario consideration: maximum number of adjacency per tag would be 2 (might go beyond this level)
xml_thresh = 2      #Actually it's 3 but default one goes to random_tag

total_links = {}
if random_filename in files:
    random_filepath = os.path.join(xml_path, random_filename)

    file_loc = pathlib.Path(random_filepath)
    filename = file_loc.name    # returns the filename with extenstion frm the whole path
    
    # Getting the whole connections for the single xml file (i.e single block)
    traffic_consolidation = extract_inout(random_filepath) 

    if len(traffic_consolidation) >0:
        foreign_blocks = find_foreign(traffic_consolidation, random_xml_tag)
        foreign_blocks = list(foreign_blocks)
        if len(foreign_blocks) >0:
            if random_xml_tag in foreign_blocks:
                foreign_blocks.remove(random_xml_tag)

            # Now will explore the links of those foreign blocks
            if len(foreign_blocks) >0:
                for i, neighbor_tag in enumerate(foreign_blocks):
                    if i > xml_thresh:
                        break
                    neighbor_tag_filename = neighbor_tag + ".cnf.xml"
                    if neighbor_tag_filename in files: # sometimes tag might not be present in files location
                        tag_path = os.path.join(xml_path, neighbor_tag_filename)
                        linking_tags = extract_inout(tag_path)
                        if linking_tags:
                            total_links[neighbor_tag] = linking_tags

## Inside the traffic_consolidation list you can find the set of links only corresponding to the user given tag
## Inside the total_links dictionary you can find the self connections of foreign blocks associated with user given tag


''' Below lines are just to display the output (you might get reference error incase if the data type is empty) '''
print("Connections of the {}".format(random_xml_tag))
display_out(traffic_consolidation)


if len(total_links):
    for tag in foreign_blocks:
        if tag in total_links:
            print("\n")
            print("Connections of the {}".format(tag))
            display_out(total_links[tag])
            

        
        