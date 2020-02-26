"""
This program is mainly used for generating the dfg and convert the dfg to csv
which can be used later
"""
from pdgs_generation import *
import argparse
from os.path import isfile, join
from os import listdir

class DFG_generator:
    def __init__(self, file_dir, sink_funcs=['exec']):
        self.exported_stats = []
        self.dfg = None
        self.vul_pathes = []
        self.sink_funcs = sink_funcs
        self.file_pathes = []
        for root, dirs, fs in os.walk(file_dir):
            for f in fs:
                if f.endswith('.js'):
                    self.file_pathes.append(os.path.join(root, f))
    
    def check_all_files(self):
        """
        check all files of a vulnerability
        """
        for file_path in self.file_pathes:
            print("checking: ", file_path)
            self.dfg = get_data_flow(file_path, dict())
            self.mark_input_func()
            self.traversal(self.dfg, 0, 
                    monitor=self.check_sink)
            self.log_results()


    def traversal(self, node, level, monitor=None):
        """
        traversal a tree from the root
        Args:
            node: the node to start
            monitor: for each node, triger the monitor function
        """
        if node is None:
            return []
        path = [node]
        if monitor is not None:
            monitor(node)
        #print("\t" * level, node.id, node.name, node.attributes, node.data_dep_children)
        for child in node.children:
            path += self.traversal(child, level, monitor)
        return path
        
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
                    child = child.extremity
                    #print(child)
                    if child not in [s[0] for s in stack]:
                        nodes_group = child.data_dep_parents \
                                if hasattr(child, 'data_dep_parents') else []
                        # print(child.id, nodes_group)
                        stack.append((child, iter(nodes_group)))
                        if len(nodes_group) == 0:
                            pathes.append([node[0] for node in stack])
                            # print(stack)
                except StopIteration:
                    stack.pop()
        return pathes

    def get_nearest_statement(self, node):
        """
        return the nearest statement node
        """
        while not node.is_statement():
            node = node.parent
        return node

    def _do_mark_input_func(self, node):
        if hasattr(node, 'attributes') and 'name' in node.attributes \
                and node.attributes['name'] == "exports":
            cur_stat = self.get_nearest_statement(node)
            pathes = self.trace_up(cur_stat)
            for path in pathes:
                for n in path:
                    self.exported_stats.append(n.id)

    def mark_input_func(self, start_node=None):
        """
        mark all the exported functions
        """

        if start_node is None:
            start_node = self.dfg
        self.traversal(self.dfg, 0, lambda node: self._do_mark_input_func(node))

    def check_sink(self, node):
        #print('parents:+++++++++', node.id, node.name, node.attributes, node.data_dep_parents)
        found = False
        if hasattr(node, 'name'):
            if node.name == 'CallExpression':
                # get the statement
                all_children = self.traversal(node, 0)
                for child in all_children:
                    if child.name == "Identifier" and \
                            child.attributes['name'] in self.sink_funcs:
                        found = True
                if not found:
                    return False
                parent_node = self.get_nearest_statement(node) 
                pathes = self.trace_up(parent_node)
                for path in pathes:
                    for n in path:
                        if n.id in self.exported_stats:
                            self.vul_pathes.append(path)
                            break
    
    def log_results(self):
        """
        log the results
        """
        for path in self.vul_pathes:
            print("==============================")
            for node in path:
                print("--------------------")
                all_children = self.traversal(node, 0, 
                    monitor=lambda x: print(x.name, x.id, x.attributes))
            print([n.id for n in path])

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--input_dir')
    args = argparser.parse_args()
    input_dir_path = args.input_dir
    dfg_generator = DFG_generator(input_dir_path)
    dfg_generator.check_all_files()
    return dfg_generator.vul_pathes

main()
