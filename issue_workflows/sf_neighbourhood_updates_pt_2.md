#Updating Who's on First Neighbourhood Records (part two)

_Before you jump into part two of editing Who's on First neighbourhood records, make sure to check out [part one](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/issue_workflows/sf_neighbourhood_updates_pt_1.md) (covers the first four steps)!_

##5. Update Records

In the first part of the tutorial, we found open data, modified it, and reconciled it to work with Who's On First. Now for the fun part - preparing our data for import!

Who's on First treats each placetype slightly different, so we've broken this section down by placetype to detail what work needs to take place for each.

In this section, you will:

* Update and create new **neighbourhoods**
* Reclassify neighbourhoods, creating new **macrohoods** (upgrading)
* Reclassify neighbourhoods, creating new **microhoods** (downgrading)
* Update the **locality** record
* Take care of any **deprecated** records and **outliers**
* File the **Pull Request**

###Update and create neighbourhoods

There were two outcomes with the new SF OpenData neighbourhood records. These outcomes were either:

* **A** - The modified SF OpenData record was joined to an existing Who's On First record, the existing WoF geometry was archived as an alt-geometry, and the SF OpenData was added to the record's default geometry. Names were also updated, with new attributes given to the existing records.

* **B** - The modified SF OpenData record did not join to an existing record. A new ID and record for the neighbourhood feature was created. This option requires a completely new `wof:id` (minted by Brooklyn Integers).

<img width="600" alt="SF OpenData updated and new neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/all_hoods.png">

_Image: SF OpenData neighbourhoods projected in QGIS, purple representing new records and orange representing updated records._

_Note: Our data source for San Francisco included large parks as separate neighbourhood shapes (see: Golden Gate Park, McLaren Park), but some authoritative data sources do not include large parks and open spaces as individual neighbourhoods. If this is the case in your locality, you'll need to split large parks from their current neighbourhood shape, creating new neighbourhood shapes for them. As a general rule, parks over one million square meters (roughly 250 acres) should have their own neighbourhood record. Because the authoritative shapes will be modified when creating new park shapes, we set the `src:geom` field to [`mz`](https://github.com/whosonfirst/whosonfirst-sources/blob/master/sources/mapzen.json) (you can choose another source name that is different from the authoritative source, if you modify the source shape)._

The SF OpenData source contained 117 neighbourhood records, four of which were combination names. 

* `Aquatic Park / Ft. Mason`
* `Downtown / Union Square`
* `Laurel Heights / Jordan Park`
* `Lincoln Park / Ft. Miley`

These neighbourhoods need to be split into separate parts because WoF records should reflect a single area - not a combined place. In this case, we removed one name from each record and created a microhood record with that removed name. 

**List of Neighbourhoods from SF OpenData**

`Alamo Square`, `Anza Vista`, `Apparel City`, `Aquatic Park / Ft. Mason`, `Ashbury Heights`, `Balboa Terrace`, `Bayview`, `Bernal Heights`, `Bret Harte`, `Buena Vista`, `Candlestick Point SRA`, `Castro`, `Cathedral Hill`, `Cayuga`, `Central Waterfront`, `Chinatown`, `Civic Center`, `Clarendon Heights`, `Cole Valley`, `Corona Heights`, `Cow Hollow`, `Crocker Amazon`, `Diamond Heights`, `Dogpatch`, `Dolores Heights`, `Downtown / Union Square`, `Duboce Triangle`, `Eureka Valley`, `Excelsior`, `Fairmount`, `Financial District`, `Fishermans Wharf`, `Forest Hill`, `Forest Knolls`, `Glen Park`, `Golden Gate Heights`, `Golden Gate Park`, `Haight Ashbury`, `Hayes Valley`, `Holly Park`, `Hunters Point`, `India Basin`, `Ingleside`, `Ingleside Terraces`, `Inner Richmond`, `Inner Sunset`, `Japantown`, `Laguna Honda`, `Lake Street`, `Lakeshore`, `Laurel Heights / Jordan Park`, `Lincoln Park / Ft. Miley`, `Little Hollywood`, `Lone Mountain`, `Lower Haight`, `Lower Nob Hill`, `Lower Pacific Heights`, `Marina`, `McLaren Park`, `Merced Heights`, `Merced Manor`, `Midtown Terrace`, `Mint Hill`, `Miraloma Park`, `Mission`, `Mission Bay`, `Mission Dolores`, `Mission Terrace`, `Monterey Heights`, `Mt. Davidson Manor`, `Nob Hill`, `Noe Valley`, `North Beach`, `Northern Waterfront`, `Oceanview`, `Outer Mission`, `Outer Richmond`, `Outer Sunset`, `Pacific Heights`, `Panhandle`, `Parkmerced`, `Parkside`, `Parnassus Heights`, `Peralta Heights`, `Polk Gulch`, `Portola`, `Potrero Hill`, `Presidio Heights`, `Presidio National Park`, `Presidio Terrace`, `Produce Market`, `Rincon Hill`, `Russian Hill`, `Seacliff`, `Sherwood Forest`, `Showplace Square`, `Silver Terrace`, `South Beach`, `South of Market`, `St. Francis Wood`, `St. Marys Park`, `Stonestown`, `Sunnydale`, `Sunnyside`, `Sutro Heights`, `Telegraph Hill`, `Tenderloin`, `Treasure Island`, `Union Street`, `University Mound`, `Upper Market`, `Visitacion Valley`, `West Portal`, `Western Addition`, `Westwood Highlands`, `Westwood Park`, and `Yerba Buena Island` 

####Update existing neighbourhoods with new shapes and names

For cases where neighbourhood names were not an exact match between SF OpenData and Who's On First (remember `Haight Ashbury` vs. `Haight-Ashbury`), make sure we preserve the old WoF name name as a `variant` name (below) and set the SF OpenData name as the feature's `wof:name`.

 _"name:eng_x_variant":[_     
  _"Haight-Ashbury"_    
  _],_
  
<img width="600" alt="SF OpenData updated and new neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/updated_hoods.png">

_Image: SF OpenData neighbourhoods projected in QGIS that mapped cleanly to an existing WoF ID._
  
Once we've completed this step, we need to fill out other necessary attribute fields. These include all attribute fields in our .geojson file retrieved using our `external_editor` command option in part one of the tutorial.

####Create new WoF neighbourhood records

Since these new features do not have an existing WoF record to update, this step is fairly simple. We need to assign each new neighbourhood record a new [Brooklyn Integer](http://www.brooklyninteger.com), which become the `wof:id` for each record. Then, just like our last step, we need to fill out necessary attribute fields in our .geojson file.

<img width="600" alt="SF OpenData updated and new neighbourhood data projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/new_neighbourhoods_wlabel.png">

_Image: Neighbourhoods in SF OpenData that should be added to WoF._

After our attributes field values are filled out, the following will occur upon import to our .geojson files:

* All "contained by" records will be found and the hierarchy will be rebuilt (in order of placetype).
* To automate this reverse geocoding, the Point-In-Polygon (PIP) server will be reindexed. This will allow us to regenerate hierarchy values and assign new parent IDs for any record that falls within a new neightbourhood geometry.

### Reclassify neighbourhoods, creating new **macrohoods** (upgrading)

While we recognied four valid macrohoods in San Francisco, only two of these records were in Who's on First as existing neighbourhoods. The other two were not existing neighbourhood records that were not in Who's on First were imported as new features that did not supersede an existing record.

Since our source data only included neighbourhood shapes, we'll have to create our own macrohood shapes. We created new shapes by combining geometries from the SF OpenData neighbourhoods. To combine geometries, the Dissolve tool in QGIS was used. For example, the shape for the Sunset District macrohood record was created by selecting neighbourhood records that fall completely within the area we're designating as the Sunset District macrohood: Outer Sunset, Parkside, Golden Gate Heights, and Inner Sunset. With those features selected, the Dissolve tool was used to export the merged geometry of these four neighbourhood geometries by clicking the "Vector" dropdown menu and selecting `Geoprocessing Tools` > `Dissolve`.

These four records (below) were imported as new macrohoods. The `wof:id` of these macrohood records will become the `wof:parent_id` of any neighbourhood within the given macrohood shape. Again, these `wof:id` values will be minted from Brooklyn Integers (just as we've done in previous steps) and the macrohood attributes will need to be updated accordingly. Since a change to the `wof:placetype` value qualifies as a "[Significant Event](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/significant_event.md)," new macrohood records' `wof:id` will become the `wof:superseded_by` value in the the original neighbourhood record and the original neighbourhood records' `wof:id`  will become the `wof:supersedes` value in these new macrohood records.

<img width="600" alt="SF OpenData neighbourhood data and new macrohoods projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/macro_wlabel.png">

_Image: SF OpenData neighbourhood-based data and new macrohoods projected in QGIS._

###Reclassify neighbourhoods, creating new **microhoods** (downgrading)

There were 51 leftover WoF records after figuring out concordances between data sources and reclassifying macrohoods. These records were generally smaller than sections of larger neighbourhoods and were determined to be more appropriate as microhoods.

These leftover WoF neighbourhood records need to be adjusted to align with the SF OpenData geometries so they can be imported to WoF as new microhoods. This is important because microhoods should _generally_ not overlap neighbourhoods. There is no rule about yes-or-no overlap between neighbourhoods and microhoods (or even between neighbourhoods and neighbourhoods, or microhoods to microhoods), but we are looking for cleaner geometry that's less overlapping for the **default** - overlapping geometries can always become alt-geometry records. 

**Optional:** note that the new microhood shapes can be generalized slightly (shown below). The Zetashapes occasionally cut through neighbourhoods at odd angles, so adding a missing block or two into your new microhood geometry is acceptable. 

<img width="600" alt="Neighbourhood geometries being cut to become new microhood geometries" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/1.gif">

_GIF: Neighbourhood geometries being cut to become new microhood geometries._

Shapes were modified using the Split Features tool in the Advanced Digitizing Toolbar in QGIS. This toolbar does not automatically appear in QGIS; to access the Advanced Editor Toolbar (below), we'll need to enable it under QGIS's View tab. Navigate to the View tab in QGIS and select `Toolbars` > `Advanced Digitizing Toolbar`. 

<img width="600" alt="Advanced Digitizing Toolbar in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/12.png">

_Image: Advanced Digitizing Toolbar in QGIS, with the Split Feature tool highlighted._

Alternatively, the Clip with Polygon from Another Layer tool in the Digitizing Toolbar can be used to automatically cut neighbourhood polygons into microhood polygons. 

Since we are creating new microhood records, we'll need to use Brooklyn Integers to get new `wof:id` values, similar to what we did with new neighbourhood records. Lastly, since a change to the `wof:placetype` value qualifies as a "[Significant Event](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/significant_event.md)," new microhood records' `wof:id` will become the `wof:superseded_by` value in the the original neighbourhood record and the original neighbourhood records' `wof:id`  will become the `wof:supersedes` value in these new microhood records.

<img width="600" alt="SF OpenData neighbourhood data and updated WoF microhoods projected in QGIS" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/microhoods.png">

_Image: SF OpenData neighbourhood data and updated WoF microhoods projected in QGIS._

###Update the locality record

Now that we've fixed our neighbourhood shapes... what about the locality (city) shape? 

The existing Who's On First shape for San Francisco was technically correct, showing all land, water, and offshore islands administered by the city. But, its not the city's seven mile by seven mile iconic shape that many residents and visitors recognize as the shape of San Francisco. [A new geometry of San Francisco](https://github.com/whosonfirst/whosonfirst-data/blob/master/data/859/225/83/85922583-alt-mapzen.geojson) without the outlying areas (Treasure Island and Farallon Islands) was produced as a new alt-geometry of just the contiguous San Francisco (comparison below). 

<img width="600" alt="Comparison of San Francisco's WoF geometry and alt-geometry" src="https://mapzen-assets.s3.amazonaws.com/images/sf-neighbourhood-updates/overview.png">

_Image: Comparison of San Francisco's new WoF geometry and its original geometry, now preserved as an alt-geometry._

This new geometry was created using the Dissolve tool in QGIS with the nieghbourhood shapes from SF OpenData. This alt-geometry was more detailed than the [current outline for San Francisco](https://github.com/whosonfirst/whosonfirst-data/blob/master/data/859/225/83/85922583.geojson) and is debatably the general outline that most consider the San Francisco locality.

When we update WoF neighbourhoods to default to a new geometry, we also need to preserve the earlier Zetashapes geometry as an alt-geometry in WoF. An alt-geometry is a dedicated WoF record that only contains source information and a geometry - check out an example of an alt-geometry [here](https://github.com/whosonfirst/whosonfirst-data/blob/master/data/859/225/83/85922583-alt-mapzen.geojson). Alt-geometries use the same `wof:id` as the record's main geometry, but append `-alt-"source"`.

Because we're mixing data from different sources, we should also modify the shapes so they are more consistent with eachother regardless of the source. We'll revisit this in part 5.

###Take care of any deprecated records and outliers

While the above steps took care of the majority of our issues, there were a few remaining edits to be made in San Francisco:

* The **Westlake** neighbourhood in Daly City was incorrectly parented to San Francisco. This record needed to have its `wof:hierarchy` and `wof:parent` fields updated to replace the ID for Daly City with the ID for San Francisco. This hierarchy change qualifies as a **Significant Event**, so the record was cessated and superseded to a new record for this neighbourhood. This requires us to duplicate the old file, update the `wof:id` property and filename to the new ID, linking up the `wof:supersedes` and `wof:supersedes_by` properties in both records.
 
* The **Transmission** neighbourhood in San Francisco need to be deprecated and given an `mz:is_funky` value of `1`. Using local knowledge, it was determined that this neighbourhood would be cessated and superseded to the nearby record of "La Lengua", rather than a new microhood.

* The Who's On First record for the **Ft. Winfield Scott** neighbourhood in Marin County needed to be updated with a new geometry and correct parenting; it was also given a new name, `Fort Baker`. This qualifies as a **Significant Event**, so the record was deprecated and superseded to a new record for this neighbourhood.

We also have to ensure that all microhood, neighbourhood, and macrohood records are given appropriate `mz:min_zoom` and `mz:max_zoom` values.  These values should be consistent across place types, as they are used to determine at what zoom level the name label will appear (and when it will disappear). 

For existing features, probably don't modify the existing `min_zoom` and `max_zoom` values. But for new features, do the following:

- `neighbourhood`: 
  - Default: `min_zoom`:`15`, optionally modify up to `13` for important places.
  - Default: `max_zoom`:`18`, rarely modify.
- `macrohood`: 
  - Default: `min_zoom`:`13`, optionally modify up to `11` for important places.
  - Default: `max_zoom`:`15`, rarely modify. 
- `microhood`: 
  - Default: `min_zoom`:`16`, rarely modify.
  - Default: `max_zoom`:`18`, rarely modify.
  
##Let's Recap

A big **thank you** to those who have made it to this point in the tutorial! Before we finalize our PR, let's recap the work we've completed so far and make sure we have all records in order.

We've found a new administrative source, compared it to our Who's on First record and made one of the following updates (depending on that feature's unique situation):

* **A.** Updated the WoF neighbourhood feature's geometry with a new administrative geometry and imported new source attributes.
* **B.** Minted a new Brooklyn Integer for new administrative neighbourhood shapes that are new to Who's on First.
* **C.** "Downgraded" the neighbourhood feature to a microhood. This required minting a new Brooklyn Integer for our microhood record, updating the `edtf:cessation`, `mz:is_current`, `mz:min_zoom`, `mz:max_zoom`, `lbl:latitude`, `lbl:longitude` attribute fields accordingly, and superseding our old neighbourhood record to our new microhood record.
* **D.** "Upgraded" the neighbourhood feature to a microhood. This required minting a new Brooklyn Integer for our microhood record, updating the `edtf:cessation`, `mz:is_current`, `mz:min_zoom`, `mz:max_zoom`, `lbl:latitude`, `lbl:longitude` attribute fields accordingly, and superseding our old neighbourhood record to our new macrohood record.
* **E.** Deprecated our neighbourhood record, as it was never valid to begin with.

Now, we should have a collection of .geojson files that we have use to create a pull request (if this step is too difficult or not possible for some reason, [email us](mailto:stephen.epps@mapzen.com), as we may be able to import your .geojson files independently of a pull request). While you may have updated several other attribute fields(`lbl` fields, `zoom` fields, etc.), the following required attributes should _always_ be in your .geojson files:

* `wof:name`
* `wof:id`
* `wof:placetype`
* `wof:country`
* `wof:parent_id`

##Now that we have files... server magic!

We've developed in-house tools to automate much of the import process for Who's on First. The following tasks will be auto-completed for records that we've edited:

* Updates to the **supersedes** and **supersedes_by** fields.
* All hierarchy values of "contained by" records need to be updated to include the new `wof:id`. To automate this reverse geocoding, we'll use the Point-In-Polygon (PIP) server which will rebuild a record's hierarchy.

The Point-In-Polygon server is a tool that update parent IDs for descendent records. Records are assigned a hierarchy based on their `wof:parent`, and, since we've updated many records in San Francisco, twe'll need to ensure these are all correct before import. This automated Point-In-Polygon server does an excellent job in automating this process compared to doing this work by hand.

##Conclusion

Now that you've completed all the necessary steps, file a [pull request in our whosonfirst-data repository](https://github.com/whosonfirst/whosonfirst-data/pulls)! We'll review the pull request and let you know if we have any questions.

This was an exercise in data curation and data management that will undoubtedly be replicated in other cities around the world. Taking a look at cities like [New York City](https://whosonfirst.mapzen.com/spelunker/id/85977539/descendants/?&placetype=neighbourhood#9/40.6805/-74.0656), [Buenos Aires](https://whosonfirst.mapzen.com/spelunker/id/85668081/descendants/?&placetype=neighbourhood#11/-34.5939/-58.4518), [Helsinki](https://whosonfirst.mapzen.com/spelunker/id/101748417/descendants/?&placetype=neighbourhood#11/60.2107/24.9411), and [Cape Town](https://whosonfirst.mapzen.com/spelunker/id/101928027/descendants/?&placetype=neighbourhood#10/-34.0028/18.4627), for example, you'll notice that we still have work to do to improve our neighbourhood records. A few take-aways:

* Anyone has the ability to contribute to neighbourhood updates for their locality.
* There will always be an argument for and against a change to a neighbourhood boundary.
* When it comes to neighbourhood boundaries, there is no right answer, but we care about your opinion. Please share!
* Neighbourhoods, macrohoods, and microhoods are ever-changing. Make the shapes better today!

Please remember - some of this work is automated and some of this work is not. Please contact us via an [issue](https://github.com/whosonfirst/whosonfirst-data/issues/new) or an [email](mailto:stephen.epps@mapzen.com) to work through the best approach for your city.

**Thanks for reading and happy mapping!**
