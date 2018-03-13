###
### This is the code that ties everything together.
### Most of the actual work is done in reflections & weyl depending on
### whether or not the group has a real realization
###

r"""
<Very short 1-line summary>

<Paragraph description>

EXAMPLES::

<Lots and lots of examples>

AUTHORS:

- YOUR NAME (2005-01-03): initial version

- person (date in ISO year-month-day format): short desc

"""

# ****************************************************************************
#       Copyright (C) 2013 YOUR NAME <your email>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# ****************************************************************************


class ReflectionGroupModel:
    def __init__(self):

        self.W = -1
        self.field = ""
        self.real = True
        self.rank = -1
        self.reflections = []

        self.model = -1
        self.my_point = ()
        self.start = False
        self.projection_vector = ()
        self.reflection_colors = {}
        self.reflection_edges = {}
        self.show_outside = False
        self.outside_size = -1
        self.outside_edges = []
        self.points = {}
        self.model_reflections = []
        self.model_points = []
        self.lie_type = "none"

        self.code = ""
        self.obj = ""

    def setOutside(self, outside):
        self.show_outside = outside

    def setOutsideSize(self, size):
        self.outside_size = size

    def setStart(self, start):
        self.start = start

    def setGroup(self, group):#, point):
        # need error checking
        self.W = group
        self.field = str(group).split()[1]
        self.real = group.is_real()
        self.rank = group.rank()
        self.reflections = group.reflections()
        if self.real:
            self.lie_type = group.cartan_type()[0]

    def point(self, point):
        """
        Sets the initial point on the model.

        INPUT:

        - ``point`` -- tuple of three integers

        TEST:
            sage: W = ReflectionGroupModel()
            sage: W.setPoint((5,10,20))

        ..TODO::
            Add error checking for inputs that aren't
            tuples of three integers.

        """
        self.my_point = point

    def setReflections(self, reflList):
        self.model_reflections = reflList

    def setPoints(self, pointslist):
        self.model_points = pointslist

    def printGroup(self):
        print self.W
        print self.field
        print self.real
        print self.rank
        print self.reflections

    def canPrint(self):
        model_refl_words = []
        for string in self.model_reflections.keys():
            if self.model_reflections[string]:
                string = string[1:].strip("[]").split(",")
                for i in range(len(string)):
                    string[i] = int(string[i])
                model_refl_words.append(self.W.from_reduced_word(string))
        if self.W.subgroup(model_refl_words).is_isomorphic(self.W):
            return True
        else:
            return False

    def makeOutsideEdges(self):
        list_of_outside_edges = []
        for r in self.W.simple_reflections():
          for w2 in self.W:
            single_edge = [w2.reduced_word(), (r*w2).reduced_word()]
            single_edge2 = [(r*w2).reduced_word(), w2.reduced_word()]
            list_of_outside_edges.append(single_edge)
            list_of_outside_edges.append(single_edge2)
        self.outside_edges = list_of_outside_edges


    def create(self):
        self.setModel()
        if self.real == True:
            self.buildRealModel()
        else:
            self.buildComplexModel()
        if not self.canPrint():
            print "This model has disconnected pieces and will not 3D print properly. Please try a lower dimension."


    def showModel(self):
        self.model.show(viewer="threejs", frame=False)

    def buildRealModel(self):
        def all_points():
          for r3 in self.W:
            key = "w" + str(r3.reduced_word())
            if self.model_points[key] == True:
              self.model += sphere(self.points[r3],.75,color='black')
            else:
              self.model += sphere(self.points[r3],.75,color='gray')


        self.model = line3d([(0,0,0),(0,0,0)])

        for r in self.reflections:
            key = "r" + str(r.reduced_word())
            if self.model_reflections[key] == True:
              for x in self.reflection_edges[r]:
                  if x in self.outside_edges and self.show_outside:
                      self.model += line3d([tuple(self.points[self.W.from_reduced_word(x[0])]), tuple(self.points[self.W.from_reduced_word(x[1])])], opacity=0.5, radius=self.outside_size,color = Color(self.reflection_colors[r]))
                  else:
                      self.model += line3d([tuple(self.points[self.W.from_reduced_word(x[0])]), tuple(self.points[self.W.from_reduced_word(x[1])])], opacity=0.5, radius=0.25,color = Color(self.reflection_colors[r]))
        all_points()
        if self.start == True:
          self.model += sphere(three_tuple(self.my_point), 1, color='gray')

    def buildComplexModel(self):
        the_object = Polyhedron(vertices=[[0,0,0]]).projection().render_solid_3d()
        for r in self.reflections:
            key = "r" + str(r.reduced_word())
            if self.model_reflections[key] == True:
                for x in self.reflection_edges[r]:
                    refl_verts = []
                    for i in range(r.order()):
                        refl_verts.append(list(self.points[self.W.from_reduced_word(x[i])]))
                    # if r.order() > 2: # change to iterating through refl_verts
                    #     the_object += line3d((refl_verts[0],refl_verts[1]))
                    #     refl_verts = makePolyhedron(refl_verts)

                    the_object += Polyhedron(vertices=refl_verts).projection().render_solid_3d(color=Color(self.reflection_colors[r]))
        self.model = the_object

        def makePolyhedron(orig_points):
            delta = .05
            new_points = []
            for point in orig_points:
                point1 = (point[0] + delta, point[1] + delta, point[2] + delta)
                point2 = (point[0] - delta, point[1] - delta, point[2] - delta)
                new_points.append()

    def setModel(self):
        if self.real == True:
            self.setRealModel()
        else:
            self.setComplexModel()

    def setComplexModel(self):
        RainBow = rainbow(len(list(self.reflections)))
        my_index = 0
        for r in self.reflections:
            self.reflection_colors[r] = RainBow[my_index]
            my_index = my_index+1
            reflection_loops = []
            group_elements_list = self.W.list()
            for w in self.W:
                if w in group_elements_list:
                    my_hyper_edge = []
                    for i in range(r.order()):
                        group_elements_list.remove(r^i*w)
                        my_hyper_edge.append((r^i*w).reduced_word())
                    reflection_loops.append(my_hyper_edge)
            self.reflection_edges[r] = reflection_loops

        As_4D_Real_Points = {}
        for w in self.W:
            a = CC(vector(w.matrix()*vector(self.my_point))[0]).real()
            b = CC(vector(w.matrix()*vector(self.my_point))[0]).imag()
            c = CC(vector(w.matrix()*vector(self.my_point))[1]).real()
            d = CC(vector(w.matrix()*vector(self.my_point))[1]).imag()
            new_point_4d = vector((a,b,c,d))
            As_4D_Real_Points[w] = new_point_4d

        # Projection vector. Change to input
        n = vector((1,-1,1,-1)).normalized()# this is the normal vector to whatever hyperplane we are using to project from 4D to 3D. We will want to be able to change this to find a "pretty" projection.
        points_in_hyperplane = {}
        for w in self.W:
            v = vector(As_4D_Real_Points[w])
            projected_point = v - v.dot_product(n)*n
            points_in_hyperplane[w] = projected_point

        self.points = {}
        for w in self.W:
            v = points_in_hyperplane[w]
            a = v[0]
            b = v[1]
            c = v[2]
            self.points[w] = (10*a,10*b,10*c)

    def setRealModel(self):
        mirror_vectors = []
        if self.lie_type == "A":
          mirrors = [(0,1,-1), (1,-1,0), (0,1,1)]  ## this is special for this group, sub in matrix manipulation for general/complex refl.
          for v in mirrors:
              mirror_vectors.append(vector(v).normalized())
        elif self.lie_type == "B":
          mirrors = [(1,-1,0), (0,1,-1),(0,0,1)]  ## this is special for this group, sub in matrix manipulation for general/complex refl.
          for v in mirrors:
              mirror_vectors.append(vector(v).normalized())

        def reflect_across(my_point,mirror_vector):
            return vector(my_point) - 2*vector(my_point).inner_product(mirror_vector)*mirror_vector


        List_of_Points = []
        if self.lie_type == "A":
          for w1 in self.W:
              word_length = len(w1.reduced_word())
              if word_length == 0:
                  List_of_Points.append(self.my_point)
              else:
                  new_point = copy(self.my_point)
                  for i in Sequence(1..word_length):
                      new_point = reflect_across(new_point,vector(mirror_vectors[w1.reduced_word()[i-1]-1]))
                  List_of_Points.append(new_point)
        if self.lie_type == "B":
          for w in self.W:
            new_point = vector(self.my_point) * w.matrix()
            List_of_Points.append(vector(three_tuple(tuple(new_point))))

        for j in range(len(list(self.W))):
            self.points[self.W[j]] = List_of_Points[j]

        RainBow = rainbow(len(self.reflections))
        my_index = 0
        for r in self.reflections:
            self.reflection_colors[r] = RainBow[my_index]
            my_index = my_index+1
            pairs = []
            for w in self.W:
                single_edge = [w.reduced_word(), (w*r).reduced_word()]
                if [(w*r).reduced_word(), w.reduced_word()] not in pairs:
                    pairs.append(single_edge)
            self.reflection_edges[r] = pairs

    ###  Export related
    def writeOpenSCADCode(self):
        size = .25
        for r in self.W.reflections():
            for x in self.reflection_edges[r]:
                self.code += "{color(" + str(list(Color(self.reflection_colors[r]).rgb())) + ")hull(){"
                if x in self.outside_edges:
                    size = .75
                else:
                    size = .25
                for i in range(r.order()):
                    substring = "translate(" + str(list(self.points[self.W.from_reduced_word(x[i])] )) + ")sphere(r="+str(size)+");"
                    self.code += substring
                end = "}}"
                self.code += end

    def writeOpenSCADDiv(self):
        # Print html with at least one character escaped,
        # for Firefox compatibility
        pretty_print(html('&lt;div id=scad hidden>'+self.code+"&lt;/div>"))

    def setObj(self):
        self.obj = self.model.obj()

def three_tuple(tup):
  new_tup = ()
  if len(tup) == 1:
    return tup + (0, 0)
  elif len(tup) == 2:
    return tup + (0,)
  else:
    return tup


def reflectionGroupTests():
    test = ReflectionGroupModel()
    test.printGroup()
    W = ReflectionGroup(['B',2])
    #W = ReflectionGroup((2,2,2))
    test.setGroup(W)
    test.setPoint((20,10,5))
    test.printGroup()
    test.create()
    test.showModel()

    # test2 = ReflectionGroupModel()
    # WW = ReflectionGroup((2,1,3))
    # test2.setGroup(WW, (20,10,5))
    # test2.printGroup()
    # test2.create()

#reflectionGroupTests()
