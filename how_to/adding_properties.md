# Adding (and Validating) Who's On First Property Definitions

## The Basic Workflow

1. Clone or fork the [`whosonfirst-properties`](https://github.com/whosonfirst/whosonfirst-properties) repo
1. Create a branch to hold the definition for the property definition you're just about to add. Make the branch name meaningful, a la `git-flow`. Something like `[your initials]-add-[property-name]` should do the trick.
1. Copy [`properties_template.json`](https://github.com/whosonfirst/whosonfirst-properties/blob/master/properties_template.json) to `properties/[prefix]/[name].json`.
1. Get a new [Brooklyn Integer](#add-id) for the property definition's `id` property.
1. Flesh out the rest of the template. The `id`, `name`, `prefix` and `type` properties are _mandatory_ but adding in the other properties, especially the `description` would really help.
1. [Validate _all_ the property definitions](#validate-properties), including the new one.
1. Clone or fork the [`whosonfirst-json-schema`](https://github.com/whosonfirst/whosonfirst-json-schema) repo.
1. [Regenerate](#update-schema) the WOF `properties` JSON schema.
1. Clone or fork the [`whosonfirst-data`](https://github.com/whosonfirst-data/whosonfirst-data) repo, or wherever the new properties will actually live (see the caveat below), and add them, in some way, to the WOF documents.
1. [Validate _all_ the WOF documents](#validate-docs) potentially affected by the new property
1. Add your changes, commit, push and issue a Pull Request for `whosonfirst-data`.
1. Add your changes, commit, push and issue a Pull Request for `whosonfirst-properties`.
1. Add your changes, commit, push and issue a Pull Request for `whosonfirst-json-schema`.
1. Make coffee and bask in the satisfaction of a job well done.

_Caveat:_ at some point in the future a lot of this _should_ be automated in a
CI type environment. At the moment it's not, so for now, it's a manual process.

_Caveat:_ Not all WOF documents live in the `whosonfirst-data` repo, brands and venues
don't, but they all live in the `whosonfirst-data` organisation's repos.

## <a name="add-id"></a>Adding a Property Definition ID

Each property definition contains a unique id, typically derived from [Brooklyn Integers](https://www.brooklynintegers.com).

For adding a single id in an ad-hoc manner, the following `cURL` incantation will give you a new `id` (assuming you have `curl` and `jq` already installed that is).

```
$ curl --silent -X POST -F "method=brooklyn.integers.create" https://api.brooklynintegers.com/rest | jq '.'
{
  "integers": [
    {
      "integer": 1159339441
    }
  ],
  "integer": 1159339441,
  "notice": "see the 'integers' array? that is the new new and the old way of returning vanilla attributes is deprecated as of 20120730",
  "stat": "ok"
}
```


## <a name="validate-properties"></a>Validating the Property Definitions

You will need ...
* A clone or fork of the [`whosonfirst-json-schema`](https://github.com/whosonfirst/whosonfirst-json-schema) repo
* A working NodeJS install

```
$ cd /path/to/whosonfirst-json-schema
$ $ ./scripts/wof-validate-props --dir /path/to/whosonfirst-properties/properties --schema schema/properties/properties.json --verbose
1041 files scanned, 1011 selected, 1011 valid, 0 invalid
```

## <a name="update-schema"></a>Updating the Who's On First Document JSON Schema

You will need ...
* A clone or fork of the [`py-whosonfirst-json-schema`](https://github.com/whosonfirst/py-whosonfirst-json-schema) repo
* A working Python 2.7 install

```
$ cd /path/to/py-whosonfirst-json-schema
$ virtualenv .
$ source ./bin/activate
(py-whosonfirst-json-schema) $ pip install -e .
(py-whosonfirst-json-schema) $ ./scripts/wof-build-schema /path/to/whosonfirst-properties > /path/to/whosonfirst-json-schema/schema/properties.json
(py-whosonfirst-json-schema) $ deactivate
```

## <a name="validate-docs"></a>Validating the Who's On First GeoJSON Documents

You will need the prerequisites from [validating the property definitions](#validate-properties) above.

```
$ cd /path/to/whosonfirst-json-schema
$ ./scripts/wof-validate-docs --dir ~/Data/Downloads/whosonfirst-data/data --schema schema/docs/whosonfirst.json --references schema/docs/wof-*.json --references schema/geojson/geojson-*.json --verbose
951541 files scanned, 729533 selected, 729533 valid, 0 invalid
```

_Caveat:_ This is **not** a quick process. On a 2017 MacBook Pro with 16 GB of RAM and a 3.1 GHz Core i7 processor expect to loose over 1.5 hours while this eats up CPU cycles.

## See also

* https://github.com/whosonfirst/whosonfirst-properties
* https://github.com/whosonfirst/whosonfirst-json-schema
* https://github.com/whosonfirst/py-whosonfirst-json-schema
