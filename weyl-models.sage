# from classes.model import ReflectionGroupModel
# print ReflectionGroupModel()
########################
### GLOBAL VARIABLES ###
########################
a = 0
b = 0
c = 0
start = False
contlistrefls = []
contlistpoints = []
refls = {}
points = {}
g_lie_type = 0
outer_edges = False
show_point = False
#simple_refls = False
W = "none"
passthrough = 0

########################
### HELPER FUNCTIONS ###
########################

def reflect_across(my_point,mirror_vector):
    return vector(my_point) - 2*vector(my_point).inner_product(mirror_vector)*mirror_vector

def three_tuple(tup):
  new_tup = ()
  if len(tup) == 1:
    return tup + (0, 0)
  elif len(tup) == 2:
    return tup + (0,)
  else:
    return tup

def all_points(W, points, Points_as_vertices, the_object):
  for r3 in W:
    key = "w" + str(r3.reduced_word())
    if points[key] == True:
      the_object += sphere(Points_as_vertices[r3],1,color='gray')
  return the_object

def outside_edge_list(W, the_object, Points_as_vertices, Labeled_by_reflections_colors):
  outside_edges = {}
  for r in W.simple_reflections():
      pairs = []
      for w2 in W:
        single_edge = [w2.reduced_word(), (r*w2).reduced_word()]
        if [(r*w2).reduced_word(), w2.reduced_word()] not in pairs:
          pairs.append(single_edge)
      outside_edges[r] = pairs

  if outer_edges == True:
    for r in W.simple_reflections():
      for x in outside_edges[r]:
        the_object += line3d([tuple(Points_as_vertices[W.from_reduced_word(x[0])]), tuple(Points_as_vertices[W.from_reduced_word(x[1])])], opacity=1, radius=0.75,color = Color(Labeled_by_reflections_colors[r]))
  return the_object, outside_edges


########################
### INTERACT CODE    ###
########################

### First parameter choices
@interact()
# TODO do control list to let Lie type have no underscore
def _f(Lie_type = ["A", "B/C"], rank = [1, 2, 3]):
  global contlistrefls, contlistpoints
  contlistrefls = []
  contlistpoints = []
  global refls, points
  refls = {}
  points = {}

  if Lie_type == "B/C":
    Lie_type = "B"
  global g_lie_type
  g_lie_type = Lie_type
  group = WeylGroup([Lie_type, rank])
  global W
  W = group
  #print W

  ### Checkboxes for model
  contlist = [("x",input_box(default=20, width='5', label=None, type=None)), ("y", input_box(default=10, width='5', label=None, type=None)), ("z", input_box(default=5, width='5', label=None, type=None))]
  contlist.append(("show initial point: ", checkbox(default=True, label=None)))
  contlist.append(("highlight outside edges", checkbox(default = True, label = None)))
  layout_list = [['x','y','z'], ['show initial point: ', 'highlight outside edges']]
  @interact(controls=contlist, layout=layout_list)
  def f(**kwargs):
    global a,b,c  ## understand global scoping later??
    a = kwargs['x']
    b = kwargs['y']
    c = kwargs['z']
    global outer_edges
    outer_edges = kwargs['highlight outside edges']
    global start
    start = kwargs['show initial point: ']
    ### ask for projection vector

  @interact(controls=[("Show all points", checkbox(default=True, label=None))])#,("Show only simple reflections", checkbox(default=False, label=None))])
  def f(**kwargs):
      global show_point #, simple_refls
      show_point = kwargs["Show all points"]
      #simple_refls = kwargs["Show only simple reflections"]

      # input for showing reflections
      refl = []
      for w in W.reflections():
        refl.append(w.reduced_word())
      contlistrefls = []
      for word in refl:
        contlistrefls.append((str("r" + str(word)), checkbox(default=True, label=None))) #default = simple_refls

      new_list = [[]]
      for string, box in contlistrefls:
        new_list[0].append(string)
      @interact(controls=contlistrefls, layout=new_list)
      def f(**kwargs):
          global refls
          refls = kwargs.copy()

      # input for showing vertices
      points_list = []
      for w in W:
        points_list.append(w.reduced_word())
      contlistpoints = []
      for word in points_list:
        contlistpoints.append((str("w" + str(word)), checkbox(default=show_point, label=None)))

      new_list = [[]]
      for string, box in contlistpoints:
        new_list[0].append(string)
      @interact(controls=contlistpoints, layout=new_list)
      def f(**kwargs):
        global points
        points = kwargs.copy()


### Build actual model and show viewer (user refresh)
# @interact()
# def _f(refresh = ["Update Model"]):
# TODO text control for the text, empty string key
@interact(controls=[("When you're ready, click here to generate your model!", ["Generate"])])
def _f(**kwargs):
  # print kwargs["When you're ready, click here to generate your model!"]

  # Suppresses errors until all arguments are valid integers
  if (type(a) == Integer and type(b) == Integer and type(c) == Integer):
    if g_lie_type == "B":
      if rank(W) == 3:
        my_point = (a, b, c)
      elif rank(W) == 2:
        my_point = (a, b)
      elif rank(W) == 1:
        my_point = (a,)
    elif g_lie_type == "A":
      my_point = (a,b,c)

    # if rank(W) == 3:
    #     my_point = (a, b, c)
    # elif rank(W) == 2:
    #     my_point = (a, b)
    # elif rank(W) == 1: # and g_lie_type == "B":
    #     my_point = (a,)


    ### This code seems to be unrelated to the rest of the model. but when
    # I deleted it, the model didn't appear (on higher dimensions). Check, don't know what's going on
    spline_edges = []
    for  r in W.reflections():
        group_elements_list = list(W)

        for w in W:
            if w in group_elements_list:
                spline_edges.append([r.reduced_word(), w.reduced_word(),(w*r).reduced_word()])
                group_elements_list.remove(w)
                group_elements_list.remove(w*r)

    mirror_vectors = []
    if g_lie_type == "A":
      mirrors = [(0,1,-1), (1,-1,0), (0,1,1)]  ## this is special for this group, sub in matrix manipulation for general/complex refl.
      for v in mirrors:
          mirror_vectors.append(vector(v).normalized())
    elif g_lie_type == "B":
      mirrors = [(1,-1,0), (0,1,-1),(0,0,1)]  ## this is special for this group, sub in matrix manipulation for general/complex refl.
      for v in mirrors:
          mirror_vectors.append(vector(v).normalized())

    # print g_lie_type, mirror_vectors

    List_of_Points = []
    if g_lie_type == "A":
      for w1 in W:
          if len(w1.reduced_word()) == 0:
              List_of_Points.append(my_point) #vector(three_tuple(tuple(my_point)))) ## TODO trying to make 2D???
          else:
              #   new_point = vector(three_tuple(tuple(my_point))) # (a,b,c)
              new_point = (a,b,c)
              for i in Sequence(1..len(w1.reduced_word())):
                  new_point = reflect_across(new_point,vector(mirror_vectors[w1.reduced_word()[i-1]-1]))
              List_of_Points.append(new_point)
            #   print new_point
    if g_lie_type == "B":
      for w in W:
        new_point = vector(my_point) * w.matrix()
        List_of_Points.append(vector(three_tuple(tuple(new_point))))

    Points_as_vertices = {}
    for j in range(len(list(W))):
        Points_as_vertices[W[j]] = List_of_Points[j]

    Labeled_by_reflections_Spline_Edges = {}
    Labeled_by_reflections_colors = {}
    RainBow = rainbow(len(W.reflections()));
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
    # if False: #simple_refls == True:
    #     for r2 in W.simple_reflections():
    #         key = "r" + str(r2.reduced_word())
    #         if refls[key] == True:
    #           for x in Labeled_by_reflections_Spline_Edges[r2]:
    #               the_object += line3d([tuple(Points_as_vertices[W.from_reduced_word(x[0])]), tuple(Points_as_vertices[W.from_reduced_word(x[1])])], opacity=0.5, radius=0.5,color = Color(Labeled_by_reflections_colors[r2]))
    # else:
    for r2 in W.reflections():
        key = "r" + str(r2.reduced_word())
        refls[key] = True ### TODO debug
        if refls[key] == True:
          for x in Labeled_by_reflections_Spline_Edges[r2]:
              the_object += line3d([tuple(Points_as_vertices[W.from_reduced_word(x[0])]), tuple(Points_as_vertices[W.from_reduced_word(x[1])])], opacity=0.5, radius=0.5,color = Color(Labeled_by_reflections_colors[r2]))
    #the_object += Polyhedron(vertices=[[2,0,0], [0,2,0], [0,0,2]]).projection().plot()
    # print "points", points, "start", start
    the_object = all_points(W, points, Points_as_vertices, the_object)
    the_object, outside_edges = outside_edge_list(W, the_object, Points_as_vertices, Labeled_by_reflections_colors)
    if start == True:
      the_object += sphere(three_tuple(my_point), 1, color='black')
      #the_object.show(viewer="threejs", frame=False)
    else:
      print the_object.parent()


    list_of_outside_edges = []
    for r in W.simple_reflections():
      for w2 in W:
        single_edge = [w2.reduced_word(), (r*w2).reduced_word()]
        single_edge2 = [(r*w2).reduced_word(), w2.reduced_word()]
        list_of_outside_edges.append(single_edge)
        list_of_outside_edges.append(single_edge2)

    openSCADcode = ""
    size = .25
    for r in W.reflections():
        for x in Labeled_by_reflections_Spline_Edges[r]:
            string = "{color(" + str(list(Color(Labeled_by_reflections_colors[r]).rgb())) + ")hull(){"
            openSCADcode += string
            if x in list_of_outside_edges:
                size = .75
            else:
                size = .25
            for i in range(r.order()):
                substring = "translate(" + str(list(Points_as_vertices[W.from_reduced_word(x[i])] )) + ")sphere(r="+ str(size) +");"
                openSCADcode += substring
            end = "}}"
            openSCADcode += end
    # print openSCADcode

    the_object.show(viewer="threejs", frame=False)
    #saved = the_object.save("filetest.obj")
    #pretty_print(html("this is the object"))
        #   with open("new_file.obj", "w+") as f:
        #        f.write(the_object.obj())
        #        print "done"
    global passthrough
    passthrough = the_object
    pretty_print(html('&lt;div id=scad hidden>'+openSCADcode+"&lt;/div>"))

  else:
    print "Arguments must be integers. Please enter all valid arguments to render model."
    return
