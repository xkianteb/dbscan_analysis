import sys


class Node:
	pass

def kdtree(pointList, depth=0):
	if not pointList:
		return None

	# Select axis based on depth so that axis cycles through all valid values
	try:
		k = (len(pointList[0]) -1)# Assumes all points have the same dimension
	except:
		k = pointList[0].dimension()
	axis = (depth % k) + 1

	# Sort point list to select median
	pointList.sort(key=lambda x: x[axis])
	median = len(pointList) // 2 # Choose median

	# Create node and construct subtrees
	node = Node()
	node.location = pointList[median]
	node.axis = axis
        node.label = pointList[median][0]
	node.leftChild = kdtree(pointList[:median], depth+1)
	node.rightChild = kdtree(pointList[median+1:], depth+1)
	return node

def fast_kdtree_constr(pointList):
	if not pointList:
		return None
	try:
		N = len(pointList[0]) # Assumes all points have the same dimension
	except:
		N = pointList[0].dimension()
	
	PTR = [i for i in range(len(pointList))]
	
	SortedList = []
	for i in range(N):
		SortedList.append([]); SortedList[i] = list(PTR)

	del PTR
	for i in range(N): # Sort point list
		SortedList[i].sort(key=lambda x: pointList[x][i])
	
	return kdtreeConstr(pointList, SortedList)


def kdtreeConstr(pointList, SortedList, depth=0):
	if len(SortedList[0]) == 0:
		return None

	# Select axis based on depth so that axis cycles through all valid values
	try:
		k = len(pointList[0]) # Assumes all points have the same dimension
	except:
		k = pointList[0].dimension()
	axis = depth % k

	# Select median
	m = len(SortedList[axis]) // 2
	median = SortedList[axis][m] # Choose median

	# Create New SortedList
	T = {}
	for i in SortedList[0]:
		T[i] = False
	
	newLists = ([], [])

	for j in [0, 1]:
		if j == 0:
			for i in SortedList[axis][:m]:
				T[i] = True
		else:
			for i in SortedList[axis][:m]:
				T[i] = False
			for i in SortedList[axis][m+1:]:
				T[i] = True

		for i in range(k):
			newLists[j].append([])
			if i == axis:
				if j == 0:
					newLists[0][i] = SortedList[axis][:m]
				else:
					newLists[1][i] = SortedList[axis][m+1:]
			else:
				for l in SortedList[i]:
					if T[l]:
						newLists[j][i].append(l)

	List1, List2 = newLists[0], newLists[1]
	del T; del SortedList; del newLists
	
	# Create node and construct subtrees
	node = Node()
	node.location = pointList[median]
	node.axis = axis
	node.leftChild = kdtreeConstr(pointList, List1, depth+1)
	node.rightChild = kdtreeConstr(pointList, List2, depth+1)
	return node



def query(rec, node):
	if node == None:
		return
	axis = node.axis
	median = node.location[axis]
	try:	# for Iso_rectangle, Iso_cuboid,...
		low = rec.min_coord(axis)
		high = rec.max_coord(axis)
	except:
		try:	# for bboxes
			low = rec.min(axis)
			high = rec.max(axis)
		except:	# for tuples
			low = rec[axis][0]
			high = rec[axis][1]
	if median >= low:
		for point in query(rec, node.leftChild):
			yield point
	if median <= high:
		for point in query(rec, node.rightChild):
			yield point
	try:	# for Iso_rectangle, Iso_cuboid,...
		if rec.has_on_unbounded_side(node.location):
			return
	except:
		try:
			Dimension = node.location.dimension()
		except:
			Dimension = len(node.location)
		for axis in range(Dimension):
			c = node.location[axis]
			try:
				low = rec.min(axis)
				high = rec.max(axis)
			except:
				low = rec[axis][0]
				high = rec[axis][1]			
			if c < low or c > high:
				return
	yield node.location

