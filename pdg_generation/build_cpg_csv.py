"""
This program is mainly used for generating the dfg and convert the dfg to csv
which can be used later
"""
from pdgs_generation import *
import argparse
from os.path import isfile, join
from os import listdir

class DFG_generator:
    def __init__(self, file_dir):
        print(file_dir)
        file_pathes = [join(file_dir, f) for f in listdir(file_dir) 
                if isfile(join(file_dir, f)) and os.path.splitext(f)[1] == '.js']
        for file_path in file_pathes:
            pdg = get_data_flow(file_path, dict())
            self.traversal(pdg, 0, monitor=self.check_sink)

    def traversal(self, node, level, monitor=None):
        """
        traversal a tree from the root
        Args:
            node: the node to start
            monitor: for each node, triger the monitor function
        """
        if monitor is not None:
            monitor(node)
        # print("\t" * level, node.id, node.name, node.attributes, node.data_dep_children)
        for child in node.children:
            self.traversal(child, level + 1, monitor)
        
    def trace_up(self, node):
        """
        trace up from a node, follow the data flow edge
        """
        pathes = []
        nodes = [node]
        for start in nodes:
            nodes_group = start.data_dep_parents \
                    if hasattr(start, 'data_dep_parents') else []

            stack = [(start, iter(nodes_group))]
            while stack:
                parent, children = stack[-1]
                try:
                    child = next(children)
                    if child not in stack:
                        nodes_group = start.data_dep_parents \
                                if hasattr(child, 'data_dep_parents') else []
                        stack.append((child.extremity, iter(nodes_group)))
                        if len(nodes_group) == 0:
                            pathes.append([node[0] for node in stack])
                            print(stack)
                except StopIteration:
                    stack.pop()
        return pathes

    def check_sink(self, node):
        print('parents:+++++++++', node.name, node.attributes, node.data_dep_parents)
        if hasattr(node, 'name'):
            if node.name == 'ExpressionStatement':
                if node.data_dep_parents is not None:
                    for dpp in node.data_dep_parents:
                        print (dpp.extremity.id)
            elif node.name == 'CallExpression':
                parent_node = node.parent
                pathes = self.trace_up(parent_node)
                for path in pathes:
                    print("======================")
                    for n in path:
                        print("--------------------")
                        self.traversal(n, 0, monitor=self.check_input)
                    print([n.attributes for n in path])
            else:
                pass
                # print(node.id, node.name, node.attributes, node.data_dep_children)

    def check_input(self, node):
        print(node.id, node.name, node.attributes)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--input_dir')
    args = argparser.parse_args()
    input_dir_path = args.input_dir
    dfg_generator = DFG_generator(input_dir_path)


main()
