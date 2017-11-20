## Various latitude/longitude properties

### geom

Find out more about the `geom` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/geom).

The `geom:latitude` and `geom:longitude` represent a geometric centroid for a record.

These values are machine-generated math centroids for a record's geometry.

### intersection

Find out more about the `intersection` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/intersection).

The `intersection:latitude` and `intersection:longitude` are used in [intersection records](https://whosonfirst.mapzen.com/spelunker/placetypes/intersection/) to indicate the location of an intersection. 

The values are latitude and longitude values from the source data used to generate the Voronoi intersection polygons.

### lbl

Find out more about the `lbl` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/lbl).

The `lbl:latitude` and `lbl:longitude` represent an optional, curated location for a given record where the label or search result pin should be placed.

### local

Find out more about the `local` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/local).

The `local:latitude` and `local:longitude` represent where a local resident would say the center of a place is.

For a neighbourhood this could be a subway stop, large park, or major street intersection.

Take the [Mission](https://whosonfirst.mapzen.com/spelunker/id/1108830809/) in [San Francisco](https://whosonfirst.mapzen.com/spelunker/id/85922583/), for example;; locals in San Francisco would likely say the center of the "Mission" somewhere close to the 16th and Mission St BART Station.

### nav

Find out more about the `nav` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/nav).

The `nav:latitude` and `nav:longitude` represent the centroid used for turn-by-turn navigation and "snapped" to the nearest road to the record's "entrance" (like the main entrance to a museum).

For a locality this could be city hall or the center of downtown, or the road intersection of the largest roads in the place.

### reversegeo

Find out more about the `reversegeo` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/reversegeo).

The `reversegeo:latitude` and `reversegeo:longitude` represent a centroid used for reverse-geocoding and point-in-polygon work.

These properties are either hand-crafted or sourced from Mapshaper.

These properties are the "first choice" when conducting reverse-geocoding and point-in-polygon work and are not meant for other purposes like labeling a map or displaying search results.

The `reversegeo` centroid should fall within a record's geometric bounding box.

### tourist

Find out more about the `tourist` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/tourist).

The `tourist:latitude` and `tourist:longitude` represent what the "tourist" centroid for a place is.

Take the [Mission](https://whosonfirst.mapzen.com/spelunker/id/1108830809/) in [San Francisco](https://whosonfirst.mapzen.com/spelunker/id/85922583/), for example; tourists visiting San Francisco would likely say the center of the "Mission" is Mission Dolores Park.

**See also**: 

https://github.com/whosonfirst/go-whosonfirst-geojson-v2/blob/master/properties/whosonfirst/whosonfirst.go#L65-L92