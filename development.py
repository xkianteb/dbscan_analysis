import kdtree
import dbscan
import vptree
import numpy as np

tree = []
UNCLASSIFIED = False
NOISE = None
debug = False

def _dist(p,q):
	return math.sqrt(np.power(p-q,2).sum())

def _eps_neighborhood(p,q,eps):
	return _dist(p,q) < ep

def _eps_vp_neighborhood(m,point_id,eps):
    q = vptree.NDPoint(m[point_id][1:3])
    neighbors = vptree.get_all_in_range(tree, q, eps)
    return neighbors

#def _eps_kd_neighborhood(m,point_id,eps):
    

def _region_query(m, point_id, eps):
    n_points = m.shape[1]
    neighbors = _eps_vp_neighborhood(m, point_id, eps)
    seeds = ([x.idx for d,x in neighbors])
    if debug:
        print "Seed: " + str(seeds)
        print "-----------------------------------------"
    return seeds

def _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points):
    seeds = _region_query(m, point_id, eps)
    if len(seeds) < min_points:
        classifications[point_id] = NOISE
        return False
    else:
        classifications[point_id] = cluster_id
        for seed_id in seeds:
            classifications[int(seed_id)] = cluster_id
            
        while len(seeds) > 0:
            current_point = seeds[0]
            results = _region_query(m, current_point, eps)
            if len(results) >= min_points:
                for i in range(0, len(results)):
                    result_point = int(results[i])
                    print "Index: " + str(result_point)
                    if classifications[result_point] == UNCLASSIFIED or \
                       classifications[result_point] == NOISE:
                        if classifications[result_point] == UNCLASSIFIED:
                            seeds.append(result_point)
                        classifications[result_point] = cluster_id
            seeds = seeds[1:]
        return True
        
def dbscan(structre, m, eps, min_points):
    """
    Inputs:
    m - A matrix whose columns are feature vectors
    eps - Maximum distance two points can be to be regionally related
    min_points - The minimum number of points to make a cluster
    
    Outputs:
    An array with either a cluster id number or dbscan.NOISE (None) for each
    column vector in m.
    """
    cluster_id = 1
    n_points = m.shape[0]
    print "N_points: " + str(m.shape)
    classifications = [UNCLASSIFIED] * n_points
    for point_id in range(1, n_points):
        if classifications[point_id] == UNCLASSIFIED:
            if _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points):
                cluster_id = cluster_id + 1
    return classifications


def main():    
    eps = 10
    min_points = 2
    structure = 'kd'

    csv_import = np.loadtxt('data.csv',delimiter=',', skiprows=1)
    data = csv_import
    data[:,:1] = csv_import[:,:1] -1

    global tree
    if structure == 'vp':
        # Store the data in the VP Tree
        points = [vptree.NDPoint(x[1:3],x[0]) for x in  data] 
        tree = vptree.VPTree(points)
    elif structure == 'kd':
        # Store the data in the KD Tree
        points = [x[0:3] for x in  data]
        tree = kdtree.kdtree(points)


    print "Tree: " + str(tree)
    tmp_data = data[0]
    #print "tmp_data: " + str(tmp_data)
    tmp_data = tmp_data[:, np.newaxis]
    #print "tmp_data: " + str(tmp_data)   
    #print "Shape: " + str(data.shape)[1]
    tmp_zero = np.zeros(((data.shape[1]-1), 2))
    #print "tmp_zero: " + str(tmp_zero.shape)
    tmp_zero[:,:-1] = (tmp_data[1:] - eps)
    
    tmp_zero[:,1:] = (tmp_data[1:] + eps)
    #tmp_data = tmp_zero
    #print "tmp_data: " + str(tuple(tmp_data.tolist()))  
    tmp_data = tuple([tuple(tmp_zero[i]) for i in range(0,len(tmp_zero))])
    #print "test: " + str(test) 


    results = kdtree.query(tmp_data, tree)
    for x in results:
        print "x--------: " + str(x[0])

    # Loop through until all points has been visited
    #q = vptree.NDPoint(data[0][1:3])
    #neighbors = vptree.get_all_in_range(tree, q, eps)

    #print "query:"
    #print "\t", q
    #print "nearest neighbors: "
    #for d, n in neighbors:
    #    print "\t", n

   # print points[0]
 
    #results = dbscan(structure, data, eps, min_points)
    #print "Results: " + str(results)

if  __name__ =='__main__':
	main()
