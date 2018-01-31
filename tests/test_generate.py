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
from uuid import UUID, RFC_4122, NAMESPACE_OID
import re

from arcp import generate

# Some test data
TEST_UUID_v1 = UUID("dbc0802a-0682-11e8-9895-b8ca3ad10ac0")
TEST_UUID_v4 = UUID("8c36d39a-18be-4aa8-b1ce-fef330b00a28")
OID = "1.3.6.1.4.1.13661"

uuid_re = re.compile(r"^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")


class UUIDTest(unittest.TestCase):
    """Test arcp_uuid()"""
    def testUUID(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/",
            generate.arcp_uuid(TEST_UUID_v1))
        # UUID version should not matter
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/",
            generate.arcp_uuid(TEST_UUID_v4))            
    def testUUIDPath(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt",
            generate.arcp_uuid(TEST_UUID_v1, "/folder/file.txt"))
    def testUUIDPathQuery(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt?q=s",
            generate.arcp_uuid(TEST_UUID_v1, "/folder/file.txt", "q=s"))
    def testUUIDPathQueryFrag(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt?q=s#hash",
            generate.arcp_uuid(TEST_UUID_v1, "/folder/file.txt", "q=s", "hash"))
    def testUUIDQuery(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/?a=b&c=d",
            generate.arcp_uuid(TEST_UUID_v1, query="a=b&c=d"))
    def testUUIDFrag(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/#hash",
            generate.arcp_uuid(TEST_UUID_v1, fragment="hash"))
    def testUUIDstr(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/",
            generate.arcp_uuid("dbc0802a-0682-11e8-9895-b8ca3ad10ac0"))
    def testUUIDstrFromUpperCase(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/",
            generate.arcp_uuid("dbc0802a-0682-11e8-9895-b8ca3ad10ac0"))    
    def testUUIDstrPathQueryFrag(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt?q=s#hash",
            generate.arcp_uuid("dbc0802a-0682-11e8-9895-b8ca3ad10ac0", 
                               "/folder/file.txt", "q=s", "hash"))
    def testUUIDstrInvalidUUID(self):
        with self.assertRaises(Exception):
            # Too short
            generate.arcp_uuid("5da78af6")
        with self.assertRaises(Exception):
            # empty
            generate.arcp_uuid("")


class RandomTest(unittest.TestCase):
    """Test arcp_random(), with implicit or explicit UUID"""
    def testRandom(self):
        u = generate.arcp_random()
        u2 = generate.arcp_random()
        # always fresh
        self.assertNotEqual(u, u2) 
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/"))
    def testRandomValidUUID(self):
        u = generate.arcp_random()
        # Extract UUID to ensure it is v4
        uuidStr = u.replace("arcp://uuid,", "").strip("/")
        # Ensure RFC4122 compliance
        self.assertIsNotNone(uuid_re.match(uuidStr))
        # ensure lower-case in output
        self.assertEqual(uuidStr, uuidStr.lower())
        # must be valid UUID
        uuid = UUID(uuidStr)
        # must be RFC_4122 variant, version 4 (random)
        self.assertEqual(RFC_4122, uuid.variant)
        self.assertEqual(4, uuid.version)
        
    def testRandomPath(self):
        u = generate.arcp_random("/folder/file.txt")
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/folder/file.txt"))
        self.assertEqual(
            # initial / in path is optional
            len(generate.arcp_random("file.txt")), 
            len(generate.arcp_random("/file.txt")))
    def testRandomQuery(self):
        u = generate.arcp_random(query="q=a")
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/?q=a"))
    def testRandomFrag(self):
        u = generate.arcp_random(fragment="hash")
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/#hash"))
    def testRandomPathQueryFrag(self):
        u = generate.arcp_random("/folder/file.txt", "a=b&c=d", "hash")
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/folder/file.txt?a=b&c=d#hash"))

    # Now test providing a fixed UUID        
    def testUUID(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/",
            generate.arcp_random(uuid=TEST_UUID_v4))
        # UUID version must be 4
        with self.assertRaises(Exception):
            generate.arcp_random(uuid=TEST_UUID_v1)
    def testUUIDPath(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/folder/file.txt",
            generate.arcp_random("/folder/file.txt", uuid=TEST_UUID_v4))
    def testUUIDstr(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/",
            generate.arcp_random(uuid="8c36d39a-18be-4aa8-b1ce-fef330b00a28"))
        with self.assertRaises(Exception):
            # UUID version must be 4
            generate.arcp_random(uuid="dbc0802a-0682-11e8-9895-b8ca3ad10ac0")
            
    def testUUIDstrPathQueryFrag(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/folder/file.txt?q=s#hash",
            generate.arcp_random("/folder/file.txt", "q=s", "hash", 
                uuid="8c36d39a-18be-4aa8-b1ce-fef330b00a28"))
    def testUUIDstrInvalidUUID(self):
        with self.assertRaises(Exception):
            # Too short
            generate.arcp_random(uuid="5da78af6")
        with self.assertRaises(Exception):
            # empty
            generate.arcp_random(uuid="")      



class LocationTest(unittest.TestCase):
    """Test arcp_location()"""
    def testExampleZip(self):
        # URL and expected UUID as in
        # https://tools.ietf.org/id/draft-soilandreyes-arcp-02.html#rfc.appendix.A.2
        self.assertEqual("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/", 
            generate.arcp_location("http://example.com/data.zip"))
        self.assertEqual("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/pics/", 
            generate.arcp_location("http://example.com/data.zip", "/pics/"))
        self.assertEqual("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/pics/flower.jpeg", 
            generate.arcp_location("http://example.com/data.zip", "/pics/flower.jpeg"))

    def testExampleZipUUIDValid(self):
        u = generate.arcp_location("http://example.com/")
        # Extract UUID to ensure it is v4
        uuidStr = u.replace("arcp://uuid,", "").strip("/")
        # Ensure RFC4122 compliance
        self.assertIsNotNone(re.match(uuid_re, uuidStr))
        # ensure lower-case in output
        self.assertEqual(uuidStr, uuidStr.lower())
        # must be valid UUID
        uuid = UUID(uuidStr)
        # must be RFC_4122 variant, version 5 (name sha1)
        self.assertEqual(RFC_4122, uuid.variant)
        self.assertEqual(5, uuid.version)

    def testLocationOtherNamespace(self):
        u = generate.arcp_location(OID, namespace=NAMESPACE_OID, path="/example")
        self.assertEqual("arcp://uuid,215aa48f-233f-507f-8484-3eb5d6e23e9d/example", u)

    def testLocationNamespaceUUIDstrPathQueryFrag(self):
        self.assertEqual("arcp://uuid,215aa48f-233f-507f-8484-3eb5d6e23e9d/folder/file.txt?q=s#hash",
            generate.arcp_location(OID, "/folder/file.txt", "q=s", "hash", 
                namespace=NAMESPACE_OID))
