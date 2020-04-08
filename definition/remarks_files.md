## What is a remarks file?

To document special cases, unique administrative hierarchies, and intricacies of various records in Who's On First, we have introduced "remarks" files. Think of remarks files as a unique change log for a given record.

For example, Who's On First maintains just one remarks file, the `1158857531-remarks.md` file for [St. Petersburg, Russia](https://spelunker.whosonfirst.org/id/1158857531/), though there will inevitably be more remarks files in the future.

The following is needed to indicate that remarks file(s) are present for a record:

1. 1. A new [`mz:remarks`](https://github.com/whosonfirst/whosonfirst-properties/blob/master/properties/mz/remarks.json) property in the record's properties list.

2. Create a `{id}-remarks.md` file next to the {id}.geojson file that contains human-readable markdown-formatted notes, with the following header:

```
## {id}

### Date: _YYYY-MM-DD_
### Author: _github username_
### Notes
```

And... that's it. Take a look at the [St. Petersburg files](https://github.com/whosonfirst-data/whosonfirst-data-admin-ru/tree/master/data/115/885/753/1) to get a better understanding of the file structure and contents of the remarks file.