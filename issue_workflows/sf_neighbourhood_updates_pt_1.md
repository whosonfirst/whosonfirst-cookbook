#Updating Who's on First Neighbourhood Records (part one)

The [Who's on First](https://whosonfirst.mapzen.com/) (WOF) project is not pretending to be the authority of truth, but rather a home for data from various sources and a project that we hope generates discussion. The WOF gazetteer houses data for many geographies, including counties (which parent cities) and cities (which parent microhoods, neighbourhoods, and macrohoods). Neighbourhoods are the places where we live and work in cities; _the more neighbourhood data, the better._

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

##The Issue

We received a [report](https://github.com/whosonfirst/whosonfirst-data/issues/125) in the [whosonfirst-data repository](https://github.com/whosonfirst/whosonfirst-data) that the shape of San Francisco’s Golden Gate Park neighbourhood was both too small and extended into adjacent neighbourhoods. While researching online sources for a better shape, we noticed that most adjacent neighbourhood shapes in WOF could also be improved to align better with the road network and local expectations. After researching neighbourhood shapes online, we downloaded neighbourhood shapes for San Francisco from [SF OpenData](https://data.sfgov.org/), a city data website, to compare with the neighbourhood records in our WOF repository. We then filed a [new issue](https://github.com/whosonfirst/whosonfirst-data/issues/316) to handle all neighbourhood updates for San Francisco.

Before we begin, it is important to understand where WOF neighbourhood records came from and how the geometries were generated.

Typically, Who’s On First sources [Quattroshapes](http://www.quattroshapes.com) geometries for most neighbourhoods globally. However, many neighbourhoods in the United States, including San Francisco, source their default geometry from [Zetashapes](http://www.zetashapes.com). The Zetashapes project follows the same basic principles as Quattroshapes, but builds shapes up from Census 2010 features and can draw shapes that are too big, small, or just plain weird. We’ve seen problems with shapes extending in the water and far out into neighboring rural areas. This technique is responsible for the issues that we are correcting in San Francisco.

Drawing neighbourhood shapes is a tricky business. Strangers generally agree on what a neighbourhood is named and its rough shape, but even good friends can argue vehemently about where one neighbourhood ends and another begins - even if there are hard edges between neighbourhoods or they should overlap. Recognizing this, Who’s On First allows multiple alternate geometries for a place, but for practical reasons we need to set just one shape as the default geometry.

**To clean up our neighbourhood geometries, we needed to take five steps:**

* **#1** _Review WOF records for your locality. Get a sense of where they could be improved and where they are acceptable, focusing on names and shapes._
* **#2** _Research other neighbourhood sources on the internet._
* **#3** _Download authoritative neighbourhood geometries from a reliable, open license data source for your locality._
* **#4** _Reconciling WOF records with authoritative neighbourhood geometries. Things to think about: Is the number of neighbourhood records similar? Are the shapes similar or better? Could you draw your own shapes?_
* **#5** _Update records, either though a clean import or creating a new hybrid using the best of both (and your local knowledge)._

##1: Review Who's on First records for your locality

In this section, you will:

* Use the `git checkout` command in your terminal to **clone necessary repositories**
* **Collect** a .geojson file for all neighbourhoods in your locality (city)
* Add your .geojson file to a QGIS document for **review**

If you'd like to bypass this step, Mapzen is happy to send you a "starter kit" with a .geojson file that includes WOF neighbourhoods records for your locality (please [email us](mailto:stephen.epps@mapzen.com)). 

However, if you do want to build from source...

_Note: Windows users should ensure they have Powershell 3.0 before beginning any GitHub work from the terminal. A Powershell 3.0 download can be found [here](https://www.microsoft.com/en-us/download/details.aspx?id=34595). Additionally, all users should ensure they have `setuptools` for Python by [downloading](https://pypi.python.org/pypi/setuptools) Python 2.7 (or a more current version) and `GDAL 2.1` by [downloading](http://www.qgis.org/en/site/) QGIS 2.14 (or a more current version)._

* Run `git checkout` on the [WOF Data repository](https://github.com/whosonfirst/whosonfirst-data), [WOF Properties repository](https://github.com/whosonfirst/whosonfirst-properties), and [WOF Utils repository](https://github.com/whosonfirst/py-mapzen-whosonfirst-utils). _Note the PATH of those repos, and update in the script snippet below._
* Run the `install` script in whosonfirst-utils repository.
* Open the `wof-csv-to-feature-collection.py` script in your `Utils` repo. Update line 63 with your local filepath.
* Then, do the following...

Entering the following string in the terminal from the whosonfirst-utils repository's `scripts` folder allows us to collect San Francisco's neighbourhoods as a single .geojson file:

>_python wof-csv-to-feature-collection -p /usr/local/mapzen/whosonfirst-data/data -c /usr/local/mapzen/whosonfirst-data/meta/wof-neighbourhood-latest.csv --aliases /usr/local/mapzen/whosonfirst-properties/aliases/property_aliases.json -o ~/Desktop/SF_Neighbourhoods.geojson --slim --slim-template external_editor -f 85922583_

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/terminal_command.png">

_Image: Data collection script in the terminal._

_Note: The trailing number `85922583` at the end of this script is the WOF ID for [San Francisco](https://whosonfirst.mapzen.com/spelunker/id/85922583/#10/37.7850/-122.7278). When running this script, make sure to update that ID with whatever record you need neighbourhood geometries for. An ID is a unique identifier for records in WOF. Each record in WOF has an ID. To find the ID for your city, search the [Spelunker](https://whosonfirst.mapzen.com/spelunker) and copy the ID._

**Voilà!** We have a .geojson of WOF neighbourhood records in San Francisco!

To better understand what we're requesting of our command, here is a breakdown of exactly what is included:

* **`python`**  Used to invoke python
* **`wof-csv-to-feature-collection`**  The python script that collects WOF records.
* **`-p /PATH/whosonfirst-data/data`** sets the path to the local copy of all the WOF data. You will need to update this PATH depending on where you checked the file out.
* **`-c /PATH/whosonfirst-data/meta/wof-neighbourhood-latest.csv`** The metafile for the placetype you are interested in - neighbourhood. You will need to update this PATH depending on where you checked the file out.
* **`--aliases /usr/local/mapzen/whosonfirst-properties/aliases/property_aliases.json`** Pulling in various aliases for attribute fields for your output file.
* **`-o ~/Desktop/SFNeighbourhoods.geojson`** Your output file.
* **`--slim`** Option parser to limit property export to subset (roughly those in the CSV file) and reduce file size.
* **`--slim-template`** Option parser to trim key names to fit Esri Shapefile format (10 charachter length limit).
* **`external_editor`** Return only necessary attribute fields for neighbourhood edits. 
* **`-f 85922583`** ID of the locality you need neighbourhood records for, found by searching our [Spelunker](https://whosonfirst.mapzen.com/spelunker).

From the WOF repository for San Francisco, a total of **156** records for neighbourhoods were collected. QGIS was used to preview Who’s On First neighbourhood shapes (below). 

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/bay_overview1.png">

_Image: San Francisco neighbourhood records in comparison to the San Francisco Bay Area._

You might notice the general shape of San Francisco present in the above below, but it's tough to make out because many neighbourhood geometries extend into San Francisco Bay. Additionally, many of these WOF neighbourhood shapes cross into what most people would consider a different neighbourhood, and, in two cases, include areas in different counties. The good news? The majority of these neighbourhood records contain usable information in their WOF attribute fields.

<img width="600" alt="San Francisco neighbourhood records in WOF" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/new_contig.png">

_Image: San Francisco neighbourhood records from Who's on First projected in QGIS._

In some cities, we have detailed polygon shapes for most, but not all neighbourhoods. For a handful, we only know the name and the approximate point representing the label centroid. We need to establish a concordance between all WOF records, points and polygons - please add polygons! _(Step 4)_

##2: Research other neighbourhood sources

In this section, you will:

- **Find** new data to import
- **Verify** open license

Because Who’s On First is liberally licensed open data, we must be selective about adding new data. We either need to find a new source that is open data with a CC-BY or CC-0 license that allows commercial and derivative works or create new shapes based on local knowledge and by cross-referencing multiple sources. Ideally, this new source should be an improvement over what Who’s On First already knows about the place!

The City and County of San Francisco hosts various [neighbourhood-related shapefiles](https://data.sfgov.org/browse?q=neighborhoods) through it's OpenData portal, so we had a few options to choose from. 

Just because your locality hosts a neighbourhood dataset, does not mean the neighbourhood geometries are useable. For example, city planning departments often group neighbourhoods together for planning purposes; you can start with these geometries, but they should be double-checked before import. For instance, if a shape is named _Name 1_ - _Name 2_ - _Name 3_ (e.g. Mission-Potrero-SoMa), it should _probably_ be split into three polygons before import, one for each neighbourhood. 

Remember - don't blindly trust an authoritative set of neighbourhood shapes. Review a few other neighbourhood sources to compare names, attributes, shape detail, and coverage. Ensuring that you have an accurate set of neighbourhood shapes and adequate attributes will save time when reconciling the data with existing Who's on First records.

We did not choose the planning department shapes, as those were too coarse and used more for statistical groupings (there weren’t as many neighbourhoods as we had already, and their shapes were way too big, more like macrohoods). The Mayor’s Office geometries were built to match local expectations and there was a similar number of places to what was in Who’s On First. Their colloquial shapes matched up with what we thought they should like as San Francisco locals.

Once we verified the data was provided through an [open license](https://data.sfgov.org/terms-of-use), we created a [new source](https://github.com/whosonfirst/whosonfirst-sources/blob/master/sources/sfgov.json), `sfgov`, in our [sources repository](https://github.com/whosonfirst/whosonfirst-sources/tree/master/sources) to give credit to the original author. This dataset was then downloaded to our desktop and added to a new QGIS document to compare with the existing shapes in WOF. Lucky for us, the SF OpenData is already in the WGS84 projection and does not need to be reprojected.


##3: Download authoritative neighbourhood geometries

In this section, you will:

- **Download** data
- **Open** your data 
- **Begin comparison** with existing Who's on First records

<img width="600" alt="SF OpenData neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/sf_opendata.png">

_Image: Only the SF OpenData neighbourhood data projected in QGIS._

Once the data source was added to our source repository, the data was downloaded and placed into a new QGIS document to compare to the geometries of WOF records (above). You can see the clean, non-overlapping geometries in the SF OpenData, unlike our existing WOF geometries (below).

<img width="600" alt="SF OpenData neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/2.gif">

_Image: A comparison of SF OpenData neighbourhoods (blue borders) and WOF records (multi-colored), projected in QGIS._

Now that we have WOF data and data provided by the City of San Francisco, we can begin reconciling the two datasets. We will join the two datasets based on a common attribute; in this case the `wof:name` field from the WOF data was joined to the SF OpenData's `name` field. The join tool in QGIS can be found by navigating to the properties of the WOF .geojson layer and clicking the "Join" option (below).

<img width="600" alt="Join Properties tab in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/5.png">

_Image: Join Properties tool in QGIS._

In an ideal world, all WOF records would join cleanly to SF OpenData records, but that was not the case. This join method worked for the most part, but because the spellings are not identical between each of the attribute tables, this join needs to be verified and improved by hand. For example, QGIS's join tool did not join a value of `Haight Ashbury` to a value of `Haight-Ashbury` or a value of `Mission District` to a value of `Mission`. As described below, it's not a matter of which name field is "more correct", but a matter of importing additional names from your authoritative source while preserving the existing `wof:name` in a `eng_x_variant` name field.

Alternately, we could perform this join based on location, instead of an attribute field. QGIS has functionality to perform a spatial join ([some documentation here](http://www.qgistutorials.com/en/docs/performing_spatial_joins.html)), which would be helpful if our WOF geometries were geographically similar to our administrative data. However, because our geometries in San Francisco overlap substantially with the SF OpenData geometries, an attribute join is more likely to give us matching records between the two datasets (generally, neighbourhood names are unique in city). If you are unsure of which join is best for your locality, give them both a try and compare the results.

Who's on First | SF OpenData | Note 
---|---|---
Alamo Square | Alamo Square | _in both, great!_
Anza Vista | Anza Vista | _in both, great!_
Baja Noe |  | _no match, no alternate name spelling, WOF only_
 | Bret Harte | _no WOF record, let's research._
Haight Ashbury | | _no name match, but does have alternate name: `Haight-Ashbury`_
Cathedral Hill | Cathedral Hill | _in both, great!_

_Image: Comparison of WOF and SF OpenData name attributes._

This method assigned `wof:id` values to each SF OpenData record that joined to a WOF record. After comparing, **96** of **117** SF OpenData records were assigned a `wof:id`. With the records that did not join based on the `name` field join, we will have to reconcile, adding the `wof:id` manually whenever possible.

<img width="300" alt="Attributes table after joining datasets" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/joined_attributes.png">

_Image: SF OpenData attribute table after joining datasets. Records with NULL values need to be imported by hand._

Examples of neighbourhoods that WOF did not have at the time of import are `Bret Harte` and `Candlestick Point SRA` (meaning these records will need a new WOF ID). Since these neighbourhoods were not in the WOF database, we should consider importing them as new neighbourhood records.

##4: Reconciling Who's on First records with authoritative neighbourhood geometries

In this section, you will:

- **Verify** data from your authoritative source
- **Develop** an action plan to modify data

Remember - not all of the existing neighbourhood records matched to an SF OpenData geometry (96 new records were given existing IDs, but there were 156 existing neighbourhood records). This begs the question: *What should happen to the 60 leftover neighbourhood records?* 

There are three options for the 60 leftover records:

* **Deprecate** the record, as it was never a valid neighbourhood to begin with. Research can't verify this name or shape. Sometimes a neighbourhood falls out of common usage, or the error was an error.
* **Downgrade** the record as a microhood and give it a `parented_by` value for the neighbourhood it falls within. People still use this name, but only the residents of those few city blocks.
* **Upgrade** the neighbourhood records to a macrohood (see: *Sunset, Richmond, Downtown*).

###Modifying SF OpenData

Before importing the city-provided geometries, it is important to ensure the new neighbourhood boundaries will work in Who’s On First. While we can easily import the new neighbourhood geometries raw from our source (SF OpenData), we should "trust but verify" our data before the  import.

The majority of geometries in the SF OpenData source were imported as-is, though two neighbourhood records were edited prior to import (_Rincon Hill_ and _Financial District South_). Using our local knowledge and opinions, we adjusted these neighbourhood boundaries slightly. 

###Modifying WOF Data

What are our options for records that are only in WOF (not in SF OpenData)?

Once we've retrieved all existing WOF neighbourhood shapes in San Francisco, they were added to a QGIS document (below) and given a new numerical field titled "status". The status values were color-coded to display the following options for each of WOF neighbourhood records:

* **1 - Neighbourhood.** _Valid neighbourhood record. Both datasets agree this is a neighbourhood, probably needs a new shape and name._
* **2 - Reclassify up to macrohood.** _Neighbourhood records that will become macrohood records._
* **3 - Reclassify down to microhoods.** _Neighbourhood records that will be reclassified as microhood records. WOF records not in SF OpenData that are smaller than the surrounding neighbourhood should change placetypes to microhood._
* **4 - Reclassify down to microhoods... maybe.** _Needs more investigation. Probably change placetype to a microhood._
* **5 - Deprecate neighbourhood.** _Invalid record, should be "deprecated" and "superseded" in WOF. Everyone agrees this neighbourhood is an error._

<img width="600" alt="Assigning records' status in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/record_status.png">

_Image: Developing an action plan in QGIS by assigning records' status in QGIS, reviewing WOF record matches with new SF OpenData source. Colors represent status value._

When we update WOF neighbourhoods to default to a new geometry, we also need to preserve the earlier Zetashapes geometry as an alt-geometry in WOF. An alt-geometry is a dedicated WOF record that only contains source information and a geometry - check out an example of an alt-geometry [here](https://github.com/whosonfirst/whosonfirst-data/blob/master/data/859/225/83/85922583-alt-mapzen.geojson). Alt-geometries use the same `wof:id` as the record's main geometry, but append `-alt-"source"`.

Because we're mixing data from different sources, we should also modify the shapes so they are more consistent with eachother regardless of the source. We'll revisit this in part 5.

**Congratulations!** You have just finished collected new neighbourhood shapes for WOF! In the next part of this tutorial, we'll prepare the data for import. But first, a well-deserved break.

To finalize your work and prepare data for import, check out [part two](https://github.com/whosonfirst/whosonfirst-docs/wiki/Issue-%23125---A-Guide-to-Updating-Neighbourhood-Records-in-Who's-on-First-%28part-2%29)!
