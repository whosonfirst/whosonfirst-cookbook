## How To: Running the GeoNames Import Script

**The GeoNames import script**: https://github.com/mapzen/whosonfirst-toolbox/blob/master/scripts/geonames_import_script_local.py.

[GeoNames](http://www.geonames.org) is a "geographical database [that] covers all countries and contains over eleven million placenames that are available for download free of charge". The data is provided under a [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/).

Who's On First is happy to house the vast majority of these place names in our administrative records. Periodically, we re-run our import script to ensure that we have the best concordance to this database as possible. Using the unique GeoNames identifier (a concordance in Who's On First records), we can "link" each Who's On First record to the large the `alternateNames.zip` file from the GeoNames [free gazetteer data site](http://download.geonames.org/export/dump/).

Below is a step-by-step guide to run the GeoNames name import script. Before starting, make sure you have a local copy of the `whosonfirst-data` repo, the `whosonfirst-toolbox` repo, and the GeoNames `alternateNames.zip` file from the GeoNames [free gazetteer data site](http://download.geonames.org/export/dump/).

1. Rename the `alternateNames.txt` file to `alternateNames.csv`

2. Open the `alternateNames.csv` file and add the following to the first line of the file:
  
```
alternateNameId	geonameid	isolanguage	alternate_name	isPreferredName	isShortName	isColloquial	isHistoric  
```
  
3. Run the following command:

```
python  ../geonames_import_script_local.py -i ../alternateNames.csv -m ../whosonfirst-data/meta/wof-concordances-latest.csv -d 1000
```

And that's it. Following these steps will add any missing name or abbreviation from the GeoNames file.
