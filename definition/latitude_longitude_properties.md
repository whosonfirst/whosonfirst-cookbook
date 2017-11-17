## Various latitude/longitude properties


### geom

Find out more about the `geom` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/geom).

The `geom:latitude` and `geom:longitude` represent a geometric centroid for a record.

These values are machine-generated math centroids for a record's geometry.

### intersection

Find out more about the `intersection` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/intersection).

The `intersection:latitude` and `intersection:longitude` represent the intersection location for a given record.

### lbl

Find out more about the `lbl` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/lbl).

The `lbl:latitude` and `lbl:longitude` represent the label location for a given record.

### local

Find out more about the `local` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/local).

The `local:latitude` and `local:longitude` represent what the "local" centroid for a "place" is. 

### nav

Find out more about the `nav` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/nav).

The `nav:latitude` and `nav:longitude` represent the centroid used for a navigation endpoint.

### reversegeo

Find out more about the `reversegeo` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/reversegeo).

The `reversegeo:latitude` and `reversegeo:longitude` represent a centroid used for reverse-geocoding and point-in-polygon work.

These properties are either hand-crafted or sourced from Mapshaper.

These properties are the "first choice" when conducting reverse-geocoding and point-in-polygon work and are not meant for any other purpose.

The `reversegeo` centroid must fall within a record's geometric bounding box.

### tourist

Find out more about the `tourist` property [here](https://github.com/whosonfirst/whosonfirst-properties/tree/master/properties/tourist).

The `tourist:latitude` and `tourist:longitude` represent what the "tourist" centroid for a "place" is.

Take the [Mission](https://whosonfirst.mapzen.com/spelunker/id/1108830809/) in [San Francisco](https://whosonfirst.mapzen.com/spelunker/id/85922583/), for example; tourists visiting San Francisco would likely say the center of the "Mission" is Mission Dolores Park.

**See also**: 

https://github.com/whosonfirst/go-whosonfirst-geojson-v2/blob/master/properties/whosonfirst/whosonfirst.go#L65-L92