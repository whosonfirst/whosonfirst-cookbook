# Updating Who's On First Neighbourhood Records (part one)

The [Who's On First](https://whosonfirst.mapzen.com/) (WOF) project is not pretending to be the authority of truth, but rather a home for data from various sources and a project that we hope generates discussion. The WOF gazetteer houses data for many geographies, including counties (which parent cities) and cities (which parent microhoods, neighbourhoods, and macrohoods). Neighbourhoods are the places where we live and work in cities; _the more neighbourhood data, the better._

![San Francisco, CA](https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/1.jpg)
_Photo Credit: [Travis Wise, Flickr](https://www.flickr.com/photos/photographingtravis/15876578760/in/photolist-qbXBJy-wS7pFF-2XzRnL-HbtCbX-rbmAJj-7dPz43-9Py6me-hEkAuS-8gihrC-8BCzsr-uVZPsT-92LBPi-Ecaiho-HDBW9C-7dPw9s-exakrT-dNzgiu-aJaiTz-nK4F3y-FtbMW-bywi7N-hzeCpW-8HXuPC-jeVkWQ-uiA2S7-pzMxbL-bjH5AC-bsyv8U-keLDPc-gWDhS-xadSek-nQz7At-brj2fe-wuPTK4-4856y6-pdYCPT-wSCsAz-FtesM-7j84Hs-dqBe97-5RT97n-fzhNSx-4heGvv-fKii4T-nqgSDG-xpnL1d-dHcAn7-pQYC72-9wduZD-wuF3bm_)_

**Our Audience:** Those who care about neighbourhoods and have a few hours to a few days to spend diving into QGIS. 

**Your Skills/Experience:** This tutorial was written with the intermediate to advanced GIS user. While this tutorial tries to explain the editing process in detail, some information may not be immediately clear to a beginning user.

**Why are neighbourhoods important to mapping?**

* **Labelling.** When we use a mapping application, we want neighbourhoods to be labeled on the map (in the right place and at the right zoom).
* **Ability to search.** Neighbourhoods should be searchable (with the ability to know how large the feature is and fit it into view).
* **Browsing venues.** We should be able to browse venues by neighbourhood.

It is important to understand where [placetypes](https://github.com/whosonfirst/whosonfirst-placetypes) fall within the WOF hierarchy. Neighbourhoods, macrohoods, and microhoods are described below:

* **Neighbourhoods:** A centralized community within a larger city, town, or borough.
* **Macrohoods:** A grouping of neighbourhoods within a larger city, town, or borough.
* **Microhoods:** A geographically localized sub-section of a neighbourhood.

This tutorial addresses the issues we found with San Francisco's neighbourhoods and describes the workflow we took in fixing them. In the end, we hope you can follow along and edit neighbourhoods for your own city!

**What are your options when updating neighbourhoods?**

* Notice just one neighbourhood that needs cleaning up? File a [Github issue](https://github.com/whosonfirst/whosonfirst-data/issues/new), or [email us](mailto:stephen.epps@mapzen.com). _[See something, say something.]_
* Notice an open dataset of administrative data? Open an [issue](https://github.com/whosonfirst/whosonfirst-data/issues/new) in our WOF repository. 
* Still interested but confused about all this Github and WOF-isms? We can send you a "starter kit" that includes your requested neighbourhoods. [Email us](mailto:stephen.epps@mapzen.com).
* Follow the instructions below and send us a [pull request](https://github.com/whosonfirst/whosonfirst-data/pulls).

**Key terms:**

Check out [these key terms](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/key_terms.md) if you have any questions about the vocabulary used in this guide.

## The Issue

We received a [report](https://github.com/whosonfirst/whosonfirst-data/issues/125) in the [whosonfirst-data repository](https://github.com/whosonfirst/whosonfirst-data) that the shape of San Francisco’s Golden Gate Park neighbourhood was both too small and extended into adjacent neighbourhoods. While researching online sources for a better shape, we noticed that most adjacent neighbourhood shapes in WOF could also be improved to align better with the road network and local expectations. After researching neighbourhood shapes online, we downloaded neighbourhood shapes for San Francisco from [SF OpenData](https://data.sfgov.org/), a city data website, to compare with the neighbourhood records in our WOF repository. We then filed a [new issue](https://github.com/whosonfirst/whosonfirst-data/issues/316) to handle all neighbourhood updates for San Francisco.

Typically, Who’s On First sources [Quattroshapes](http://www.quattroshapes.com) geometries for most neighbourhoods around the globe. However, many neighbourhoods in the United States, including San Francisco, source their default geometry from [Zetashapes](http://www.zetashapes.com). The Zetashapes project follows the same basic principles as Quattroshapes, but builds shapes up from Census 2010 features and can draw shapes that are too big, small, or _just plain weird_. We’ve seen problems with shapes extending in the water and far out into neighboring rural areas. This technique is responsible for the issues that we are correcting in San Francisco.

Drawing neighbourhood shapes is a tricky business. Strangers generally agree on what a neighbourhood is named and its rough shape, but even good friends can argue vehemently about where one neighbourhood ends and another begins - even if there are hard edges between neighbourhoods or they should overlap. Recognizing this, Who’s On First allows multiple alternate geometries for a place, but for practical reasons we need to set just one shape as the default geometry.

**To clean up our neighbourhood geometries, we needed to take five steps:**

* **#1** _Review WOF records for your locality. Get a sense of where they could be improved and where they are acceptable, focusing on names and shapes._
* **#2** _Research other neighbourhood sources on the internet._
* **#3** _Download authoritative neighbourhood geometries from a reliable, open license data source for your locality._
* **#4** _Reconciling our data sources. Things to think about: Is the number of neighbourhood records similar? Are the shapes similar or better? Could you draw your own shapes?_
* **#5** _Update records, either though a clean import or creating a new hybrid using the best of both (and your local knowledge)._

While specifics listed in this tutorial may reference San Francisco, our hope is that you will be able to follow along with these steps to update the neighbourhood records in your locality.

## 1: Review Who's On First records for your locality

In this section, you will either:

* Use the handy [Bundler Tool](https://whosonfirst.mapzen.com/spelunker/download/85688637/?exclude=nullisland#5/37.419/-119.307) (this example link points to descendants of California) to gather a collection of neighbourhood features in your given locality

**OR**

* Use the `git checkout` command in your terminal to **clone necessary repositories**
* **Collect** a .geojson file for all neighbourhoods in your locality (city)
* Add your .geojson file to a QGIS document for **review**

The Bundler Tool quickly gathers a collection of descendant records in GeoJSON format given your the parent record's ID. Simply click the "Download Descendants" link on any record's page in the Spelunker.

This is the "quick and easy" method to gathering neighbourhood records, however, this tool only gathers up to 500 WOF records. For larger queries or markets, you will need to clone necessary repositories and collect a .geojson file. Instructions below:

* Ensure that you have the most recent software packages. Windows users should have Powershell 3.0 before beginning any GitHub work from the terminal. A Powershell 3.0 download can be found [here](https://www.microsoft.com/en-us/download/details.aspx?id=34595). Additionally, all users should ensure they have `setuptools` for Python by [downloading](https://pypi.python.org/pypi/setuptools) Python 2.7 (or a more current version) and `GDAL 2.1` by [downloading](http://www.qgis.org/en/site/) QGIS 2.14 (or a more current version).
* Run `git checkout` on the [WOF Data repository](https://github.com/whosonfirst/whosonfirst-data), [WOF Properties repository](https://github.com/whosonfirst/whosonfirst-properties), and [WOF Utils repository](https://github.com/whosonfirst/py-mapzen-whosonfirst-utils).
* Run the `install` script in whosonfirst-utils repository.
* Open the `wof-csv-to-feature-collection.py` script in your `Utils` repo. Update line 63 with your local filepath.

Once complete, entering the following string in the terminal from the whosonfirst-utils repository's `scripts` folder allows us to collect San Francisco's neighbourhoods as a single .geojson file (updating filepaths of your local machine accordingly):

>_python wof-csv-to-feature-collection -p /usr/local/mapzen/whosonfirst-data/data -c /usr/local/mapzen/whosonfirst-data/meta/wof-neighbourhood-latest.csv --aliases /usr/local/mapzen/whosonfirst-properties/aliases/property_aliases.json -o ~/Desktop/SF_Neighbourhoods.geojson --slim --slim-template external_editor -f 85922583_

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/terminal_command.png">

_Image: Data collection script in the terminal._

_Note: The trailing number `85922583` at the end of this script is the WOF ID for [San Francisco](https://whosonfirst.mapzen.com/spelunker/id/85922583/#10/37.7850/-122.7278). When running this script, make sure to update that ID with whatever record you need neighbourhood geometries for. An ID is a unique identifier for records in WOF. Each record in WOF has an ID. To find the ID for your city, search the [Spelunker](https://whosonfirst.mapzen.com/spelunker) and copy the ID._

**Voilà!** We have a .geojson of WOF neighbourhood records in San Francisco! By changing the trailing ID (explained below), you can collect neighbourhood records for your own locality (city).

To better understand what we're requesting of our command, here is a breakdown of exactly what is included:

* **`python`**  Used to invoke python
* **`WOF-csv-to-feature-collection`**  The python script that collects WOF records.
* **`-p /PATH/whosonfirst-data/data`** sets the path to the local copy of all the WOF data. You will need to update this PATH depending on where you checked the file out.
* **`-c /PATH/whosonfirst-data/meta/WOF-neighbourhood-latest.csv`** The metafile for the placetype you are interested in - neighbourhood. You will need to update this PATH depending on where you checked the file out.
* **`--aliases /usr/local/mapzen/whosonfirst-properties/aliases/property_aliases.json`** Pulling in various aliases for attribute fields for your output file.
* **`-o ~/Desktop/SFNeighbourhoods.geojson`** Your output file.
* **`--slim`** Option parser to limit property export to subset (roughly those in the CSV file) and reduce file size.
* **`--slim-template`** Option parser to trim key names to fit Esri Shapefile format (10 charachter length limit).
* **`external_editor`** Return only necessary attribute fields for neighbourhood edits. 
* **`-f 85922583`** ID of the locality you need neighbourhood records for, found by searching our [Spelunker](https://whosonfirst.mapzen.com/spelunker).

**About the `external_editor` option:**
* This option was created for our neighbourhood editors and exports only relevant and required record attributes for WOF neighbourhood records. All required attributes (and applicable optional attributes) should be included when filing your PR of updated neighbourhood records. The `external_editor` attribute fields include:

* **'name'** The attribute that will be used for the `wof:name` field. Required for all files.
* **'id'** The attribute that will be used for the `wof:id` field. Required for all files.
* **'placetype'** The attribute that will be used for the `wof:placetype` field. Required for all files.
* **'parent_id'** The attribute that will be used for the `wof:parent_id` field. Should equal the `wof:id` of the next placetype up in the feature's hierarchy. Required for all files.
* **'is_landuse_aoi'** Used to signify an "area of interest" land use, different than the `wof:placetype` would suggest.
* **'supersedes'** The attribute that will be used for the `wof:supersedes` field. Required for all files that supersede another WOF record.
* **'superseded_by'** The attribute that will be used for the `wof:superseded_by` field. Required for all files that are superseded by another WOF record.
* **'deprecated'** The attribute that will be used for the `edtf:deprecated` field. A date field _(YYYY-MM-DD)_ used to signify when we determined this record was "junk" and incorrect since inclusion in Who's On First. Required for all files that are deprecated. (see: [cessation vs. deprecated documentation](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/deprecated_vs_cessation.md))
* **'cessation'** The attribute that will be used for the `edtf:cessation` field. A date field _(YYYY-MM-DD)_ used to signify when we determined this record was no longer valid in Who's On First (usually when it has been replaced by another record). Also requires a new field called `mz:is_current` to be created. The `mz:is_current` field value is '0' if the record has a `edtf:cessation` date. (see: [cessation vs. deprecated documentation](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/deprecated_vs_cessation.md))
* **'eng_preferred_name'** Preferred alternative names for a feature. 
* **'eng_variant_name'** Variant alternative names for a feature. 
* **'max_zoom'** Maximum zoom level at which feature labels appear on a map. Required for all new features to Who's On First.
* **'min_zoom'** Minimum zoom level at which feature labels appear on a map. Required for all new features to Who's On First.
* **'lbl_latitude'** A decimal value of a feature's Y coordinate. Value should be derived from [MapShaper](https://github.com/mbloch/mapshaper) and included on any new shape imported to Who's On First. New X/Y coordinates attributes will be created when running a geojson or shapefile through the MapShaper tool. These new fields will be used for `lbl:latitude` and `lbl:longitude`. The MapShaper tool is also available via [http://mapshaper.org/](http://mapshaper.org/).
* **'lbl_longitude'** A decimal value of a feature's X coordinate. Value should be derived from [MapShaper](https://github.com/mbloch/mapshaper) and included on any new shape imported to Who's On First. New X/Y coordinates attributes will be created when running a geojson or shapefile through the MapShaper tool. These new fields will be used for `lbl:latitude` and `lbl:longitude`. The MapShaper tool is also available via [http://mapshaper.org/](http://mapshaper.org/).
* **'rev_lat'** Equal to the `lbl_latitude` value. This field will be used to rebuild the feature's hierarchy.
* **'rev_long'** Equal to the `lbl_longitude` value. This field will be used to rebuild the feature's hierarchy.
* **'is_funky'** Optional.
* **'is_hard_boundary'** Optional.
* **'is_official'** Optional.
* **'tier_locality'** Optional.
* **'country_id'** The `wof:id` of the feature's parent country.
* **'region_id'** The `wof:id` of the feature's parent region.
* **'locality_id'** The `wof:id` of the feature's parent locality.
* **'WOF_country'** Usually equal to the ISO code, this is a two-digit key representing the country your features are in. Required for all features.
* **'iso_country'** Set by the [Internation Organization for Standardization](http://www.iso.org/iso/home.html), This is a two-digit key (listed [here](https://en.wikipedia.org/wiki/ISO_3166-1)) representing the country your features are in. Required for all features.
* **'src_geom'** Optional. Contains the source name of the feature's geometry. Given for research purposes.
* **'mz_note'** Optional. Contains information about that given feature, if available.

From the WOF repository for San Francisco, a total of **165** (157 polygon geometries, 8 point geometries) records for neighbourhoods were collected using our `external_editor` option. QGIS was used to preview Who’s On First neighbourhood shapes (below). 

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/bay_overview1.png">

_Image: San Francisco neighbourhood records (light purple) in comparison to the San Francisco Bay Area and the WOF shapes of San Francisco (blue)._

You might notice the general shape of San Francisco present in the photo below, but it's tough to make out. Many of these WOF neighbourhood shapes cross into what most people would consider a different neighbourhood, and, in two cases, include areas in different counties. The good news? The majority of these neighbourhood records contain usable information in their WOF attribute fields. Also, be mindful of the differences between single-part and multi-part polygon edits in QGIS. If your neighbourhood shapes are single-part polygons to begin with, you are unable to add a multi-part polygon into your feature collection. 

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/new_contig.png">

_Image: San Francisco neighbourhood records from Who's On First projected in QGIS._

In some cities, we have detailed polygon shapes for most, but not all neighbourhoods. Occassionally, we only know the name and the approximate point representing the label centroid. We need to establish a concordance between all WOF records, points and polygons. We'll need to add a polygon shape to replace these points; this is covered below in step four.

## 2: Research other neighbourhood sources

In this section, you will:

- **Find** new data to import
- **Verify** open license

Because Who’s On First is liberally licensed open data, we must be selective about adding new data. We either need to find a new source that is open data with a CC-BY or CC-0 license that allows commercial and derivative works or create new shapes based on local knowledge and by cross-referencing multiple sources. Ideally, this new source should be an improvement over what Who’s On First already knows about the place.

In our example, the City and County of San Francisco hosts various [neighbourhood-related shapefiles](https://data.sfgov.org/browse?q=neighborhoods) through it's OpenData portal, so we had a few options to choose from. 

Just because your locality hosts a neighbourhood dataset, does not mean the neighbourhood geometries are useable. For example, city planning departments often group neighbourhoods together for planning purposes; you can start with these geometries, but they should be double-checked before import. For instance, if a shape is named _Name 1_ - _Name 2_ - _Name 3_ (e.g. Mission-Potrero-SoMa), it should _probably_ be split into three polygons before import, one for each neighbourhood. 

Don't blindly trust an authoritative set of neighbourhood shapes. Review a few other neighbourhood sources to compare names, attributes, shape detail, and coverage. Ensuring that you have an accurate set of neighbourhood shapes and adequate attributes will save time when reconciling the data with existing Who's On First records.

In San Francisco, we did not choose the planning department shapes, as those were too coarse and used more for statistical groupings (there weren’t as many neighbourhoods as we had already, and their shapes were way too big, more like macrohoods). After research, it was found that the Mayor's Office created a set of geometries that were built to match local expectations and there was a similar number of places to what was in Who’s On First. Their colloquial shapes matched up with what we thought they should like as San Francisco locals.

Once we verified the data was provided through an [open license](https://data.sfgov.org/terms-of-use), we created a [new source](https://github.com/whosonfirst/whosonfirst-sources/blob/master/sources/sfgov.json), `sfgov`, in our [sources repository](https://github.com/whosonfirst/whosonfirst-sources/tree/master/sources) to give credit to the original author. This dataset was then downloaded to our desktop and added to a new QGIS document to compare with the existing shapes in WOF. Lucky for us, the SF OpenData is already in the WGS84 projection and does not need to be reprojected.

Lastly, we need to add any properties that are retained from the source data file to our [properties_alias.json file](https://github.com/whosonfirst/whosonfirst-properties/blob/master/aliases/property_aliases.json). In San Francisco, for example, we have a `sfgov:name` field. In order to bring this property in, we will need to add it to the property_alias.json file (see file for formatting examples).

## 3: Download authoritative neighbourhood geometries

In this section, you will:

- **Download** data
- **Open** your data 
- **Begin comparison** with existing Who's On First records

<img width="600" alt="SF OpenData neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/sf_opendata.png">

_Image: SF OpenData neighbourhood data projected in QGIS._

Once the data source was added to our source repository, the data was downloaded and placed into a new QGIS document (above) to compare to the geometries of WOF records. You can see the clean, non-overlapping geometries in the SF OpenData, unlike our existing WOF geometries (below).

<img width="600" alt="SF OpenData neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/2.gif">

_Image: WOF records projected in QGIS._

Now that we have WOF records and data provided by the City of San Francisco, we can begin reconciling the two datasets. We will join the two datasets based on a common attribute; in this case the `wof:name` field from the WOF data was joined to the SF OpenData's `name` field. The join tool in QGIS can be found by navigating to the properties of the WOF .geojson layer and clicking the "Join" option (below).

<img width="600" alt="Join Properties tab in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/5.png">

_Image: Join Properties tool in QGIS._

In an ideal world, all WOF records would join cleanly to SF OpenData records, but that is typically not the case. This join method worked for the most part, but because the spellings are not identical between each of the attribute tables, this join needs to be verified and improved by hand. For example, QGIS's join tool did not join a value of `Haight Ashbury` to a value of `Haight-Ashbury` or a value of `Mission District` to a value of `Mission`. As described below, it's not a matter of which name field is "more correct", but a matter of importing additional names from your authoritative source while preserving the existing `wof:name` in a `eng_x_variant` name field.

Alternately, we could perform this join based on location, instead of an attribute field. QGIS has functionality to perform a spatial join ([some documentation here](http://www.qgistutorials.com/en/docs/performing_spatial_joins.html)), which would be helpful if our WOF geometries were geographically similar to our administrative data. However, because our geometries in San Francisco overlap substantially with the SF OpenData geometries, an attribute join is more likely to give us matching records between the two datasets (generally, neighbourhood names are unique in city). If you are unsure of which join is best for your locality, give them both a try and compare the results.

Occasionally, Who's On First has duplicate records. Duplicate records _should_ be noted in the `mz:note` property (with a "duplicate", "dupe" or "dup" value) or with a `1` value in the `mz:is_funky` or `mz:is_current` property. If you come across duplicate features when comparing and joining records, prefer the current record over the record with a `mz:note` of "duplicate", "dupe" or "dup" or a `1` value in the `mz:is_funky` or `mz:is_current` property.

Who's On First | SF OpenData | Note 
---|---|---
Alamo Square | Alamo Square | _in both, great! Let's import the new geometry!_
Anza Vista | Anza Vista | _in both, great! Let's import the new geometry!_
Baja Noe |  | _no match, no alternate name spelling, WOF only_
 | Bret Harte | _no WOF record, let's research._
Haight Ashbury | | _no name match, but does have alternate name: `Haight-Ashbury`_
Cathedral Hill | Cathedral Hill | _in both, great!_

_Image: Comparison of WOF and SF OpenData name attributes._

This method assigned `wof:id` values to each SF OpenData record that joined to a WOF record. After comparing, **96** of **117** SF OpenData records were assigned a `wof:id`. With the records that did not join based on the `name` field join, we will have to reconcile, adding the `wof:id` manually whenever possible. This is done easiest by reviewing each name in your WOF attributes table with  each name of your source data.

<img width="300" alt="Attributes table after joining datasets" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/joined_attributes.png">

_Image: SF OpenData attribute table after joining datasets. Records with NULL values need to be imported by hand._

Examples of neighbourhoods that WOF did not have at the time of import are `Appearel City` and `Buena Vista` (meaning these records will need a new WOF ID). Since these neighbourhoods were not in the WOF database, we should consider importing them as new neighbourhood records.

## 4: Reconciling our data sources

In this section, you will:

- **Develop** an action plan to modify data
- Note possible **data modifications** needed in our datasets

**Remember** - not all of the existing neighbourhood records matched to an SF OpenData geometry (96 new records were given existing IDs, but there were 165 existing neighbourhood records). This begs the question: *What should happen to the 69 leftover neighbourhood records?* 

There are three options for the 69 leftover records:

* **Deprecate** the record, as it was never a valid neighbourhood to begin with. Research can't verify this name or shape. Sometimes a neighbourhood falls out of common usage, or the error was an error.
* **Downgrade** the record as a microhood and give it a `parented_by` value for the neighbourhood it falls within. People still use this name, but only the residents of those few city blocks.
* **Upgrade** the neighbourhood records to a macrohood (see: *Sunset, Richmond, Downtown*).

### Modifying SF OpenData

Before importing the city-provided geometries, it is important to ensure the new neighbourhood boundaries will work in Who’s On First. While we can easily import the new neighbourhood geometries raw from our source (SF OpenData), we should "trust but verify" our data before the  import.

The majority of geometries in the SF OpenData source were imported as-is, though four neighbourhood records in our San Francisco example were edited prior to import. Using our local knowledge and opinions, we adjusted these neighbourhood boundaries slightly. 

### Modifying WOF Data

After our WOF shapes were added to a QGIS document (below), they were given a new integer attribute field titled "status" based on concordance with our administrative source data. The status values were color-coded to display the following options for each of WOF neighbourhood records:

* **1 - Neighbourhood.** _Valid neighbourhood record. Both datasets agree this is a neighbourhood, probably needs a new shape and name._
* **2 - Reclassify up to macrohood.** _Neighbourhood records that will become macrohood records._
* **3 - Reclassify down to microhoods.** _Neighbourhood records that will be reclassified as microhood records. WOF records not in SF OpenData that are smaller than the surrounding neighbourhood should change placetypes to microhood._
* **4 - Reclassify down to microhoods... maybe.** _Needs more investigation. Probably change placetype to a microhood._
* **5 - Deprecate neighbourhood.** _Invalid record, should be "deprecated" and "superseded" in WOF. Everyone agrees this neighbourhood is an error._

<img width="600" alt="Assigning records' status in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/record_status.png">

_Image: Developing an action plan in QGIS by assigning records' status in QGIS, reviewing WOF record matches with new SF OpenData source. Colors represent status value._

**Congratulations!** You have finished collecting and evaluating new neighbourhood shapes for WOF! In the next part of this tutorial, we'll prepare the data for import. But first, a well-deserved break.

To finalize your work and prepare data for import, check out [part two](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/issue_workflows/sf_neighbourhood_updates_pt_2.md)!
