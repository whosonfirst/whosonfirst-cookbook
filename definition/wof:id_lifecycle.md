# Who's On First ID Life Cycle Documentation

## Feature Life Cycle Rules

This document sets to establish guidelines and rules around the Who's On First ID (`wof:id`); a unique ID used to track features in [Who's On First](https://whosonfirst.mapzen.com/). These rules are meant to help a data consumer understand changes to a `wof:id`, what constitutes a change, and how Who's On First tracks new, existing, and outdated features through the use of a `wof:id`. The steps below set a standard to ensure that all users and mapping services are able to track the  history and life cycle of a given feature. 

Documenting these rules is important, as Who's On First's rules may differ from the assumptions of a data consumer or application. While these life cycle rules are subject to change, it is essential for Who's On First to outline the rules and guidelines around features; this allows users and mapping services to optimize data usage and understand the assumptions in the data structure.

### What is a `wof:id`?

A `wof:id` is a [unique 64-bit identifier](https://en.wikipedia.org/wiki/Organizationally_unique_identifier#64-bit_Extended_Unique_Identifier_.28EUI-64.29) that represents a single point or polygon feature in the Who's On First database. This identifier is commonly produced by the [Brooklyn Integers](https://www.brooklynintegers.com) service, though, technically any _unique_ 64-bit identifier can be used if Who's On First has not already maintained that id for a known record. Unlike [OpenStreetMap](http://wiki.openstreetmap.org/wiki/Elements) (OSM) or the [United Kingdom's Local Ordnance Survey](https://www.europa.uk.com/resources/os/os-mastermap-topography-layer-user-guide.pdf) (OS), a `wof:id` is stable to an individual feature and will not update when minor updates to a feature occur. Once a feature is given a `wof:id`, that feature will maintain that `wof:id` for it's entire lifecycle, unless that feature experiences a Significant Event (explained below).


### What is Significant Event?

While minor edits (we'll call these Minor Events)allow for a feature to be edited in place and maintain the same `wof:id` it had prior to the edit, major edits to a feature are designated as **Significant Events**. 

Updates and edits that qualify as absolute Significant Events* :

- Changing a point feature's location more than **10km**
- Changing a polygon feature's area more than **50%**
- Changing a feature's `wof:name` **without** storing the original `wof:name` as an **alt-name**
- Changing a feature's `wof:name` due to the original `wof:name` being **wrong to being with**
- Giving a feature a new `wof:parent_id` when the parent's `wof:placetype` is a **country or region**
- Changing a feature's **`wof:placetype`**
- Updating a feature's `wof:hierarchy` to include an **updated `wof:id`**
- Replacing or superseding a record (**cessation event**; see below)

_* This list, as written today, may be incomplete or unable to capture the subtleties and demands of real-life._

If an existing feature experiences a Significant Event, the following needs to occur:

- The feature's raw data (geojson) should be duplicated into a new feature with a new `wof:id`
- The duplicate feature (new) receives a `wof:supersedes` value equal to that of the existing feature's `wof:id`
- The existing feature (old) receives a `wof:superseded_by` value equal to that of the new feature's `wof:id`
- The existing feature (old) recieves a `mz:is_current` value equal to `0`.
- Depending on whether or not the existing feature (old) was ever correct to begin with, it will recieve either a new date (YYYY-MM-DD) in the `edtf:cessation` field or the `edtf:deprecated` field (explained below)

When a Significant Event occurs, a new `wof:id` is minted for a new feature and superseding work needs to occur (explained below).

### What are `supersedes` and `superseded_by` values?

We'll refer to the existing feature (old) feature as the **superseded** version and the duplicate feature (new) as the **superseding** version.

Keeping up with `wof:id` changes and new features taking the place of old, outdated features can be tricky business. Who's On First has a built-in series of attributes that can be used to track the changes and updates to a feature, even if a Significant Event has taken place and replaced a `wof:id`. The updating of the `wof:supersedes` and `wof:superseded_by` values in the respective records are what allows a data consumer or application to track the history of a given feature by linking together the history of any given feature at any given time. This superseding work also tracks which features are no longer valid (and which features _are_ valid). This history is not inherent to the linked feature list, but rather the linked feature list _and_ GitHub log.

Who's On First is not in the business of removing features from history, but rather looks to take a snapshot in time and preserve features based on what **_was_** and what **_is_**. The `wof:id` field allows Who's On First to provide an accurate description of the present, while also retaining historical records of a place.

Below, the life cycle and tracking rules are outlined to help you understand what changes require a new `wof:id` and what changes allow the `wof:id` to be kept as-is.

## Lifecycle Flowchart

![flowchart_final](https://cloud.githubusercontent.com/assets/18567700/18650617/db069f3e-7e7a-11e6-9b22-e9272613a480.png)
 _The above flowchart outlines potential updates to a new or existing Who's On First feature._
 
### Birth

If a feature unknown to Who's On First is added to the database, a new unique 64-bit identifier is minted and used for that feature's `wof:id`.

Creating a new feature that was previously unknown to Who's On First is the most straightforward workflow. If the new feature will not have any descendants, the feature can be imported directly into Who's On First without modifications to existing features. However, if the new feature parents any existing Who's On First records, this feature will need to be placed in the hierarchy of all of its descendants.

### Life

These rules pertain to features that are already known to Who's On First. A wide-variety of changes can occur to such features, which fall into one of two categories: Minor Events or Significant Events. Minor Events require edits to be made to the features and _do not_ require additional work (like superseding, deprecating, etc.). Significant Events, however, _do_ require additional work to be completed, as outlined in the "Significant Events" section above. Significant Events fall into one of two categories: **real-world changes** or **error corrections**, which can either be **geometry edits** or **attribute edits**. 

See the "Examples" section below for more in-depth descriptions of update possibilities for existing features. 

### Death

When an existing feature in Who's On First ceases to exist in the real-world or is removed due to an error-correction, it is replaced and inception events occur. 

## Examples

###Birth

#### Adding a feature that does not have descendants

If adding a new `venue` record to Who's On First, for example, a new `wof:id` should be minted and the feature (with appropriate venue properties) should be added to the database.


#### Adding a feature that has descendants

If adding a new `county` record to Who's On First that has descendant records, for example, a new `wof:id` should be minted and the feature (with appropriate county properties) should be added to the database. Additionally, the `wof:hierarchy` and `wof:belongsto` fields of all descendants needs to be updated to include that new `wof:id` of the new county. Example of `wof:hierarchy` field update below:

Descendant's `wof:hierarchy` before import of parent:

````
"wof:hierarchy":[
        {
            "continent_id":102191575,
            "country_id":85633793,
            "locality_id":85922583,
            "region_id":85688637
        }
    ],
````

Descendant's `wof:hierarchy` after import of parent:

````
"wof:hierarchy":[
        {
            "continent_id":102191575,
            "country_id":85633793,
            "county_id":102087579,
            "locality_id":85922583,
            "region_id":85688637
        }
    ],
````

###Life

#### Moving a feature's location more than ten kilometers from it's original location

Who's On First uses ten kilometers as a measure of significance for feature updates. Though a user or service may consider a smaller or larger distance to be significant, Who's On First considers one-tenth of a decimal degree (roughly ten kilometers) to be significant enough to warrant a new `wof:id` and feature.

If an error correction needed to occur to move Iceland, for example, fifty kilometers to the east (let's pretend it was imported incorrectly), the record for Iceland would receive a date (the date of it's error correction) in the `edtf:deprecated` field (see description below), an updated `mz:is_current` field, and the `wof:id` of the newly created Iceland record in it's `wof:superseded_by` field.

The new Iceland record would receive a new `wof:id`, and would have it's `wof:supersedes` field updated to include the `wof:id` of the original Iceland record. This new record would be our superseding features.

####Changing a polygon feature's area more than **50%**

The case of Yugoslavia is a perfect example of a real-world geometry change causing a new `wof:id` to be minted. In this case, Yugoslavia was dissolved and split into several different countries (and a disputed area). The record for Yugoslavia would receive a date (the date of it's dissolution) in the `edtf:cessation` field, an updated `mz:is_current` field, and the `wof:id`s of the newly created countries in it's `wof:superseded_by` field.

The new countries, [Slovenia](https://whosonfirst.mapzen.com/spelunker/id/85633779/#8/46.154/14.993), [Croatia](https://whosonfirst.mapzen.com/spelunker/id/85633229/#6/44.518/16.455), [Bosnia and Herzegovina](https://whosonfirst.mapzen.com/spelunker/id/85632609/#7/43.941/17.661), the [Republic of Macedonia](https://whosonfirst.mapzen.com/spelunker/id/85632373/#8/41.622/21.739), [Montenegro](https://whosonfirst.mapzen.com/spelunker/id/85632667/#7/42.711/19.385) and [Serbia](https://whosonfirst.mapzen.com/spelunker/id/85633755/#6/44.244/20.927) which includes ([Vojvodina](https://whosonfirst.mapzen.com/spelunker/id/404227537/#7/45.418/20.198) and [Kosovo](https://whosonfirst.mapzen.com/spelunker/id/85633259/#8/42.567/20.899)), would each receive a new `wof:id`, and would have their `wof:supersedes` field updated to  include the `wof:id` of Yugoslavia. These would be our superseding features.

This superseding work would allow someone looking at, say, Montenegro, to see when it was created and what superseded feature it came from.

####Changing a feature's **`wof:placetype`**

If Who's on First incorrectly classified a set of localities as regions, said region records would become the superseded records, with new superseding locality records created in their place. The `mz:is_current` field, `wof:superseded_by`, and `edtf:cessation` date field would be updated for each of the superseded region records. Completely new features with new `wof:id`s, a corrected `wof:placetype` field, and updated `wof:supersedes` field would be created for the superseding locality records. 

In this case, since the correction was made on the `wof:placetype` field and other attribute field values were correct, all other correct attributes would be transferred to the superseding feature (zoom levels, geometries, concordances, hierarchies, etc).


#### Adding a new feature to Who's On First

An example of a new feature to Who's On First: A venue record for a new restaurant that recently opened in New York City. If said restaurant was opened in September 2016, Who's On First would not known about this feature previous to this date, which means a new `wof:id` would be created and attached to a venue record in the New York venues repository for inclusion into Who's On First. Note that since this feature was never in Who's On First prior to the creation of this new venue record, a new `wof:id` would be minted from Brooklyn Integers.

Another example could be a new military facility on a Pacific Island. Similar to the new venue record described above, this facility would receive a new `wof:id`, geometry, and attributes. This feature is an example of a completely new feature to Who's On First.

###Death

#### Adding a `edtf:deprecated` date to a feature

If the feature being updated was _never_ correct to begin with, the following work needs to occur:

* `edtf:deprecated` - This **string** attribute field will be added to the feature. It is equal to the date (YYY-MM-DD) that the feature was invalidated. Example below:

````
 "edtf:deprecated":"2016-10-01",
````

* `mz:is_current` - This **integer** attribute field will be added to the feature. It is equal to `0` to indicate that the feature is deprecated. Example below:

````
 "mz:is_current":0,
````

#### Adding a `edtf:cessation` date to a feature

If an existing Who's On First feature _was_ correct at one point in time but no longer exists in the real-world, the following work needs to occur if it _was not_ replaced by another feature*:

* `edtf:cessation` - This **string** attribute field will be updated to the feature. It is equal to the date (YYY-MM-DD) that the feature was invalidated. Example below:

````
 "edtf:cessation":"2016-10-01",
````

* `mz:is_current` - This **integer** attribute field will be added to the feature. It is equal to `0` to indicate that the feature is deprecated. Example below:

````
 "mz:is_current":0,
````

*_If the feature was replaced by another feature, a new `wof:id` should also be minted and superseding work should take place, as outlined above_
