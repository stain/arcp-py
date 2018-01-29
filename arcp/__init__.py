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
Create/parse arcp (Archive and Package) URIs.

This module provides functions for creating arcp_ URIs, 
which can be used for identifying or parsing hypermedia 
files packaged in an archive like a ZIP file::

    >>> from arcp import *

    >>> arcp_random()
    'arcp://uuid,dcd6b1e8-b3a2-43c9-930b-0119cf0dc538/'

    >>> arcp_random("/foaf.ttl", fragment="me")
    'arcp://uuid,dcd6b1e8-b3a2-43c9-930b-0119cf0dc538/foaf.ttl#me'

    >>> arcp_hash(b"Hello World!", "/folder/")
    'arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/folder/'

    >>> arcp_location("http://example.com/data.zip", "/file.txt")
    'arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/file.txt'

arcp URLs can be used with ``urllib.parse``, 
for instance using ``urljoin`` to resolve relative references::

    >>> css = arcp.arcp_name("app.example.com", "css/style.css")
    >>> urllib.parse.urljoin(css, "../fonts/foo.woff")
    'arcp://name,app.example.com/fonts/foo.woff'


In addition this module provides functions that can be used
instead of ``urllib.parse.urlparse`` to parse
arcp URIs::

    >>> is_arcp_uri("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/file.txt")
    True

    >>> is_arcp_uri("http://example.com/t")
    False

    >>> u = parse_arcp("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/file.txt")
    ARCPSplitResult(scheme='arcp',prefix='uuid',name='b7749d0b-0e47-5fc4-999d-f154abe68065',
      uuid='b7749d0b-0e47-5fc4-999d-f154abe68065',path='/file.txt',query='',fragment='')

    >>> u.path
    '/file.txt'
    >>> u.prefix
    'uuid'
    >>> u.uuid
    UUID('b7749d0b-0e47-5fc4-999d-f154abe68065')
    >>> u.uuid.version
    5

    >>> parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/folder/").hash
    ('sha-256', '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069')


.. _arcp: https://tools.ietf.org/html/draft-soilandreyes-arcp-02
"""

SCHEME="arcp"
def _register_scheme(scheme=SCHEME):
    import urllib.parse as urlp
    """Ensure app scheme works with urllib.parse.urljoin and friends"""    
    for u in (urlp.uses_relative, urlp.uses_netloc, urlp.uses_fragment):
        if not scheme in u:
            u.append(scheme)
_register_scheme()

# Convenience export of public functions
from .parse import is_arcp_uri, parse_arcp
from .generate import arcp_uuid, arcp_random, arcp_location, arcp_name, arcp_hash
