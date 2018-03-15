r"""
Model building class for rigid 3d cayley graphs of reflection groups.

<Paragraph description>

EXAMPLES::

<Lots and lots of examples>

AUTHORS:

- YOUR NAME (2005-01-03): initial version

- person (date in ISO year-month-day format): short desc

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
        Return boolean of whether input can construct group
        (group itelf?)
        """
        return True


    def _verify_point(self, point):
        """
        Perform error checking on point input
        Return boolean of whether point is 3d
        (point itelf, if more permissive?)
        """
        return True
        # error check
        # accept 2d points and add third dimension?
        # or fail if not 3d point


    def _verify_proj_plane(self, plane):
        """
        Perform error checking on point input
        Return boolean of whether point is 3d
        (point itelf, if more permissive?)
        """
        return True
        #TODO raise warning


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
        """
        pass

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


    def _create_edge_boundaries(edge_polyhedron):
        # get 1faces of edge, and add to object
        _object = sage.plot.plot3d.base.Graphics3dGroup([])
        edge_face = edge_polyhedron.faces(2)[0]
        v_list = list(edge_face.vertices())
        v_list.append(edge_face.vertices()[0])
        _object += line3d(v_list, color="purple", radius=.1)
        return _object

    def _thicken_polygon(polytope_in_2d, thickness):
        new_points = []
        normal_vector = (vector(polytope_in_2d.vertices()[1]) - vector(polytope_in_2d.vertices()[0])).cross_product(vector(polytope_in_2d.vertices()[2]) - vector(polytope_in_2d.vertices()[0]))
        for point in polytope_in_2d.vertices():
            point1 = vector(point) + .5*thickness*normal_vector
            point2 = vector(point) - .5*thickness*normal_vector
            new_points.append(point1)
            new_points.append(point2)
        return Polyhedron(vertices = new_points).plot() #returns as a Graphics3d object
