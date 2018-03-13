# This is an example using the .cayley_graph() method.

# Initialize the group.
W = ReflectionGroup((1,1,4))

# Use the reflections as the generators of Cayley graph.
G = W.cayley_graph(generators = W.reflections(),side = "left").to_undirected()

# Create a dictionary of the locations of each vertex using an initial point.
initial_point = vector([1,2,3])
vertex_position = {}
for vertex in G.vertices():
    vertex_position[vertex] = vertex.matrix()*initial_point

# Show the 3D model, size parameters can be changed at will.
G.show3d(pos3d = vertex_position, color_by_label=True, edge_size=.1, vertex_size=.1)

# Print a .obj file
model = G.plot3d(pos3d = vertex_position, color_by_label=True, edge_size=.05, vertex_size=.1)
file = model.obj()
o = open("object_file.obj",'w')
o.write(str(file))
