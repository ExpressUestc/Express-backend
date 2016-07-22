# coding:utf8

'''
find shortest path between two cities
e.g.
input:成都 上海
output：
[] 中间经过的城市
[] 每个城市的转移时间
'''
import pandas

from collections import defaultdict
from heapq import *

def dijkstra_raw(edges, from_node, to_node):
    g = defaultdict(list)
    for l, r, c in edges:
        g[l].append((c, r))
    q, seen = [(0, from_node, ())], set()
    while q:
        (cost, v1, path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == to_node:
                return cost, path
            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost + c, v2, path))
    return float("inf"), []


def dijkstra(edges, from_node, to_node):
    len_shortest_path = -1
    ret_path = []
    length, path_queue = dijkstra_raw(edges, from_node, to_node)
    if len(path_queue) > 0:
        len_shortest_path = length  ## 1. Get the length firstly;
        ## 2. Decompose the path_queue, to get the passing nodes in the shortest path.
        left = path_queue[0]
        ret_path.append(left)  ## 2.1 Record the destination node firstly;
        right = path_queue[1]
        while len(right) > 0:
            left = right[0]
            ret_path.append(left)  ## 2.2 Record other nodes, till the source-node.
            right = right[1]
        ret_path.reverse()  ## 3. Reverse the list finally, to make it be normal sequence.
    return len_shortest_path, ret_path

M = 999999  # This represents a large distance. It means that there is no link.
dataframe =  pandas.read_excel('~/gitProjects/Express-backend/Express/map/province.xlsx')
dataset =  dataframe.fillna(value=M).values.tolist()
header = dataframe.index.tolist()

### ==================== Given a list of nodes in the topology shown in Fig. 1.
list_nodes_id = range(len(dataset))
### ==================== Given constants matrix of topology.

### M_topo is the 2-dimensional adjacent matrix used to represent a topology.
M_topo = dataset

### --- Read the topology, and generate all edges in the given topology.
edges = []
for i in range(len(M_topo)):
    for j in range(len(M_topo[0])):
        if i != j and M_topo[i][j] != M:
            edges.append((i, j, M_topo[i][j]))  ### (i,j) is a link; M_topo[i][j] here is 1, the length of link (i,j).

# input should be unicode
def getPath(_from,_to):
    length, Shortest_path = dijkstra(edges, header.index(_from), header.index(_to))
    time,path = [],[]
    for index,num in enumerate(Shortest_path):
        path.append(header[num])
        if index == len(Shortest_path)-1:
            break
        time.append(dataset[Shortest_path[index]][Shortest_path[index+1]])
    return path,time
# test
if __name__ == '__main__':
    path,time = getPath(u'成都',u'上海')
    for item in path:
        print item
    for item in time:
        print item