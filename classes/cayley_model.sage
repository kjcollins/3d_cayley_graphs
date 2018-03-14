r"""
Model building class for rigid 3d cayley graphs of reflection groups.

<Paragraph description>

EXAMPLES::

<Lots and lots of examples>

AUTHORS:

- YOUR NAME (2005-01-03): initial version

- person (date in ISO year-month-day format): short desc

"""

class ClassName(object): #TODO we might want to inherit from an object. Graphics?
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

        self.vertex_properties = ["radius", "size", "shape", "label", "visible"]
        self.vertices = self._construct_vertices_dict() # design?

        self.edge_properties = ["thickness", "color", "fill", "visible"]
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
        pass
        # keys are possible properties of vertices
        # values are a second dictionary with vertices mapped
        # to the value of that property

    def _outside_edges(self): #if private, "create" method
                                # if public, return if known, create if uninitialized?
        pass

    def _construct_edges_dict(self):
        pass

    def plot3d(self):
        """
        """
        pass
