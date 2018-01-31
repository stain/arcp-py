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

from arcp import generate

from uuid import UUID

test_uuid_v1 = UUID("dbc0802a-0682-11e8-9895-b8ca3ad10ac0")
test_uuid_v4 = UUID("8c36d39a-18be-4aa8-b1ce-fef330b00a28")

class UUIDTest(unittest.TestCase):
    """Test generate.arcp_uuid()"""
    def testUUID(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/",
            generate.arcp_uuid(test_uuid_v1))
        # UUID version should not matter
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/",
            generate.arcp_uuid(test_uuid_v4))            
    def testUUIDPath(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt",
            generate.arcp_uuid(test_uuid_v1, "/folder/file.txt"))
    def testUUIDPathQuery(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt?q=s",
            generate.arcp_uuid(test_uuid_v1, "/folder/file.txt", "q=s"))
    def testUUIDPathQueryFrag(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/folder/file.txt?q=s#hash",
            generate.arcp_uuid(test_uuid_v1, "/folder/file.txt", "q=s", "hash"))
    def testUUIDQuery(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/?a=b&c=d",
            generate.arcp_uuid(test_uuid_v1, query="a=b&c=d"))
    def testUUIDFrag(self):
        self.assertEqual("arcp://uuid,dbc0802a-0682-11e8-9895-b8ca3ad10ac0/#hash",
            generate.arcp_uuid(test_uuid_v1, fragment="hash"))
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
    """Test generate.arcp_random(), with implicit or explicit UUID"""
    def testRandom(self):
        u = generate.arcp_random()
        u2 = generate.arcp_random()
        self.assertNotEqual(u, u2)

        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/"))
        # Extract UUID to ensure it is v4
        


    def testRandomPath(self):
        u = generate.arcp_random("/folder/file.txt")
        self.assertTrue(u.startswith("arcp://uuid,"))
        self.assertTrue(u.endswith("/folder/file.txt"))


    def testUUID(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/",
            generate.arcp_random(uuid=test_uuid_v4))
        # UUID version must be 4
        with self.assertRaises(Exception):
            generate.arcp_random(uuid=test_uuid_v1)
    def testUUIDPath(self):
        self.assertEqual("arcp://uuid,8c36d39a-18be-4aa8-b1ce-fef330b00a28/folder/file.txt",
            generate.arcp_random("/folder/file.txt", uuid=test_uuid_v4))
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

if __name__ == '__main__':
    unittest.main()