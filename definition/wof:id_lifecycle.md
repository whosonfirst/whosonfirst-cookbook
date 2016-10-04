# Who's On First ID Life Cycle Documentation

## Feature Life Cycle Rules

This document sets to establish guidelines and rules around the Who's On First ID (`wof:id`); a unique ID used to track features in [Who's On First](https://whosonfirst.mapzen.com/). These rules are meant to help downstream data consumers understand changes to a `wof:id`, what constitutes a change, and how Who's On First tracks new, existing, and outdated features through the use of a `wof:id`. The steps below establish a convention to ensure that all users and mapping services are able to track the  history and life cycle of a given feature. 

Documenting these rules is important, as Who's On First's rules may differ from the assumptions of a data consumer or application. While these life cycle rules are subject to change, it is essential for Who's On First to outline the rules and guidelines around features; this allows users and mapping services to optimize data usage and understand the assumptions in the data structure. 

It is also important to note that while we strive to provide the most accurate and up-to-date `wof:id` life cycle rules, this document, as written today, is a working document. We expect churn in the Who's On First database, which means we will not be able to capture every possible scenario or rule at the moment, but we are working towards being able to do just that.

### What is a `wof:id`?

A `wof:id` is a unique 64-bit identifier that represents a single point or polygon feature in the Who's On First database. This identifier is commonly produced by the [Brooklyn Integers](https://www.brooklynintegers.com) service, though, technically any _unique_ 64-bit identifier can be used if Who's On First has not already maintained that ID for a known record. Unlike other databases that track features, for example the [United Kingdom's Local Ordnance Survey](https://www.europa.uk.com/resources/os/os-mastermap-topography-layer-user-guide.pdf) (OS), a `wof:id` is stable to an individual record and will not update when minor updates to a feature occur. Once a record is given a `wof:id`, that record will maintain that `wof:id` for it's entire life cycle, unless that record's feature experiences a Significant Event. The record's `wof:id` allows Who's On First to preserve that feature in history.


### What is Significant Event?

While minor edits (we'll call these Minor Events) allow for a feature to be edited in place and maintain the same `wof:id` it had prior to the edit, major edits to a feature are designated as **Significant Events** and have specific rules attached to them.

Updates and edits that qualify as Significant Events* :

- Changing a point feature's location more than **10km**
- Changing a polygon feature's area more than **50%**
- Changing a feature's `wof:name` **without** storing the original `wof:name` as an **alternative name**
- Changing a feature's `wof:name` due to the original `wof:name` being **wrong to begin with**
- Giving a feature a **new** `wof:parent_id`
- Giving a feature a **new** `wof:placetype`
- Updating a feature's `wof:hierarchy` to include an **updated `wof:id`**
- Replacing or superseding a record (**end of life event**; see below)

_* This list, as written today, may be incomplete or unable to capture the subtleties and demands of real-life._

### What does a Significant Event entail?

When a Significant Event occurs, a new `wof:id` is minted for a new feature and superseding work needs to occur. If an existing feature experiences a Significant Event, the following needs to occur:

- The feature's raw data (GeoJSON) should be duplicated into a new feature with a new `wof:id`
- The newly duplicated feature receives a `wof:supersedes` value equal to that of the existing feature's `wof:id`
- The existing feature receives a `wof:superseded_by` value equal to that of the new feature's `wof:id`
- The existing feature receives a `mz:is_current` value equal to `0`
- If the existing feature was never correct to begin with, it will receive a new date _(YYYY-MM-DD)_ in the `edtf:deprecated` property. Otherwise, the `edtf:cessation` property will be given a date _(YYYY-MM-DD)_. This `edtf` date should equal the date when the feature was edited.

In the flowchart below, we'll refer to these steps a the "rebirth" of a feature.

### Tracking change history with supersedes and superseded_by properties

We'll refer to the existing feature as the **superseded** version and the newly duplicated feature as the **superseding** version.

Keeping up with `wof:id` changes and new features taking the place of old, outdated features can be tricky. Who's On First has a built-in series of properties that can be used to track the changes and updates to a feature, even if a Significant Event has taken place and replaced a `wof:id`. The updating of the `wof:supersedes` and `wof:superseded_by` values in the respective records are what allows a data consumer or application to track the history of a given feature by linking together the history of any given feature at any given time. This superseding work also tracks which features are no longer valid (and which features _are_ valid). This history is not inherent to the chain of superseded features, but rather the chain of superseded features _and_ the Git changelog for said feature.

While Who's On First does not currently have an audit trail for each feature, the Git changelog for each feature is the closest approximation to such a trail. This idealized audit log is a future goal for Who's On First, but for now, the use of Git and the supersede properties allow a user to track the history of a given feature.

Who's On First is not in the business of removing features from history, but rather looks to take a snapshot in time and preserve features based on what **_was_** and what **_is_**. The `wof:id` field allows Who's On First to provide an accurate description of the present, while also retaining historical records of a place.

## Life Cycle Flowchart

![final_flowchart](https://cloud.githubusercontent.com/assets/18567700/19081530/9bb20ea4-8a28-11e6-82e9-c3a1e85da9f2.png)
 _The above flowchart outlines potential updates to a new or existing Who's On First feature._
 
### Create

If a feature unknown to Who's On First is added to the database, a new unique 64-bit identifier is minted (typically through [Brooklyn Integers](https://www.brooklynintegers.com)) and used for that feature's `wof:id`.

If the new feature does not have any descendants, the feature can be imported directly into Who's On First without modifications to existing features. However, if the new feature parents any existing Who's On First records, this feature will need to be placed in the hierarchy of all of its descendants. 

If the new feature has descendants _and_ the new feature's descendant records already have a record with a `wof:placetype` equal to that of the new feature, all descendants will be superseded into new records. If not, the new features can be imported directly without any superseding work done to the descendant records.

### Alter

These rules pertain to features that are already known to Who's On First. A wide-variety of changes can occur to such features, which fall into one of two categories: Minor Events or [Significant Events](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/significant_event.md). Minor Events require edits to be made to the features and _do not_ require additional work (like superseding, deprecating, etc.). Significant Events, however, _do_ require additional work to be completed, as outlined in the "Significant Events" section above. Significant Events fall into one of two categories: **real-world changes** or **error corrections**, which can either be **geometry edits** or **property edits**. 

See the "Examples" section below for more in-depth descriptions of update possibilities for existing features. 

### End of Life

When an existing feature in Who's On First ceases to exist in the real-world or is removed due to an error-correction, inception events occur and it may be replaced with a new feature that takes it's place. 

If the feature actually existed in the real-world at one point in time, but is no longer current, it's record will recieve an `edtf:cessation` date _(YYY-MMM-DD)_, equal to the date it was edited and an `mz:is_current` property equal to `0`. If that feature was replaced with another feature, work to supersede the old feature with the new feature is also required. Example of updated properties for a replaced WOF feature, below:

```
"edtf:cessation": 2016-10-01,
...
"mz:is_current":0,
...
"wof:superseded_by":9964566319,
```

If the feature was _never_ an actual feature in the real-world (typically due to an error in Who's On First), the record will recieve an `edtf:deprecated` date _(YYY-MMM-DD)_, equal to the date it was edited and an `mz:is_current` property equal to `0`. Example of updated properties for a deprecated WOF feature below:

```
"edtf:deprecated": 2016-10-01,
...
"mz:is_current":0,
```

## Examples

### Creating Features

#### Adding a feature that does not have descendants

If adding a new `venue` record to Who's On First, for example, a new `wof:id` should be minted and the feature (with appropriate venue properties) should be added to the database.

An example of a new feature without descendants to Who's On First: A venue record for a new restaurant that recently opened in New York City. Who's On First would not know about this feature prior to it's opening, which means a **new** `wof:id` would be created and attached to a venue record in the New York venues repository for inclusion into Who's On First. Note that since this feature was never in Who's On First prior to the creation of this new venue record, a new `wof:id` would be minted from Brooklyn Integers.

Another example could be a new military facility on a Pacific Island. Similar to the new venue record described above, this facility would receive a new `wof:id`, geometry, and properties. This feature is an example of a completely new feature to Who's On First.

#### Adding a feature that has descendants

If adding a previously unknown `county` record to Who's On First that has descendant records, a new `wof:id` should be minted and the feature (with appropriate properties) should be added to the database. These descendant records can be found by searching the feature's parent country in our [Spelunker](https://whosonfirst.mapzen.com/spelunker) and searching through it's descendant records to see if any fall within your new county's geometry. Occasionally, this type of feature addition to Who's On First occurs. In the example below, let's envision a feature that _should_ have had a county record in it's hierarchy, but for some unknown reason, Who's On First never had that data to begin with. 

With this example, the `wof:hierarchy` and `wof:belongsto` properties of all descendants needs to be updated to include the new `wof:id` of the new county. An example of the `wof:hierarchy` property update is shown below.

Descendant's `wof:hierarchy` before import of parent; notice the `wof:hierarchy` does not contain a "county_id":

```
"wof:hierarchy":[
        {
            "continent_id":102191575,
            "country_id":85633793,
            "locality_id":85922583,
            "region_id":85688637
        }
    ],
```

Descendant's `wof:hierarchy` after import of parent; the hierarchy now contains a "county_id":

```
"wof:hierarchy":[
        {
            "continent_id":102191575,
            "country_id":85633793,
            "county_id":102087579,
            "locality_id":85922583,
            "region_id":85688637
        }
    ],
```

### Altering Features

#### Moving a feature's location more than ten kilometers from it's original location

Who's On First uses ten kilometers as a measure of significance for feature updates. Though a user or service may consider a smaller or larger distance to be significant, Who's On First considers one-tenth of a decimal degree (roughly ten kilometers) to be significant enough to warrant a new `wof:id` and feature. This value was decided on because at the equator, one degree is equal to 69 kilometers; one tenth of 69 kilometers is 6.9 kilometers, which we used to round up to 10 kilometers.

If an error correction needed to occur to move Iceland, for example, fifty kilometers to the east (let's pretend the feature for Iceland was imported incorrectly), the record for Iceland would receive a date (the date of it's error correction) in the `edtf:deprecated` property, an updated `mz:is_current` property, and the `wof:id` of the newly created Iceland record in it's `wof:superseded_by` property.

The new Iceland record would receive a new `wof:id`, and would have it's `wof:supersedes` property updated to include the `wof:id` of the original Iceland record. This new record would be our superseding features.

####Changing a polygon feature's area more than **50%**

Who's On First uses 50% as a measure of whether or not a change in a feature's geometry is a "Significant Event". Simply put, a change of over half of a feature's geometry means the majority of that feature has changed; Who's On First uses this 50% as a trigger to supersede features and qualify an edit as significant.

The case of Yugoslavia is a perfect example of a real-world geometry change causing a new `wof:id` to be minted. In this case, Yugoslavia was dissolved and split into several different countries (and a disputed area). The record for Yugoslavia would receive a date (the date of it's dissolution) in the `edtf:cessation` property, an updated `mz:is_current` property, and the `wof:id` values of the newly created countries in it's `wof:superseded_by` property.

The new countries, [Slovenia](https://whosonfirst.mapzen.com/spelunker/id/85633779/#8/46.154/14.993), [Croatia](https://whosonfirst.mapzen.com/spelunker/id/85633229/#6/44.518/16.455), [Bosnia and Herzegovina](https://whosonfirst.mapzen.com/spelunker/id/85632609/#7/43.941/17.661), the [Republic of Macedonia](https://whosonfirst.mapzen.com/spelunker/id/85632373/#8/41.622/21.739), [Montenegro](https://whosonfirst.mapzen.com/spelunker/id/85632667/#7/42.711/19.385) and [Serbia](https://whosonfirst.mapzen.com/spelunker/id/85633755/#6/44.244/20.927) which included ([Vojvodina](https://whosonfirst.mapzen.com/spelunker/id/404227537/#7/45.418/20.198) and [Kosovo](https://whosonfirst.mapzen.com/spelunker/id/85633259/#8/42.567/20.899)), would each receive a new `wof:id`, and would have their `wof:supersedes` property updated to include the `wof:id` of Yugoslavia. These would be our superseding features.

This superseding work would allow someone looking at, say, Montenegro, to see when it was created and what superseded feature it came from.

####Changing a feature's **`wof:placetype`**

If Who's on First incorrectly classified a set of localities as regions, the region records would become the **superseded** records and the locality records would be the **superseding** records. The `mz:is_current` property, `wof:superseded_by`, and `edtf:cessation` date property would be updated for each of the superseded region records. Completely new features with new `wof:id` values, a corrected `wof:placetype` property, and updated `wof:supersedes` property would be created for the superseding locality records. 

In this case, since the correction was made on the `wof:placetype` property and other property values were correct, all other correct properties would be transferred to the **superseding** feature (zoom levels, geometries, concordances, hierarchies, etc).

### Ending the Life of a Feature

#### Adding a `edtf:deprecated` date to a feature

If the feature being updated was _never_ correct to begin with, the following work needs to occur:

* `edtf:deprecated` - This **string** attribute field will be added to the feature. It is equal to the date _(YYY-MM-DD)_ that the feature was edited as no longer current. Example below:

```
 "edtf:deprecated":"2016-10-01",
```

* `mz:is_current` - This **boolean** attribute field will be added to the feature. It is equal to `0` (represented as an integer) to indicate that the feature is deprecated. Example below:

```
 "mz:is_current":0,
```

#### Adding a `edtf:cessation` date to a feature

If an existing Who's On First feature _was_ correct at one point in time but no longer exists in the real-world, the following work needs to occur if it _was not_ replaced by another feature*:

* `edtf:cessation` - This **string** attribute field will be updated to the feature. It is equal to the date _(YYY-MM-DD)_ that the feature was edited as no longer current. Example below:

```
 "edtf:cessation":"2016-10-01",
```

* `mz:is_current` - This **boolean** attribute field will be added to the feature. It is equal to `0` (represented as an integer) to indicate that the feature is deprecated. Example below:

```
 "mz:is_current":0,
```

_If the feature was replaced by another feature, a new `wof:id` should also be minted and superseding work should take place, as outlined above_
