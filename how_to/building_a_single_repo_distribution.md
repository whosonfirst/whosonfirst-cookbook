# Bundling "combined" SQLite distribution files

This document is not meant to be a replacement for documentation in the repositories below, but rather a simple guide to creating a "combined" SQLite distribution file using more than one `whosonfirst-data-admin-*` repository.

This is a brief overview of Who's On First's `wof-dist-build` tool and what is needed to create a SQLite distribution file for a single Who's On First admin repo. This tool can be used to combine other repositories, but with this example, we're only concerned with admin repositories.

Note that this also assumes you have various tools and repositories on your local machine before proceeding:
- A single `whosonfirst-data-admin-*` repository (in this example, we'll use the `whosonfirst-data-admin-at` repo)
- The most recent Go release (1.12+) installed
- A clone of the `go-whosonfirst-dist` repository
- Other supplemental Who's On First repositories (more details to follow...)

Lastly, all of this work assumes that all GeoJSON files in all repositories validate using the `go-whosonfirst-validate` tool, specifically with the `-names` flag envoked. This validation should not be an issue, but the tool should be run over all repositories before building the dist file.

If the above requirements are met, from the `go-whosonfirst-dist` repository, run the following command:

```
./bin/wof-dist-build -build-bundle -custom-repo -preserve-checkout -local-checkout -timings -verbose -workdir /path/to/wof_data/ whosonfirst-data-admin-at
```

This command includes:

- `./bin/wof-dist-build`: Runs the wof-dist-build Go tool
- `-build-bundle -custom-repo -preserve-checkout -local-checkout -timings -verbose`: Various flags, specific to the input/output of the distribution we're creating
- `-workdir /path/to/wof_data/`: Working directory, or where to write our file
- `whosonfirst-data-admin-at`: The repository that we're using to build a SQLite distribution

Since we've passed the `-verbose` flag, we'll quickly get a warning about alt-geometries, a list of checkouts being considered, and commit hashes:

```
[wof-dist-build] STATUS local_checkouts are [/path/to/wof_data/whosonfirst-data-admin-at]
[wof-dist-build] STATUS commit hashes are map[whosonfirst-data-admin-at:1d4077eaba9c1a8f603f32039d59d9adc9773d24] ([/path/to/wof_data/whosonfirst-data-admin-at])
```

Then, we'll see status times roughly every minute until the distribution writes to disc:

```
[wof-dist-build] STATUS time to index concordances (11858) : 2.361684362s
[wof-dist-build] STATUS time to index geojson (11858) : 4.338336093s
[wof-dist-build] STATUS time to index spr (11858) : 15.788493078s
[wof-dist-build] STATUS time to index names (11858) : 10.232274425s
[wof-dist-build] STATUS time to index ancestors (11858) : 4.070876322s
[wof-dist-build] STATUS time to index all (11858) : 1m0.000291189s
```

Then, we see additional updates about status times telling us that records were indexed, and no errors were reported:

```
[wof-dist-build] STATUS Built  without any reported errors
[wof-dist-build] STATUS local sqlite is /path/to/wof_data/whosonfirst-data-admin-at-latest.db
[wof-dist-build] STATUS build metafile from sqlite ([/path/to/wof_data/whosonfirst-data-admin-at-latest.db])
```

Then, we'll see an update letting us know that the combined .db file took ~8 minutes to prepare:

```
2019/12/18 13:57:20 time to prepare /path/to/wof_data/whosonfirst-data-admin-at-latest.db 4.648786041s
2019/12/18 13:57:20 time to prepare all 21067 records 4.64882645s
```

And finally, we see various updates about status times, file compression, and file deletion:

```
[wof-dist-build] STATUS time to build metafiles (/path/to/wof_data/whosonfirst-data-admin-at-latest.csv,/path/to/wof_data/whosonfirst-data-admin-at-latest.csv,/path/to/wof_data/whosonfirst-data-admin-at-latest.csv) 4.658622011s
[wof-dist-build] STATUS time to build bundles () 1.329968966s
[wof-dist-build] STATUS time to build UNCOMPRESSED distributions for whosonfirst-data-admin-at 2m6.679797982s
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 540ns
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.db
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.db 512ns
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 281ns
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest 420ns
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest 375ns
[wof-dist-build] STATUS register function to compress /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest 332ns
[wof-dist-build] STATUS time to wait to start compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 379ns
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 42.998874ms
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 43.929923ms
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.csv 44.25833ms
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest 3.151578231s
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest 3.15282233s
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest 3.1585305s
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.db (throttle)
[wof-dist-build] STATUS time to compress /path/to/wof_data/whosonfirst-data-admin-at-latest.db 42.886099998s
[wof-dist-build] STATUS All done compressing /path/to/wof_data/whosonfirst-data-admin-at-latest.db
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest.db
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS remove uncompressed file /path/to/wof_data/whosonfirst-data-admin-at-latest.csv
[wof-dist-build] STATUS time to remove uncompressed files for whosonfirst-data-admin-at 76.065893ms
[wof-dist-build] STATUS time to build COMPRESSED distributions for whosonfirst-data-admin-at 2m49.642221454s
[wof-dist-build] STATUS time to build distributions for 1 repos 2m49.642352574s
[wof-dist-build] STATUS ITEMS map[whosonfirst-data-admin-at:[whosonfirst-data-admin-at-latest.csv whosonfirst-data-admin-at-latest.csv whosonfirst-data-admin-at-latest.csv whosonfirst-data-admin-at-latest whosonfirst-data-admin-at-latest whosonfirst-data-admin-at-latest whosonfirst-data-admin-at-latest.db]]
[wof-dist-build] STATUS Wrote inventory /path/to/wof_data/whosonfirst-data-admin-at-inventory.json
```

This should result in the creation of five files:

- whosonfirst-data-admin-at-inventory.json
- whosonfirst-data-admin-at-latest.db.bz2
- whosonfirst-data-admin-at.csv.bz2
- whosonfirst-data-admin-at-latest.tar.bz2

### See also:

- https://dist.whosonfirst.org/
- https://whosonfirst.org/
- https://github.com/whosonfirst/go-whosonfirst-validate
- https://github.com/whosonfirst/go-whosonfirst-dist
- https://github.com/whosonfirst/go-whosonfirst-dist-publish
- https://git-scm.com/
- https://git-lfs.github.com/
- https://github.com/src-d/go-git
