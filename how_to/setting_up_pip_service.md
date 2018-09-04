# Setting up a point-in-polygon service

When updating records in the [whosonfirst-data](https://www.github.com/whosonfirst-data/whosonfirst-data) repository, it is often necessary to update [hierarchies](https://github.com/whosonfirst/whosonfirst-properties/blob/master/properties/wof/hierarchy.json) of new and existing geojson records.

This document is not meant to be a replacement for documentation in the repositories below, but rather a general outline for spinning up a point-in-polygon (PIP) service to update whosonfirst-data records.



## Steps

Assuming you already have cloned the [whosonfirst-data](https://www.github.com/whosonfirst-data/whosonfirst-data) repository, supplemental repositories, and the most recent versions of [PostGIS](https://postgis.net/), follow the steps below:

**clone repositories** 
  
 * [go-whosonfirst-pgis](https://github.com/whosonfirst/go-whosonfirst-pgis)
 * [py-mapzen-whosonfirst-spatial](https://github.com/whosonfirst/py-mapzen-whosonfirst-spatial/)
 * [py-mapzen-whosonfirst-hierarchy](https://github.com/whosonfirst/py-mapzen-whosonfirst-hierarchy/)

**index whosonfirst-data in postgres**

After navigating to the `go-whosonfirst-pgis` repository, follow the README file to index all of the whosonfirst-data record into postgres.

This will setup postgis and create the database that we will load the whosonfirst-data into:

```
createuser -P whosonfirst
createdb -O whosonfirst whosonfirst
psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" whosonfirst
psql -c "CREATE TABLE whosonfirst (id BIGINT PRIMARY KEY,parent_id BIGINT,placetype_id BIGINT,is_superseded SMALLINT,is_deprecated SMALLINT,meta JSON, geom_hash CHAR(32), lastmod CHAR(25), geom GEOGRAPHY(MULTIPOLYGON, 4326), centroid GEOGRAPHY(POINT, 4326))" whosonfirst
psql -c "GRANT ALL ON TABLE whosonfirst TO whosonfirst" whosonfirst
psql -c "CREATE INDEX by_geom ON whosonfirst USING GIST(geom);" whosonfirst
psql -c "CREATE INDEX by_centroid ON whosonfirst USING GIST(centroid);" whosonfirst
psql -c "CREATE INDEX by_placetype ON whosonfirst (placetype_id);" whosonfirst
```

Run the wof-pgis-index tool, via:

```
./bin/wof-pgis-index -verbose -mode directory /path/to/whosonfirst-data
```

## Updating a Who's On First record

The [py-mapzen-whosonfirst-hierarchy](https://github.com/whosonfirst/py-mapzen-whosonfirst-hierarchy/) repository has a handy [rebuild script] that can be used to PIP a single Who's On First record.

By running the following command, the `wof-hierarchy-rebuild` tool will update the hierarchy of the `data/856/886/37/85688637.geojson` record using the new postgres index we've just spun up.

`wof-hierarchy-rebuild -C postgis /path/to/whosonfirst-data/data/856/886/37/85688637.geojson -U -v`



## Updating descendant records 

With a few minor tweaks to the `wof-hierarchy-rebuild` script, descendants of a Who's On First record can be updated, too.

Changing [line 67](https://github.com/whosonfirst/py-mapzen-whosonfirst-hierarchy/blob/master/scripts/wof-hierarchy-rebuild#L67) of the `wof-hierarchy-rebuild` tool from:

`changed = ancs.rebuild_feature(feature)`

to 

`changed = ancs.rebuild_and_export_feature(feature, data_root = options.data_root)`

will invoke the [rebuild_and_export_feature](https://github.com/whosonfirst/py-mapzen-whosonfirst-hierarchy/blob/master/mapzen/whosonfirst/hierarchy/__init__.py#L582) function which trickles down updates to descendant records and exports.

## See also:

- https://gist.github.com/ibraheem4/ce5ccd3e4d7a65589ce84f2a3b7c23a3
- https://github.com/whosonfirst/go-whosonfirst-pip-v2/issues/15
