########################
### GLOBAL VARIABLES ###
########################
a = 0
b = 0
c = 0
r = 0
p = 0
n = 0
# start = False
# contlistrefls = []
# contlistpoints = []
# refls = {}
# points = {}
# g_lie_type = 0
# outer_edges = False
# show_point = False
######    simple_refls = False
W = "none"
# passthrough = 0

########################
### INTERACT CODE    ###
########################
rpn = [(" ", text_control("Choose a Reflection Group: ")),("r",input_box(default=6, label=None, type=None)), ("p", input_box(default=3, label=None, type=None)), ("n", input_box(default=2, label=None, type=None)), \
("", text_control("Or, choose an exceptional reflection group with a value between 4 and 37:")), ("val", input_box(default=4, label=None, type=None)), ("Go:", ["Use arguments (r,p,n)","Use exceptional group"])]
@interact(controls=rpn)
def f(**kwargs):
  global r,p,n
  r = kwargs['r']
  p = kwargs['p']
  n = kwargs['n']
  val = kwargs['val']
  refl_type = kwargs["Go:"]
  print refl_type
  if refl_type == 'Use arguments (r,p,n)':
      if (type(r) == Integer and type(p) == Integer and type(n) == Integer):
        if p.divides(r):
          group = ReflectionGroup((r,p,n)) ## another file for exceptional complex
        else:
          print "p must divide r"
      else:
        print "use integers"
  elif refl_type == 'Use exceptional group':
      if type(val) == Integer and val >= 4 and val <= 37:
          group = ReflectionGroup((val))
  print group

  ### Check!!!
  rank = group.rank()



  global W
  W = group
  # message: rank too high
  # warning: p must divide r

refl = []
for w in W.reflections():
    refl.append(w.reduced_word())

points_list = []
for w in W:
    points_list.append(w.reduced_word())

a = 0
b = 0
c = 0
start = False
contlistrefls = []
contlistpoints = []
refls = {}
points = {}

contlist = [("x",input_box(default=20, label=None, type=None)), ("y", input_box(default=10, label=None, type=None)), ("z", input_box(default=5, label=None, type=None))]
contlist.append(("show initial point: ", checkbox(default=True, label=None)))
@interact(controls=contlist)
def f(**kwargs):
  global a,b,c  ## understand global scoping later??
  a = kwargs['x']
  b = kwargs['y']
  c = kwargs['z']
  global start
  start = kwargs['show initial point: ']
  ### ask for projection vector


# input for showing reflections
for word in refl:
  contlistrefls.append((str("r" + str(word)), checkbox(default=True, label=None)))
@interact(controls=contlistrefls)
def f(**kwargs):
    global refls
    refls = kwargs.copy()

# input for showing vertices
for word in points_list:
  contlistpoints.append((str("w" + str(word)), checkbox(default=True, label=None)))
@interact(controls=contlistpoints)
def f(**kwargs):
  global points
  points = kwargs.copy()


@interact()
def _f(refresh = ["refresh"]):

  # Suppresses errors until all arguments are valid integers
  if (type(a) == Integer and type(b) == Integer and type(c) == Integer):
    my_point = (a, b, c)

    spline_edges = []
    for  r in W.reflections():
        group_elements_list = list(W)

        for w in W:
            if w in group_elements_list:
                spline_edges.append([r.reduced_word(), w.reduced_word(),(w*r).reduced_word()])
                group_elements_list.remove(w)
                group_elements_list.remove(w*r)

    mirrors = [(0,1,-1), (1,-1,0), (0,1,1)]  ## this is special for this group, sub in matrix manipulation for general/complex refl.
    mirror_vectors = []
    for v in mirrors:
        mirror_vectors.append(vector(v).normalized())

    def reflect_across(my_point,mirror_vector):
        return vector(my_point) - 2*vector(my_point).inner_product(mirror_vector)*mirror_vector

    List_of_Points = []
    for w1 in W:
        if len(w1.reduced_word()) == 0:
            List_of_Points.append(my_point)
        else:
            new_point = (a,b,c)
            for i in Sequence(1..len(w1.reduced_word())):
                new_point = reflect_across(new_point,vector(mirror_vectors[w1.reduced_word()[i-1]-1]))
            List_of_Points.append(new_point)
    Points_as_vertices = {}
    for j in range(len(list(W))):
        Points_as_vertices[W[j]] = List_of_Points[j]

    Labeled_by_reflections_Spline_Edges = {}
    Labeled_by_reflections_colors = {}
    RainBow = rainbow(6);
    my_index = 0
    for r in W.reflections():
        Labeled_by_reflections_colors[r] = RainBow[my_index]
        my_index = my_index+1
        pairs = []
        for w2 in W:
            single_edge = [w2.reduced_word(), (w2*r).reduced_word()]
            if [(w2*r).reduced_word(), w2.reduced_word()] not in pairs:
                pairs.append(single_edge)
        Labeled_by_reflections_Spline_Edges[r] = pairs

    the_object = line3d([(0,0,0),(0,0,0)])

    for r2 in W.reflections():
        key = "r" + str(r2.reduced_word())
        if refls[key] == True:
          for x in Labeled_by_reflections_Spline_Edges[r2]:
              the_object += line3d([tuple(Points_as_vertices[W.from_reduced_word(x[0])]), tuple(Points_as_vertices[W.from_reduced_word(x[1])])], opacity=0.5, radius=0.5,color = Color(Labeled_by_reflections_colors[r2]))

    for r3 in W:
      key = "w" + str(r3.reduced_word())
      if points[key] == True:
        the_object += sphere(Points_as_vertices[r3],1,color='gray')

    if start == True:
      (the_object+sphere((a,b,c), 1, color='black')).show(viewer="threejs")
    else:
      the_object.show(viewer="threejs")
  else:
    print "Arguments must be integers. Please enter all valid arguments to render model."
    return
