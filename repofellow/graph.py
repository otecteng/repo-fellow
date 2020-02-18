from repofellow.injector import Injector,Project
from itertools import combinations,groupby
class GraphProject:
    def __init__(self,contributions):
        self.data = contributions

    def caculate(self):
        # get dev projects to generate node
        developer = list(map(lambda x:x.developer ,self.data))
        for i,_ in groupby(developer):
            print(i)
        # convert com of projects to edge
        # draw
        return "caculated"

        

