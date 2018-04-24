"""
Model building class for rigid 3d Cayley graphs of reflection groups.

This class takes a reflection group and creates a rigid 3d model of the
Cayley graph. Vertex placement is determined by the group action on $\mathbb{R}^3$
and by default all reflections are included as generators. Higher order reflections
are represented as filled in polygons since the ultimate purpose of this package
is to create files that can be sent to a 3d printer and made "throwable," i.e.
physically printed. The class can handle real reflection groups of rank at most 3,
and complex reflection groups or rank at most 2, which are realized first in real
4d and then parallel projected into 3d for visualization and printing.

EXAMPLES::

<Lots and lots of examples>

AUTHORS:

- Kate Collins (2018-03-15): initial version
- Elizabeth Drellich (2018-03-15): initial version
- Eric Stucky (2018-03-15): initial version
- Kaisa Taipale (2018-03-15): initial version


TODO:
- Finish documenting what is implemented here
- implement setting vertex size, shape, and maybe one or two other parameters
- set defaults for how thickness of edges affects fill (later, more logic can
  be implemented)
- override default class methods for a few we might want (equality, addition)
- check developer guide for advice of where in Sage to submit this for review
"""

from sage.structure.sage_object import SageObject
from random import randint, seed
from time import time
import warnings


class ReflectionGroup3d(SageObject): # we might want to inherit from a more specific object. Graphics?
    """

    """
    def __init__(self, group, point=(20,10,30), proj_plane=[0,0,0,1]):
        self._verify_group(group)
        self.group = group

        self._real_dimension(group)

        point = self._verify_point(group, point)
        self.init_point = vector(point) # decide about vector construction

        self._verify_proj_plane(proj_plane)
        self.proj_plane = proj_plane

        self.reflections = self.group.reflections()

        self.vertex_properties = {"radius":10,
                                  "shape":"sphere",
                                  "label":None,
                                  "visible":True,
                                  "position":None,
                                  "color":"gray"}
        self.vertices = {}
        self._construct_vertices_dict()

        self.edge_properties = {"edge_thickness":.01,
                                "color":"gray",
                                "fill":True,
                                "fill_size": .05,
                                "boundaries": True,
                                "boundary_thickness":.01,
                                "visible":True}
        # IDEA: only include "boundaries" if the group chosen has edges that can use them?

        # if x param exists: set it
        # else: add default
        self.edges = {}
        self._construct_edges_dict()

        self._outside_edges()


        # get methods, set methods, and how plot3d will take parameters
        # are the visualization things that the constructor doesn't cover



    def _verify_group(self, group):
        """
        Perform error checking on group input
        Return boolean of whether input group can be represented in 3d

        INPUT:

        - ``group`` -- a group

        OUTPUT:

        Boolean True if W is a complex reflection group of rank at most 2 or a is_real
        reflection group of rank at most 3. If False, returns an error message.

        EXAMPLES:

        ::

            sage: W = ReflectionGroup(["C",3]) #long time
            sage: ReflectionGroup3d(W) #long time
            <class '__main__.ReflectionGroup3d'>

        If the group's rank is too big::

            sage: W = ReflectionGroup((5,1,3))
            sage: ReflectionGroup3d(W)
            Traceback (most recent call last):
            ...
            TypeError: Group must be real with rank < 4, or complex with rank < 3

        If the group is in the wrong format::

            sage: W = SymmetricGroup(4)
            sage: ReflectionGroup3d(W)
            Traceback (most recent call last):
            ...
            TypeError: Group should be defined as a ReflectionGroup

        """
        if group.parent() in [ReflectionGroup((3,1,2)).parent(),ReflectionGroup(["A",2]).parent()]:
            if group.rank() < 3:
                return True
            elif group.rank() == 3:
                if group.is_real():
                    return True
                else:
                    raise TypeError("Group must be real with rank < 4, or complex with rank < 3")
            else:
                raise TypeError("Group must be real with rank < 4, or complex with rank < 3")
        else:
            raise TypeError("Group should be defined as a ReflectionGroup")


    def _real_dimension(self, group):
        """
        Determines the real dimension of the groups

        INPUT:

        - ``group`` -- a group

        OUTPUT:

        Integer

        EXAMPLES:

        ::
            sage: W = ReflectionGroup(["C",3])
            sage: A = ReflectionGroup3d(W) # long time
            sage: A.real_dimension
            3

        ::
            sage: W = ReflectionGroup((3,1,2))
            sage: A = ReflectionGroup3d(W) # long time
            doctest:warning
            ...
            UserWarning: Point was shortened to match group rank
            sage: A.real_dimension
            4
        """
        if group.is_real() == True:
            self.real_dimension = group.rank()
        else:
            self.real_dimension = 2*group.rank()


    def _verify_point(self, group, point):
        """
        Perform error checking on point input
        If rank two reflection group, need 2d point
        else need 3d point

        INPUT:

        - ``group`` -- a group

        - ``point`` -- a tuple of integers

        OUTPUT:

        Boolean True if the group's rank is equal to the length of the tuple

        EXAMPLES:

        ::
            sage: W = ReflectionGroup(["C",3])
            sage: my_point = (1,2)
            sage: ReflectionGroup3d(W, my_point)
            Traceback (most recent call last):
            ...
            TypeError: Check dimension of point (does not match group rank)

        ::
            sage: W = ReflectionGroup(["C",3])
            sage: my_point_1 = (1,2,3)
            sage: ReflectionGroup3d(W, my_point_1) # long time
            <class '__main__.ReflectionGroup3d'>
        """
        if group.rank() == len(point):
            return point
        elif group.rank() < len(point):
            warnings.warn("Point was shortened to match group rank")
            return tuple(point[:group.rank()])
        else:
            raise TypeError("Check dimension of point (does not match group rank)")



    def _verify_proj_plane(self, plane):
        """
        Perform error checking on vector input
        Return boolean of whether vector is the normal to a hyperplane
        in 4d

        INPUT:

        - ``plane`` -- a tuple of integers

        OUTPUT:

        -

        """
        if len(plane) == 4:
            if [plane[k] in RR for k in range(4)] == [True, True, True, True]:
                if tuple(plane) != (0,0,0,0):
                    return True
                else:
                    raise TypeError("plane is determined by a non-zero normal vector in R^4")
            else:
                raise TypeError("plane is determined by a non-zero normal vector in R^4")
        else:
            raise TypeError("plane is determined by a non-zero normal vector in R^4")


    def _construct_vertices_dict(self):
        """
        Create a dictionary whose keys are properties, and whose values
        track the properties that individual vertices have.

        In particular, values are themselves dictionaries, whose keys
        are group elements and whose values are the values of the
        corresponding properties.


        OUTPUT:

        A dictionary whose keys are strings corresponding to graphical
        properties of the vertices in the 3d model, and whose values
        are dictionaries. The value-dictionary associated to a
        particular property consists of a group element and the value of
        the property at its corresponding vertex.


        EXAMPLES:

            sage: W = ReflectionGroup(["A",2])
            sage: G = ReflectionGroup3d(W, (3,2))
            sage: G.vertex_properties.keys()
            ['color', 'label', 'visible', 'shape', 'radius', 'position']
            sage: G.vertices["position"].values()
            [(-5, 3, 0), (5, -2, 0), (-3, 5, 0), (3, 2, 0), (2, -5, 0), (-2, -3, 0)]

        """
        def pad_position(v, point):
            pos = v.matrix()*point
            # tup_pos = tuple(v.matrix()*point)
            if self.real_dimension < 3:
                return vector(tuple(pos)+((0,)*(3-len(pos))))
            elif self.real_dimension == 3:
                return pos
            else:
                pos4d = vector((CC(pos[0]).real_part(), CC(pos[0]).imag_part(), CC(pos[1]).real_part(), CC(pos[1]).imag_part()))
                proj_pos4d = pos4d - vector(self.proj_plane).normalized().dot_product(pos4d)*pos4d.normalized()
                return proj_pos4d[0:3]

        for key, value in self.vertex_properties.items():
            if key=="position":
                self.vertices[key] = \
                {v:pad_position(v, self.init_point) for v in self.group.list()}
                # style?
            else:
                self.vertices[key] = {v:value for v in self.group.list()}

    def _construct_edges_dict(self):
        """
        Constructs the dictionary of edge properties.

        The dictionary maps properties edges can have, to dictionaries of
        the value of that property for each edge in the model. These are
        created based on the object defaults, and can be changed with
        set methods.

        EXAMPLES:

            sage: W = ReflectionGroup(["A",2])
            sage: G = ReflectionGroup3d(W, (3,2))
            sage: G.edge_properties.keys()
            ['boundary_thickness', 'color', 'boundaries', 'visible',
            'edge_thickness', 'fill_size', 'fill']
            sage: G.edges["visible"].keys()
            [((1,2,6)(3,4,5), (1,5)(2,4)(3,6)),
             ((), (1,5)(2,4)(3,6)),
             ((), (1,3)(2,5)(4,6)),
             ((1,3)(2,5)(4,6), (1,6,2)(3,5,4)),
             ((1,2,6)(3,4,5), (1,3)(2,5)(4,6)),
             ((1,5)(2,4)(3,6), (1,6,2)(3,5,4)),
             ((1,2,6)(3,4,5), (1,4)(2,3)(5,6)),
             ((1,4)(2,3)(5,6), (1,6,2)(3,5,4)),
             ((), (1,4)(2,3)(5,6))]

        TODO:
            - The properties for the edges should be able to be changed by user
              inputs in constructing the models, as well.
        """
        cosets = []

        reflections = self.group.reflections().list()
        subgroups = []
        self.reflection_edges = {}
        while reflections: # is nonempty
            refl = reflections[0]
            subgroup = self.group.subgroup([refl])
            subgroups.append(subgroup)
            coset = self.group.cosets(subgroup)
            self.reflection_edges[refl] = [tuple(e) for e in coset]

            cosets += coset
            i=1
            while i<refl.order():
                reflections.remove(refl**i)
                i+=1

        for key, value in self.edge_properties.items():
            if key=="color":
                self.edges[key] = {}
                acc = 0
                seed(time())
                for subgp in subgroups:
                    acc += 1
                    color = (randint(0,255), randint(0,255), randint(0,255))
                    for e in self.group.cosets(subgp):
                        self.edges[key][tuple(e)] = color
            else:
                # defaults
                self.edges[key] = {tuple(e):value for e in cosets}


    def _outside_edges(self): #if private, "create" method
                                # if public, return if known, create if uninitialized?
        """
        Creates a dictionary which categorizes edges as begin 1-faces of the polytope,
        contained in 2-faces of the polytope, or internal to the structure.
        """
        convex_bounding_polyhedron = Polyhedron(vertices = self.vertices["position"].values())
        outside_edge_dictionary = {}
        faces1_by_vertices = []
        faces2_by_vertices = []
        for face in (convex_bounding_polyhedron.faces(1)):
            face_vertices = []
            for i in range(len(face.vertices())):
                face_vertices.append(tuple(face.vertices()[i]))
            faces1_by_vertices.append(set(face_vertices))
        for face in (convex_bounding_polyhedron.faces(2)):
            face_vertices = []
            for i in range(len(face.vertices())):
                face_vertices.append(tuple(face.vertices()[i]))
            faces2_by_vertices.append(set(face_vertices))
        for k in self.group.reflections():
            S = self.group.subgroup([k])
            for j in range(len(self.group.cosets(S))):
                vertex_set = []
                for grp_elm in self.group.cosets(S)[j]:
                    coordinates = tuple(self.vertices["position"][grp_elm])
                    vertex_set.append(coordinates)
                if set(vertex_set) in faces1_by_vertices:
                    outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "1-face"
                elif set(vertex_set) not in faces1_by_vertices:
                    for two_face in faces2_by_vertices:
                        if set(vertex_set).issubset(two_face):
                            outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "external edge"
                        else:
                            outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "internal edge"

        self.outside_edge_dictionary = outside_edge_dictionary

    def one_faces(self, **kwds):
        """
        Allows user to change properties of edges that are a one-face of the convex hull.

        If called without arguements, returns a list of such edges.

        INPUTS:
        - ``color`` -- a color

        - ``thickness``  -- a non-negative real number

        EXAMPLES:

        Make only the edges that are 1-faces of the convex hull thicker::
            sage: W = ReflectionGroup(["B",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.one_faces(thickness=.5)
            sage: G.plot3d()
            Graphics3d Object

        Make only the edges that are 1-faces of the convex hull black::
            sage: W = ReflectionGroup(["B",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.one_faces(color="black")
            sage: G.plot3d()
            Graphics3d Object
                    """
        one_faces = [i for i,j in self.outside_edge_dictionary.items() if j == "1-face"]
        if len(kwds) == 0:
            return one_faces
        if "color" in kwds:
            self.edge_color(color=kwds["color"],edges=one_faces)
        if "thickness" in kwds:
            self.edge_thickness(edge_thickness=kwds["thickness"], edges=one_faces)

    def outside_edges(self, **kwds):
        """
        Allows user to change properties of edges that are on the exterior of the convex hull.

        If called without arguements, returns a list of such edges.

        INPUTS:

        - ``color`` -- a color

        - ``thickness`` -- a non-negative reall number

        EXAMPLES:

        ::
            sage: W = ReflectionGroup(["A",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.outside_edges(color = "black", thickness =.5)
            sage: G.edges["color"][G.outside_edges()[0]] == "black"
            True
            sage: G.edges["color"][G.inside_edges()[0]] == "black"
            False
            sage: G.edges["edge_thickness"][G.outside_edges()[0]]
            0.500000000000000
        """
        one_faces = [i for i,j in self.outside_edge_dictionary.items() if j == "1-face"]
        exterior_edges = [i for i,j in self.outside_edge_dictionary.items() if j == "external edge"]
        outside_edges = union(one_faces, exterior_edges)
        if len(kwds) == 0:
            return outside_edges
        if "color" in kwds:
            self.edge_color(color=kwds["color"],edges=outside_edges)
        if "thickness" in kwds:
            self.edge_thickness(edge_thickness=kwds["thickness"], edges=outside_edges)

    def inside_edges(self, **kwds):
        """
        Allows user to change properties of edges that are on the interior of the convex hull.

        If called without arguements, returns a list of such edges

        INPUTS:

        - ``color`` -- a color

        - ``thickness`` -- a non-negative reall number

        EXAMPLES:

        Making all interior edges the same color::
            sage: W = ReflectionGroup(["A",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.inside_edges(color="red")
            sage: G.G.edges["color"][G.inside_edges()[0]] == "red"
            True

        Making all interior edges go away::
            sage: W = ReflectionGroup(["B",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.inside_edges(thickness=0)
            sage: G.plot3d()
            Graphics3d Object

        """
        inside_edges = [i for i,j in self.outside_edge_dictionary.items() if j == "internal edge"]
        if len(kwds) == 0:
            return inside_edges
        if "color" in kwds:
            self.edge_color(color=kwds["color"],edges=inside_edges)
        if "thickness" in kwds:
            self.edge_thickness(edge_thickness=kwds["thickness"], edges=inside_edges)

    def list_edges(self, r=None):
        """
        Lists the edges of the current model. Lists edges corresponding to a
        single reflection, if specified.

        EXAMPLES:

        ::

        ::


        """
        if r == None:
            return self.edges["visible"].keys()
        # if r is in self.group.reflections():
        try:
            return self.reflection_edges[r]
        except KeyError:
            raise KeyError("%s is not a reflection of this group."%str(r))

    def edge_thicknesses(self):
        return self.edges["edge_thickness"]

    def edge_thickness(self, edge_thickness=None, **kwds):
        """
        Change the thickness of all edges.

        If called with no input, returns current edge thickness

        INPUTS:

        - ``positive real number`` -- the desired thickness

        EXAMPLES:

        ::

        ::

        """
        if edge_thickness == None:
            return self.edge_properties["edge_thickness"]
        if "reflections" in kwds:
            for r in kwds["reflections"]:
                for e in self.list_edges(r):
                    self.edges["edge_thickness"][e] = edge_thickness
        if "edges" in kwds:
            for e in kwds["edges"]:
                self.edges["edge_thickness"][e] = edge_thickness
#        self.edge_properties["edge_thickness"] = edge_thickness
#        for edge in self.edges["edge_thickness"].keys():
#            self.edges["edge_thickness"][edge] = edge_thickness


    def edge_colors(self):
        """
        Returns the dictionary mapping edges to their set colors.

        SEEALSO:
            :func:`~cayley_model.edge_color`
        """
        return self.edges["color"]


    def edge_color(self, color=None, **kwds):
        """
        Change the color of all edges.

        If called with no input, returns current color

        INPUTS:

        - ``color`` -- the desired color of all edges

        EXAMPLES:

        Changing colors of some reflections::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.edge_color("red", reflections=G.group.reflections().list()[:2])
                sage: G.edge_color("purple", reflections=G.group.reflections().list()[3:5])
                sage: G.edge_colors() # random


        Changing colors of all edges::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.edge_color("red")
                sage: G.edge_colors() # random

        Changing colors of a select few edges::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.edge_color("purple", edges=G.edges["visible"].keys()[3:5])
                sage: G.edge_colors() # random

        """
        if color == None:
            return self.edge_properties["color"]
        if "reflections" in kwds:
            for r in kwds["reflections"]:
                for e in self.list_edges(r): #make self.edges(r) return the list of edges for reflection r
                    self.edges["color"][e] = color
        if "edges" in kwds:
            for e in kwds["edges"]:
                self.edges["color"][e] = color
        if len(kwds) == 0:
            self.edge_properties["color"] = color
            for e in self.edges["color"].keys():
                self.edges["color"][tuple(e)] = color

    def vertex_colors(self):
        """
        Return the dictionary mapping vertices to their set colors.

        EXAMPLES:
        Return default colors::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.vertex_colors()
                {(): 'gray',
                 (2,5)(3,9)(4,6)(8,11)(10,12): 'gray',
                 (1,2,3,12)(4,5,10,11)(6,7,8,9): 'gray',
                 (1,2,10)(3,6,5)(4,7,8)(9,12,11): 'gray',
                 (1,3,7,9)(2,11,6,10)(4,8,5,12): 'gray',
                 (1,3)(2,12)(4,10)(5,11)(6,8)(7,9): 'gray',
                 (1,4,6)(2,3,11)(5,8,9)(7,10,12): 'gray',
                 (1,4)(2,8)(3,5)(7,10)(9,11): 'gray',
                 (1,5,12)(2,9,4)(3,10,8)(6,7,11): 'gray',
                 (1,5,9,10)(2,12,8,6)(3,4,7,11): 'gray',
                 (1,6)(2,9)(3,8)(5,11)(7,12): 'gray',
                 (1,6,4)(2,11,3)(5,9,8)(7,12,10): 'gray',
                 (1,7)(2,4)(5,6)(8,10)(11,12): 'gray',
                 (1,7)(2,6)(3,9)(4,5)(8,12)(10,11): 'gray',
                 (1,8,11)(2,5,7)(3,12,4)(6,10,9): 'gray',
                 (1,8)(2,7)(3,6)(4,10)(9,12): 'gray',
                 (1,9)(2,8)(3,7)(4,11)(5,10)(6,12): 'gray',
                 (1,9,7,3)(2,10,6,11)(4,12,5,8): 'gray',
                 (1,10,2)(3,5,6)(4,8,7)(9,11,12): 'gray',
                 (1,10,9,5)(2,6,8,12)(3,11,7,4): 'gray',
                 (1,11)(3,10)(4,9)(5,7)(6,12): 'gray',
                 (1,11,8)(2,7,5)(3,4,12)(6,9,10): 'gray',
                 (1,12,3,2)(4,11,10,5)(6,9,8,7): 'gray',
                 (1,12,5)(2,4,9)(3,8,10)(6,11,7): 'gray'}

        Return colors after some have been set individually:
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.vertex_color("red", vertices=G.group.list()[:2])
                sage: G.vertex_color("purple", vertices=G.group.list()[3:5])
                sage: G.vertex_colors()
                {(): 'red',
                 (2,5)(3,9)(4,6)(8,11)(10,12): 'red',
                 (1,2,3,12)(4,5,10,11)(6,7,8,9): 'gray',
                 (1,2,10)(3,6,5)(4,7,8)(9,12,11): 'gray',
                 (1,3,7,9)(2,11,6,10)(4,8,5,12): 'gray',
                 (1,3)(2,12)(4,10)(5,11)(6,8)(7,9): 'gray',
                 (1,4,6)(2,3,11)(5,8,9)(7,10,12): 'gray',
                 (1,4)(2,8)(3,5)(7,10)(9,11): 'gray',
                 (1,5,12)(2,9,4)(3,10,8)(6,7,11): 'gray',
                 (1,5,9,10)(2,12,8,6)(3,4,7,11): 'gray',
                 (1,6)(2,9)(3,8)(5,11)(7,12): 'gray',
                 (1,6,4)(2,11,3)(5,9,8)(7,12,10): 'purple',
                 (1,7)(2,4)(5,6)(8,10)(11,12): 'purple',
                 (1,7)(2,6)(3,9)(4,5)(8,12)(10,11): 'gray',
                 (1,8,11)(2,5,7)(3,12,4)(6,10,9): 'gray',
                 (1,8)(2,7)(3,6)(4,10)(9,12): 'gray',
                 (1,9)(2,8)(3,7)(4,11)(5,10)(6,12): 'gray',
                 (1,9,7,3)(2,10,6,11)(4,12,5,8): 'gray',
                 (1,10,2)(3,5,6)(4,8,7)(9,11,12): 'gray',
                 (1,10,9,5)(2,6,8,12)(3,11,7,4): 'gray',
                 (1,11)(3,10)(4,9)(5,7)(6,12): 'gray',
                 (1,11,8)(2,7,5)(3,4,12)(6,9,10): 'gray',
                 (1,12,3,2)(4,11,10,5)(6,9,8,7): 'gray',
                 (1,12,5)(2,4,9)(3,8,10)(6,11,7): 'gray'}

        """
        return self.vertices["color"]

    def vertex_color(self, color=None, **kwds):
        """
        Set the vertex color for all vertices.

        If called with no input, return the current model vertex color setting.

        INPUT:

        - ``color`` - an RGB color 3-tuple, where each tuple entry
            is a float between 0 and 1.
        - ``vertices`` - a list of vertices to change to the color.

        EXAMPLES:

        Change all the vertex colors to red::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.vertex_color("red")

        Change some to red::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.vertex_color("red", vertices=G.group.list()[:2])

        Get current model vertex color::
                sage: W = ReflectionGroup(['A',3])
                sage: G = ReflectionGroup3d(W) # long time
                sage: G.vertex_color("purple")
                sage: G.vertex_color()
                'purple'

        TODO: this example.
        """

        if color is None:
            try:
                return self.vertex_properties["color"]
            except KeyError:
                self.vertex_properties["color"] = "gray"
                self.vertices["color"] = {v:color for v in self.group.list()}
                return self.vertex_properties["color"]
        # self.vertex_properties["color"]=rgbcolor(c)
        if "vertices" in kwds:
            for v in kwds["vertices"]:
                self.vertices["color"][v] = color
        if len(kwds) == 0:
            self.vertex_properties["color"] = color
            for v in self.group.list():
                self.vertices["color"][v] = color



    def plot3d(self):
        """
        Create a graphics3dGroup object that represents the reflection
        group, according to chosen visualization parameters.

        This method does not take inputs; changes to parameters should
        be made using the setter methods.

        (2018-03-15): Setter methods are not currently implemented.

        EXAMPLES:

            sage: W = ReflectionGroup(['A',3])
            sage: G = ReflectionGroup3d(W) # long time
            sage: G.plot3d() #long time
            Graphics3d Object

        ::

            sage: W = ReflectionGroup(['A',3])
            sage: G = ReflectionGroup3d(W) # long time
            sage: G.plot3d() #long time
            Graphics3d Object


        SEEALSO:
            :func:`~sage.graphs.generic_graphs.GenericGraph.plot3d`


        TODO:
            Permit 4d real and 2d complex reflection group visualization
            using
                - Orthogonal projection using proj_plane
                - Schlegel projection
                - Stereographic projection

        """
        x = sage.plot.plot3d.base.Graphics3dGroup([])

        for edge, visible in self.edges['visible'].items():
            if visible:
                x += self._create_edge(edge)

        for vertex, visible in self.vertices['visible'].items():
            if visible:
                x += point3d(self.vertices["position"][vertex],
                                color = self.vertices["color"][vertex],
                                size = self.vertices["radius"][vertex])
        return x

    def _create_edge(self, coset):
        r"""
        Returns graphics edge object based on order of edge.

        INPUT:

        - ``coset`` -- a tuple defining the edge of a reflection group.

        OUTPUT:

        The edge of the reflection group as a graphics object.

        EXAMPLES:

        ::
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3])) # long time
            sage: edge = w._create_edge(w.edges["visible"].keys()[0])
            sage: print(edge.jmol_repr(edge.default_render_params())) # TODO: this color is generated randomly. Need to test better
            ['draw line_1 diameter 1 curve {-10.0 40.0 -60.0}  {-40.0 10.0 -30.0} ',
             'color $line_1  [102,102,255]']

        ::
            sage:
            sage:
            sage:

        """
        edge_points = [self.vertices["position"][coset_elt] for coset_elt in coset]
        if len(coset) == 2:
            # TODO parameters. KEEP INCLUDING MORE HERE
            return line3d(edge_points, color=self.edges["color"][coset], radius=self.edges["edge_thickness"][coset])
        else: # length is greater than 2
            _object = sage.plot.plot3d.base.Graphics3dGroup([])
            edge_polyhedron = Polyhedron(vertices=edge_points)
            if self.edges["fill"][coset]: #fix
                _object += self._thicken_polygon(edge_polyhedron,
                            self.edges["boundary_thickness"][coset])
            if self.edges["boundaries"][coset]: #fix
                _object += self._create_edge_boundaries(edge_polyhedron)

            if not self.edges["fill"][coset] and not self.edges["boundaries"][coset]:
                raise NotImplementedError("Visible edge has neither fill nor boundary!")

            return _object # TODO parameters


    def _create_edge_boundaries(self, edge_polyhedron):
        r"""
        Return graphics object with boundaries to a higher order edge (order>2).

        INPUT:

        - ``edge_polyhedron`` -- a :class:`Polyhedron`.

        OUTPUT:

        The edges, or boundaries, of the polyhedron as a graphics object.

        EXAMPLES:

            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3])) # long time
            sage: poly = Polyhedron(vertices = [[1, 2, 3], [0,1,0], [1,0,1]])
            sage: edge_boundaries = w._create_edge_boundaries(poly)
            sage: edge_boundaries.all
            [Graphics3d Object]

        TODO:

        - provide more visualization options for object.
        """
        _object = sage.plot.plot3d.base.Graphics3dGroup([])
        edge_face = edge_polyhedron.faces(2)[0]
        v_list = list(edge_face.vertices())
        v_list.append(edge_face.vertices()[0])
        _object += line3d(v_list, color="purple", radius=.1)

        return _object

    def _thicken_polygon(self, polytope_in_2d, thickness):
        """
        Return graphics object representing polyhedron in 3d with thickness.

        INPUT:

        - ``polytope_in_2d`` -- a :class:`Polyhedron`.

        OUTPUT:

        A graphics3dGroup object of the same polyhedron in 3d.

        EXAMPLES:

        Example of a polygon edge::
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3])) # long time
            sage: p = Polyhedron(vertices = [[1, 2, 3], [0,1,0], [1,0,1]])
            sage: poly_3d = w._thicken_polygon(p, .01)
            sage: poly_3d.all
            [Graphics3d Object, Graphics3d Object, Graphics3d Object, Graphics3d Object]

        TODO:

        - examples that better test what the graphics object contains
        """
        new_points = []
        long_normal_vector = vector(CC,((vector(polytope_in_2d.vertices()[1]) - vector(polytope_in_2d.vertices()[0])).cross_product(vector(polytope_in_2d.vertices()[2]) - vector(polytope_in_2d.vertices()[0]))).normalized())
        rounded_vector = []
        for entry in list(long_normal_vector):
            rounded_vector.append(round(entry,3))
        normal_vector = vector(rounded_vector)

        for point in polytope_in_2d.vertices():
            point1 = vector(point) + .5*thickness*normal_vector
            point2 = vector(point) - .5*thickness*normal_vector
            new_points.append(point1)
            new_points.append(point2)

        return Polyhedron(vertices = new_points).plot()
