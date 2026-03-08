# This python script is used to extract out the blocks and it's correponding connections,
# parameters and symbol attributes. Later than we could use all these to order the 
# connections and appropriate block parameters
# Latest one

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

            if send_mainblock == rec_mainblock:     # both send and receiving blocks are same
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



def master_only(traffic_data, block_dict, inhouse, MasterNode):
    ''' This function used to describe the connections of inhouse main and no foreign blocks'''

    print("************   Link Explanation starts here (Master only)  ***************")

    master_stat = "{} is the master/main connection holder for all connections. \
    Moreover it has been linked with following blocks{}\n"

    global master_node
    # Below line is only for the master connections or in house connections
    if len(inhouse) >0:
        for mstr in inhouse:
            mstr_conns = block_dict[mstr]
            master_node = mstr
            if len(mstr_conns) >0:
                print(master_stat.format(mstr, mstr_conns))

    #. *******************. Finding Start and End Blocks  ********************

     # Note: When the xml file has only master connection and there is no foreign connection
     # then we can't find which one is start block (so we can take a whole block and process it)

    #. **************** Printing as per structure using ordered blocks ********

    # print("Ordered Blocks Final", mstr_conns)

    for conn_block in mstr_conns:
        print("\n")
        print("***   {} Block section ***".format(conn_block))
        print("\n")
        for tf in traffic_data:
            # Target: Finding inner block routemap
            # Condition: either one of the block consists this conn_block or both sometimes
            if tf[1].split('.')[1] == conn_block and tf[1].split('.')[0] == MasterNode:  # Sender
                abbr_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                rec_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                if tf[0].split('.')[0] == master_node:
                    print("Block {} is sending the input to {} (Master)".format(abbr_block, rec_block))
                else:
                    print("Block {} is sending the input to {} (Foreign {})".format(abbr_block, rec_block, tf[0].split('.')[0]))

            elif tf[0].split('.')[1] == conn_block and tf[0].split('.')[0] == MasterNode:  # Receiver
                abbr_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                send_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                if tf[1].split('.')[0] == master_node:
                    print("Block {} is receiving the input from {} (Master)".format(abbr_block, send_block))
                else:
                    print("Block {} is receiving the input from {} (Foreign {})".format(abbr_block, send_block, tf[1].split('.')[0]))





def master_and_foreign(traffic_data, block_dict, inhouse, foreign, MasterNode):
    ''' This function used to describe the connections of inhouse main and foreign blocks'''

    print("************   Link Explanation starts here (Master and Foreign)  ***************")

    master_stat = "{} is the master/main connection holder for all connections. \
Moreover it has been linked with following blocks{}\n"

    foreign_link_stat = "{} is a foreign block and connectd with {}\n"
    secondary_blocks = []
    global master_node
    # Below line is only for the master connections or in house connections
    if len(inhouse) >0:
        for mstr in inhouse:
            mstr_conns = block_dict[mstr]
            master_node = mstr
            if len(mstr_conns) >0:
                secondary_blocks.extend(mstr_conns)        # Extension of the list
                print(master_stat.format(mstr, mstr_conns))
    if len(foreign) >0: # Need to consider the foreign sub blocks too (Not just master block)
        for fgn in foreign:
            fgn_cns = block_dict[fgn]
            mstr_conns.extend(fgn_cns)

    # Below line is just to explain the overview of the available foreign blocks
    # Also the overview of foreign block's relation with master block (i/p end or o/p end)
    if len(foreign) >0:
        for fgn in foreign:
            fgn_conns = block_dict[fgn]
            if len(fgn_conns) >0:
                secondary_blocks.extend(fgn_conns)    # Extension of the list
                print(foreign_link_stat.format(fgn, fgn_conns))
    
    secondary_blocks = list(set(secondary_blocks))     # Ensuring no duplicates


    ordered_blocks = []
    global foreign_node_visit 
    foreign_node_visit = False

    #. *******************. Finding Start and End Blocks  ********************

    # Target: Picking up the start point connection (at first it will be foreign block)
    # Condition: if node has one way connection --> start, node has more than two way connection --> middle
    FgnLinkedBlocks = []

    for fgn in foreign:
        fgn_conns = block_dict[fgn]
        if len(fgn_conns) >0:   # find which one has minimal connections of it's next conn
            for fgn in fgn_conns:
                # Daca - 2 out 1 in
                # Suba - 1 out 2 in
                # find the immediate connection of those foreign blocks and ensure the in/out of them
                for tf in traffic_data:
                    # Target: Finding the connections that matches the fgn (block)
                    if tf[0].split('.')[1] == fgn:    # Receiver block
                        sender = tf[1].split('.')[1]
                        FgnLinkedBlocks.append(sender)

                    elif tf[1].split('.')[1] == fgn:    # Sender block
                        receiver = tf[0].split('.')[1]
                        FgnLinkedBlocks.append(receiver)

    FgnLinkedBlocks = list(set(FgnLinkedBlocks))
    print("Foreign linked blocks", FgnLinkedBlocks)

    if len(FgnLinkedBlocks) >0:
        #Target: If the only i/p connection is determined by FGN block then it's our first path
        for FgnLink in FgnLinkedBlocks:
            # Pick when there is only foreign input no other block input
            FgnIp = 0
            for tf in traffic_data:
                if tf[0].split('.')[1] == FgnLink:
                    if tf[1].split('.')[0] != master_node:
                        FgnIp +=1
                    # else:
                    #     print("Cond passed else", tf[1].split('.')[0], FgnLink)
                    #     FamIP +=1
        
            # print("Foreign I/P and Family I/P of {}".format(FgnLink), FgnIp, FamIP)
            if FgnIp >0:
                ordered_blocks.append(FgnLink)

    # *****************. Ordering the blocks ********** #
    # Target: now we have the starting block with this we can iterate through the network

    def ordering(StartBlock, ordered_blocks, traffic_data):
        # Target: with the help of Start Block (DACA) we can proceed next consecutive blocks
        # by doing the recursive iteration.
        visited_blocks = set()
        TempQueue = [StartBlock]

        while TempQueue:
            # print("Temp Queue", TempQueue)
            # print("Visited blocks", visited_blocks)
            # print("ordered blocks", ordered_blocks)
            current = TempQueue.pop(0)     # this will help us to control the flow logic
            if current in visited_blocks:
                continue
            visited_blocks.add(current)
            # print("Current Ride", current)

            for tf in traffic_data:   # Concentrate on passing to whom
                # print("(dst, src)", (tf[0].split('.')[1], tf[1].split('.')[1]))
                # print(tf[1].split('.')[1], "->", tf[0].split('.')[1])
                
                if ((tf[1].split('.')[1] == current)) and tf[0].split('.')[1] != tf[1].split('.')[1]: # only it's not loop
                    NextBlock = tf[0].split('.')[1]
                    if NextBlock not in ordered_blocks:    # ensure it's not existed prev.
                        ordered_blocks.append(NextBlock)
                    TempQueue.append(NextBlock)
                # Problem: when PIDA enters it went into loop and the program keep taking 
                # PIDA as a startBlock (Need to change StartBlock when this condition occurs)


    if len(ordered_blocks) >0:
        StartBlock = ordered_blocks[0]
        ordering(StartBlock, ordered_blocks, traffic_data)

    #. ****************. End of the ordering functio **************** #

    OrderBlockSet = set(ordered_blocks)
    MstrBlockSet = set(mstr_conns)
    Missed = MstrBlockSet.difference(OrderBlockSet)
    # if len(Missed) >0:
    #     for miss in Missed:
    #         ordered_blocks.append(miss)


    # Note: Always direction from left to right is possible, where as (Always sender)
    # Not always direction from right to left is possible (There might not be a receiver)

    # $$$$$$$$$ New Implementation for missing blocks insertion at index pos $$$$

    if len(Missed) >0:
        visited_blocks = set()
        TempQueue = list(Missed)
    
        while TempQueue:
            current = TempQueue.pop(0)     # this will help us to control the flow logic
            if current in visited_blocks:
                continue
            visited_blocks.add(current)
            
            for tf in traffic_data:
                if tf[1].split('.')[1] == current:
                    rec = tf[0].split('.')[1]
                    if rec in ordered_blocks:
                        # print("Rec presents", rec)
                        idx = ordered_blocks.index(rec)
                        if idx == 0:
                            ordered_blocks.insert(idx, current)
                        else:
                            ordered_blocks.insert(idx, current)
                    else:
                        TempQueue.append(current)

     # $$$$$$$$$ New Implementation for missing blocks insertion at index pos $$$$

    #. **************** Printing as per structure using ordered blocks ********

    print("Ordered Blocks", ordered_blocks)

    for conn_block in ordered_blocks:
        print("\n")
        print("***   {} Block section ***".format(conn_block))
        print("\n")
        for tf in traffic_data:
            # Target: Finding inner block routemap
            # Condition: either one of the block consists this conn_block or both sometimes
            if tf[1].split('.')[1] == conn_block and tf[1].split('.')[0] == MasterNode:  # Sender
                abbr_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                rec_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                if tf[0].split('.')[0] == master_node:
                    print("Block {} is sending the input to {} (Master)".format(abbr_block, rec_block))
                    # print("'{}' --> '{}'".format(tf[1], tf[0]))
                else:
                    print("Block {} is sending the input to {} (Foreign {})".format(abbr_block, rec_block, tf[0].split('.')[0]))
                    # print("'{}' --> '{}'".format(tf[1], tf[0]))
            elif tf[0].split('.')[1] == conn_block and tf[0].split('.')[0] == MasterNode:  # Receiver
                abbr_block = tf[0].split('.')[1] + '.' + tf[0].split('.')[2]
                send_block = tf[1].split('.')[1] + '.' + tf[1].split('.')[2]
                if tf[1].split('.')[0] == master_node:
                    print("Block {} is receiving the input from {} (Master)".format(abbr_block, send_block))
                    # print("'{}' --> '{}'".format(tf[0], tf[1]))
                else:
                    print("Block {} is receiving the input from {} (Foreign {})".format(abbr_block, send_block, tf[1].split('.')[0]))
                    # print("'{}' --> '{}'".format(tf[0], tf[1]))



def order_init(MasterXmlBlock, BasePath):
    ''' Function receives input xml block and find it's ordering pattern inside the xml file '''
    try:
        files = os.listdir(BasePath)
        target_filename = MasterXmlBlock + ".cnf.xml"


        if target_filename in files:
            random_filepath = os.path.join(BasePath, target_filename)

            file_loc = pathlib.Path(random_filepath)
            filename = file_loc.name    # returns the filename with extenstion frm the whole path
            
            # Getting the whole connections for the single xml file (i.e single block)
            traffic_consolidation = extract_inout(random_filepath)

            # Uncomment to view the block connections
            # display_out(traffic_consolidation)
            
            block_dict = grouping(traffic_consolidation)
            # Separating the foreign block and current (random) block from the block_dict's key

            inhouse, foreign = block_separator(block_dict, MasterXmlBlock)

            # print("inhouse", inhouse)
            # print("foreign", foreign)
            if len(inhouse) >0 and len(foreign) >0:
                master_and_foreign(traffic_consolidation, block_dict, inhouse, foreign, MasterXmlBlock)
            elif len(foreign) == 0: # incase if there is no foreign connections (xml itself)
                master_only(traffic_consolidation, block_dict, inhouse, MasterXmlBlock)

    except Exception as e:
        print("Error Occured while calling Order Init function @block_ordering", e)

# order_init("250MHS4497", "./single_file/new2")


## Inside the traffic_consolidation list you can find the set of links only corresponding to the user given tag
## Inside the total_links dictionary you can find the self connections of foreign blocks associated with user given tag