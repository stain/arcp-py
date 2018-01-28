# arcp-py

Create/parse [arcp (Archive and Package) URIs](https://tools.ietf.org/html/draft-soilandreyes-arcp-02)


## License

* (c) 2018 Stian Soiland-Reyes, The University of Manchester, UK

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file
[LICENSE.txt](LICENSE.txt) for details.


## Usage


```python
>>> arcp.arcp_random("/foaf.ttl", fragment="me")
'arcp://uuid,dcd6b1e8-b3a2-43c9-930b-0119cf0dc538/foaf.ttl#me'

>>> arcp.arcp_hash(b"abc", "/folder/")
'arcp://ni,sha-256;ungWv48Bz-pBQUDeXa4iI7ADYaOWF3qctBD_YfIAFa0/folder/'

>>> arcp.arcp_location("http://example.com/data.zip", "/file.txt")
'arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/file.txt'

>>> arcp.parse_arcp("arcp://uuid,b7749d0b-0e47-5fc4-999d-f154abe68065/file.txt").uuid.version
5

>>> css = arcp.arcp_name("app.example.com", "css/style.css")
>>> urllib.parse.urljoin(css, "../fonts/foo.woff")
'arcp://name,app.example.com/fonts/foo.woff'
```

