########################
### GLOBAL VARIABLES ###
########################
a = 0
b = 0
c = 0
r = 0
p = 0
n = 0
start = False
######    simple_refls = False
model = ReflectionGroupModel()
# TODO include start point, other points black if chosen
# TODO simple reflections (same as real)
# TODO check render abilities ## further on
# TODO projection vector ## try/further on
# TODO user messages
# TODO change model build to use polyhedron/line3d method we worked through

########################
### INTERACT CODE    ###
########################
rpn = [(" ", text_control("Choose a Reflection Group: ")),("r",input_box(default=6, width='5', label=None, type=None)), ("p", input_box(default=3, width='5', label=None, type=None)), ("n", input_box(default=2, width='5', label=None, type=None)), \
("", text_control("Or, choose an exceptional reflection group with a value between 4 and 37:")), ("val", input_box(default=4, width='5', label=None, type=None)), ("Go:", ["Use arguments (r,p,n)","Use exceptional group"])]
layout_list = [[rpn[0][0]],["r","p","n"],[""],["val"],["Go:"]]
@interact(controls=rpn, layout=layout_list)
def f(**kwargs):
    global r,p,n
    r = kwargs['r']
    p = kwargs['p']
    n = kwargs['n']
    val = kwargs['val']
    refl_type = kwargs["Go:"]
    if refl_type == 'Use arguments (r,p,n)':
      if (type(r) == Integer and type(p) == Integer and type(n) == Integer):
        if p.divides(r):
          try:
              group = ReflectionGroup((r,p,n))
          except ImportError:
              print "We're relying on a package to create these models that sometimes crashes. Please try refreshing, or come back later and we'll try to have this back up."
        else:
          print "p must divide r"
      else:
        print "use integers"
    elif refl_type == 'Use exceptional group':
      if type(val) == Integer and val >= 4 and val <= 37:
        try:
            group = ReflectionGroup((val))
        except ImportError:
            print "We're relying on a package to create these models that sometimes crashes. Please try refreshing, or come back later and we'll try to have this back up."
    try:
        print group
        rank = group.rank()
        if group.is_real():
            real_dim = 1
        else:
            real_dim = 2
        if rank * real_dim > 4:
            print "This model is bigger than we can handle in our visualizer right now. Please choose different parameters."
        else:
            global model
            model.setGroup(group)

            contlist = [("x",input_box(default=20, width='5', label=None, type=None)), ("y", input_box(default=10, width='5', label=None, type=None)), ("z", input_box(default=5, width='5', label=None, type=None))]
            contlist.append(("show initial point: ", checkbox(default=True, label=None)))
            layout_list = [["x","y","z"],["show initial point: "]]
            @interact(controls=contlist,layout = layout_list)
            def f(**kwargs):
              global model, a,b,c
              a = kwargs['x']
              b = kwargs['y']
              c = kwargs['z']
              model.setStart(kwargs['show initial point: '])
              ### ask for projection vector


            refl = []
            for w in model.reflections:
                refl.append(w.reduced_word())
            contlistrefls = []
            # input for showing reflections
            for word in refl:
              contlistrefls.append((str("r" + str(word)), checkbox(default=True, label=None)))
            layout_list = [[]]
            for string, box in contlistrefls:
              layout_list[0].append(string)
            @interact(controls=contlistrefls, layout=layout_list)
            def f(**kwargs):
                model.setReflections(kwargs.copy())

            points_list = []
            for w in model.W:
                points_list.append(w.reduced_word())
            contlistpoints = []
            # input for showing vertices
            for word in points_list:
              contlistpoints.append((str("w" + str(word)), checkbox(default=True, label=None)))
            layout_list = [[]]
            for string, box in contlistpoints:
              layout_list[0].append(string)
            @interact(controls=contlistpoints, layout=layout_list)
            def f(**kwargs):
              model.setPoints(kwargs.copy())

    except UnboundLocalError:
        print "Group was unable to be created. Please change your parameters and try again."


@interact(controls=[(" ", text_control("When you're ready, click here to generate your model!")), ("", ["Generate"])])
def _f(**kwargs):
  global model
  # Suppresses errors until all arguments are valid integers
  if (type(a) == Integer and type(b) == Integer and type(c) == Integer):
    # TODO does this need to be 2d, sometimes? When?
    if model.rank == 3:
        model.setPoint((a, b, c))
    elif model.rank == 2:
        model.setPoint((a, b))
    elif model.rank == 1:
        model.setPoint((a,))
    model.create()
    model.writeOpenSCADCode()
    model.showModel()
    model.writeOpenSCADDiv()


  else:
    print "Arguments must be integers. Please enter all valid arguments to render model."
    return
