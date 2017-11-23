## What is the wof:controlled property used for?

Many Who’s On First records have a `wof:controlled` property that is used to maintain curated property values in a given Who’s On First record during automatic updates and other editing tasks. Extreme caution should be exercised when changing values in properties that are marked controlled. The most common use of this property is to maintain the `wof:hierarchy` and `wof:parent_id` properties, as follows:

```
"wof:controlled":[
    "wof:hierarchy",
    "wof:parent_id"
]
```

In the case above, the `wof:controlled` property includes `wof:hierarchy` and `wof:parent_id`; because Who's On First tools respect controlled properties during automatic updates any potential changes to the records `wof:hierarchy` or `wof:parent_id` values would be skipped.

This is a useful tool for records with dual-hierarchies, or for records that have hand-crafted hierarchies that we have specifically set (and would prefer not to reset). The record for [the City of New York](https://whosonfirst.mapzen.com/spelunker/id/85977539/), for example, has the following `wof:controlled` property:

```
"wof:controlled":[
    "wof:hierarchy",
    "wof:parent_id",
    "wof:belongs_to"
]
```

This has been set due to the City of New York having five "legal" parents at the county level (Kings, Queens, New York, Bronx, and Richmond). This means that any future work done to this record will not reset the hand-crafted dual-hierarchy, `wof:parent_id`, or `wof:belongs_to` property values.

Check out our hierarchy building Python code, here, for more detail: https://github.com/whosonfirst/py-mapzen-whosonfirst-hierarchy/blob/master/mapzen/whosonfirst/hierarchy/__init__.py#L48-L79


