class Polynode(object):

    def __init__(self, contour):
        '''attribute names needs to be Contour and Childs 
        to has the same attributes with PyPolynode '''
        self.Contour = contour
        self.Childs = []
        self.depth = 0