## What is a remarks file?

To capture special cases, unique administrative hierarchies, and intricacies of various records in Who's On First, we have introduced "remarks" files. Think of remarks files as a unique change log for a given record.

As of writing this, Who's On First maintains just one remarks file, the `1158857531-remarks.md` file for [St. Petersburg, Russia](https://whosonfirst.mapzen.com/spelunker/id/1158857531), though there will inevitably be more remarks files in the future.

The following is needed to add a remarks file to a record:

1. A new [`mz:remarks`](https://github.com/whosonfirst/whosonfirst-properties/blob/master/properties/mz/remarks.json) property in the record's properties. The convention is as follows (where `{id}` is the record's `wof:id`):

```
"mz:remarks":[
  "{id}-remarks.md"
],

```

2. Create a `{id}-remarks.md` file that contains human-readable markdown-formatted notes, as well as the following header:

```
## {id}

### Date: _YYYY-MM-DD_
### Author: _github username_
### Notes
```

And... that's it. Take a look at the [St. Petersburg files](https://github.com/whosonfirst-data/whosonfirst-data/tree/master/data/115/885/753/1) to get a better understanding of the file structure and contents of the remarks file.