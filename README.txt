Userman
=======

Simple user account handling system for use with web services. Built on
top of Tornado and CouchDb.

API
---

The RESTful API is documented at http://userman-dev.scilifelab.se/apidoc
.

A number of code examples for using the API can be found in the nosetest
**test\_*.py*\* files.

Note that each call to the API must include an API token which is the
only mechanism used for authentication in the API. The API token is
specific for the user account, and is available in the user page for the
account.

Development server
------------------

The development server is at http://userman-dev.scilifelab.se/ . It is
currently reachable only from within SciLifeLab Stockholm.

Production server
-----------------

The production server has not yet been installed. It will probably be at
https://userman.scilifelab.se/ and will be reachable from outside
SciLifeLab. Accounts will be subject to approval by the Userman
administrator.
