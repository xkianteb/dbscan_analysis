import sys
from kdtree import KDTree
import vptree
import numpy as np
import math
import matplotlib.pyplot as plt
import random

tree = []
UNCLASSIFIED = False
NOISE = None
debug = False

def _dist(p,q):
	return math.sqrt(np.power(p-q,2).sum())

def _eps_neighborhood(p,q,eps):
	return _dist(p,q) < eps

def _eps_vp_neighborhood(m,point_id,eps):
    q = vptree.NDPoint(m[point_id][1:3])
    neighbors = vptree.get_all_in_range(tree, q, eps)
    return neighbors

def _eps_kd_neighborhood(m,point_id,eps):
    point = m[point_id][1:3]
    neighbors = np.array(tree.query(query_point=point,eps=eps**2))
    return np.ravel(neighbors[:,:-2]).tolist()

# Searchs a region for neighboring points
def _region_query(structure, m, point_id, eps):
    n_points = m.shape[1]
    seeds = []
 
    if structure == "vp":
        neighbors = _eps_vp_neighborhood(m, point_id, eps)
        seeds = ([x.idx for d,x in neighbors])
    elif structure == "kd":
        neighbors = _eps_kd_neighborhood(m, point_id, eps)
        seeds = neighbors
    else:
        for i in range(0, n_points):
            if not i == point_id:
                if _eps_neighborhood(m[:,point_id], m[:,i], eps):
                    seeds.append(i)

    if debug:
        print "Seed: " + str(seeds)
        print "-----------------------------------------"
    return seeds

# Expands the cluster to find neighboring points
# of points in the cluster
def _expand_cluster(structure, m, classifications, point_id, cluster_id, eps, min_points):
    seeds = _region_query(structure, m, point_id, eps)
    if len(seeds) < min_points:
        classifications[point_id] = NOISE
        return False
    else:
        classifications[point_id] = cluster_id
        for seed_id in seeds:
            classifications[int(seed_id)] = cluster_id
            
        while len(seeds) > 0:
            current_point = seeds[0]
            results = _region_query(structure, m, current_point, eps)
            if len(results) >= min_points:
                for i in range(0, len(results)):
                    result_point = int(results[i])
                    if classifications[result_point] == UNCLASSIFIED or \
                       classifications[result_point] == NOISE:
                        if classifications[result_point] == UNCLASSIFIED:
                            seeds.append(result_point)
                        classifications[result_point] = cluster_id
            seeds = seeds[1:]
        return True
        
# Core DBSCAN Algorithm
def dbscan(structure, m, eps, min_points):
    start = 1
    n_points = m.shape[0]
    if structure == 'base':
        start = 0
        n_points = m.shape[1]

    cluster_id = 1
    classifications = [UNCLASSIFIED] * n_points
    for point_id in range(start, n_points):
        if classifications[point_id] == UNCLASSIFIED:
            if _expand_cluster(structure,m, classifications, point_id, cluster_id, eps, min_points):
                cluster_id = cluster_id + 1
    return classifications

# Maps cluster id to random color
def num_to_color(nums):
    graph = []
    colors = {}
    r = lambda: random.randint(0,255)
    for x in nums:
        number = x[0]
        if not number in colors:
            colors[number] = ('#%02X%02X%02X' % (r(),r(),r()))
        graph.append(colors[number])
    return graph

def main(): 
    eps = float(sys.argv[1])
    min_points = int(sys.argv[2])
    structure = sys.argv[3]
    plot = sys.argv[4]

    csv_import = np.loadtxt('data.csv',delimiter=',', skiprows=1)
    data = csv_import
    data[:,:1] = csv_import[:,:1] -1
    results = []

    global tree
    if structure == 'vp':
        # Store the data in the VP Tree
        points = [vptree.NDPoint(x[1:3],x[0]) for x in  data] 
        tree = vptree.VPTree(points)
        results = dbscan(structure, data, eps, min_points)
    elif structure == 'kd':
        # Store the data in the KD Tree
        points = data[:,:-1]
        tree = KDTree.construct_from_data(np.array(points)) 
        results = dbscan(structure, data, eps, min_points)
    elif structure == 'base':
        m = data[:,1:3].transpose()
        results = dbscan(structure, m, eps, min_points)

    # Transpose the matrix
    tmp = np.array(results)[:, np.newaxis]
    data[:,-1:] = tmp
    np.savetxt('output.csv', data, delimiter=',')
 
    # Plot
    if plot.lower() == 'true':
        X = data[:,1:2]
        Y = data[:,2:3]
        C = np.array(num_to_color(data[:,3:4].astype(int)))
        plt.scatter(X, Y, color=C)
        plt.show()

if  __name__ =='__main__':
	main()
