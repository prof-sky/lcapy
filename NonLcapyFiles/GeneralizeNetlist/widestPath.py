from maxWidth import MaxWidth

class WidestPath(MaxWidth):
    def __init__(self, width, depth, index, parent):
        super().__init__(width, depth)
        self._index = index
        self._parent = parent

    def toList(self):
        asList = []
        asList.extend(super().toList())
        asList.append(self.index)
        asList.append(self.parent)
        return asList

    def toTuple(self):
        asTuple = ()
        for val in super().toTuple():
            asTuple.__add__(val)
        asTuple.__add__(self.index)
        asTuple.__add__(self.parent)

        return asTuple

    @property
    def index(self):
        return self._index

    @property
    def parent(self):
        return self._parent

