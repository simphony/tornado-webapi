from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.resource_handler import ResourceHandler


class WorkingResourceHandler(ResourceHandler):

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create(self, representation):
        id = type(self).id
        self.collection[str(id)] = representation
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update(self, identifier, representation):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[identifier] = representation

    @gen.coroutine
    def delete(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        del self.collection[identifier]

    @gen.coroutine
    def items(self):
        return list(self.collection.keys())


class StudentHandler(WorkingResourceHandler):
    pass


class TeacherHandler(ResourceHandler):
    @gen.coroutine
    def retrieve(self, identifier):
        return {}

    @gen.coroutine
    def items(self):
        return []


class UnsupportAllHandler(ResourceHandler):
    pass


class UnprocessableHandler(ResourceHandler):
    @gen.coroutine
    def create(self, representation):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def update(self, identifier, representation):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def retrieve(self, identifier):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def items(self):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")


class UnsupportsCollectionHandler(ResourceHandler):
    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class BrokenHandler(ResourceHandler):
    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class ExceptionValidatedHandler(ResourceHandler):
    def validate_representation(self, representation):
        raise Exception("woo!")


class OurExceptionValidatedHandler(ResourceHandler):
    def validate_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class NullReturningValidatedHandler(ResourceHandler):
    def validate_representation(self, representation):
        pass


class CorrectValidatedHandler(WorkingResourceHandler):
    def validate_representation(self, representation):
        representation["hello"] = 5
        return representation


class AlreadyPresentHandler(ResourceHandler):
    @gen.coroutine
    def create(self, *args):
        raise exceptions.Exists()


class InvalidIdentifierHandler(ResourceHandler):
    def validate_identifier(self, identifier):
        raise Exception("woo!")


class OurExceptionInvalidIdentifierHandler(ResourceHandler):
    def validate_identifier(self, identifier):
        raise exceptions.BadRepresentation("woo!")


class SheepHandler(ResourceHandler):
    """Sheep plural is the same as singular."""
    __collection_name__ = "sheep"


class OctopusHandler(ResourceHandler):
    """Octopus plural is a matter of debate."""
    __collection_name__ = "octopi"


class Frobnicator(ResourceHandler):
    """A weird name to test if it's kept"""
