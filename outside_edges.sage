#Choose a group and initial point to get a working example
W = ReflectionGroup((1,1,4))
initial_point = vector([1,2,3])

vertex_position = {}
for vertex in G.vertices():
    vertex_position[vertex] = vertex.matrix()*initial_point

# Create a bounding polyhedron, that should be able to be turned on and off as well
# The polyhedron is also needed to determine which edges are "outside"
convex_bounding_polyhedron = Polyhedron(vertices = vertex_position.values())

# Create a dictionary of which edges are 1-faces (i.e. edges) of the convex polytope
outside_edge_dictionary = {}
faces1_by_vertices = []
for face in (convex_bounding_polyhedron.faces(1)):
    face_vertices = []
    for i in range(len(face.vertices())):
        face_vertices.append(tuple(face.vertices()[i]))
    faces1_by_vertices.append(set(face_vertices))
for j in range(len(W.cosets(S))):
    vertex_set = []
    for grp_elm in W.cosets(S)[j]:
        coordinates = tuple(vertex_position[grp_elm])
        vertex_set.append(coordinates)
    if set(vertex_set) in faces1_by_vertices:
        outside_edge_dictionary[tuple(W.cosets(S)[j])] = True

# Create a dictionary of which edges are contained in the 2-faces (i.e. faces) of the convex polytope
outside_face_dictionary = {}
faces2_by_vertices = []
for face in (convex_bounding_polyhedron.faces(2)):
    face_vertices = []
    for i in range(len(face.vertices())):
        face_vertices.append(tuple(face.vertices()[i]))
    faces2_by_vertices.append(set(face_vertices))
for j in range(len(W.cosets(S))):
    vertex_set = []
    for grp_elm in W.cosets(S)[j]:
        coordinates = tuple(vertex_position[grp_elm])
        vertex_set.append(coordinates)
    for two_face in faces2_by_vertices:
        if set(vertex_set).issubset(two_face):
            outside_face_dictionary[tuple(W.cosets(S)[j])] = True

print outside_edge_dictionary
print outside_face_dictionary

#Check if an individual edge is on the outside of the polytope, and if that edge is an edge of the polytope.
def is_outside_edge(self):
    if outside_edge_dictionary[tuple(self)] == True:
        return True
    else:
        return False

def on_outside_face(self):
    if outside_face_dictionary[tuple(self)] == True:
        return True
    else:
        return False
