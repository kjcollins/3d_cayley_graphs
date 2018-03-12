W = ReflectionGroup((4,2,2))
my_point = (3,2) # this is where we decide on a point to reflect around,

Labeled_by_reflections_Spline_Edges = {}
Labeled_by_reflections_colors = {}
RainBow = rainbow(len(list(W.reflections())));
my_index = 0
for r in W.reflections():
    Labeled_by_reflections_colors[r] = RainBow[my_index]
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

three_d_points = {}
for w in W:
    v = points_in_hyperplane[w]
    a = v[0]
    b = v[1]
    c = v[2]
    three_d_points[w] = (10*a,10*b,10*c)


the_object = Polyhedron(vertices=[[0,0,0]]).projection().render_solid_3d()
# the_object = Polyhedron(vertices=[[0,0,0],[1,1,1],[0,0,1]]).projection().render_solid_3d(color='yellow')
#and finally we print the code to put into OpenSCAD
openSCADcode = ""
counter = 0
for r in W.reflections():
    for x in Labeled_by_reflections_Spline_Edges[r]:
        refl_verts = []
        string = "{color(" + str(list(Color(Labeled_by_reflections_colors[r]).rgb())) + ")hull(){"
        openSCADcode += string
        # print string
        for i in range(r.order()):
            substring = "translate(" + str(list(three_d_points[W.from_reduced_word(x[i])] )) + ")sphere(r=.15);"
            openSCADcode += substring
            refl_verts.append(list(three_d_points[W.from_reduced_word(x[i])]))
            # print substring
        end = "}}"
        openSCADcode += end
        # print refl_verts
        the_object += Polyhedron(vertices=refl_verts).projection().render_solid_3d(color=Color(Labeled_by_reflections_colors[r]))
        counter += 1
        # print counter
        # print end
print openSCADcode
the_object.show(viewer="threejs")
html("&lt;div id=scad hidden>"+openSCADcode+"&lt;/div>")
