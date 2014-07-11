" Userman: Various constants."

import re

# For CouchDB view ranges.
# CouchDB uses the Unicode Collation Algorithm, which is not the same
# as the ASCII collation sequence. The endkey is inclusive, by default.
HIGH_CHAR = 'ZZZZZZZZ'

IUID_RX   = re.compile(r'^[0-9a-z]{32}$')

# Tornado server
USER_COOKIE_NAME = 'userman_user'
TEMPLATE_PATH    = 'templates'
STATIC_PATH      = 'static'
STATIC_URL       = r'/static/'
LOGIN_URL        = r'/login'

# Database
DB_DOCTYPE = 'userman_doctype'
USER       = 'user'
TEAM       = 'team'
SERVICE    = 'service'
LOG        = 'log'

# Roles
ADMIN = 'admin'
ROLES = [USER, ADMIN]

# Account status
PENDING  = 'pending'            # Account created, admin needs to approve
APPROVED = 'approved'           # Account approved, activation code sent
ACTIVE   = 'active'             # Account activated by user
BLOCKED  = 'blocked'            # Account blocked by admin
STATUSES = set([PENDING, APPROVED, ACTIVE, BLOCKED])
