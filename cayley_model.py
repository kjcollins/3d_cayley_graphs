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

The point of entry for working with ReflectionGroup3d is
:func:`sage.combinat.root_system.reflection_group_real.ReflectionGroup`,
and similar objects.

EXAMPLES::
    Basic plot of a reflection group:
        sage: ReflectionGroup(['A',3])                             # optional - gap3
        Irreducible real reflection group of rank 3 and type A3
        sage: w = ReflectionGroup(['A',3])                         # optional - gap3
        sage: ReflectionGroup3d(w)
        Rigid graphical representation of Irreducible real reflection group of rank 3 and type A3
        sage: g = ReflectionGroup3d(w)
        sage: g.plot3d()
        Graphics3d Object

    G(3,1,2) (add tests of what is in this group):
        sage: g312 = ReflectionGroup((3,1,2))
        sage: g_plot = ReflectionGroup3d(g312, point=(21,11,31))
        doctest:warning
        ...
        UserWarning: Point was shortened to match group rank
        sage: g_plot.plot3d()
        Graphics3d Object

    G(6,2,2):
        sage: g622 = ReflectionGroup((6,2,2))
        sage: g_plot = ReflectionGroup3d(g622, point=(21,11,31))
        doctest:warning
        ...
        UserWarning: Point was shortened to match group rank
        sage: g_plot.plot3d()
        Graphics3d Object

    G4:
        sage: g4 = ReflectionGroup((4))
        sage: g_plot = ReflectionGroup3d(g4, point=(21,11,31))
        doctest:warning
        ...
        UserWarning: Point was shortened to match group rank
        sage: g_plot.plot3d()
        Graphics3d Object

    A1 x A1:
        sage: A1A1 = ReflectionGroup(['A',1], ['A',1])
        sage: g_plot = ReflectionGroup3d(A1A1, point=(21,11,31))
        doctest:warning
        ...
        UserWarning: Point was shortened to match group rank
        sage: g_plot.plot3d()
        Graphics3d Object

    A1 x A2:
        sage: A1A2 = ReflectionGroup(['A',1], ['A',2])
        sage: g_plot = ReflectionGroup3d(A1A2, point=(21,11,31))
        sage: g_plot.plot3d()
        Graphics3d Object

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
    - check developer guide for advice of where in Sage to submit this for review
    - implement addition of ReflectionGroup3d objects

    - note: changed proj plane default. see if we can notify why object doesn't appear
    with some planes?
    - also skewed initial point, that's important to avoid vertices overlapping

    tests for:
        - _verify_proj_plane

    To test:
        G(3,1,2)
        G(6,2,2)
        G4
        A1 x A1
        A1 x A2


    in tests:
        - check that optional package fails gracefully
        - check that the model isn't plotted unnecessarily (slows down testing)
        consider improving workflow for turning reflections on and off:
        currently g_plot.visibility(False, reflections=[g_plot.group.reflections()[1], g_plot.group.reflections()[6]])
"""

from sage.structure.sage_object import SageObject
# from sage.plot.plot3d.base import Graphics3d
from random import randint, seed
from time import time
import warnings
warnings.simplefilter("always")

from sage.combinat.root_system.reflection_group_complex import ComplexReflectionGroup, IrreducibleComplexReflectionGroup
from sage.combinat.root_system.reflection_group_real import RealReflectionGroup, IrreducibleRealReflectionGroup


class ReflectionGroup3d(SageObject): # could we inherit from something specific?
    def __init__(self, group, point=(21,11,31), proj_plane=[1,2,3,4]):
        """
        EXAMPLES::
            This class allows a user to plot a reflection group.
                sage: w = ReflectionGroup(['A',3])                         # optional - gap3
                sage: g = ReflectionGroup3d(w)
                sage: g.plot3d()
                Graphics3d Object

            The group, input point, and project plane can be changed:
                sage: w = ReflectionGroup(['A',3], point=(15,8, 18))       # optional - gap3
                sage: g = ReflectionGroup3d(w)

            Visualization parameters can be changed after the model is created:
                sage: w = ReflectionGroup(['A',3])                         # optional - gap3
                sage: g = ReflectionGroup3d(w)
                sage: g.edge_color('purple')
                sage: g.plot3d()
                Graphics3d Object
        """
        self._verify_group(group)
        self.group = group

        self._real_dimension(group)

        point = self._verify_point(group, point)
        self.init_point = vector(point) # decide about vector construction

        self._verify_proj_plane(proj_plane)
        self.proj_plane = proj_plane

        self.reflections = self.group.reflections()

        self.vertex_properties = {"radius":1.5,
                                  "shape":"sphere",
                                  "label":None,
                                  "visible":True,
                                  "position":None,
                                  "color":"gray"}
        self.vertices = {}
        self._construct_vertices_dict()

        self.edge_properties = {"edge_thickness":1,
                                "color":None,
                                "fill":True,
                                "fill_size": .5,
                                "boundaries": True, # TODO edge fill parameters implementation
                                "boundary_thickness":1,
                                "visible":True}
        # IDEA: only include "boundaries" if the group chosen has edges that can use them?

        # if x param exists: set it
        # else: add default
        self.edges = {}
        self._construct_edges_dict()

        self._outside_edges()


        # get methods, set methods, and how plot3d will take parameters
        # are the visualization things that the constructor doesn't cover


    def __repr__(self):
        return "Rigid graphical representation of %s"%(str(self.group))


    def __eq__(self, other):
        if self.is_isomorphic(other):
            return True
        else:
            return False


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
            Rigid graphical representation of Irreducible real reflection group of rank 3 and type C3

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


        TODO:
        - replace group_types with the list of categories we want to allow, rather than hardcoding from example groups

        """
        # group_types = [IrreducibleComplexReflectionGroup, IrreducibleRealReflectionGroup, ComplexReflectionGroup, RealReflectionGroup]
        group_types = [ReflectionGroup((3,1,2)).parent(),ReflectionGroup(["A",2]).parent(), ReflectionGroup(["A", 2], ["B", 1]).parent(), ReflectionGroup((6,2,2)).parent()]
        # print(g_cat for gcat.categories) ## TODO
        # if group.parent() in group_types:
        if type(group) in group_types:
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
            Rigid graphical representation of Irreducible real reflection group of rank 3 and type C3
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

        Boolean True if a usable 4-tuple is entered

        EXAMPLES:

        A zero vector cannot be used as the projection plane::
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3]), proj_plane=(0,0,0,0))
            Traceback (most recent call last):
            ...
            TypeError: A non-zero normal vector in R^4 is required to determine a plane.

        A vector in R^3 cannot be used as the projection plane::
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3]), proj_plane=(2,1,1))
            Traceback (most recent call last):
            ...
            TypeError: A non-zero normal vector in R^4 is required to determine a plane.


        """
        if len(plane) == 4:
            if [plane[k] in RR for k in range(4)] == [True, True, True, True]:
                if tuple(plane) != (0,0,0,0):
                    return True
        raise TypeError("A non-zero normal vector in R^4 is required to determine a plane.")



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
                # print "??", vector(tuple(pos)+((0,)*(3-len(pos))))
                return vector(tuple(pos)+((0,)*(3-len(pos))))
            elif self.real_dimension == 3:
                # print "?", pos
                return pos
            else:
                pos4d = vector((CC(pos[0]).real_part(), CC(pos[0]).imag_part(), CC(pos[1]).real_part(), CC(pos[1]).imag_part()))
                proj_pos4d = pos4d - vector(self.proj_plane).normalized().dot_product(pos4d)*vector(self.proj_plane).normalized()

                return vector([round(num,0) for num in proj_pos4d[0:3]])

        for key, value in self.vertex_properties.items():
            if key=="position":
                self.vertices[key] = \
                {v:pad_position(v, self.init_point) for v in self.group.list()}
                # TODO warn if same
                positions = [tuple(vec) for vec in self.vertices["position"].values()]
                if len(set(positions)) < len(positions):
                    warnings.warn("Vertex positions overlap. Use a different initial point to change.")
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
            coset = self.group.cosets(subgroup, side='right')
            self.reflection_edges[refl] = [tuple(e) for e in coset]

            cosets += coset
            i=1
            while i<refl.order():
                reflections.remove(refl**i)
                i+=1

        for key, value in self.edge_properties.items():
            if key=="color":
                self.edges[key] = {}
                rainbow_colors = rainbow(len(subgroups))
                for i, subgp in enumerate(subgroups):
                    color = rainbow_colors[i]
                    for e in self.group.cosets(subgp):
                        self.edges[key][tuple(e)] = color
            else:
                # defaults
                self.edges[key] = {tuple(e):value for e in cosets}


    def _outside_edges(self): # private creation method
        """
        Creates a dictionary which categorizes edges as begin 1-faces of the polytope,
        contained in 2-faces of the polytope, or internal to the structure.

        EXAMPLES:

        Check that every edge is either on the inside or outside::
            sage: W = ReflectionGroup(["A",3])
            sage: G = ReflectionGroup3d(W)
            sage: set(G.outside_edges()).intersection(set(G.inside_edges()))
            set()
            sage: len(G.outside_edges())+len(G.inside_edges()) == len(G.edges["color"])
            True

        Check that the 1-faces are also outside edges::
            sage: W = ReflectionGroup(["A",3])
            sage: G = ReflectionGroup3d(W)
            sage: set(G.one_faces()).issubset(G.outside_edges())
            True

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
        one_faces_list = []
        outside_list = []
        inside_list = []
        for k in self.group.reflections():
            S = self.group.subgroup([k])
            for j in range(len(self.group.cosets(S))):
                vertex_set = []
                for grp_elm in self.group.cosets(S)[j]:
                    coordinates = tuple(self.vertices["position"][grp_elm])
                    vertex_set.append(coordinates)
                # print vertex_set
                outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "internal edge"
                if set(vertex_set) in faces1_by_vertices:
                    outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "1-face"
                    one_faces_list.append(tuple(self.group.cosets(S)[j]))
                else:
                    for two_face in faces2_by_vertices:
                        if set(vertex_set).issubset(two_face):
                            outside_edge_dictionary[tuple(self.group.cosets(S)[j])] = "external edge"
                            outside_list.append(tuple(self.group.cosets(S)[j]))
                # print outside_edge_dictionary[tuple(self.group.cosets(S)[j])]

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
        one_faces = [i for i,j in self.outside_edge_dictionary.items() if j == "1-face"] # TODO could be saved state and not calculated twice
        if len(kwds) == 0:
            return one_faces
        if "color" in kwds:
            self.edge_color(color=kwds["color"],edges=one_faces)
        if "thickness" in kwds:
            self.edge_thickness(edge_thickness=kwds["thickness"], edges=one_faces)


    def outside_edges(self, **kwds):   # public get/set method

        """
        Allows user to change properties of edges that are on the exterior of the convex hull.

        If called without arguments, returns a list of such edges.

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
            0.5
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
            sage: G.edges["color"][G.inside_edges()[0]] == "red"
            True

        Cannot make all interior edges go away::
            sage: W = ReflectionGroup(["B",3])
            sage: G = ReflectionGroup3d(W)
            sage: G.inside_edges(thickness=0)
            Traceback (most recent call last):
            ...
            RuntimeError: Use visibility method to make edges disappear
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

        List all edges of the model::
            sage: w = ReflectionGroup(["A", 3])
            sage: g = ReflectionGroup3d(w)
            sage: g.list_edges()
            [((1,8,11)(2,5,7)(3,12,4)(6,10,9), (1,11)(3,10)(4,9)(5,7)(6,12)),
             ((), (1,4)(2,8)(3,5)(7,10)(9,11)),
             ((), (1,8)(2,7)(3,6)(4,10)(9,12)),
             ...
             ((), (1,11)(3,10)(4,9)(5,7)(6,12)),
             ((1,4,6)(2,3,11)(5,8,9)(7,10,12), (1,4)(2,8)(3,5)(7,10)(9,11)),
             ((2,5)(3,9)(4,6)(8,11)(10,12), (1,11,8)(2,7,5)(3,4,12)(6,9,10))]

        List the edges corresponding to one reflection in the model::
            sage: w = ReflectionGroup(["A", 3])
            sage: g = ReflectionGroup3d(w)
            sage: g.list_edges(g.group.reflections().values()[0])
            [((), (1,7)(2,4)(5,6)(8,10)(11,12)),
             ((2,5)(3,9)(4,6)(8,11)(10,12), (1,7)(2,6)(3,9)(4,5)(8,12)(10,11)),
             ((1,2,3,12)(4,5,10,11)(6,7,8,9), (1,8,11)(2,5,7)(3,12,4)(6,10,9)),
             ((1,2,10)(3,6,5)(4,7,8)(9,12,11), (1,8)(2,7)(3,6)(4,10)(9,12)),
             ((1,3,7,9)(2,11,6,10)(4,8,5,12), (1,9)(2,8)(3,7)(4,11)(5,10)(6,12)),
             ((1,3)(2,12)(4,10)(5,11)(6,8)(7,9), (1,9,7,3)(2,10,6,11)(4,12,5,8)),
             ((1,4,6)(2,3,11)(5,8,9)(7,10,12), (1,10,9,5)(2,6,8,12)(3,11,7,4)),
             ((1,4)(2,8)(3,5)(7,10)(9,11), (1,10,2)(3,5,6)(4,8,7)(9,11,12)),
             ((1,5,12)(2,9,4)(3,10,8)(6,7,11), (1,11)(3,10)(4,9)(5,7)(6,12)),
             ((1,5,9,10)(2,12,8,6)(3,4,7,11), (1,11,8)(2,7,5)(3,4,12)(6,9,10)),
             ((1,6)(2,9)(3,8)(5,11)(7,12), (1,12,5)(2,4,9)(3,8,10)(6,11,7)),
             ((1,6,4)(2,11,3)(5,9,8)(7,12,10), (1,12,3,2)(4,11,10,5)(6,9,8,7))]

        """
        if r == None:
            return self.edges["visible"].keys()
        try:
            return self.reflection_edges[r]
        except KeyError:
            raise KeyError("%s is not a reflection of this group."%str(r))


    def edge_thicknesses(self):
        """
        Returns the dictionary mapping edges to their set thicknesses.

        EXAMPLES:
            sage: w = ReflectionGroup(['A', 3])
            sage: g = ReflectionGroup3d(w)
            sage: g.edge_thicknesses()
            {((), (2,5)(3,9)(4,6)(8,11)(10,12)): 1,
             ((), (1,4)(2,8)(3,5)(7,10)(9,11)): 1,
             ((), (1,6)(2,9)(3,8)(5,11)(7,12)): 1,
             ((), (1,7)(2,4)(5,6)(8,10)(11,12)): 1,
             ...
             ((1,11,8)(2,7,5)(3,4,12)(6,9,10), (1,12,3,2)(4,11,10,5)(6,9,8,7)): 1,
             ((1,12,3,2)(4,11,10,5)(6,9,8,7), (1,12,5)(2,4,9)(3,8,10)(6,11,7)): 1}

        SEEALSO:
            :func:`~cayley_model.edge_thickness`
        """
        return self.edges["edge_thickness"]


    def edge_thickness(self, edge_thickness=None, **kwds):
        """
        Change the thickness of all edges.

        If called with no input, returns current edge thickness.
        New size of edge restricted to precision of 3.


        INPUTS:

        - ``positive real number`` -- the desired thickness

        EXAMPLES:

        Make all edges a given thickness::
            sage: w = ReflectionGroup(["A", 3])
            sage: g = ReflectionGroup3d(w)
            sage: g.edge_thickness()
            1
            sage: g.edge_thickness(0.05)
            sage: g.edge_thickness()
            0.05

        Make only some edges thicker::
            sage: outside = g.outside_edges()
            sage: g.edge_thickness(1, edges = outside)
            sage: g.edges["edge_thickness"]
            {((1,8,11)(2,5,7)(3,12,4)(6,10,9), (1,11)(3,10)(4,9)(5,7)(6,12)): 1.5,
            ((), (1,4)(2,8)(3,5)(7,10)(9,11)): 1.5, ((), (1,8)(2,7)(3,6)(4,10)(9,12)): 1.5,
            ((1,2,10)(3,6,5)(4,7,8)(9,12,11), (1,8)(2,7)(3,6)(4,10)(9,12)): 1.5,
            ((1,2,10)(3,6,5)(4,7,8)(9,12,11), (1,7)(2,4)(5,6)(8,10)(11,12)): 1.5,
            ((1,12,3,2)(4,11,10,5)(6,9,8,7), (1,12,5)(2,4,9)(3,8,10)(6,11,7)): 1.5,
            ((2,5)(3,9)(4,6)(8,11)(10,12), (1,6,4)(2,11,3)(5,9,8)(7,12,10)): 1.5,
            ((1,3)(2,12)(4,10)(5,11)(6,8)(7,9), (1,9,7,3)(2,10,6,11)(4,12,5,8)): 1.5,
            ((1,3)(2,12)(4,10)(5,11)(6,8)(7,9), (1,6)(2,9)(3,8)(5,11)(7,12)): 1.5,
            ((1,3)(2,12)(4,10)(5,11)(6,8)(7,9), (1,8)(2,7)(3,6)(4,10)(9,12)): 1.5,
            ((1,3,7,9)(2,11,6,10)(4,8,5,12), (1,9)(2,8)(3,7)(4,11)(5,10)(6,12)): 1.5,
            ((1,9)(2,8)(3,7)(4,11)(5,10)(6,12), (1,9,7,3)(2,10,6,11)(4,12,5,8)): 1.5,
            ((1,2,3,12)(4,5,10,11)(6,7,8,9), (1,5,12)(2,9,4)(3,10,8)(6,7,11)): 1.5,
            ((1,7)(2,6)(3,9)(4,5)(8,12)(10,11), (1,10,9,5)(2,6,8,12)(3,11,7,4)): 1.5,
            ((1,9,7,3)(2,10,6,11)(4,12,5,8), (1,11,8)(2,7,5)(3,4,12)(6,9,10)): 1.5,
            ((1,8)(2,7)(3,6)(4,10)(9,12), (1,10,2)(3,5,6)(4,8,7)(9,11,12)): 1.5,
            ((1,7)(2,4)(5,6)(8,10)(11,12), (1,10,2)(3,5,6)(4,8,7)(9,11,12)): 1.5,
            ((2,5)(3,9)(4,6)(8,11)(10,12), (1,4,6)(2,3,11)(5,8,9)(7,10,12)): 1.5,
            ((1,4,6)(2,3,11)(5,8,9)(7,10,12), (1,6)(2,9)(3,8)(5,11)(7,12)): 1.5,
            ((1,4)(2,8)(3,5)(7,10)(9,11), (1,9)(2,8)(3,7)(4,11)(5,10)(6,12)): 0.05,
            ...
            ((), (1,11)(3,10)(4,9)(5,7)(6,12)): 0.05,
            ((1,4,6)(2,3,11)(5,8,9)(7,10,12), (1,4)(2,8)(3,5)(7,10)(9,11)): 1.5,
            ((2,5)(3,9)(4,6)(8,11)(10,12), (1,11,8)(2,7,5)(3,4,12)(6,9,10)): 0.05}

        """

        if edge_thickness == None:
            return self.edge_properties["edge_thickness"]
        edge_thickness = round(edge_thickness, 3)
        if edge_thickness == 0:
            raise RuntimeError('Use visibility method to make edges disappear')
        if "reflections" in kwds:
            for r in kwds["reflections"]:
                for e in self.list_edges(r):
                    self.edges["edge_thickness"][e] = edge_thickness
        if "edges" in kwds:
            for e in kwds["edges"]:
                self.edges["edge_thickness"][e] = edge_thickness

        if len(kwds) == 0:
            self.edge_properties["edge_thickness"] = edge_thickness
            for e in self.edges["edge_thickness"].keys():
                self.edges["edge_thickness"][tuple(e)] = edge_thickness


    def visibility(self, visible, **kwds):
        """
        Sets visibility of edges, reflections, vertices, or groups of vertices on or off.

        INPUT:
            A boolean for whether the visibility of the selected object should
            be turned on (True) or off (False).

            An object or list of objects in the model.

        EXAMPLES:

            Make all vertices invisible:
                sage: U = ReflectionGroup((4))
                sage: J = ReflectionGroup3d(U,  point=(20,9,7))
                sage: V = J.vertices["color"].keys()
                sage: J.visibility(False, vertices = V)
                sage: J.plot3d()
                Graphics3d Object

            Make all edges invisible:
                sage: J.visibility(True, vertices = V)
                sage: E = J.edges["color"].keys()
                sage: J.visibility(False, edges = E)
                sage J.plot3d()
                Graphics3d Object

            Make all edges of a single reflection invisible:
                sage: B3 = ReflectionGroup(["B",3])
                sage: B = ReflectionGroup3d(B3)
                sage: r1 = B.reflections[1]
                sage: B.visibility(False, reflections = [r1])
                sage: B.plot3d()
                Graphics3d Object

            Make subset of edges invisible:
                sage: A3 = ReflectionGroup(["A",3])
                sage: A = ReflectionGroup3D(A3)
                sage: A.visibility(False, edges = A.inside_edges())
                sage: A.plot3d()
                Graphics3d Object

            Make subset of vertices invisible:
                sage: odd = [a for a in A if a.sign() == -1]
                sage: A.visibility(False, vertices = odd)
                sage: A.plot3d()
                Graphics3d Object


        """
        if visible == None:
            return self.edge_properties["visible"], self.vertex_properties["visible"]

        # if type(_object) == type([]):
            # pass

        if "reflections" in kwds:
            for r in kwds["reflections"]:
                for e in self.list_edges(r):
                    self.edges["visible"][e] = visible
        if "edges" in kwds:
            for e in kwds["edges"]:
                self.edges["visible"][e] = visible

        if "vertices" in kwds:
            for v in kwds["vertices"]:
                self.vertices["visible"][v] = visible
        #
        # if len(kwds) == 0:
        #     self.edge_properties["visible"] = visible
        #     for e in self.edges["visible"].keys():
        #         self.edges["visible"][tuple(e)] = visible


    def edge_colors(self):
        """
        Returns the dictionary mapping edges to their set colors.

        SEEALSO:
            :func:`~cayley_model.edge_color`

        EXAMPLES:

        Returns the default color dictionary::
            sage: W = ReflectionGroup((2,1,2))
            sage: G = ReflectionGroup3d(W)
            doctest:warning
            ...
            UserWarning: Point was shortened to match group rank
            sage: set(G.edge_colors().values()) == set(rainbow(len(G.reflections)))
            True

        ::
            sage: W = ReflectionGroup((2,1,2))
            sage: G = ReflectionGroup3d(W)
            doctest:warning
            ...
            UserWarning: Point was shortened to match group rank
            sage: G.edge_color("red")
            sage: G.edge_colors().values() == ['red'] * 16
            True
        """
        return self.edges["color"]


    def edge_color(self, color=None, **kwds):
        """
        Change the color of all edges.

        If called with no input, returns current color.

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
        order2 = 0
        order3 = 0

        for edge, visible in self.edges['visible'].items():
            if visible:
                if len(edge) == 2:
                    order2 += 1
                else:
                    order3 += 1
                x += self._create_edge(edge)

        # print "order 2", order2, "order 3", order3
        for vertex, visible in self.vertices['visible'].items():
            if visible:
                x += sphere(self.vertices["position"][vertex],
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
        if len(edge_points) == 2:
            # TODO parameters. KEEP INCLUDING MORE HERE
            return line3d(edge_points, color=self.edges["color"][coset], radius=self.edges["edge_thickness"][coset])
        else: # length is greater than 2
            edge_polyhedron = Polyhedron(vertices=edge_points)
            if len(edge_polyhedron.faces(2)) == 0:
                return line3d(edge_points, color=self.edges["color"][coset], radius=self.edges["edge_thickness"][coset])

            _object = sage.plot.plot3d.base.Graphics3dGroup([])
            if self.edges["fill"][coset]: #fix
                _object += self._thicken_polygon(edge_polyhedron, coset)
                #            self.edges["boundary_thickness"][coset])
            if self.edges["boundaries"][coset]: #fix
                _object += self._create_edge_boundaries(edge_polyhedron, coset)

            if not self.edges["fill"][coset] and not self.edges["boundaries"][coset]:
                raise NotImplementedError("Visible edge has neither fill nor boundary!")

            return _object # TODO parameters


    def _create_edge_boundaries(self, edge_polyhedron, coset):
        r"""
        Return graphics object with boundaries to a higher order edge (order>2).

        INPUT:

        - ``edge_polyhedron`` -- a :class:`Polyhedron`.

        OUTPUT:

        The edges, or boundaries, of the polyhedron as a graphics object.

        EXAMPLES:

            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3])) # long time
            sage: poly = Polyhedron(vertices = [[1, 2, 3], [0,1,0], [1,0,1]])
            sage: edge_boundaries = w._create_edge_boundaries(poly, w.edges["visible"].keys()[0])
            sage: edge_boundaries.all
            [Graphics3d Object]

        TODO:

        - provide more visualization options for object.
        """
        _object = sage.plot.plot3d.base.Graphics3dGroup([])
        # print edge_polyhedron.faces(1)

        # print edge_polyhedron.faces(2) # SHOULD BE TWO, changed while debugging projection
        edge_face = edge_polyhedron.faces(2)[0] # SHOULD BE TWO, changed while debugging projection
        v_list = list(edge_face.vertices())
        v_list.append(edge_face.vertices()[0])
        _object += line3d(v_list, color=self.edges["color"][coset], radius=1)

        return _object


    def _thicken_polygon(self, polytope_in_2d, coset):
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
            sage: poly_3d = w._thicken_polygon(p, w.edges["visible"].keys()[0]) # test had .01 as second arg originally?
            sage: poly_3d.all
            [Graphics3d Object, Graphics3d Object, Graphics3d Object, Graphics3d Object]

        TODO:

        - examples that better test what the graphics object contains
        """
        thickness = self.edges["boundary_thickness"][coset]
        fill = self.edges["fill_size"][coset]
        # print "COSET", str(coset)

        new_points = []
        # print polytope_in_2d.vertices()
        long_normal_vector = vector(CC,((vector(polytope_in_2d.vertices()[1]) - vector(polytope_in_2d.vertices()[0])).cross_product(vector(polytope_in_2d.vertices()[2]) - vector(polytope_in_2d.vertices()[0]))).normalized())
        rounded_vector = []
        for entry in list(long_normal_vector):
            rounded_vector.append(round(entry,3))
        normal_vector = vector(rounded_vector)

        for point in polytope_in_2d.vertices():
            point1 = vector(point) + fill*thickness*normal_vector
            point1 = vector([round(i,1) for i in point1])
            point2 = vector(point) - fill*thickness*normal_vector
            point2 = vector([round(i,1) for i in point2])
            # print (point1), (point2)
            new_points.append(point1)
            new_points.append(point2)

        w = Polyhedron(vertices = new_points)
        return w.plot(color=self.edges["color"][coset])
