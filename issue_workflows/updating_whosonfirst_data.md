# Updating Who’s On First Data

[Who’s On First](https://whosonfirst.org/) (WOF) records are split into per-country GitHub repos, using records' country codes. Indonesia records, for example, live in [whosonfirst-data-admin-id](https://github.com/whosonfirst-data/whosonfirst-data-admin-id).

Records that are not country-specific (timezones, continents, disputed areas, etc.) can live in these repos:

* [whosonfirst-data-admin-xx](https://github.com/whosonfirst-data/whosonfirst-data-admin-xx)  
* [whosonfirst-data-admin-xy](https://github.com/whosonfirst-data/whosonfirst-data-admin-xy)  
* whosonfirst-data-admin-x\*

Steps to update WOF records for a specific country, below:

### Step 1: Obtain all relevant, current WOF records

* Export all records from the country being updated  
  * Do not include any record with a mz:is\_current property value of 0  
  * This can be done locally (similar steps outlined [here](https://github.com/whosonfirst/whosonfirst-cookbook/blob/main/issue_workflows/sf_neighbourhood_updates_pt_1.md)) or by using the [Geocode Earth distributions](https://geocode.earth/data/whosonfirst/#AD)  
* If updating a country that claims a disputed area OR a continent:  
  * Export records from the \-xx and \-xy repo, too  
    * Similarly, use local scripts or the Geocode Earth distributions

### Step 2: Obtain a source dataset(s)

* Verify the license is CC0, CC-BY, or equivalent in terms

### Step 3: Add the source to the [whosonfirst-sources](https://github.com/whosonfirst/whosonfirst-sources/) repo

* Add a new json with properties filled out, license terms listed, usage flags  
  * [Example source](https://github.com/whosonfirst/whosonfirst-sources/blob/main/sources/atgov.json)  
* Run the [makefile](https://github.com/whosonfirst/whosonfirst-sources/blob/main/Makefile) to update docs/readme

### Step 4: Develop an import plan

* Visualize the new source data in QGIS  
* Compare each division to the existing placetype setup in WOF  
* Add a comment in the WOF issue with a suggestion of how to import the new source data  
  * [Example](https://github.com/whosonfirst-data/whosonfirst-data/issues/1109#issuecomment-378777529)

### Step 5: Match source data \<\> WOF records

* As an example, if updating places for Indonesia and a new source is found that includes new localities, counties, and regions in the country:  
  * Match the source data file with localities to the existing localities in WOF  
  * Match the source data file with counties to the existing counties in WOF  
  * Match the source data file with region to the existing regions in WOF  
  * Note: This approach generally works, but there are situations where a new placetype needs to be introduced into WOF, or cases where placetypes will be changed.  
    * If this happens, develop a unique approach in the WOF issue

* For each "match" of a placetype, a file for each of the following would be produced:  
  * 'matched' records: any records that are the same between WOF and the source dataset  
    * Essentially a copy of the source data file (shapefile, GeoJON, etc) with an appended wof\_id field. The wof\_id value would be the ID of the matching WOF feature.  
  * 'added' records: any records in the source dataset that are not currently in WOF  
    * Essentially a copy of the source data file (shapefile, GeoJON, etc) with an appended wof\_id field. The wof\_id value would be empty since there was no match for this source feature.  
  * 'removed' records: any records in WOF that are not in the source dataset  
    * Since these features wouldn't exist in the source data, WOF IDs of those features can either live in a csv file or as a GeoJSON/shapefile with WOF geometries.

### Step 6: Create superseding links, as needed

* In some cases, a new WOF record will "supersede" an existing WOF record  
* There isn't really one simple/standardized way to manage these, but tracking them is helpful  
* In the past, adding these as a new column (next to the new wof\_id field) has been easy

### Step 7: Use Mapshaper to add centroid

* For each 'matched' and 'added' file, pass the `"-each 'lbl\_longitude=$.innerX , lbl\_latitude=$.innerY'"` option to produce new x,y label centroids for each feature geometry
* Export them as GeoJSON files
* https://github.com/mbloch/mapshaper

### Step 8: Update records

* Craft a Python script to update geometries and properties of any 'matched' feature  
  * [Example script](https://github.com/whosonfirst/whosonfirst-cookbook/blob/main/scripts/2032_update_full_placetype.py%20)  
* Existing geometry is stored as an alt geometry  
* src: properties needs to be updated  
  * Value should match the name of the new source being added to the source repo  
* wof:geom\_alt property needs to be updated  
  * Same, value should match the name of the new source being added to the source repo  
* If there is a relevant, unique source id, add that as a new concordance  
* If there is a population, add that as a wof:population value  
  * Using that value, add a wof:population\_rank value, too  
* Ensure the wof:name and name: properties are set appropriately  
  * Make sure the English name and names of any official/spoken language are correct  
* Bring over any top-level properties from the source data onto the WOF record  
  * If there are any, file a new PR in the whosonfirst-properties repo  
* Set wof:supersedes property if this record is superseding an old/not current record  
  * Bring over any concordances, names, zoom values from the record being superseded

### Step 9: Add new records

* Craft a Python script to create new records, as needed.  
  * [Example script](https://github.com/whosonfirst/whosonfirst-cookbook/blob/main/scripts/1264_parkcity_neighbourhoods.py)  
* New ids are needed \- these can be created using the [Brooklyn Integers API](https://brooklynintegers.com/api/) / using the [Export tooling](https://github.com/whosonfirst/go-whosonfirst-exportify) in WOF (automatically)  
* If there is a relevant, unique source id, add that as a new concordance  
* If there is a population, add that as a wof:population value  
  * Using that value, add a [wof:population\_rank](https://github.com/whosonfirst/whosonfirst-properties/tree/main/properties/wof#population_rank) value, too  
* Ensure the wof:name and name: properties are set appropriately  
  * Make sure the English name and names of any official/spoken language are correct  
* Bring over any top-level properties from the source data onto the WOF record  
  * If there are any, file a new PR in the whosonfirst-properties repo  
* Set wof:supersedes property if this record is superseding an old/not current record  
  * Bring over any concordances, names, zoom values from the record being superseded

### Step 10: Remove records

* Set the mz:is\_current value to 0  
* Set the edtf:deprecated / edtf:cessation date  
  * edtf:deprecated \- Indicates the date when a place was determined to be invalid (was never a "going concern")  
  * edtf:cessation \- Indicates when a place stopped being a "going concern". The semantics for something ceasing may vary from placetype to placetype. For example, a venue may cease operations or a country may split in to multiple countries.  
* Set wof:superseded\_by properties if these records are being superseded by a new record

### Step 11: PIP records

* Steps [here](https://github.com/whosonfirst/whosonfirst-cookbook/blob/main/how_to/setting_up_pip_service.md) no longer work  
* Something similar is needed to correctly update and set hierarchies  
* At minimum, any of the per-country repos plus the whosonfirst-data-admin-xy repo need to be indexed. The xy repo contains continents, which all records will need to reference in their hierarchies.

### Steps 12: Merge all changes

* Merge any work in the [whosonfirst-sources](https://github.com/whosonfirst/whosonfirst-sources/) repo  
* Merge any work in the [whosonfirst-properties](https://github.com/whosonfirst/whosonfirst-properties/) repo  
* Merge any work in the whosonfirst-data-admin-\* repo(s)

### Steps 13: Provide top-level statistics

* It it helpful to add basic stats in the relevant whosonfirst-data-admin-\* pull request being merged  
  * Number of features edited (helpful for users, changelog)
  * Quick note per commit (helpful for users, WOF team in the future)

