"""
Model building class for rigid 3d Cayley graphs of reflection groups.

This class takes a reflection or Weyl group and creates a rigid 3d model of the
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

"""

from sage.structure.sage_object import SageObject
from random import randint, seed
from time import time


class ReflectionGroup3d(SageObject): # we might want to inherit from an object. Graphics?
    """docstring for """
    def __init__(self, group, point=(2,1,3), proj_plane=[0,0,0,1]):
        self._verify_group(group):
        self.group = group

        self._verify_point(group, point):
        self.init_point = vector(point) # decide about vector construction

        self._verify_proj_plane(proj_plane):
        self.proj_plane = proj_plane

        self.reflections = self.group.reflections()

        self.vertex_properties = {"radius":1,
                                  "shape":"sphere",
                                  "label":None,
                                  "visible":True,
                                  "position":None,
                                  "color":"gray"}
        self.vertices = {}
        self._construct_vertices_dict()

        self.edge_properties = {"edge_thickness":.5,
                                "color":"gray",
                                "fill":True,
                                "fill_size": .5,
                                "boundaries": True,
                                "boundary_thickness":.5,
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

            sage: W = WeylGroup(["C",3])
            sage: ReflectionGroup3d(W)

        If the group's rank is too big::

            sage: W = ReflectionGroup((5,1,3))
            sage: ReflectionGroup3d(W)
            TypeError: Group must be real with rank < 4, or complex with rank < 3

        If the group is in the wrong format::

            sage: W = SymmetricGroup(4)
            sage: ReflectionGroup3d(W)
            TypeError: Group should be defined as a WeylGroup or ReflectionGroup

        """
        if group.parent() in [WeylGroup(["A",2]).parent(), ReflectionGroup((3,1,2)).parent(),ReflectionGroup(["A",2]).parent()]:
            if group.rank() < 3:
                return True
            elif group.rank() == 3:
                if group.is_real():
                    return True
            else:
                raise TypeError("Group must be real with rank < 4, or complex with rank < 3")
        else:
            raise TypeError("Group should be defined as a WeylGroup or ReflectionGroup")



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

            sage: W = WeylGroup(["C",3])
            sage: my_point = (1,2)
            sage: ReflectionGroup3d(W, point=my_point)
            TypeError: Check dimension of point (does not match group rank)

        ::

            sage: W = WeylGroup(["C",3])
            sage: my_point = (1,2,3)
            sage: ReflectionGroup3d(W, point=my_point)


        """
        if group.rank() == len(point):
            return True
    	elif group.rank() < len(point):
            self.point = tuple(point[:group.rank()-1])
            raise UserWarning("Point was shortened to match group rank")
            return True
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

        Boolean True if plane is the normal vector of a suitable hyperplane for
        projecting the final object into three dimensions.

        EXAMPLES:

        ::

            sage: W = ReflectionGroup(3,1,2)
            sage: ReflectionGroup3d(W, plane=(1,2,3,4))

        ::

            sage: W = ReflectionGroup(3,1,2)
            sage: ReflectionGroup3d(W, plane=(0,0,0,0))
            TypeError: plane is determined by a non-zero normal vector in R^4

        ::

            sage: W = ReflectionGroup(3,1,2)
            sage: ReflectionGroup3d(W, plane=(1,2,3))
            TypeError: plane is determined by a non-zero normal vector in R^4

        ::

            sage: W = ReflectionGroup(3,1,2)
            sage: ReflectionGroup3d(W, plane=(1,2,3,sqrt(-3)))
            TypeError: plane is determined by a non-zero normal vector in R^4

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
        Generates dictionary of vertex properties.

        INPUT:

        OUTPUT:

        """
        # keys are possible properties of vertices
        # values are a second dictionary with vertices mapped
        # to the value of that property
        for key, value in self.vertex_properties.items():
            if key=="position":
                self.vertices[key] = \
                {v:v.matrix()*self.init_point for v in self.group.list()}
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
                reflections.remove(refl^i)
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

    def plot3d(self):
        """
        Creates graphics3dGroup object that represents the reflection
        group, according to chosen visualization parameters.

        This method does not take inputs; changes to parameters should
        be made using the setter methods.

        (2018-03-15): Setter methods are not currently implemented.
        ***** EXAMPLES HAVE NOT BEEN PROPERLY TESTED.

        EXAMPLES:

            sage: W = ReflectionGroup3d(ReflectionGroup(['A',3]))
            sage: W.plot3d() #long time
            Graphics3d Object

        ::

            sage: W = ReflectionGroup3d(ReflectionGroup(['A',3]))
            sage: W.plot3d() #long time
            Graphics3d Object


        SEEALSO:
            :func:`~sage.graphs.generic_graphs.GenericGraph.plot3d`


        TODO:
            Permit 4d real and 2d complex reflection group visualization
            using proj_plane or a Schlegel projection

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
                _object += _thicken_polygon(edge_polyhedron,
                            self.edges["thickness"][coset])
            if self.edges["boundaries"][coset]: #fix
                _object += _create_edge_boundaries(edge_polyhedron)

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
        r"""
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
        verts = polytope_in_2d.vertices()
        normal_vector = (vector(verts[1]) - \
                         vector(verts[0])).cross_product(vector(verts[2]) \
                          - vector(verts[0]))

        for point in polytope_in_2d.vertices():
            point1 = vector(point) + .5*thickness*normal_vector
            point2 = vector(point) - .5*thickness*normal_vector
            new_points.append(point1)
            new_points.append(point2)

        return Polyhedron(vertices = new_points).plot()
