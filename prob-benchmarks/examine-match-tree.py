#!/usr/bin/env python

from sys import argv, stdout, stderr
from re import search, finditer, MULTILINE, DOTALL

''' Map atoms to SAS+ variable, value pairs '''
# To use the match tree, there needs to be a mapping from atoms to variable indices
#  along with the corresponding value of that variable
# Generate this by reading the file "output" which contains these mappings
atom_to_var_value = dict()
var_value_to_atom = dict()
num_var_values_dict = dict() # The number of potential variables each variable may have

with open('output', 'r') as f:
    for (i, match) in enumerate(finditer(r'begin_variable(.*?)end_variable',
                                f.read(),
                                MULTILINE | DOTALL)):
        lines = match.group(1).strip().split("\n")

        assert "-1" == lines[1], \
            "Expected variable %s to be followed by -1" % (lines[0])

        # var_index = int(lines[0][3:]) # Apparently this doesn't match
                                        # up with the policy var indices
        var_index = i                   # So this line makes it explicit

        num_var_values_dict[var_index] = int(lines[2])

        for var_value, raw_atom in enumerate(lines[3:]):
            if (raw_atom.startswith("Atom ")):
                # Note the format of raw_atom: "predicate(term1, term2, ...)""
                atom_to_var_value[(raw_atom[5:])] = [var_index, var_value]
            # The <none of these> case doesn't matter for traversing the tree

# Convert num_var_values_dict to a list indexed by the variable index
num_vars = max(num_var_values_dict.keys())+1
num_var_values = []
for i in range(num_vars):
    if i in num_var_values_dict.keys():
        num_var_values.append(num_var_values_dict[i])
    else:
        num_var_values.append(0)

# Create the match tree now
class MatchTreeNode:
    def __init__(self, var_index=-1, num_values=-1):
        self.bucket = []    # A list of [actions, SC?, distance]
        self.var_index = var_index
        if (var_index >= 0):
            self.value_nodes = [None for i in range(num_values)]
        self.star_node = None
    def get_actions(self, var_values):
        ret = self.bucket[:]    # make a copy
        if (self.var_index >= 0):   # var_index == -1 implies this is a star node, so there are no values
            ret += self.value_nodes[var_values[self.var_index]].get_actions(var_values)
        if (self.star_node):
            ret += self.star_node.get_actions(var_values)
        return ret
    def get_deepest_path(self):
        longest_so_far = []
        if (self.var_index >= 0):
            for subnode in self.value_nodes:
                candidate_longest = subnode.get_deepest_path()
                if (len(candidate_longest) > len(longest_so_far)):
                    longest_so_far = candidate_longest
        if (self.star_node):
            candidate_longest = self.star_node.get_deepest_path()
            if (len(candidate_longest) > len(longest_so_far)):
                longest_so_far = candidate_longest
        return [self] + longest_so_far
    def get_total_paths(self):
        paths = 1
        if (self.var_index >= 0):
            for subnode in self.value_nodes:
                paths += subnode.get_total_paths()
        if (self.star_node):
            paths += self.star_node.get_total_paths()
        return paths
    def get_average_path_length(self):
        branches = 0
        accumulated_path_length = 0.0
        if (self.var_index >= 0):
            for subnode in self.value_nodes:
                branches += 1
                accumulated_path_length += subnode.get_average_path_length()
        if (self.star_node):
            branches += 1
            accumulated_path_length += self.star_node.get_average_path_length()
        if (branches == 0):
            return 1.0
        return 1.0 + (accumulated_path_length/branches)
    def _recursive_str(self, indent=""):
        ret = ""
        if (self.var_index >= 0):
            ret += indent + "Node var" + str(self.var_index) + ":\n"
            indent += "  "
        ret += indent + "Bucket: " + str(self.bucket)
        if (self.var_index >= 0):
            for (i, subnode) in enumerate(self.value_nodes):
                ret += "\n" + indent + "Value " + \
                    str(i+1) + ":\n" + subnode._recursive_str(indent + "  ")
        ret += "\n" + indent + "Star:\n"
        
        if (self.star_node):
            ret += self.star_node._recursive_str(indent + "  ")
        else:
            ret += indent + "  None"
            
        return ret
    def __str__(self):
        return self._recursive_str()

# Helper function for gen_match_tree
def gen_bucket_from_check(lines):
    line = lines.pop(0)
    assert line.startswith("check"), \
        "Error in building match tree: Expected \"check\", got %s" % line
    num_items = int(line[6:])
    ret_bucket = [] # List of (action, SC?, d) that works as a bucket in a MatchTreeNode
    for j in range(num_items):
        line = lines.pop(0)

        # The line is currently in the form "action / SC? / d=distance"
        raw_atom, raw_sc, raw_distance = line.split(" / ")
        
        if (raw_sc == "SC"):
            is_sc = True
        else:
            is_sc = False
        
        distance = int(raw_distance.split("=")[1].strip())

        ret_bucket.append((raw_atom, is_sc, distance))

    return ret_bucket

# Creates the match tree recursively
def gen_match_tree(lines):  # This array of lines are modified in-place as it is called recursively
    line = lines.pop(0)
    assert line.startswith("switch"), \
        "Error in building match tree: Expected \"switch\", got %s" % line
    var_index = int(line[7:])
    num_values = num_var_values[var_index]

    ret = MatchTreeNode(var_index, num_values)

    # First read the default bucket
    ret.bucket = gen_bucket_from_check(lines)
    
    # Now read the node for each value
    for i in range(num_values):
        if (lines[0].startswith("switch")):
            # Recursively build the next match tree
            ret.value_nodes[i] = gen_match_tree(lines)
            continue
        
        # If it's not another switch, it's expected to be a check
        ret_matchtree_child = MatchTreeNode()
        ret_matchtree_child.bucket = gen_bucket_from_check(lines)

        ret.value_nodes[i] = ret_matchtree_child
    
    # Lastly, read the star node
    if (lines[0].startswith("switch")):
        ret.star_node = gen_match_tree(lines)
    else:
        ret_matchtree_child = MatchTreeNode()
        ret_matchtree_child.bucket = gen_bucket_from_check(lines)

        ret.star_node = ret_matchtree_child

    return ret

# Build the policy from the policy file produced by PRP
policy = None
with open('policy.out', 'r') as f:
    policy = gen_match_tree(f.readlines())

if (not policy):
    stderr.write("%s: Error in building policy\n" % (argv[0]))
    exit(1)

deepest_path = policy.get_deepest_path()
stdout.write("Longest path: %d\n" % (len(deepest_path)))
'''
stdout.write("Longest path: If...\n")
for i in range(len(deepest_path)):
    var_index = deepest_path[i].var_index
    if (var_index >= 0):
        next_node = deepest_path[i+1]
        if (next_node in deepest_path[i].value_nodes):
            var_value = deepest_path[i].value_nodes.index(next_node)
            translated_condition = 
        else:
            stdout.write("(var%d = *)\n" % (var_index))

for node in deepest_path:
    var_index = node.var_index

    stdout.write("%d " % (node.var_index))
stdout.write("\n")
'''

stdout.write("Total paths: %d\n" % (policy.get_total_paths()))
stdout.write("Average path length: %.2f\n" % (policy.get_average_path_length()))

stdout.write("Policy dump:\n")
stdout.write(str(policy))
