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


import unittest

from arcp import parse

class TestIsArcpURI(unittest.TestCase):
    """Test is_arcp_uri()"""

    def test_arcp_uri(self):
        self.assertTrue(parse.is_arcp_uri(
            "arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/"))

    def test_not_arcp_uri(self):
        self.assertFalse(parse.is_arcp_uri(
            "http://example.com/"))

    def test_arcp_uri_authority_fallback(self):
        self.assertTrue(parse.is_arcp_uri(
            "arcp://example.com"))
        self.assertTrue(parse.is_arcp_uri(
            "arcp://x-unknown,abc"))


class TestParse(unittest.TestCase):
    """Test parse_arcp()"""

    def _test_tuple(self, t):
        (scheme,netloc,path,params,query,fragment) = t
        self.assertEqual(t.scheme, scheme)
        self.assertEqual(t.netloc, netloc)
        self.assertEqual(t.path, path)
        self.assertEqual(t.params, params)
        self.assertEqual(t.query, query)
        self.assertEqual(t.fragment, fragment)

    def test_parse(self):
        t = parse.parse_arcp("arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/")
        self._test_tuple(t)
        self.assertEqual("arcp", t.scheme)
        self.assertEqual("uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c", t.netloc)
        self.assertEqual("/", t.path)
        self.assertEqual("", t.params)
        self.assertEqual("", t.query)
        self.assertEqual("", t.fragment)

    def test_parse_path_query_fragment(self):
        t = parse.parse_arcp("arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/file;p=1?q=a#frag")
        self._test_tuple(t)
        self.assertEqual("arcp", t.scheme)
        self.assertEqual("uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c", t.netloc)
        self.assertEqual("/file", t.path)
        self.assertEqual("p=1", t.params)
        self.assertEqual("q=a", t.query)
        self.assertEqual("frag", t.fragment)

    def test_parse_authority_fallback(self):
        t = parse.parse_arcp("arcp://example.com/")
        self._test_tuple(t)
        self.assertEqual("arcp", t.scheme)
        self.assertEqual("example.com", t.netloc)
        self.assertEqual("/", t.path)
        self.assertEqual("", t.params)
        self.assertEqual("", t.query)
        self.assertEqual("", t.fragment)

    def parseFails(self):
        with self.assertRaises(Exception):
            parse.parse_arcp("http://example.com/")

    def parse_prefix(self):
        self.assertEqual("uuid",
             parse.parse_arcp("arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/").prefix)
        self.assertEqual("ni",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/").prefix)
        self.assertEqual("name",
             parse.parse_arcp("arcp://name,example.com/").prefix)

        # authority fall-back
        self.assertIsNone(
             parse.parse_arcp("arcp://example.com/").prefix)
        # silly..but valid by specification
        self.assertEqual("",
             parse.parse_arcp("arcp://,example.com/").prefix)
        # Unknown prefixes are also picked up (should they?)
        self.assertEqual("x-unknown",
             parse.parse_arcp("arcp://x-unknown,abc").prefix)

