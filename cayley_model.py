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

- Note for developers (and anyone else confused by Sage doc testing):
sage -t --long --optional=mpir,python2,sage,gap3 --debug cayley_model.py
is the line that tests everything in this file. Remove the "--debug" option
if you don't want to try to interactively debug errors.

"""

from sage.structure.sage_object import SageObject
from random import randint, seed
from time import time
import warnings


class ReflectionGroup3d(SageObject): # we might want to inherit from an object. Graphics?
    """docstring for """
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
        # if x param exists: set it
        # else: add default
        self.edges = {}
        self._construct_edges_dict()

        self.outside_edges = {}


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

            sage: W = ReflectionGroup((5,1,3)) #long time
            sage: ReflectionGroup3d(W) #long time
            Traceback (most recent call last):
            ...
            TypeError: Group must be real with rank < 4, or complex with rank < 3

        If the group is in the wrong format::

            sage: W = SymmetricGroup(4) #long time
            sage: ReflectionGroup3d(W) #long time
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
            sage: A = ReflectionGroup3d(W)
            sage: A.real_dimension
            3

        ::
            sage: W = ReflectionGroup((3,1,2))
            sage: A = ReflectionGroup3d(W)
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
            sage: W = ReflectionGroup(["C",3]) #long time
            sage: my_point = (1,2)
            sage: ReflectionGroup3d(W, my_point) #long time
            Traceback (most recent call last):
            ...
            TypeError: Check dimension of point (does not match group rank)

        ::
            sage: W = ReflectionGroup(["C",3]) #long time
            sage: my_point_1 = (1,2,3)
            sage: ReflectionGroup3d(W, my_point_1) #long time
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
        """
        cosets = []

        reflections = self.group.reflections().list()
        subgroups = []
        while reflections: # is nonempty
            refl = reflections[0]
            subgroup = self.group.subgroup([refl])
            subgroups.append(subgroup)
            cosets += self.group.cosets(subgroup)
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
        for k in self.W.reflections():
            S = self.W.subgroup([k])
            for j in range(len(self.W.cosets(S))):
                vertex_set = []
                for grp_elm in self.W.cosets(S)[j]:
                    coordinates = tuple(self.vertices["position"][grp_elm])
                    vertex_set.append(coordinates)
                if set(vertex_set) in faces1_by_vertices:
                    outside_edge_dictionary[tuple(self.W.cosets(S)[j])] = "1-face"
                elif set(vertex_set) not in faces1_by_vertices:
                    for two_face in faces2_by_vertices:
                        if set(vertex_set).issubset(two_face):
                            outside_edge_dictionary[tuple(self.W.cosets(S)[j])] = "external edge"
                        else:
                            outside_edge_dictionary[tuple(self.W.cosets(S)[j])] = "internal edge"

        return outside_edge_dictionary




    def edge_thickness(self, edge_thickness=None):
        """
        Change the thickness of all edges.

        If called with no input, returns current edge thickness

        INPUTS:

        - ``positive real number`` -- the desired thickness

        EXAMPLS:

        ::

        ::

        """
        if edge_thickness == None:
            return self.edge_properties["edge_thickness"]
        self.edge_properties["edge_thickness"] = edge_thickness
        self.edges["edge_thickness"] = {tuple(e):edge_thickness for e in cosets}

    def edge_colors(self):
        return self.edges["color"]

    def edge_color(self, color=None, **kwds):
        """
        Change the color of all edges.

        If called with no input, returns current color

        INPUTS:

        - ``color`` -- the desired color of all edges

        EXAMPLS:

        ::

        ::

        """
        if color == None:
            return self.edge_properties["color"]
        if "reflections" in kwds:
            for r in kwds["reflections"]:
                for e in self.edges(r): #make self.edges(r) return the list of edges for reflection r
                    self.edges["color"][e] = color
        if "edges" in kwds:
            for e in kwds[]"edges"]:
                self.edges["color"][e] = color
        if len(kwds) == 0:
            self.edge_properties["color"] = color
            self.edges["color"] = {tuple(e):color for e in cosets}

    def vertex_colors(self, color=None):
        """
        Set the vertex color for all vertices.

        If called with no input, return the current model vertex color setting.

        INPUT:

        - ``color`` - an RGB color 3-tuple, where each tuple entry
            is a float between 0 and 1.

        EXAMPLES: Change all the vertex colors to red.

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

            sage: W = ReflectionGroup(['A',3]) #optional - gap3
            sage: G = ReflectionGroup3d(W) #long time
            sage: G.plot3d() #long time
            Graphics3d Object

        ::

            sage: W = ReflectionGroup(['A',3]) #optional - gap3
            sage: G = ReflectionGroup3d(W) #long time
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
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3]))
            sage: edge = w._create_edge(w.edges["visible"].keys()[0])
            sage: edge.jmol_repr(edge.default_render_params())
            ['draw line_1 diameter 1 curve {-1.0 4.0 -6.0}  {-4.0 1.0 -3.0} ',
             'color $line_1  [102,102,255]']

        ::
            sage:
            sage:
            sage:

        """
        edge_points = [self.vertices["position"][coset_elt] for coset_elt in coset]
        if len(coset) == 2:
            return line3d(edge_points) # TODO parameters
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

        ::
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3]))
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
            sage: w = ReflectionGroup3d(ReflectionGroup(["A", 3]))
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
