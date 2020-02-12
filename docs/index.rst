arcp (Archive and Package) URI Python library
=============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   arcp
   generate
   parse


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



``arcp`` provides functions for creating arcp_ URIs, 
which can be used for identifying or parsing hypermedia 
files packaged in an archive or package, like a ZIP file.

arcp URIs can be used to consume or reference hypermedia resources 
bundled inside a file archive or an application package, as well as 
to resolve URIs for archive resources within a programmatic framework.

This URI scheme provides mechanisms to generate a unique base URI 
to represent the root of the archive, so that relative URI references 
in a bundled resource can be resolved within the archive without having to extract the archive content on the local file system.

An arcp URI can be used for purposes of isolation (e.g. when consuming 
multiple archives), security constraints (avoiding “climb out” from the
archive), or for externally identiyfing sub-resources referenced by
hypermedia formats.

Examples:
 - ``arcp://uuid,32a423d6-52ab-47e3-a9cd-54f418a48571/doc.html``
 - ``arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/pics/``
 - ``arcp://ni,sha-256;F-34D4TUeOfG0selz7REKRDo4XePkewPeQYtjL3vQs0/``
 - ``arcp://name,gallery.example.org/``

The different forms of URI authority_ in arcp URIs can be used depending
on which uniqueness constraints to apply when addressing an archive.
See the arcp_ specification (draft-soilandreyes-arcp) for details.

Note that this library only provides mechanisms to 
*generate* and *parse* arcp URIs, and do *not* integrate with any 
particular archive or URL handling modules like 
``zipfile`` or ``urllib.request``.


License
-------

© 2018-2020 Stian Soiland-Reyes <https://orcid.org/0000-0001-9842-9718>, The University of Manchester, UK

Licensed under the 
Apache License, version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>.


Source code and contributing
----------------------------

Source code: <https://github.com/stain/arcp-py>

Feel free to raise a pull request at <https://github.com/stain/arcp-py/pulls>
or an issue at <https://github.com/stain/arcp-py/issues>.


Installing
----------

You will need Python 2.7, Python 3.4 or later (Recommended: 3.6).

If you have pip_, then the easiest is normally to install from <https://pypi.org/project/arcp/> using::

    pip install arcp

If you want to install manually from this code base, then try::

    python setup.py install




.. _arcp: https://tools.ietf.org/id/draft-soilandreyes-arcp-03.html
.. _pip: https://docs.python.org/3/installing/
.. _authority: https://tools.ietf.org/id/draft-soilandreyes-arcp-03.html#rfc.section.4.1
