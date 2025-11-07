# This script will analyse the larger volume of xml files in order to extract out the
# links and relationship between them. (we are using adjacency matrix concept to 
# get the relations between xml files (tags))

import os
import xml.etree.ElementTree as ET
import pandas as pd

exceptionals = ["OUT.VALUE", "PV.VALUE"]

def extract_inout(source, xmls):
    # xml_file = f"{tag}.cnf.xml"
    consolidated_resp = []
    for xml_file in xmls:
        ind_xml_resp = []
        xml_tag = xml_file.split(".cnf.xml")[0]
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

    return consolidated_resp

def tag_separator(consol_tags):
    necessary_tags = []
    for ind_tags in consol_tags:
        inner_tags = []
        if len(ind_tags) >0:
            for inout in ind_tags:
                input_actual = inout[0]
                input_tag = inout[0].split('.')[0]
                output_tag = inout[1]
                result = any(exc in output_tag for exc in exceptionals)
                output_tag_final = output_tag.split('.')[0] # Usual version
                ''' Below one is for advance version '''
                if result:  # only for these tags we have to check second dot split item
                    output_tag_final = output_tag.split('.')[1] # Present in first index (search tag)

                if input_tag != output_tag_final: # Wanna extract out those who are not same
                    # print("receptor and producer {} --> {} ".format(input_tag, output_tag)) 
                    inner_tags.append((input_actual, output_tag))
            necessary_tags.append(inner_tags)

    return necessary_tags
                # if result:
                #     print("Results", input_tag, output_tag)


def tag_search(tag_list, key_tag):
    ''' find the key_tag from tag_list (among inout tags) '''
    ''' from this function onwards am not following the xml file for each element in list'''
    search_match_tags = []
    for tag_ind in tag_list: # iterating through all xml_tags
        if len(tag_ind) >0:
            for inout in tag_ind:
                ip_tag_actual = inout[0]
                op_tag = inout[1]
                if key_tag in ip_tag_actual or key_tag in op_tag:
                    # print("Tags Match", ip_tag_actual, op_tag)
                    search_match_tags.append((ip_tag_actual, op_tag))

    return search_match_tags


def tag_navigator(matching_tags, key_tag):
    ''' If the key_tag present in 0th index --> input receptor || 1st index --> output producer '''
    backward_navigation = []
    forward_navigation = []
    for match in matched_tags:
        if len(match) >0:
            ip_tag = match[0]
            op_tag = match[1]
            if key_tag in ip_tag:
                backward_navigation.append(match)

            if key_tag in op_tag:
                forward_navigation.append(match)

    return backward_navigation, forward_navigation


def pipeline_maker(backward, forward):

    for back_tag in backward:
        ip_tag = back_tag[0]
        op_tag = back_tag[1]
        print("Input is passing from {} ---> to {}".format(op_tag, ip_tag)) # in this case ip_tag will be a key tag

    for for_tag in forward:
        ip_tag = for_tag[0]
        op_tag = for_tag[1]
        print("Input is going from {} ---> to {}".format(op_tag, ip_tag)) 


def separate_prime_tags(tag_list):
    ''' Function used to take the primary tag value from the given set of long tag value (Acutal one without stripe)'''
    prime_tags_cons =[]
    if tag_list:
        for inner_tag in tag_list:
            if len(inner_tag) >0:
                for tg in inner_tag:
                    ip_tag = tg[0].split('.')[0]
                    op_tag = tg[1].split('.')[0]
                    if ip_tag == op_tag:
                        op_tag = tg[1].split('.')[1]
                    prime_tags_cons.append((op_tag, ip_tag)) # Direction alignment here

    return prime_tags_cons


def independent_tags(prime_list):
    ''' Function will the set module to avoid the duplicates'''
    dump_list = []
    if len(prime_list):
        for prime in prime_list:
            dump_list.append(prime[0])
            dump_list.append(prime[1])

    return set(dump_list) # Duplicate avoidance

# ---------------- Example usage ----------------
folder = "./single_file"   # change this
files = os.listdir(folder)
xml_ext_files = []
for file in files:
    if str(file).endswith('.cnf.xml'):
        # print(file)   # available xml file
        xml_ext_files.append(file)


search_tag = "250FI4521"         # change this
# extracting all input and output tags from xml files (individually)
consolidated_tags = extract_inout(folder, xml_ext_files)

# separating necessary tags from among all 
separated_tags = tag_separator(consolidated_tags)

# Getting the primary tag value from the whole strng (mostly 1st index and in special cases use 2nd index)
edges = separate_prime_tags(separated_tags) # Prime consolidation list will have whole list (not based on xml's)

# Extracting the tags independently
# 1) Find how many independent tags are there?
nodes = independent_tags(edges)

nodes_as_list = list(nodes)

# Initialize a square matrix of zeros later you can update with nodes and edges(2D matrix)
adj_matrix = pd.DataFrame(0, index=nodes, columns=nodes)  # Unique tags --> Nodes/vertices


# Directed graph ()
for u, v in edges:
    adj_matrix.loc[u, v] = 1     # direction u -> v
    adj_matrix.loc[v, u] = -1    # reverse direction v -> u

print(adj_matrix)


visited_nodes = set()

master_incident_list = []

def iteration_adj(node, incident_set):
    
    def dfs(current_node):
        visited_nodes.add(current_node)
        for target, val in adj_matrix.loc[current_node].items():
            node_idx = adj_matrix.columns.get_loc(target)     # Return the index value for the node

            if val !=0:                                       # Checking if the node has a connection or not
                # next_node = nodes_as_list[node_idx]          # Incase if wanna go with index way
                next_node = target
                incident_set.add(target)

                if next_node not in visited_nodes:
                    dfs(next_node)                  # Recursion in progress

    dfs(node)  # For the initial phase (Trigger point)
    return incident_set


def serch_track(search_node):
    ''' Function used to track the node movement '''
    visited_vertices = set()
    track_list = set()

    def depth_first(key_node):
        visited_vertices.add(key_node)
        for node_i, node_val in adj_matrix.loc[key_node].items():

            if node_val !=0:
                next_vertex = node_i
                if node_val == 1:
                    xy_pair = (key_node, node_i)
                    track_list.add(xy_pair)

                if node_val == -1:
                    yx_pair = (key_node, node_i)
                    track_list.add(yx_pair)

                if next_vertex not in visited_vertices:
                    depth_first(next_vertex)

    depth_first(search_node)
    return track_list

            




for i, node in enumerate(adj_matrix.index):
    incident_set = set()
    output_inc = iteration_adj(node, incident_set)    
    list_output_inc = list(output_inc)     

    if len(output_inc) != 0:
        if not any(set(output_inc).issubset(set(sublist)) for sublist in master_incident_list): # Any sub part of inc set match with master incident list will not be added
            master_incident_list.append(list_output_inc)         # Appending the incident matrix (for shorter link)



if len(master_incident_list) >0:
    for ms_list in master_incident_list:
        print(ms_list)
        print("\n")
    
    # node_input = input("Enter the Node value to be search")
    node_input = "250DIC4545"

    if node_input:
        trackings = serch_track(node_input)
        print("Trackings \n",trackings)

# print("Master Incident Set \n", master_incident_list)

# print("Here are the incident Node connection \n")
# print(incident_set)


exit()
# search for specific tag where we can find the pipeline
matched_tags = tag_search(separated_tags, search_tag)

# aligning the matched tags to it's corresponding direction (backward or forward)
backward, forward = tag_navigator(matched_tags, search_tag)

# print("Backward receptors", backward)
# print("Forward producers", forward)

pipeline_maker(backward, forward)

# Note: If search tag is in input_tag then you can find who supplied input (Going back)
# Note: If search tag is in ouput_tag then you can find where it will go next (Going front)







# cmd + shift + P