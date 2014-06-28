from .query import SearchQuerySet


class Manager(object):

    def __init__(self, index):
        self._index = index

    def all(self):
        return SearchQuerySet(self._index).all()

    def filter(self, *args):
        return SearchQuerySet(self._index).filter(*args)

    def search(self, expression):
        return SearchQuerySet(self._index).search(expression)

    def order_by(self, *args):
        return SearchQuerySet(self._index).order_by(*args)
