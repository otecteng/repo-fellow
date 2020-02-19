from repofellow.injector import Injector,Project
from itertools import combinations,groupby
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
class GraphProject:
    def __init__(self,contributions):
        self.data = contributions

    def caculate(self):
        # # get dev projects to generate node
        developer = list(map(lambda x:x.developer ,self.data))
        edges = {}
        # print(developer)
        for i,_ in groupby(developer):
            projects = list(filter(lambda x:x.developer == i,self.data))
            projects = list(map(lambda x:x.project,projects))
            # nodes.add(projects)
            # convert com of projects to edge
            for j in combinations(projects,2):
                if j in edges:
                    edges[j] = edges[j] + 1
                else:
                    edges[j] = 1
        for k in edges:
            print("{} {}".format(k,edges[k]))
            G.add_edge(k[0],k[1],weight=edges[k])
        plt.figure(3)
        nx.draw(G,with_labels=True)
        plt.show()
        return "caculated"