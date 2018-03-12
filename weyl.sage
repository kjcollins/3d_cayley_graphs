########################
### GLOBAL VARIABLES ###
########################
a = 0
b = 0
c = 0
outer_edges = False
show_point = False
simple_refls = False
model = ReflectionGroupModel()

########################
### INTERACT CODE    ###
########################

### First parameter choices
@interact(controls=[("Lie type",selector(["A", "B/C"],default="A", buttons=True)),("rank",selector([1, 2, 3], default=2, buttons=True))])
def _f(**kwargs):
  Lie_type = kwargs["Lie type"]
  rank = kwargs["rank"]

  if Lie_type == "B/C":
    Lie_type = "B"
  group = WeylGroup([Lie_type, rank])
  global model
  model.setGroup(group)
  print group

  ### Checkboxes for model
  contlist = [("x",input_box(default=20, width='5', label=None, type=None)), ("y", input_box(default=10, width='5', label=None, type=None)), ("z", input_box(default=0, width='5', label=None, type=None))]
  contlist.append(("highlight initial point", checkbox(default=True, label=None)))
  contlist.append(("highlight outside edges", checkbox(default = True, label = None)))
  layout_list = [['x','y','z'], ['highlight initial point', 'highlight outside edges']]
  @interact(controls=contlist, layout=layout_list)
  def f(**kwargs):
    global a,b,c
    a = kwargs['x']
    b = kwargs['y']
    c = kwargs['z']
    outside = kwargs['highlight outside edges']
    if a < b or b < c:
        print "Highlighting outside edges requires x>y>z, please permute your the values into that order."
        outside = False
        model.setOutside(outside)
    else:
        model.setOutside(outside)
    if outside:
        @interact(controls=[("", text_control("Edges are set to .25")),("Outside edge size", slider(.25,1, step_size=.05, default=.75))])
        def f(**kwargs):
            model.setOutsideSize(kwargs['Outside edge size'])

    model.setStart(kwargs['highlight initial point'])
  contlist = [("Show all points", checkbox(default=True, label=None)),("Show only simple reflections", checkbox(default=False, label=None))]
  @interact(controls=[("Show all points", checkbox(default=True, label=None)),("Show only simple reflections", checkbox(default=False, label=None))])
  def f(**kwargs):
      global show_point , simple_refls
      show_point = kwargs["Show all points"]
      simple_refls = kwargs["Show only simple reflections"]

      # input for showing reflections
      refl = []
      for w in model.reflections:
        if simple_refls == True:
            if w in model.W.simple_reflections():
                refl.append((w.reduced_word(), True))
            else:
                refl.append((w.reduced_word(), False))
        else:
            refl.append((w.reduced_word(), True))



      contlistrefls = []
      for word, show_refl in refl:
        contlistrefls.append((str("r" + str(word)), checkbox(default=show_refl, label=None))) #default = simple_refls

      layout_list = [[]]
      for string, box in contlistrefls:
        layout_list[0].append(string)
      @interact(controls=contlistrefls, layout=layout_list)
      def f(**kwargs):
          model.setReflections(kwargs.copy())

      # input for showing vertices
      points_list = []
      for w in model.W:
        points_list.append(w.reduced_word())
      contlistpoints = []
      for word in points_list:
        contlistpoints.append((str("w" + str(word)), checkbox(default=show_point, label=None)))

      layout_list = [[]]
      for string, box in contlistpoints:
        layout_list[0].append(string)
      @interact(controls=contlistpoints, layout=layout_list)
      def f(**kwargs):
        model.setPoints(kwargs.copy())


### Build actual model and show viewer (user refresh)
@interact(controls=[(" ", text_control("When you're ready, click here to generate your model!")), ("", ["Generate"])])
def _f(**kwargs):
  global model
  model.makeOutsideEdges()
  # Suppresses errors until all arguments are valid integers
  if (type(a) == Integer and type(b) == Integer and type(c) == Integer):
    if model.lie_type == "B":
        if model.rank == 3:
            model.setPoint((a, b, c))
        elif model.rank == 2:
            model.setPoint((a, b))
        elif model.rank == 1:
            model.setPoint((a,))
    elif model.lie_type == "A":
        model.setPoint((a,b,c))

    model.create()
    model.writeOpenSCADCode()
    model.showModel()
    model.writeOpenSCADDiv()

  else:
    print "Arguments must be integers. Please enter all valid arguments to render model."
    return
