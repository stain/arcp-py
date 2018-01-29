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


from uuid import UUID, NAMESPACE_URL
import urllib.parse as urlp
from base64 import urlsafe_b64decode
from binascii import hexlify

SCHEME="arcp"

def is_arcp_uri(uri):
    # tip: urllib will do lowercase for us
    return urlp.urlparse(uri).scheme == SCHEME

def parse_arcp(uri):
    return ARCPParseResult(*urlp.urlparse(uri))

def urlparse(uri):
    u = urlp.urlparse(uri)    
    if (u.scheme == SCHEME):
        return ARCPParseResult(*u)
    else:
        return u

class ARCPParseResult(urlp.ParseResult):
    __slots__ = ()

    def __init__(self, *args):
        if self.scheme != SCHEME:
            raise Exception("uri has scheme %s, expected %s" % 
                            (self.scheme, SCHEME))

    @property
    def _host_split(self):
        if "," in self.netloc:
            return self.netloc.split(",", 1)
        else:
            return (None, self.netloc)

    @property
    def prefix(self):
        (prefix,name) = self._host_split
        return prefix

    @property
    def name(self):
        (prefix,name) = self._host_split
        return name
    
    @property
    def uuid(self):
        if self.prefix != "uuid":
            return None
        return UUID(self.name)
    
    @property
    def ni(self):
        if self.prefix != "ni":
            return None
        # TODO: Validate algval?
        algval = self.name
        return algval
    
    @property
    def hash(self):
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
