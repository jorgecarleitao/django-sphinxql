from .query import QuerySet


class Manager(object):

    def __init__(self, index):
        self._index = index

    def all(self):
        return QuerySet(self._index).all()

    def filter(self, *args):
        return QuerySet(self._index).filter(*args)

    def search(self, expression):
        return QuerySet(self._index).search(expression)

    def order_by(self, *args):
        return QuerySet(self._index).order_by(*args)
