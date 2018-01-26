#!/usr/bin/env python

from uuid import uuid4, uuid5, UUID, NAMESPACE_URL
import urllib.parse as urlparse
import re

SCHEME="arcp"

def _register_scheme(scheme=SCHEME):
    """Ensure app scheme works with urllib.parse.urljoin and friends"""    
    for u in (urlparse.uses_relative, urlparse.uses_netloc, urlparse.uses_fragment):
        if not scheme in u:
            u.append(scheme)
_register_scheme()

def arcp_uuid(uuid, path="/", query=None, fragment=None):
    if not isinstance(uuid, UUID):
        # ensure valid UUID
        uuid = UUID(uuid)

    # TODO: Ensure valid path?    
    path = path or ""
    authority = "uuid,%s" % uuid
    s = (SCHEME, authority, path, query, fragment)
    return urlparse.urlunsplit(s)

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

def arcp_name(name, path="/", query=None, fragment=None):
    if not _REG_NAME.fullmatch(name):
        raise Exception("Invalid name: %s" % name)
    authority = "name," + name
    s = (SCHEME, authority, path, query, fragment)
    return urlparse.urlunsplit(s)

def arcp_hash():
    #TODO
    pass
