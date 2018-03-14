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
from random import randint


class ReflectionGroup3d(SageObject): # we might want to inherit from an object. Graphics?
    """docstring for """
    def __init__(self, group, point=(2,1,3), proj_plane=[0,0,0,1]):
        if self._verify_group(group):
            self.group = group
        else:
            # TODO find better error, and style of raising it
            raise TypeError("Group input does not specify reflection group.")

        if self._verify_point(point):
            self.init_point = point
        else:
            raise TypeError("Point not valid.")

        if self._verify_plane(proj_plane):
            self.proj_plane = proj_plane
        else:
            raise TypeError("Projection plane not valid.")
            # any other errors externally?

        self.reflections = self.group.reflections()

        self.vertex_properties = {"radius":1, "shape":"sphere", "label":None, "visible":True, "position":None}
        self.vertices = self._construct_vertices_dict() # design?

        self.edge_properties = {"thickness":.5, "color":"gray", "fill":True, "visible":True}
        self.edges = self._construct_edges_dict()

        self.outside_edges = {}

        # get methods, set methods, and how plot3d will take parameters
        # are the visualization things that the constructor doesn't cover



    def _verify_group(self, group):
        """
        Perform error checking on group input
        Return boolean of whether input can construct group
        (group itelf?)
        """
        pass


    def _verify_point(self, point):
        """
        Perform error checking on point input
        Return boolean of whether point is 3d
        (point itelf, if more permissive?)
        """
        pass
        # error check
        # accept 2d points and add third dimension?
        # or fail if not 3d point


    def _verify_proj_plane(self, plane):
        """
        Perform error checking on point input
        Return boolean of whether point is 3d
        (point itelf, if more permissive?)
        """
        pass
        #TODO raise warning

    # def get_data_from_cayley_graph(self): # TODO rename
    #     G = self.group.cayley_graph(generators=self.reflections(), side="left")
    #     # every vertex has same number of cycles
    #     # every vertex has one cycle for each color


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
        cosets = {}

        reflections = self.group.reflections().list()
        subgroups = []
        while reflections: # is nonempty
            refl = reflections[0]
            subgp = self.group.subgroup([refl])
            i=1
            while i<refl.order():
                group.remove(refl^i)
                i+=1

        for key, value in self.edge_properties.items():
            if key=="color":
                for subgp in subgroups:
                    color = (randint(0,255), randint(0,255), randint(0,255))
                    self.edges[key] = {e:color for e in \
                                       tuple(self.group.cosets(subgp))}
                                       # style?
            else:
                self.edges[key] = {e:value for e in cosets.items()} #????
                # defaults


    def _outside_edges(self): #if private, "create" method
                                # if public, return if known, create if uninitialized?
        """
        """
        pass

    def plot3d(self):
        """
        """
        pass
