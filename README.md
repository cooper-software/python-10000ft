# tenthousandfeet

This is an unofficial python client for the [10000ft API](http://10kft.github.io/api-documentation/). As far as I know there isn't an official one. [10000ft](http://www.10000ft.com) is a relatively new service and the API is even fresher. The goal for this client is 100% coverage and lightweightyness. Here's hoping you find it useful but keep in mind the freshness.

# Install

You can install with `easy_install` or `pip`.

```sh
pip install tenthousandfeet
```

# Usage

The python client closely follows the structure of the API [documented here](http://10kft.github.io/api-documentation/). The client has a number of collections which support some or all of the `list`, `show`, `create`, `update` and `delete` methods. Collections may also have subcollections which work the same way but are available as an attribute of the parent collection.

Here's a quick example:

```python
from tenthousandfeet import TenThousandFeet

# Create a client
client = TenThousandFeet('AUTH_TOKEN')

# Get all the users in your organization
users = client.users.list()

# Get the status history for a user
statuses = client.users.statuses(users[0]['id']).list()

# Dates are handled for you
projects = client.projects.list()
projects[0]['created_at'] # -> datetime.datetime(2014, 7, 23, 0, 22, 24, tzinfo=tzutc())

# it works the other way too
# (and the client will remove prefixed underscores from paramter names
# so you can use the reserved word "from")
from datetime import datetime
future_projects = client.projects.list(_from=datetime.now())
```

## Authentication

10000ft uses token-based authentication. All you need to do is pass in your token to the client like this:

```python
from tenthousandfeet import TenThousandFeet
client = TenThousandFeet('AUTH_TOKEN')
```

## Endpoints

The 10000ft team provides both [test and pre-production endpoints](http://www.10000ft.com/reference/integration/custom-integrations), which is incredibly helpful. The URLs are defined in the client to make switching easier.

```python
from tenthousandfeet import TenThousandFeet, VNEXT_URL
client = TenThousandFeet('AUTH_TOKEN', endpoint=VNEXT_URL)
```

## Error handling

If the service returns a non-200 or 201 HTTP response, the client with raise `tenthousandfeet.Error`.

```python
try:
    client.projects.list()
except tenthousandfeet.Error, e:
    print "Error with status code %d and message %s" % (e.status_code, e.message)
```

## Collection methods

Collections have one or more of the following methods:

* `list(**kwargs)` - get a list of items
* `show(object_id, **kwargs)` - Get a single item
* `create(**kwargs)` - Create a new item
* `update(object_id, **kwargs)` - Update an existing item
* `delete(object_id, **kwargs)` - Delete an existing item

## Sub-collections

In addition to the above methods, some collections have sub-collections. A sub-collection works the same way as a collection but you must provide an object ID to retrieve one like so:

```python
budget_items = client.projects('project123').budget_items.list()
```

## Collections

Here is a list of the collections as defined by this client. I'll do my best to keep this up to date but please refer to the [official docs](http://10kft.github.io/api-documentation/) for the latest information.

### projects
__methods:__ list, show, create, update, delete<br />
__sub-collections:__ phases, users, budget_items, tags, time_entries 

### users
__methods:__ list, show, create, update<br />
__sub-collections:__ statuses, assignments, tags, time_entries

### projects.phases
Phases are the same as projects but they have a project as a parent.

### projects.users
__methods:__ list

### projects.budget_items
__methods:__ list, show, create, update, delete

### (projects|users).tags
__methods:__ list, create, delete

### (projects|users).time_entries
__methods:__ list, show, create, update, delete

### users.statuses
__methods:__ list, create

### users.assignments
__methods:__ list, show, create, delete

### budget_item_categories
__methods:__ list<br />

### leave_types
__methods:__ list, show<br />

# Thanks and stuff

Thanks to the 10000ft team for making an API available (and a usefully consistent one, at that!). Future thanks to any that find errors in this document or the software.