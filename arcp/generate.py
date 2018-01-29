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
from urllib.parse import urlunsplit
import re
from hashlib import sha256
from base64 import urlsafe_b64encode, urlsafe_b64decode

SCHEME="arcp"

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
    return urlunsplit(s)

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
    return urlunsplit(s)

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
    return urlunsplit(s)

