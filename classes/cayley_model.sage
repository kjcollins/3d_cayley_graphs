r"""
Model building class for rigid 3d cayley graphs of reflection groups.

<Paragraph description>

EXAMPLES::

<Lots and lots of examples>

AUTHORS:

- Kate Collins (2018-03-15): initial version
- Elizabeth Drellich (2018-03-15): initial version
- Eric Stucky (2018-03-15): initial version
- Kaisa Taipale (2018-03-15): initial version

"""

from sage.structure.sage_object import SageObject
from random import randint, randrange, seed
from time import time


class ReflectionGroup3d(SageObject): # we might want to inherit from an object. Graphics?
    """docstring for """
    def __init__(self, group, point=(2,1,3), proj_plane=[0,0,0,1]):
        if self._verify_group(group):
            self.group = group
        else:
            # TODO find better error, and style of raising it
            raise TypeError("Group input does not specify reflection group.")

        if self._verify_point(point):
            self.init_point = vector(point) # decide about vector construction
        else:
            raise TypeError("Point not valid.")

        if self._verify_proj_plane(proj_plane):
            self.proj_plane = proj_plane
        else:
            raise TypeError("Projection plane not valid.")
            # any other errors externally?

        self.reflections = self.group.reflections()

        self.vertex_properties = {"radius":1, "shape":"sphere", "label":None, "visible":True, "position":None, "color":"gray"}
        self.vertices = {}
        self._construct_vertices_dict() # design?

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

        - ''group'' -- a group

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
            TypeError: "Group should be defined as a WeylGroup or ReflectionGroup"

        """
        if group.parent() in [WeylGroup(["A",2]).parent(), ReflectionGroup((3,1,2)).parent(),ReflectionGroup(["A",2]).parent()]:
            if group.rank() < 3:
                return True
            elif group.rank() == 3:
                if group.is_real():
                    return True
            else:
                return False
                raise TypeError("Group must be real with rank < 4, or complex with rank < 3")
        else:
            raise TypeError("Group should be defined as a WeylGroup or ReflectionGroup")


    def _verify_point(self, group, point):
        """
        Perform error checking on point input
        Return boolean of whether point is appropriate for group
	    If rank two reflection group, need 2d point
        else need 3d point

        INPUT:

        - ''group'' -- a group

        - ''point'' -- a tuple of integers

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
    	else:
	        return False
	        raise TypeError("Check dimension of point (does not match group rank)")


    def _verify_proj_plane(self, plane):
        """
        Perform error checking on vector input
        Return boolean of whether vector is the normal to a hyperplane
        in 4d

        INPUT:

        - "plane" -- a tuple of integers

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
                    return False
                    raise TypeError("plane is determined by a non-zero normal vector in R^4")
            else:
                return False
                raise TypeError("plane is determined by a non-zero normal vector in R^4")
        else:
            return False
            raise TypeError("plane is determined by a non-zero normal vector in R^4")


    def _construct_vertices_dict(self):
        """
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
            print cosets
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
                    print acc, len(subgp), subgp
                    color = (randrange(0,255,1), randint(0,255), randint(0,255))
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
        Creates graphics3dGroup object that represents the reflection group,
        according to chosen visualization parameters
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
        """
        Creates edge object. Handles logic of order of edge --> how edge
        is constructed
        returns graphics 3d object that is just one edge
        """
        edge_points = [self.vertices["position"][coset_elt] for coset_elt in coset]
        if len(coset) == 2:
            return line3d(edge_points) # parameters
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

            #.projection().render_solid_3d(color=Color(self.reflection_colors[r]))
            return _object #parameters


    def _create_edge_boundaries(self, edge_polyhedron):
        # get faces of edge, and add to object
        r"""
        Return graphics object with boundaries to a higher order edge (order>2).

        INPUT:

        - ``edge_polyhedron`` -- a :class:`Polyhedron`.

        OUTPUT:

        The edges, or boundaries, of the polyhedron as a graphics object.

        EXAMPLES:


        """
        _object = sage.plot.plot3d.base.Graphics3dGroup([])
        edge_face = edge_polyhedron.faces(2)[0]
        v_list = list(edge_face.vertices())
        v_list.append(edge_face.vertices()[0])
        _object += line3d(v_list, color="purple", radius=.1)
        return _object

    def _thicken_polygon(polytope_in_2d, thickness):
        r"""
        """
        new_points = []
        normal_vector = (vector(polytope_in_2d.vertices()[1]) - vector(polytope_in_2d.vertices()[0])).cross_product(vector(polytope_in_2d.vertices()[2]) - vector(polytope_in_2d.vertices()[0]))
        for point in polytope_in_2d.vertices():
            point1 = vector(point) + .5*thickness*normal_vector
            point2 = vector(point) - .5*thickness*normal_vector
            new_points.append(point1)
            new_points.append(point2)
        return Polyhedron(vertices = new_points).plot() #returns as a Graphics3d object
