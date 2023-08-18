import os
from inspect import getsourcefile
import numpy as np
import pandas as pd
import itertools
import networkx as nx
from scipy.spatial import distance
import matplotlib.pyplot as plt
from collections import Counter

def save_cooccurrence_networks(path_to_project, path_to_current_folder, input_folder_name, output_folder_name, max_num_tags):
    path_to_posts = os.path.abspath(os.path.join(path_to_project, input_folder_name))
    path_to_output = os.path.abspath(os.path.join(path_to_current_folder, output_folder_name))
    for file in os.listdir(path_to_posts):
        filename = os.fsdecode(file)
        if(filename.endswith(".csv")):
            #data = pd.read_csv(path_to_posts + os.path.sep + filename)
            #, sep=",\\[", header=None, engine='python')
            #assuming that the tags are stored as a list in the first column
            all_tags = read_tags_from_data_file(filename, path_to_posts)

            target_tag_counts = get_target_tag_counts(all_tags, max_num_tags)
            nodes = create_nodes(target_tag_counts, all_tags, 'jaccard')
            save_cooccurrence_network(nodes, path_to_output, os.path.basename(filename))

def save_cooccurrence_for_whole_file(path_to_project, path_to_current_folder, input_folder_name, output_folder_name, graph_name, max_tags_per_file, max_num_tags):
    path_to_posts = os.path.abspath(os.path.join(path_to_project, input_folder_name))
    path_to_output = os.path.abspath(os.path.join(path_to_current_folder, output_folder_name))
    target_tag_counts = {}
    for file in os.listdir(path_to_posts):
        filename = os.fsdecode(file)
        if(filename.endswith(".csv")):
            all_tags = read_tags_from_data_file(filename, path_to_posts)
            target_tag_counts.update(get_target_tag_counts(all_tags, max_tags_per_file))
    k = Counter(target_tag_counts)
    final_tag_counts = {}
    for (tag, count) in k.most_common(max_num_tags):
        final_tag_counts[tag] = count
    nodes = create_nodes(final_tag_counts, all_tags, 'jaccard')
    save_cooccurrence_network(nodes, path_to_output, graph_name) 

#Returns a list containing the lists of tags in a data file
def read_tags_from_data_file(filename, path_to_posts):
        data = pd.read_csv(path_to_posts + os.path.sep + filename)
        #assuming that the tags are stored as a list in the first column
        return [tag_list.replace("[", "").replace("]", "").replace("'", "").split(",") for tag_list in data[data.columns[0]]]

def create_nodes(target_tag_counts, all_tags, distance_metric):
    unique_tags = get_unique_tags(target_tag_counts)
    unique_tags_index_first = get_unique_tags_index_first(unique_tags)
    combination_matrix = get_combination_matrix(all_tags, unique_tags)
    #Computing jaccard distance between each pair of vectors. Subtracting from 1 so that more 'similar' tag pairs have a larger score.
    distance_matrix = 1 - distance.cdist(combination_matrix, combination_matrix, distance_metric)
    #list of nodes, consisting of the tag pairs, their individual counts, and the jaccard distance between the tags.
    nodes = []
    for i in range(len(unique_tags)):
        for j in range(i+1, len(unique_tags)):
            distance_val = distance_matrix[i,j] 
            if distance_val > 0:
                nodes.append([unique_tags_index_first[i], unique_tags_index_first[j], target_tag_counts[unique_tags_index_first[i]], target_tag_counts[unique_tags_index_first[j]], distance_val])
    return nodes

def get_target_tag_counts(all_tags, max_num_tags):
    #Create a dictionary of word:number_of_occurrences pairs
    tag_counts = {}
    for post_tags in all_tags:
        for tag in post_tags:
            if tag in tag_counts:
                tag_counts[tag.strip()] += 1
            else:
                tag_counts[tag.strip()] = 1
    k = Counter(tag_counts)
    target_tag_counts = {}
    for (tag, count) in k.most_common(max_num_tags):
        target_tag_counts[tag] = count
    return target_tag_counts

def get_unique_tags(target_tag_counts):

    unique_tags = {}
    for tag in target_tag_counts.keys():
        if tag not in unique_tags:
            unique_tags[tag.strip()] = len(unique_tags)
    return unique_tags

def get_unique_tags_index_first(unique_tags):
    unique_tags_index_first = {}
    for tag, index in unique_tags.items():
        unique_tags_index_first[index] = tag
    return unique_tags_index_first

def get_combination_matrix(all_tags, unique_tags):
    #Get all possible combinations of the tags
    tag_combinations = [list(itertools.combinations(post_tags, 2)) for post_tags in all_tags]
    combination_matrix = np.zeros(shape=(len(unique_tags), len(unique_tags)))
    
    for tag_combination in tag_combinations:
        for combination in tag_combination:
            combination = (combination[0].strip(), combination[1].strip())
            if(combination[0].strip() in unique_tags.keys() and combination[1].strip() in unique_tags.keys()):
                combination_matrix[unique_tags[combination[0]], unique_tags[combination[1]]] += 1
                combination_matrix[unique_tags[combination[1]], unique_tags[combination[0]]] += 1

    #Avoid double counting the same tag if it appears twice in a post
    for i in range(len(unique_tags)):
        combination_matrix[i,i] /= 2
    return combination_matrix

def save_cooccurrence_network(nodes, output_folder, file_name):
    #Now we make a graph of the co-occurrence network
    G = nx.Graph()
    #Want the entire attribute dict
    G.nodes(data=True)

    for tag_pair_info in nodes:
        tag_x, tag_y, tag_x_count, tag_y_count, distance = tag_pair_info[0], tag_pair_info[1], tag_pair_info[2], tag_pair_info[3], tag_pair_info[4]

        #Populating the graph
        if not G.has_node(tag_x):
            G.add_node(tag_x, count=tag_x_count)
        if not G.has_node(tag_y):
            G.add_node(tag_y, count=tag_y_count)
        if not G.has_edge(tag_x, tag_y):
            G.add_edge(tag_x, tag_y, weight=distance)

    plt.figure(figsize=(15,15))
    pos = nx.spring_layout(G, k=0.25)


    node_size = [d['count']*100 for n,d in G.nodes(data=True)]
    nx.draw_networkx_nodes(G, pos, node_color='cyan', alpha=1.0, node_size=node_size)
    nx.draw_networkx_labels(G, pos)

    edge_width = [G.get_edge_data(u, v)['weight']*10 for u,v in G.edges()]
    nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color='black', width=edge_width)
    plt.axis('off')
    plt.savefig(os.path.join(output_folder + os.path.sep + file_name.split(".")[0]))

current_path = os.path.abspath(getsourcefile(lambda:0))
path_to_project = os.sep.join(current_path.split(os.sep)[:-2])
path_to_current_folder = os.sep.join(current_path.split(os.sep)[:-1])

#Save the co-occurence graphs for the individual post collections and then for the compilation of all of the 
save_cooccurrence_networks(path_to_project, path_to_current_folder, "tumblr_posts_info", "networks_tumblr", 50)
save_cooccurrence_for_whole_file(path_to_project, path_to_current_folder, "tumblr_posts_info", "networks_tumblr", "all", 50, 25)
