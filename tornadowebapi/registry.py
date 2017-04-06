from tornadowebapi.deserializers import BasicRESTDeserializer
from tornadowebapi.parsers import JSONParser
from tornadowebapi.renderer import JSONRenderer
from tornadowebapi.serializers import BasicRESTSerializer
from .handler import ResourceHandler, CollectionHandler, JSAPIHandler
from .utils import url_path_join, with_end_slash
from .resource import Resource
from .authenticator import NullAuthenticator


class Registry:
    """Main class that registers the defined resources,
    and provides the appropriate handlers for tornado.

    It is also responsible for holding the authenticator,
    the renderer (converts internal representation to
    HTTP response payload) and the parser (converts HTTP
    request payload to internal representation).

    A registry is normally instantiated and held on the
    Tornado Application.
    """

    def __init__(self):
        self._registered_types = {}
        self._authenticator = NullAuthenticator
        self._renderer = JSONRenderer()
        self._parser = JSONParser()
        self._serializer = BasicRESTSerializer()
        self._deserializer = BasicRESTDeserializer()

    @property
    def authenticator(self):
        return self._authenticator

    @authenticator.setter
    def authenticator(self, authenticator):
        self._authenticator = authenticator

    @property
    def renderer(self):
        """Returns the current renderer."""
        return self._renderer

    @property
    def parser(self):
        """Returns the current parser."""
        return self._parser

    @property
    def serializer(self):
        return self._serializer

    @property
    def deserializer(self):
        return self._deserializer

    @property
    def registered_types(self):
        return self._registered_types

    def register(self, typ, collection_name=None):
        """Registers a Resource type with an appropriate
        collection name. A collection name is a pluralized
        version of the resource, created by lowercasing
        the class name and adding an "s".
        The resulting collection name will be used in the URL
        representing the resource. For example, a resource Image
        will have URLs of the type

        http://example.com/api/v1/images/identifier/

        The collection name can always be overridden by specifying
        __collection_name__ in the resource class, or by specifying
        the collection_name parameter.

        Parameters
        ----------
        typ: Resource
            A subclass of the rest Resource type
        collection_name: str or None
            Overrides the resource collection name.

        Raises
        ------
        TypeError:
            if typ is not a subclass of Resource
        """
        if not issubclass(typ, Resource):
            raise TypeError("typ must be a subclass of Resource")

        if collection_name is not None:
            collection_name = collection_name
        elif hasattr(typ, "__collection_name__"):
            collection_name = typ.__collection_name__
        else:
            collection_name = typ.__name__.lower() + "s"

        self._registered_types[collection_name] = typ

    def __getitem__(self, collection_name):
        """Returns the class from the collection name with the
        indexing operator"""
        return self._registered_types[collection_name]

    def __contains__(self, item):
        """If the registry contains the given item"""
        return item in self._registered_types

    def api_handlers(self, base_urlpath, version="v1"):
        """Returns the API handlers for the interface.
        Add these handlers to your application to provide an
        interface to your Resources.


        Parameters
        ----------
        base_urlpath: str
            The base url path to serve
        version: str
            A string identifying the version of the API.

        Notes
        -----
        The current implementation does not support multiple API versions yet.
        The version option is only provided for futureproofing.
        """
        init_args = dict(
            registry=self,
            base_urlpath=base_urlpath,
            api_version=version,
        )

        return [
            (with_end_slash(
                url_path_join(base_urlpath, "api", version, "(.*)", "(.*)")),
             ResourceHandler,
             init_args
             ),
            (with_end_slash(
                url_path_join(base_urlpath, "api", version, "(.*)")),
             CollectionHandler,
             init_args
             ),
            (url_path_join(base_urlpath, "jsapi", version, "resources.js"),
             JSAPIHandler,
             init_args
             ),
        ]


#: global registry for registration of the classes.
registry = Registry()
