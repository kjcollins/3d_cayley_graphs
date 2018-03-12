## Define the group you want to work with here, will probably need to turn this into a function setup asap
W = ReflectionGroup((4))
# WW = ReflectionGroup((5));len(WW)

# my_refl = W.reflections()[2].matrix();
# eval_matrix = -1*matrix.identity(2)
# P = my_refl-eval_matrix
# M = P.kernel()
# M.basis_matrix()[0][1].parent()

# UCF = UniversalCyclotomicField
# Reflecting_Mirrors = []
# for r in W.simple_reflections():
#     order = r.order()
#     eval_matrix = UCF.gen(order)*matrix.identity(2)
#     evector_matrix = r.matrix() - eval_matrix
#     mirror = evector_matrix.kernel().basis_matrix()[0]
#     Reflecting_Mirrors.append(mirror)

## A couple different ways of presenting the vertices of the object
# List_of_Points = []
# my_point = (3,2) # this is where we decide on a point to reflect around,
# for w in W:
#     if len(w.reduced_word()) == 0:
#         List_of_Points.append(my_point)
#     else:
#         new_point = vector(my_point)*w.matrix()
#         List_of_Points.append(new_point)

# Points_as_vertices = {}
# for i in range(len(W.list())):
#     Points_as_vertices[W[i]] = List_of_Points[i]

# This creates a non-repeating list of which vertices are going to be connected by an edge
Labeled_by_reflections_Spline_Edges = {}
Labled_by_reflections_colors = {}
RainBow = rainbow(len(list(W.reflections())));
my_index = 0
for r in W.reflections():
    Labled_by_reflections_colors[r] = RainBow[my_index]
    my_index = my_index+1
    reflection_loops = []
    group_elements_list = W.list()
    for w in W:
        if w in group_elements_list:
            my_hyper_edge = []
            for i in range(r.order()):
                group_elements_list.remove(r^i*w)
                my_hyper_edge.append((r^i*w).reduced_word())
            reflection_loops.append(my_hyper_edge)
    Labeled_by_reflections_Spline_Edges[r] = reflection_loops


As_4D_Real_Points = {}
for w in W:
    a = CC(vector(w.matrix()*vector(my_point))[0]).real()
    b = CC(vector(w.matrix()*vector(my_point))[0]).imag()
    c = CC(vector(w.matrix()*vector(my_point))[1]).real()
    d = CC(vector(w.matrix()*vector(my_point))[1]).imag()
    new_point_4d = vector((a,b,c,d))
    As_4D_Real_Points[w] = new_point_4d
As_4D_Real_Points



n = vector((1,-1,1,-1)).normalized()# this is the normal vector to whatever hyperplane we are using to project from 4D to 3D. We will want to be able to change this to find a "pretty" projection.
points_in_hyperplane = {}
for w in W:
    v = vector(As_4D_Real_Points[w])
    projected_point = v - v.dot_product(n)*n
    points_in_hyperplane[w] = projected_point

# n
# for w in W:
#     p = points_in_hyperplane[w]
#     print "here", p, vector(p).dot_product(n)  #supposed to be an easy error check but there are floating point issues. basically good.



#now in 3 d, just drop the last coordinate of the thing that has been projected onto the hyperplane
three_d_points = {}
for w in W:
    v = points_in_hyperplane[w]
    a = v[0]
    b = v[1]
    c = v[2]
    three_d_points[w] = (10*a,10*b,10*c)

# for w in W:
#     print three_d_points[w]


# len(List_of_Points)
# List_of_Points


# for r in W.reflections():
#     print r.reduced_word(), len(Labeled_by_reflections_Spline_Edges[r]), Labeled_by_reflections_Spline_Edges[r]

# len(List_of_Points)  # This is a place to ??unit test?? that we didn't somehow pick a point that is ON one of the hyperplanes and thus ends up with fewer vertices than we wanted


# import matplotlib.colors as colors  #pretty colors!

the_object = Polyhedron(vertices=[[0,0,0]]).projection().render_solid_3d()
# the_object = Polyhedron(vertices=[[0,0,0],[1,1,1],[0,0,1]]).projection().render_solid_3d(color='yellow')
#and finally we print the code to put into OpenSCAD
openSCADcode = ""
counter = 0
for r in W.reflections():
    for x in Labeled_by_reflections_Spline_Edges[r]:
        refl_verts = []
        # string = "{color(" + str(list(Color(Labled_by_reflections_colors[r]).rgb())) + ")hull(){"
        # openSCADcode += string
        ### print string
        for i in range(r.order()):
            # substring = "translate(" + str(list(three_d_points[W.from_reduced_word(x[i])] )) + ")sphere(r=.15);"
            # openSCADcode += substring
            refl_verts.append(list(three_d_points[W.from_reduced_word(x[i])]))
            ### print substring
        # end = "}}"
        # openSCADcode += end
        print refl_verts
        the_object += Polyhedron(vertices=refl_verts).projection().render_solid_3d(color=Color(Labled_by_reflections_colors[r]))
        counter += 1
        print counter
        ### print end
# print openSCADcode
the_object.show(viewer="threejs")

# A3 = WeylGroup(['A',3])
# checked_reflections = []
# for a in A3.simple_reflections():
#     checked_reflections.append(a)
# # print checked_reflections
# checked_reflections.pop(0)
# WWW = A3.subgroup(checked_reflections)
# WWW.is_isomorphic(A3)
#
# aa= A3.simple_reflections()[2]#;aa
# bb=checked_reflections[0]#;bb
# # aa == bb
