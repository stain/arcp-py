#!/usr/bin/env python
## Copyright 2018 Stian Soiland-Reyes, The University of Manchester, UK
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

"""
Parse arcp URIs.

Use is_arcp_uri() to detect of an URI string is using the 
arcp: URI scheme, in which case parse_arcp() can be used
to split it into its components.

The urlparse() function can be used as a replacement for
urllib.parse.urlparse() - supporting any URIs. If the URI is 
using the arcp: URI scheme, additional components are available
as from parse_arcp().
"""
__author__      = "Stian Soiland-Reyes <http://orcid.org/0000-0001-9842-9718>"
__copyright__   = "Copyright 2018 The University of Manchester"
__license__     = "Apache License, version 2.0 (https://www.apache.org/licenses/LICENSE-2.0)"

from uuid import UUID, NAMESPACE_URL
import urllib.parse as urlp
from base64 import urlsafe_b64decode
from binascii import hexlify

SCHEME="arcp"

def is_arcp_uri(uri):
    """Return True if the uri string uses the arcp scheme, otherwise False.
    """

    # tip: urllib will do lowercase for us
    return urlp.urlparse(uri).scheme == SCHEME

def parse_arcp(uri):
    """Parse an arcp URI string into its constituent parts.

    The returned object is similar to ``urllib.parse.urlparse()``
    in that it is a tuple of 
    ``(scheme,netloc,path,params,query,fragment)``
    with equally named properties, but it also adds
    properties for arcp fields:
    
    - prefix -- arcp authority prefix, e.g. "uuid", "ni" or "name", or None if prefix is missing
    - name -- arcp authority without prefix, e.g. "a4889890-a50a-4f14-b4e7-5fd83683a2b5" or "example.com"
    - uuid -- a ``uuid.UUID`` object if prefix is "uuid", otherwise None
    - ni -- the arcp alg-val value according to RFC6920 if prefix is "ni", otherwise None
    - hash -- the hash method and hash as a hexstring if prefix is "ni", otherwise None
    """

    return ARCPParseResult(*urlp.urlparse(uri))

def urlparse(uri):
    """Parse any URI string into constituent parts.

    The returned object is similar to 
    :func:`urllib.parse.urlparse()`
    in that it is a tuple of 
    ``(scheme,netloc,path,params,query,fragment)``
    with equally named properties, but if the 
    URI scheme is "arcp" this also adds
    arcp properties as in :func:`parse_arcp()`.
    """
    u = urlp.urlparse(uri)    
    if (u.scheme == SCHEME):
        return ARCPParseResult(*u)
    else:
        return u

class ARCPParseResult(urlp.ParseResult):
    """Result of parsing an arcp URI.

    This class does not detect if the arcp URI was valid
    according to the specification.

    This class extends :class:`urlllib.parse.ParseResult`
    adding arcp properties, some of which may be `None`.
    """
    __slots__ = ()

    def __init__(self, *args):
        if self.scheme != SCHEME:
            raise Exception("uri has scheme %s, expected %s" % 
                            (self.scheme, SCHEME))
        if not self.netloc:
            raise Exception("uri has empty authority")

    def _host_split(self):
        """Return (prefix,name) if authority has "," - 
        otherwise (None, authority).
        """
        if "," in self.netloc:
            return self.netloc.split(",", 1)
        else:
            return (None, self.netloc)

    @property
    def prefix(self):
        """The arcp prefix, e.g. "uuid", "ni", "name" or None if no prefix was present.
        """
        (prefix,name) = self._host_split()
        return prefix

    @property
    def name(self):
        """The URI's authority without arcp prefix.
        """
        (prefix,name) = self._host_split()
        return name
    
    @property
    def uuid(self):
        """The arcp UUID if the prefix is "uuid", otherwise None."""
        if self.prefix != "uuid":
            return None
        return UUID(self.name)
    
    @property
    def ni(self):
        """The arcp ni string if the prefix is "ni", otherwise None."""
        if self.prefix != "ni":
            return None
        # TODO: Validate algval?
        algval = self.name
        return algval
    
    @property
    def ni_uri(self, authority=""):
        """The ni URI if the prefix is "ni", otherwise None.
        
        If the authority parameter is provided, it will be used in the returned URI.
        """
        ni = self.ni
        if ni is None:
            return None
        s = ("ni", authority, ni, None, None)
        return urlp.urlunsplit(s)

    @property
    def nih_uri(self, authority=""):
        """The nih URI if the prefix is "ni", otherwise None.
        
        If the authority parameter is provided, it will be used in the returned URI.
        """
        h = self.hash
        if h is None:
            return None
        path = "%s;%s" % h
        s = ("nih", authority, ni, path, None)
        return urlp.urlunsplit(s)
    
    @property
    def ni_well_known(self, base=""):
        """The ni .well_known URI if the prefix is "ni", otherwise None.

        The parameter base should be an absolute URI like 
        ``"http://example.com/"``
        """
        ni = self.ni
        if ni is None:
            return None        
        path = ".well-known/ni/" + ni 
        return urlp.urljoin(base, path)
        
    @property
    def hash(self):
        """A tuple (hash_method,hash_hex) if the prefix is "ni", otherwise None.
        """
        ni = self.ni
        if ni is None:
            return None
        if not ";" in ni:
            raise Exception("invalid ni hash: %s" % ni)
        (method, hash_b64) = ni.split(";", 1)
        # re-instate padding as urlsafe_base64decode is strict
        missing_padding = 4 - (len(hash_b64) % 4)
        hash_b64 += "=" * missing_padding
        hash_bytes = urlsafe_b64decode(hash_b64)
        hash_hex = hexlify(hash_bytes).decode("ascii")
        return (method.lower(), hash_hex)
    
    def __repr__(self):
        props = ["scheme='arcp'"]
        props += ["prefix='%s'" % self.prefix or ""]
        props += ["name='%s'" % self.name or ""]

        if self.uuid is not None:
            props += ["uuid='%s'" % self.uuid]
        if self.ni is not None:
            props += ["ni='%s'" % self.ni]
            # Avoid Exception in __repr__
            if ";" in self.ni:
                props += ["hash=('%s', '%s'" % self.hash]

        # Traditional URI properties
        props += ["path='%s'" % self.path or ""]
        props += ["query='%s'" % self.query or ""]
        props += ["fragment='%s'" % self.fragment or ""]
        return "ARCPParseResult(%s)" % ",".join(props)

    def __str__(self):
        return geturl()
