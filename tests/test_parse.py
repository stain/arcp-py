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

    def test_parse_empty_authority(self):
        t = parse.parse_arcp("arcp:///")
        self._test_tuple(t)
        self.assertEqual("arcp", t.scheme)
        self.assertEqual("", t.netloc)
        self.assertEqual("/", t.path)
        self.assertEqual("", t.params)
        self.assertEqual("", t.query)
        self.assertEqual("", t.fragment)


    def test_parseFails(self):
        with self.assertRaises(Exception):
            parse.parse_arcp("http://example.com/")

    def test_parse_prefix(self):
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

    def test_parse_name(self):
        self.assertEqual("example.com",
             parse.parse_arcp("arcp://name,example.com/").name)
        # but other "names" are also supported:
        self.assertEqual("ecba06ed-472e-46d4-8ab8-9570e40e0b8c",
             parse.parse_arcp("arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/").name)
        self.assertEqual("sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/").name)
        # authority fall-back
        self.assertEqual("example.com",
             parse.parse_arcp("arcp://example.com/").name)
        # unlikely, but valid by specification
        self.assertEqual("",
             parse.parse_arcp("arcp:///").name)
        # name from an unknown prefix
        self.assertEqual("abc",
             parse.parse_arcp("arcp://x-unknown,abc").name)


    def test_parse_uuid(self):
        self.assertEqual("ecba06ed472e46d48ab89570e40e0b8c",
             parse.parse_arcp("arcp://uuid,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/").uuid.hex)
        self.assertIsNone(
            parse.parse_arcp("arcp://name,ecba06ed-472e-46d4-8ab8-9570e40e0b8c/").uuid)
        self.assertIsNone(
            parse.parse_arcp("arcp://ecba06ed-472e-46d4-8ab8-9570e40e0b8c/").uuid)
        
    def test_parse_uuid_fails(self):
        with self.assertRaises(Exception):
            parse.parse_arcp("arcp://uuid,ecba06ed-WRONG/").uuid

    def test_parse_ni(self):
        self.assertEqual("sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/").ni)
        self.assertIsNone(
            parse.parse_arcp("arcp://name,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/").ni)
        self.assertIsNone(
            parse.parse_arcp("arcp://sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/").ni)

    def test_parse_ni_invalid_fails(self):
        # Below example is invalid as alg-val string 
        # does not contain ;
        with self.assertRaises(Exception):
             parse.parse_arcp("arcp://ni,sha-256/").ni_uri()
        with self.assertRaises(Exception):
             parse.parse_arcp("arcp://ni,sha-256/").nih_uri()
        with self.assertRaises(Exception):
             parse.parse_arcp("arcp://ni,sha-256/").hash()
        with self.assertRaises(Exception):
             parse.parse_arcp("arcp://ni,sha-256/").ni_well_known()
        with self.assertRaises(Exception):
             parse.parse_arcp("arcp://ni,sha-256/").ni

    def test_parse_ni_uri(self):
        self.assertEqual("ni:///sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_uri())
        self.assertIsNone(
            parse.parse_arcp("arcp://name,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_uri())
        self.assertIsNone(
            parse.parse_arcp("arcp://sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_uri())
        self.assertEqual("ni://example.com/sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_uri("example.com"))

    def test_parse_nih_uri(self):
        self.assertEqual("nih:sha-256-120;532690-57e12f-e2b74b-a07c89-2560a2;f",
             parse.parse_arcp("arcp://ni,sha-256-120;UyaQV-Ev4rdLoHyJJWCi/")
                .nih_uri())
        self.assertIsNone(
            parse.parse_arcp("arcp://name,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .nih_uri())
        self.assertIsNone(
            parse.parse_arcp("arcp://sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .nih_uri())

    def test_parse_ni_well_known(self):
        self.assertEqual("/.well-known/ni/sha-256/f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_well_known())
        self.assertIsNone(
            parse.parse_arcp("arcp://name,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_well_known())
        self.assertIsNone(
            parse.parse_arcp("arcp://sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_well_known())
        self.assertEqual("http://example.com/.well-known/ni/sha-256/f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk",
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .ni_well_known("http://example.com/"))

    def test_parse_hash(self):
        # sha256 of "Hello World!" in ascii
        self.assertEqual(("sha-256", "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"),
             parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .hash)
        self.assertIsNone(
            parse.parse_arcp("arcp://name,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .hash)
        self.assertIsNone(
            parse.parse_arcp("arcp://sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/")
                .hash)
        # md5 of "Hello World!" in ascii
        self.assertEqual(("md5", "ed076287532e86365e841e92bfc50d8c"),
             parse.parse_arcp("arcp://ni,md5;7Qdih1MuhjZehB6Sv8UNjA/")
                .hash)

    def test_parse_repr_ni(self):
        u = parse.parse_arcp("arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/file?q=a#frag")
        r = repr(u)
        self.assertIn("scheme='arcp'", r)
        self.assertIn("prefix='ni'", r)
        self.assertIn("name='sha-256;f4OxZX", r)#..
        self.assertIn("path='/file'", r)
        self.assertIn("query='q=a'", r)
        self.assertIn("fragment='frag'", r)
        self.assertIn("ni='sha-256;f4OxZX", r)#..
        self.assertIn("hash=('sha-256', '7f83b16", r)#..
        self.assertNotIn("uuid=", r)

    def test_parse_repr_uuid(self):
        u = parse.parse_arcp("arcp://uuid,32a423d6-52ab-47e3-a9cd-54f418a48571/")
        r = repr(u)
        self.assertIn("scheme='arcp'", r)
        self.assertIn("prefix='uuid'", r)
        self.assertIn("name='32a423d6-", r)#..
        self.assertIn("path='/'", r)
        self.assertIn("uuid=32a423d6-", r)# ..
        self.assertIn("query=''", r)
        self.assertIn("fragment=''", r)
        self.assertNotIn("ni=", r)
        self.assertNotIn("hash=", r)#..

    def test_parse_str_ni(self):
        uri = "arcp://ni,sha-256;f4OxZX_x_FO5LcGBSKHWXfwtSx-j1ncoSt3SABJtkGk/file?q=a#frag"
        u = parse.parse_arcp(uri)
        self.assertEqual(uri, str(u))
        

class URLParse(unittest.TestCase):
    """Test urlparse()"""
    def test_urlparse(self):
        self.assertEqual("name",
            parse.urlparse("arcp://name,example.com/").prefix)
        self.assertEqual("http",
            parse.urlparse("http://example.com/").scheme)

class NIH_CheckDigit(unittest.TestCase):
    """Test _nih_checkdigit() using RFC6920 examples"""
    def test_checkdigit(self):
        self.assertEqual("f", parse._nih_checkdigit(
          "5326-9057-e12f-e2b7-4ba0-7c89-2560-a2".replace("-", "")))
        self.assertEqual("b", parse._nih_checkdigit("53269057"))                
        self.assertEqual("0", parse._nih_checkdigit("b053269057"))
        self.assertEqual("d", parse._nih_checkdigit("acefeed"))
        self.assertEqual("0", parse._nih_checkdigit("dacefeed"))
        self.assertEqual("4", parse._nih_checkdigit("123456789abcdef"))
        self.assertEqual("0", parse._nih_checkdigit("4123456789abcdef"))
        # Consistency check -- if we add $digit (or $digit0 for even-length) 
        # in front, the new sum should be 0

class NIH_Segmented(unittest.TestCase):
    """Test _nih_segmented()"""
    def test_segment(self):
        self.assertEqual("532690-57e12f-e2b74b-a07c89-2560a2", 
            parse._nih_segmented("53269057e12fe2b74ba07c892560a2"))
        self.assertEqual("5326-9057-e12f-e2b7-4ba0-7c89-2560-a2", 
            parse._nih_segmented("53269057e12fe2b74ba07c892560a2", 4))
        self.assertEqual("532690-5", 
            parse._nih_segmented("5326905"))
        self.assertEqual("532690", 
            parse._nih_segmented("532690"))
        self.assertEqual("53269", 
            parse._nih_segmented("53269"))
        self.assertEqual("", 
            parse._nih_segmented(""))
