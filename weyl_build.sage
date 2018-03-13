"""
Attempt to rewrite weyl.sage without interactive cells
"""

########################
### GLOBAL VARIABLES ###
########################
# a = 0
# b = 0
# c = 0
# outer_edges = False
# show_point = False
# simple_refls = False
model = ReflectionGroupModel()

########################
### INTERACT CODE    ###
########################

### First parameter choices
# @interact(controls=[("Lie type",selector(["A", "B/C"],default="A", buttons=True)),("rank",selector([1, 2, 3], default=2, buttons=True))])
def group_choice(model, Lie_type, rank, **kwargs):

  if Lie_type == "B/C":
    Lie_type = "B"
  group = WeylGroup([Lie_type, rank])
  model.setGroup(group)
  # print group
  viz_choices() #TODO restructure
  show_choices() #restructure

def viz_choices(a=20, b=10, c=5, highlight_outside_edges=True, outside_edge_size=.75, highlight_initial_point=True, **kwargs):
    if a < b or b < c:
        print "Highlighting outside edges requires x>y>z, please permute your the values into that order."
        outside = False
        model.setOutside(highlight_outside_edges)
    else:
        model.setOutside(highlight_outside_edges)

    model.setOutsideSize(outside_edge_size) # have default for visualizations saved in class "kwargs" dict?
    model.setStart(highlight_initial_point)

  def show_choices(show_point=True, show_simple_refls=True):
      refl = []
      for w in model.reflections:
        if show_simple_refls == True:
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
    model.showModel()
    model.setObj()
    print(model.obj)

  else:
    print "Arguments must be integers. Please enter all valid arguments to render model."
    return
