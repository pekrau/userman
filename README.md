# Userman #

Simple user account handling system for use with web services.
Built on top of Tornado and CouchDb.


## API ##

The RESTful API is documented at http://userman-dev.scilifelab.se/apidoc .

A number of code examples for using the API can be found in the
nosetest `test_*.py` files.

Note that each call to the API must include an API token which is the
only mechanism used for authentication in the API. The API token is specific
for the user account, and is available in the user page for the account.


### Design notes ###

The API is designed such that all data sent to and received from the interface
is JSON containing pure application data. Metadata, such as the API access
token, is passed as a HTTP header item, so as not to clutter up the
data namespace. This also allows for sending other types of data as body
content, such as images, which cannot contain API access tokens.

Tip: Use the [requests](http://docs.python-requests.org/en/latest/)
package for all HTTP client code. It is way better than the urllib2 package
in the standard Python distribution.


### Packacke notes ###

Create the text variant of the README:

    pandoc -o README.txt -f markdown -t rst README.md

## Development server ##

The development server is at http://userman-dev.scilifelab.se/ .
It is currently reachable only from within SciLifeLab Stockholm.

### Installation ###

The development server is installed as an ordinary Python package in
`/usr/lib/python2.6/site-packages/userman` . The controlling configuration
file `tools-dev.yaml` (which is not part of the GitHub stuff) is located there.
I have set the owner of that directory to `per.kraulis` to make it
simpler for me... 

The development server is upgraded thus:

    $ pip install --upgrade --no-deps git+https://github.com/pekrau/userman

The Tornado service is started by the `/etc/rc.local` script.

The Apache server handles the redirect from the domain name to the Tornado
server which runs on port 8881. See `/etc/httpd/conf/httpd.conf`.

The log file written by the Tornado server currently goes to
the install directory.


## Production server ##

The source code used in production is located in:

    /usr/lib/python2.6/site-packages/userman

The configuration file is tools.yaml, of which a backup copy exists in:

    /home/per.kraulis/userman

The production server is upgraded thus:

    $ pip install --upgrade --no-deps git+https://github.com/pekrau/userman

The Tornado service is started by the `/etc/rc.local` script.

It will probably be at https://userman.scilifelab.se/ and will be reachable
from outside SciLifeLab. Accounts will be subject to approval by the
Userman administrator.
