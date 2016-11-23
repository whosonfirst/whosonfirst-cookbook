#What is an alt-geometry and how are they defined and catalogued in Who's On First?

Each record in Who's On First has a point and/or a polygon geometry. San Francisco, for example, has a polygon geometry, stored in the 85922583.geojson file ([here](https://whosonfirst.mapzen.com/spelunker/id/85922583/)). 
This polygon geometry is the **default** geometry of San Francisco; the **default** geometry is the geometry used by various Mapzen services. A record's **default** geometry is in any geojson file that follows the following convention:

`"feature's wof:id".geojson`

_Example: 85922583.geojson_

However, Who's On First also stores **alt-geometries** (alternate geometries) records. This not only allows Who's On First to maintain flexibility in record keeping, but also allows Who's On First to house geometries from a wide variety of sources. These alt-geometries fall into one of two categories: **source** or **display**.

##What rules must alt-geometries follow?

**At a minimum, alt-geometry filenames must conform to the following convention:**

`"feature's wof:id"-"alt"-"source".geojson`

_Example: 85922583-alt-mapzen.geojson_

**Alt-geometry records must include the following minimum set of properties:**

* **`id`** - The unique `wof:id` of the feature that this alt-geometry represents.
* **`type`** - Should always equal `"feature"`.
* **`properties`**
  * **`src:geom`** - The source of this alt-geometry. This source must be listed in the [`whosonfirst-sources` repo](https://github.com/whosonfirst/whosonfirst-sources).
  * **`wof:geomhash`** - The alpha-numeric geomhash code (more info [here](https://en.wikipedia.org/wiki/Geohash))
  * **`wof:id`** - The unique `wof:id` of the feature that this alt-geometry represents.
* **`bbox`** - The bounding box coordinates of the alt-geometry feature.
* **`geometry`** - The geometric coordinates of the alt-geometry feature.

An alt-geometry filename should always include the associated feature's `wof:id`, "alt", and the source name (with dashes in between each value).

##What optional rules apply to alt-geometries?

In addition to the above rules, an alt-geometry's "function" can be appended to the end of the filename. The following list of functions is a work in progress, but can include:

* **`original`** - The original data we got from source | default
* **`display`** - Used for map display purposes (eg: zoom 5)
* **`thumbnail`** - Used for screen pixel width purposes (eg: 1024px wide)
* **`groundtruth_coastal`** - Geometries that are cut at coastlines. Most likely used for reverse geocoding purposes.
* **`groundtruth_clipped`** - Geometries that are clipped at a specific boundary.
* **`folk`** - Geometries that don't map to administrative truths, but are instead used to represent what a local perspective is of the feature's area.

_Example: 85922583-alt-mapzen.geojson_
_Example: 85922583-alt-quattroshapes-original.geojson_
_Example: 85922583-alt-quattroshapes-display.geojson_
_Example: 85922583-alt-quattroshapes-display-1024px.geojson_

##Affects to the default geometry

If a default record in Who's On First has an alt-geometry record associated to it, the default record will have properties that point to it's associated alt-geometries. A snippet of these properties for the San Francisco example are shown below:

```
    "src:geom_alt":[
        "mapzen",
        "quattroshapes-original",
        "quattroshapes-original-display",
        "quattroshapes-original-display-1024px"
    ],
```

##Goals

Like most of Who's On First, this guideline is a work in progress and allows for future flexibility. We do not know every possible future use case for alt-geometries, but we can prepare for a variety of use cases by allowing flexibility and additions to the above rules.

Ideally, every feature in Who's On First will have at least two geometries; a default geometry that is some combination of simplification and file size and an alt-geometry that is either a source or display geometry.

##See also:

https://github.com/whosonfirst/whosonfirst-geometries
