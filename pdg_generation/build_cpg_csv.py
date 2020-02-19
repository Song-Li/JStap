import pickle
from pdgs_generation import *
import argparse
from os.path import isfile, join
from os import listdir

class Loader:
    def __init__(self, file_dir):
        print(file_dir)
        self.pickles = []
        store_pdg_folder(file_dir)
        pickle_path = "{}/Analysis/PDG/".format(file_dir)
        pickle_pathes = [join(pickle_path, f) for f in listdir(pickle_path) if isfile(join(pickle_path, f))]
        for cur_pickle in pickle_pathes:
            print(cur_pickle)
            self.pickles.append(pickle.load(open(cur_pickle, 'rb')))
        for cur_pickle in self.pickles:
            self.traversal_pickle(cur_pickle, 0)

    def traversal_pickle(self, node, level):
        print("\t" * level, node.attributes, node.data_dep_children)
        for child in node.children:
            self.traversal_pickle(child, level + 1)
        
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--input_dir')
    args = argparser.parse_args()
    input_dir_path = args.input_dir
    loader = Loader(input_dir_path)


main()
