# This python script is used to extract out the blocks and it's correponding connections,
# parameters and symbol attributes. Later than we could use all these to order the 
# connections and appropriate block parameters

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
        sender_block = block[1].split('.')[0]      # Considering only the 0th index of Tag
        receiver_block = block[0].split('.')[0]
         # Condition for avoiding current xml block (random one)
        if sender_block != current_tag or receiver_block != current_tag:
            if sender_block == receiver_block:     # from same family or block
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

            print(" {} ----------> {} \n".format(sender, receiver))

def grouping(traffic_data):
    ''' Function used to group the inner tags based on their block values '''
    mainblocks = []
    multi_block = {}    # contains both multi block and sub blocks
    if len(traffic_data) >0:
        for trf in traffic_data:
            receiver = trf[0]
            sender = trf[1]
            send_mainblock = sender.split('.')[0]
            rec_mainblock = receiver.split('.')[0]

            if not send_mainblock in multi_block:
                multi_block[send_mainblock] = []
                
            if not rec_mainblock in multi_block:
                multi_block[rec_mainblock] = []

        
        for trf in traffic_data:
            send_mainblock = trf[1].split('.')[0]
            rec_mainblock = trf[0].split('.')[0]

            rec_sec_block = trf[0].split('.')[1]
            send_sec_block = trf[1].split('.')[1]

            if send_mainblock == rec_mainblock: 
                if not rec_sec_block in multi_block[send_mainblock]:
                    multi_block[send_mainblock].append(rec_sec_block)

                if not send_sec_block in multi_block[send_mainblock]:
                    multi_block[send_mainblock].append(send_sec_block)
            else:
                if send_mainblock in multi_block:
                    if not send_sec_block in multi_block[send_mainblock]:
                        multi_block[send_mainblock].append(send_sec_block)

                if rec_mainblock in multi_block:
                    if not rec_sec_block in multi_block[rec_mainblock]:
                        multi_block[rec_mainblock].append(rec_sec_block)

    return multi_block


def block_separator(master_dict, current_tag):
    ''' Function used to separate the current tag (xml file) from other foreign tags'''
    inhouse_blocks = []
    foreign_blocks = []
    list_dict = list(master_dict.keys())

    if len(list_dict) >0:
        for key in list_dict:
            if current_tag == key:
                inhouse_blocks.append(key)
            else:
                foreign_blocks.append(key)

    return inhouse_blocks, foreign_blocks

def master_and_foreign(traffic_data, block_dict, inhouse, foreign):
    ''' This function used to describe the connections of inhouse main and foreign blocks'''

    print("************   Link Explanation starts here  ***************")

    master_stat = "{} is the master/main connection holder for all connections. \
Moreover it has been linked with following blocks{}\n"

    foreign_link_stat = "{} is a foreign block and connectd with {}\n"
    global master_node
    # Below line is only for the master connections or in house connections
    if len(inhouse) >0:
        for mstr in inhouse:
            mstr_conns = block_dict[mstr]
            master_node = mstr
            if len(mstr_conns) >0:
                print(master_stat.format(mstr, mstr_conns))

    # Below line is just to explain the overview of the available foreign blocks
    # Also the overview of foreign block's relation with master block (i/p end or o/p end)
    if len(foreign) >0:
        for fgn in foreign:
            fgn_conns = block_dict[fgn]
            if len(fgn_conns) >0:
                print(foreign_link_stat.format(fgn, fgn_conns))

            for tf in traffic_data:
                # Target:  foreign connection with master node 
                # Finding what relation between master and foreign nodes
                if tf[1].startswith(fgn) and tf[0].split('.')[0] == master_node:
                    print("foreign block {} is passing input to Master Node in {} block \n".format(fgn, tf[0].split('.')[1]))

                elif tf[0].startswith(fgn) and tf[1].split('.')[0] == master_node:
                    print("foreign block {} is receiving input from Master Node in {} block \n".format(fgn, tf[1].split('.')[1]))
                
    
    if master_node:
        # Only Trust: Connections are in sequential manner in xml file so we can proceed the same(no sort)
        mstr_conns = block_dict[master_node]
        if len(mstr_conns) >0:
            for conn_block in mstr_conns:
                print("\n")
                print("***   {} Block section ***".format(conn_block))
                print("\n")
                for tf in traffic_data:
                    # Target: Finding inner block routemap
                    # Condition: either one of the block consists this conn_block or both sometimes
                    if tf[0].split('.')[1] == conn_block:  # Receiver
                        abbr_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                        send_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                        if tf[1].split('.')[0] == master_node:
                            print("Block {} is receiving the input from {} (Master)".format(abbr_block, send_block))
                        else:
                            print("Block {} is receiving the input from {} (Foreign {})".format(abbr_block, send_block, tf[1].split('.')[0]))

                    elif tf[1].split('.')[1] == conn_block:  # Sender
                        abbr_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                        rec_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                        if tf[0].split('.')[0] == master_node:
                            print("Block {} is sending the input to {} (Master)".format(abbr_block, rec_block))
                        else:
                            print("Block {} is sending the input to {} (Foreign {})".format(abbr_block, rec_block, tf[0].split('.')[0]))


# xml_path = "./single_file/250DIC4545.cnf.xml"
random_xml_tag = "250DIC4545"
xml_path = "./single_file"
files = os.listdir(xml_path)
random_filename = random_xml_tag + ".cnf.xml"
# Scenario consideration: maximum number of adjacency per tag would be 2 (might go beyond this level)
xml_thresh = 3      #Actually it's 3 but default one goes to random_tag

total_links = {}
if random_filename in files:
    random_filepath = os.path.join(xml_path, random_filename)

    file_loc = pathlib.Path(random_filepath)
    filename = file_loc.name    # returns the filename with extenstion frm the whole path
    
    # Getting the whole connections for the single xml file (i.e single block)
    traffic_consolidation = extract_inout(random_filepath)
    
    block_dict = grouping(traffic_consolidation)

    print("Block list", block_dict)

    # Separating the foreign block and current (random) block from the block_dict's key

    inhouse, foreign = block_separator(block_dict, random_xml_tag)

    # print("inhouse", inhouse)
    # print("foreign", foreign)

    master_and_foreign(traffic_consolidation, block_dict, inhouse, foreign)

    exit()

## Inside the traffic_consolidation list you can find the set of links only corresponding to the user given tag
## Inside the total_links dictionary you can find the self connections of foreign blocks associated with user given tag

''' Below lines are just to display the output (you might get reference error incase if the data type is empty) '''
print("Connections of the {}".format(random_xml_tag))
display_out(traffic_consolidation)
            

        
        