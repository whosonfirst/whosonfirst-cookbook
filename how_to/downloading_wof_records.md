# Bundling Up Who's On First Records

In the wake of Who's On First's [Bundler tool](https://whosonfirst.org/blog/2017/02/10/bundler/) going offline, a simple interface to download GeoJSON bundles of Who's On First records is no longer available. Fear not; there are still methods to obtaining bundles of Who's On First records.

## Tools

Using a combination of the [metafiles](https://dist.whosonfirst.org/bundles/), the [Spelunker](https://spelunker.whosonfirst.org), and [utilities scripts](https://github.com/whosonfirst/py-mapzen-whosonfirst-utils), we can use pre-built scripts to download bundles of GeoJSON by placetype and/or by parent record.

As of today, metafiles per placetype can be found in the `*-bundle.tar.bz2` files, [here](https://dist.whosonfirst.org/bundles/).

### Bundles by Placetype

Pre-built bundles per placetype can be found [here](https://dist.whosonfirst.org/bundles/). Alternatively, you can follow the steps below to create your own.

In the `scripts` directory in the `py-mapzen-whosonfirst-utils` repository, run the following in your command line:

> python wof-csv-to-feature-collection -p /path/to/whosonfirst-data/data -c /path/to/meta/wof-borough-latest.csv -o ~/Desktop/wof_boroughs.geojson

A breakdown of what we're passing:

* **wof-csv-to-feature-collection**: calls the `wof-csv-to-feature-collection` python script
* **-p /path/to/whosonfirst-data/data**: passes the `data` endpoint as an option
* **-c /path/to/meta/wof-borough-latest.csv**:  passes the placetype-specific metafile as an option
* **-o ~/Desktop/wof_boroughs.geojson**: passes the given output file as an option

Passing this command will result in a `wof_boroughs.geojson` file that contains all `borough` records in Who's On First.

### Bundles of Placetypes by Parent ID

In the `scripts` directory in the `py-mapzen-whosonfirst-utils` repository, run the following in your command line:

> python wof-csv-to-feature-collection -p /path/to/whosonfirst-data/data -c /path/to/meta/wof-borough-latest.csv -o ~/Desktop/nyc_boroughs.geojson -a /path/to/whosonfirst-properties/aliases/property_aliases.json --slim -f 85977539

A breakdown of what we're passing:

* **wof-csv-to-feature-collection**: calls the `wof-csv-to-feature-collection` python script
* **-p /path/to/whosonfirst-data/data**: passes the `data` endpoint as an option
* **-c /path/to/meta/wof-borough-latest.csv**:  passes the placetype-specific metafile as an option
* **-o ~/Desktop/nyc_boroughs.geojson**: passes the given output file as an option
* **-a /path/to/property_aliases.json**: pulls from [property alias file](https://github.com/whosonfirst/whosonfirst-properties/blob/master/aliases/property_aliases.json) to build attribute names
* **--slim**: exports a GeoJSON bundle with minimal properties
* **-f 85977539**: passes a valid `wof:id` (in this case [New York](https://spelunker.whosonfirst.org/id/85977539/))

Passing this command will result in a `nyc_boroughs.geojson` file that contains all `borough` records in New York.

### Bundles of Specific IDs

In the `scripts` directory in the `py-mapzen-whosonfirst-utils` repository, run the following in your command line:

> python wof-csv-to-feature-collection -p /path/to/whosonfirst-data/data -o ~/Desktop/nyc_boroughs.geojson -a /path/to/whosonfirst-properties/aliases/property_aliases.json --slim -f 85977539

A breakdown of what we're passing:

* **wof-csv-to-feature-collection**: calls the `wof-csv-to-feature-collection` python script
* **-p /path/to/whosonfirst-data/data**: passes the `data` endpoint as an option
* **-c /path/to/list_of_ids.csv**: passes a list of valid wof:id values to bundle
* **-o ~/Desktop/nyc_boroughs.geojson**: passes the given output file as an option
* **-a /path/to/property_aliases.json**: pulls from [property alias file](https://github.com/whosonfirst/whosonfirst-properties/blob/master/aliases/property_aliases.json) to build attribute names
* **--slim**: exports a GeoJSON bundle with minimal properties
* **-i**: infers filepaths

Passing this command will result in a `nyc_boroughs.geojson` file that contains all `borough` records in New York.

## Caveats

As the feature count increases in your bundles, the longer this process takes. Bundling a few hundred neighbourhoods in you local area may take a couple of minutes to download, but bundling all localities in Who's On First could take up to, possibly more than, an hour.

## See also

- http://dist.whosonfirst.org
- https://github.com/whosonfirst/whosonfirst-export
