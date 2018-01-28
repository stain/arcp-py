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


from uuid import uuid4, uuid5, UUID, NAMESPACE_URL
import urllib.parse as urlp
import re
from hashlib import sha256
from base64 import urlsafe_b64encode, urlsafe_b64decode

SCHEME="arcp"
def _register_scheme(scheme=SCHEME):
    """Ensure app scheme works with urllib.parse.urljoin and friends"""    
    for u in (urlp.uses_relative, urlp.uses_netloc, urlp.uses_fragment):
        if not scheme in u:
            u.append(scheme)
_register_scheme()

def _reg_name_regex():
    # unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
    unreserved = r"[A-Za-z0-9-._~]"

    # pct-encoded = "%" HEXDIG HEXDIG
    pct_encoded = r"%[0-9A-Fa-f][0-9A-Fa-f]"
    
    # "!" / "$" / "&" / "'" / "(" / ")"
    #  / "*" / "+" / "," / ";" / "="
    sub_delims = r"[!$&'()*+,;=]"

    # reg-name    = *( unreserved / pct-encoded / sub-delims )    
    reg_name = r"(" + unreserved + r"|" + pct_encoded + sub_delims + r")*"
    return re.compile(reg_name)
_REG_NAME = _reg_name_regex()

def arcp_uuid(uuid, path="/", query=None, fragment=None):
    if not isinstance(uuid, UUID):
        # ensure valid UUID
        uuid = UUID(uuid)

    # TODO: Ensure valid path?    
    path = path or ""
    authority = "uuid,%s" % uuid
    s = (SCHEME, authority, path, query, fragment)
    return urlp.urlunsplit(s)

def arcp_random(path="/", query=None, fragment=None, uuid=None):
    if uuid is None:
        uuid = uuid4()
    elif not isinstance(uuid, UUID):
        # ensure valid UUID
        uuid = UUID(uuid)
    if not uuid.version == 4:
        raise Exception("UUID is not v4" % uuid)
    return arcp_uuid(uuid, path=path, query=query, fragment=fragment)

def arcp_location(location, path="/", query=None, fragment=None, namespace=NAMESPACE_URL):
    # TODO: Ensure location is valid url?
    uuid = uuid5(namespace, location)
    return arcp_uuid(uuid, path=path, fragment=fragment)
    
def arcp_name(name, path="/", query=None, fragment=None):
    if not _REG_NAME.fullmatch(name):
        raise Exception("Invalid name: %s" % name)
    authority = "name," + name
    s = (SCHEME, authority, path, query, fragment)
    return urlp.urlunsplit(s)

def arcp_hash(bytes=b"", path="/", query=None, fragment=None, hash=None):
    if hash is None:
        hash = sha256()
    elif hash.name != "sha256":
        # TODO: Map Python's hash-names to RFC6920
        raise Exception("hash method %s unsupported, try sha256" % hash.name)
    hashmethod = "sha-256"

    # Tip: if bytes == b"" then provided hash param is unchanged
    hash.update(bytes)

    # RFC6920-style hash encoding
    digestB64 = urlsafe_b64encode(hash.digest())
    digestB64 = digestB64.decode("ascii").strip("=")
    authority = "ni,%s;%s" % (hashmethod, digestB64)
    s = (SCHEME, authority, path, query, fragment)
    return urlp.urlunsplit(s)


def is_arcp_uri(uri):
    # tip: urllib will do lowercase for us
    return urlp.urlparse(uri).scheme == SCHEME

def parse_arcp(uri):
    return ARCPSplitResult(uri)

class ARCPSplitResult(urlp.SplitResult):
    __slots__ = ()
    def __new__(cls, uri):
        return urlp.SplitResult.__new__(cls, *urlp.urlsplit(uri))

    def __init__(self, uri):
        if self.scheme != SCHEME:
            raise Exception("uri has scheme %s, expected %s" % 
                            (split.scheme, SCHEME))

    @property
    def _host_split(self):
        if "," in self.hostname:
            return self.hostname.split(",", 1)
        else:
            return (None, self.hostname)

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
        hash_hex = urlsafe_b64decode(hash_b64)
        return (method.lower(), hash_hex)
    
    def __repr__(self):
        props = ["scheme='arcp'"]
        props += ["prefix='%s'" % self.prefix or ""]
        props += ["name='%s'" % self.name or ""]

        if self.uuid is not None:
            props += ["uuid='%s'" % self.uuid]
        if self.ni is not None:
            props += ["ni='%s'"] % self.ni
            # Avoid Exception in __repr__
            if ";" in self.ni:
                props += ["hash=('%s', '%s'"] % self.hash

        # Traditional URI properties
        props += ["path='%s'" % self.path or ""]
        props += ["query='%s'" % self.query or ""]
        props += ["fragment='%s'" % self.fragment or ""]
        return "ARCPSplitResult(%s)" % ",".join(props)

    def __str__(self):
        return geturl()
