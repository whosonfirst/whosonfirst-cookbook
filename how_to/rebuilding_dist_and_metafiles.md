# Bundling SQLite and rebuilding metafiles

This document is not meant to be a replacement for documentation in the repositories below, but rather a simple guide to rebuilding the SQLite distribution file and metafiles for the [`whosonfirst-data`](https://www.github.com/whosonfirst-data/whosonfirst-data) repository.

### Tools

Assuming you have the `Go` and `make` files installed, clone the [go-whosonfirst-dist](https://github.com/whosonfirst/go-whosonfirst-dist) repository. The repository has a `wof-dist-build` tool that we can use to rebuild dist files and metafiles.

Once you've navigated to the repository directory, the following command will trigger the rebuild:

```
> mkdir tmp
> ./bin/wof-dist-build -timings -verbose -workdir ./tmp -build-sqlite -build-meta whosonfirst-data
```

More specifically, the tool will:

1. Trigger a clone of the whosonfirst-data` repository.
2. Bundle all records from the `master` branch in the `whosonfirst-data` repository into a single `whosonfirst-data-latest.db` file.
3. Create csv "metafiles", per placetype

As of June 2018, this process takes roughly 90 minutes to run on a MacBook Pro.

### Note

This process **will not** create a SQLite distribution file that contains a geometry index.

### See also:

https://dist.whosonfirst.org/
https://whosonfirst.org/