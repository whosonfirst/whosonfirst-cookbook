#The Issue
A multi-part [issue](https://github.com/whosonfirst/whosonfirst-data/issues/162) was apparent in the WOF record for the Seattle neighbourhood of `Capitol Hill`. Most notably, three separate records appeared in our WOF dataset - `id:85807733`, `id:85882415`, and `id:85809401` - each with a geometry for a portion of the true Capitol Hill neighbourhood geometry. A workflow was necessary to not only merge these three separate geometries into a single, new record for Capitol Hill, but to also deprecate records deemed incorrect and attach and/or modify values to appropriate records. 

#Workflow
##Which Record Should Contain Capitol Hill Data?
Each WOF record has a `GN:Name` field associated to the [GeoNames](http://www.geonames.org/) service; after reviewing the three current geojson records' `GN:Name` field, the `id:85882415` record was used as the combined Capitol Hill record because it had the correct `GN:Name` identifier for the Capitol Hill neighbourhood.

HOWEVER, this geometry edit is deemed a 'Significant Event', so the the `id:85882415` record was copied into a completely new record, `id:772967579`. [Brooklyn Integers](http://www.brooklynintegers.com/create/) was used to created a unique repository number to house the new record of `id:772967579`.

##Merging Geometries
Once each .geojson file is downloaded from the WOF repository, they were added into a new QGIS document. Each of the three geometries were added to a single .geojson file. The Dissolve tool was then used to merge all geometries. The Dissolve tool exports this new geometry to a shapefile, so, using ogr2ogr or built-in QGIS functionality (Save As > .geojson), the shapefile is converted back into a .geojson file (three .geojson files > one .shp > one .geojson). Basic bash script below:

```
ogr2ogr -f GeoJSON -t_srs crs:84 newfilename.geojson existingfilename.shp
```

This new .geojson file contained the geometry needed for the updated Capitol Hill record (`id:772967579`).

Note: The `Exportify` tool should take care of .geojson formatting, as the ogr2ogr workflow creates blank spaces in the geometry record. The new geometry was pasted into `id:772967579` and processed through the Exportify tool to remove the blank spaces. See below:

<img width="647" alt="screen shot 2016-05-04 at 10 26 49 am" src="https://cloud.githubusercontent.com/assets/18567700/15023303/cc90a81c-11e4-11e6-8ccf-dead8be22bb2.png">

##Deprecating, Superseding, and Parenting
Since the `id:772967579` record absorbed geometries of `id:85807733`, `id:85882415`, and `id:85809401`, edits were made to all records to reflect new values. The following edits were made:

####id:85809401
* `"edtf:deprecated": "YYYY-MM-DD"` field added.
* `"mz:is_current": 0` field added. `0` value to signify the record is deprecated. 
* `"wof:lastmodified": XXXXXXXXXX` field automatically updated from Exportify to reflect most recent update time.
*  `"wof:superseded_by":` value updated to `85882415`.

<img width="492" alt="screen shot 2016-05-04 at 1 45 06 pm" src="https://cloud.githubusercontent.com/assets/18567700/15028614/8aa3c488-11fe-11e6-9782-b9955411e344.png">


####id:85807733 (copied to id:772967579)
* `"edtf:deprecated": "YYYY-MM-DD"` field added.
* `"mz:is_current": 0` field added. `0` value to signify the record is deprecated. 
* `"wof:lastmodified": XXXXXXXXXX` field automatically updated from Exportify to reflect most recent update time.
* `"wof:superseded_by":` value updated to `772967579`.

<img width="491" alt="screen shot 2016-05-04 at 1 45 20 pm" src="https://cloud.githubusercontent.com/assets/18567700/15028619/8c698c62-11fe-11e6-9820-b41317145330.png">

####id:85882415
* `"edtf:deprecated": "uuuu"` field added.
* All fields beginning with `geom:` automatically updated to reflect newly merged geometry.
* `wof:geom` field updated to reflect newly merged geometry.
* `"wof:lastmodified": XXXXXXXXXX` field automatically updated from Exportify to reflect most recent update time.
* `"wof:supersedes":` value updated to `85809401`.
* `"bbox":` and `"geometry":` fields automatically updated to reflect newly merged geometry

<img width="491" alt="screen shot 2016-05-04 at 1 44 55 pm" src="https://cloud.githubusercontent.com/assets/18567700/15028612/8826307e-11fe-11e6-87ca-b9a7c33ec34e.png">
