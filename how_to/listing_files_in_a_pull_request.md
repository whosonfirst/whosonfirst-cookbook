# Listing Files Changed in a Pull Request

Occassionally, GitHub pull requests to update Who's On First records can become quite large (see: PR [#660](https://github.com/whosonfirst-data/whosonfirst-data/pull/660) and [#824](https://github.com/whosonfirst-data/whosonfirst-data/pull/824)) and, when processed, can inadvertently create error messages like:

```
INFO:root:git show --pretty=format: --name-only 67c8e5c5fdcf6dbea9510f4159f2bad9c4ec516f
INFO:root:git show --pretty=format: --name-only e3d4675a3b51c01e9b196fa75261d4325e8014cd
DEBUG:root:next None
DEBUG:root:checking that /usr/local/data/whosonfirst-data/data/110/897/911/1/1108979111.geojson exists locally
ERROR:root:/usr/local/data/whosonfirst-data/data/110/897/911/1/1108979111.geojson does not exist locally, did you merge the PR?
```

### Let's Back Up

Our pull request merge tools take a beginning step to "checkout" the `whosonfirst-data` GitHub repository before processing changes. This checkout step takes time, largely due to the amount of files and file sizes in the repository. On the off-chance that we see an error message like the one above, the entire checkout has to be restarted and debugging is needed to figure out the cause of this error message. 

In being explicit and passing a specific list of files to "checkout" (instead of checking out the entire repository), we can minimize the amount of time spent preparing the pull request for processing and ensure that all modified files are checked out before proceeding.

### The Command

By running the following terminal command, a list of edited files in a given commit can be exported to a local CSV file:

`git show --pretty="" --name-only [commit] > ~/Desktop/files-in-pr.csv`

- `git show`: Show various types of objects.
- `--pretty=""`: A format option to choose any content you would like to display.
- `--name-only`: The option to only show the file path and file name.
- `[commit]`: The commit hash you would like to receive modified files from (no brackets needed).
-  `> ~/Desktop/files-in-pr.csv`: The selected, local output filepath.

This command will result in a CSV file that has rows similar to:

```
data/101/750/533/101750533.geojson
data/101/750/575/101750575.geojson
data/101/750/605/101750605.geojson
data/101/750/627/101750627.geojson
data/101/751/595/101751595.geojson
data/101/751/933/101751933.geojson
data/101/752/521/101752521.geojson
data/101/830/205/101830205.geojson
data/101/872/433/101872433.geojson
```

Using this strategy to generate CSV files of modified files in a given pull request, we can append a list of CSV files to each new pull request in the `whosonfirst-data` repository. This will help in ensuring all necessary files are checked out when processing a pull request.
