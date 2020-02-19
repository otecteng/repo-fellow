from repofellow.injector import Injector,Project
from itertools import combinations,groupby
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
class GraphProject:
    def __init__(self,contributions):
        self.data = contributions

    def caculate(self):
        return "caculated"