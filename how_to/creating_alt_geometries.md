# What is an alt-geometry and how are they defined and catalogued in Who's On First?

Each record in Who's On First has a point and/or a polygon geometry. San Francisco, for example, has a polygon geometry, stored in the 85922583.geojson file ([here](https://whosonfirst.mapzen.com/spelunker/id/85922583/)). 
This polygon geometry is the default geometry of San Francisco; a record's default geometry is in any geojson file that follows the following convention:

`id.geojson`

_Example: 85922583.geojson_

However, Who's On First also stores alt-geometry (alternate geometry) records. This not only allows Who's On First to maintain flexibility in record keeping, but also allows Who's On First to house geometries from a wide variety of sources. It also allows users and services to specify which geometry to use.

## What rules must alt-geometries follow?

At a minimum, alt-geometry filenames must conform to the following convention:

`id-alt-source.geojson`

_Example: 85922583-alt-mapzen.geojson_

The `source` must be listed in the [`whosonfirst-sources`](https://github.com/whosonfirst/whosonfirst-sources) repository. This is required record-keeping that allows any user or application to trace the origin of that geometry.

Alt-geometry records **must** include the following minimum set of properties:

* **id** - The unique `wof:id` of the feature that this alt-geometry represents
* **type** - Should always equal `"feature"`
* **properties**
  * **src:alt_label_** - The `{SOURCE}-{FUNCTION}-{EXTRAS}` portion of the alt geometry filename, not including the `ID-alt-` prefix of the `.geojson` suffix. See also: https://github.com/whosonfirst/go-whosonfirst-uri/blob/master/uri_test.go
  * **src:geom** - The source of this alt-geometry. This source must be listed in the [`whosonfirst-sources`](https://github.com/whosonfirst/whosonfirst-sources) repo
  * **wof:geomhash** - The alpha-numeric geomhash code (more info [here](https://en.wikipedia.org/wiki/Geohash))
  * **wof:id** - The unique `wof:id` of the feature that this alt-geometry represents
  * **wof:repo** - The GitHub repository name where the record can be found
* **bbox** - The bounding box coordinates of the alt-geometry feature
* **geometry** - The geometric coordinates of the alt-geometry feature

Alt-geometry records **may** include the following additional properties:

* **properties**
  * **wof:placetype** - A string value representing the record's placetype. See: the [`whosonfirst-placetypes`](https://github.com/whosonfirst/whosonfirst-placetypes) repo.
  * **lbl:latitude** - The coordinate that specifies a label's north–south position. Latitude is a decimal number between _-90.0_ and _90.0_.
  * **lbl:longitude** - The coordinate that specifies a label's east-west position. Longitude is a decimal number between _-180.0_ and _180.0_.
  * **reversegeo:latitude** - Represents the latitude value to use when reverse geocoding a record.
  * **reversegeo:longitude** - Represents the longitude value to use when reverse geocoding a record.

An alt-geometry filename should always include the associated feature's `wof:id`, "alt", and the source name (with dashes in between each value).

## What optional rules apply to alt-geometries?

In addition to the above rules, an alt-geometry can also include "use", "scope", and "detail". A filepath with such information would follow this convention:

`id-alt-source-function-scope-detail.geojson`

Where properties include:

* **source** (eg: `uscensus`) – The source of this geometry, which should match a file in the `whosonfirst-sources` repository
* **function** that is intended (e.g.: `display`) – This could include:
  * **search** - For place by text (free or structured, e.g. forward geocoding) and getting back a (label) latitude/longitude, (label) bounding box, full geometry, and hints about "hierarchy label" generation. 
  * **reverse geocode**  - For use of latitude/longitude to a place (preferring the "biggest" shape inclusive of territorial waters)
  * **data visualization** (map **display**) - Based on polygon features (e.g. choropleth, with some sophistication around water and land parts, preferring the land parts)
  * **label basemap** "points" (e.g.: `locality` townspots + text) and "polygons" (e.g.: `region` area text) - It's important to know which "locality" features `do not usually represent a single compact populated place` so their `mz:min_zoom` can be properly set, and we can choose the correct "point" or "polygon" labeling (and possibly switch between them at different zooms)
  * **showing boundary lines on a basemap** (e.g. `region` boundary, `disputed` area boundaries, with some sophistication around water and land parts – e.g. option to not show territorial water parts, coastline parts, and/or inland water parts).
* **scope** is level-of-scope (e.g.: `terrestrial`). This could include:
  * `territorial` - Default optimized for revGeo inclusive of all marine and territorial waters (no water clipping), understood that Mapzen may have modified the original, but it's still "sourced" to the source.
  * `terrestrial` - Clipped to land + terrestrial waters (e.g. clipped to ocean coastline, but not punched thru for large inland water bodies), understood that Mapzen may have modified the original, but it's still "sourced" to the source. Used for most choropleth maps.
  * `land` - No marine waters, no inland waters. Used in contexts where someone doesn't want to load separate "earth" base or "water" top layers.
  * `marine` - Geometric opposite of terrestrial, useful for boundary lines.
* **detail** is the level-of-detail (e.g.: `zoom-10` or `1024-px`)

A filename with all of the above properties would look like the following example:

* `85668127-alt-uscensus-display-terrestrial-zoom-10.geojson`

Permutations include:

* `85668127-alt-uscensus.geojson` _(common)_
* `85668127-alt-uscensus-display.geojson` _(common-optional)_
* `85668127-alt-uscensus-display-terrestrial.geojson` _(optional)_
* `85668127-alt-uscensus-display-zoom-10.geojson` _(optional)_
* `85668127-alt-uscensus-display-1024-px.geojson` _(optional)_
* `85668127-alt-uscensus-display-terrestrial-zoom-10.geojson` _(optional)_
* `85668127-alt-uscensus-display-terrestrial-1024-px.geojson` _(optional)_

## Affects to the default geometry

If a default record in Who's On First has an alt-geometry record associated to it, the default record will have properties that point to it's associated alt-geometries. A snippet of these properties for the San Francisco example are shown below:

```
    "src:geom_alt":[
        "mapzen",
        "alt-uscensus-display-zoom-10-original",
        "alt-uscensus-display-terrestrial",
        "alt-uscensus-display-zoom-10",
        "alt-uscensus-display-1024-px",
        "alt-uscensus-display-terrestrial-zoom-10"
    ],
```

## Goals

Like most of Who's On First, this guideline is a work in progress and allows for future flexibility. We do not know every possible future use case for alt-geometries, but we can prepare for a variety of use cases by allowing flexibility and additions to the above rules.

Ideally, every feature in Who's On First will have at least two geometries; a default geometry that is some combination of simplification and file size and an alt-geometry that is either a source or display geometry.

## Implementations

* [Go](https://github.com/whosonfirst/go-whosonfirst-uri)
* [Javascript](https://github.com/whosonfirst/js-mapzen-whosonfirst/blob/master/src/mapzen.whosonfirst.uri.js)
* [PHP](https://github.com/whosonfirst/flamework-whosonfirst/blob/master/www/include/lib_whosonfirst_uri.php)
* [Python](https://github.com/whosonfirst/py-mapzen-whosonfirst-uri)

## See also:

https://github.com/whosonfirst/whosonfirst-geometries
