# This function takes a 2d polygon in 3d space and gives it a thickness
def thickenPolygon(polygon, thickness):
    new_points = []
    normal_vector = (vector(polygon.vertex_list()[1]) - vector(polygon.vertex_list()[0])).cross_product(vector(polygon.vertex_list()[2]) - vector(polygon.vertex_list()[0]))
    for point in polygon.vertex_list():
        point1 = vector(point) + .5*thickness*normal_vector
        point2 = vector(point) - .5*thickness*normal_vector
        new_points.append(point1)
        new_points.append(point2)
    return Polyhedron(vertices = new_points).plot() #returns as a Graphics3d object

# Here is an example of a thickenPolygon object, both with and without a boundary.
# The order of the vertices for thickening the boundary would have to come from
# a cayley_graph method

P = polygon3d([[1, 2, 3], [0,1,0], [1,0,1]], color=(0,1,0), alpha=0.2)
Q = line3d([[1, 2, 3], [0,1,0], [1,0,1],[1,2,3]], color=(0,1,0), opacity=0.7, radius=.05)
(thickenPolygon(P,.01)+Q).show()
