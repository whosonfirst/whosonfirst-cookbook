# Who's On First ID Life Cycle Documentation

## Feature Life Cycle Rules

Feature life cycles and tracking rules are necessary in understanding changes to a `wof:id`, what constitutes a change, and how Who's On First tracks both valid and non-valid features. By following the steps below, a standard is set in Who's On First to ensure that all users and mapping services are able to follow along with changes to a feature and the history of a given feature. 

Additionally, what Who's On First considers a Significant Event may be different than what a data user would consider a Significant Event. This could mean that while a feature in Who's On First was given a new record and `wof:id`, a specific user may not agree with that change - therefore, it is important for us to outline the rules and guidelines around Who's On First features and the `wof:id` field so users and their mapping services can optimize their data usage.

### What is a `wof:id`?

A Who's On First ID (`wof:id`) is a unique 64-bit identifier that represents a single point or polygon feature in Who's On First. This identifier is commonly produced by the [Brooklyn Integers](https://www.brooklynintegers.com) service, though alternative methods of retrieving a `wof:id` are available. Unlike OpenStreetMap (OSM) or the United Kingdom's Local Ordnance Survey (OS) a `wof:id` is stable to an individual feature and will not update when minor updates to a feature occur. Once a feature is given a `wof:id`, that feature will maintain that `wof:id` for it's entire lifecycle.

That's not to say that features never change; often times a feature is updated (significant change in size, changes placetype, is given additional properties, etc.) which may require a new feature to be created with a new `wof:id`. Updates to a feature that require a new feature with a new `wof:id` to be created are classified as a "significant event". 

### What is Significant Event?

While minor edits require an update to the attribute field and the `wof:lastmodified` field, major edits or updates to a feature in Who's on First are called "Significant Events". 

Updates and edits that qualify as a Significant Event:

- Cessation events (but when other feature(s) replace it with inception events)
- Changes to the `wof:placetype` 
- Changes to the geometry, where more than 50% (area or length) is added or removed
- Moving a feature's location more than ten kilometers from it's original location

When a Significant Event occurs, a new `wof:id` is minted for a new feature; this new feature replaces the old feature that required edits. The `supersedes` and `superseded_by` values are updated in the respective records which allows a user to track the life of a given record in Who's on First.

Significant Events are detailed below in the "Life" section.

### What are `supersedes` and `superseded_by` values?

If an existing feature experiences a Significant Event, the old feature should be duplicated but receive a new `wof:id` and given a `wof:supersedes` value equal to that of the existing feature, and the existing feature should be given a `wof:superseded_by` value equal to that of the new feature's `wof:id`. 

By linking features through the `supersedes` and `superseded_by` values, it allows a downstream consumers of Who's On First data to link together the history of any given feature at any given time and to understand which features are no longer valid (and which features _are_ valid).

Who's On First is not in the business of removing features from history, but rather looks to take a snapshot in time and preserve features based on what _was_ and what _is_. 

Below, the life cycle and tracking rules are outlined to help you understand what changes require a new `wof:id` and what changes allow the `wof:id` to be kept as-is.

Keeping up with `wof:id` changes and new features taking the place of old, outdated features can be tricky business. Who's On First has a built-in series of attributes that can be used to track the changes and updates to a feature, even if a Significant Event has taken place and replaced a `wof:id`. 

We'll refer to the non-valid feature as the **superseded** version and the new feature as the **superseding** version.

## Lifecycle Flowchart

![flowchart_final](https://cloud.githubusercontent.com/assets/18567700/18595704/baf94e30-7bfa-11e6-8c41-0f58cec2a67b.png)
 _Image 1: A flowchart to describe possible work to a new or existing Who's On First feature_
### Birth

If a feature unknown to Who's on First is added to the database, a new `wof:id` is minted and used for that feature's record.

#### Creation of a New Feature

Creating a new feature that was previously unknown to Who's On First is the most straightforward; no existing records need modifications and the only required work takes place in the record for the newly created feature.

### Life

Significant modifications fall into one of two categories: _real-world changes_ or _error corrections_. Both of these categories can have one of two edits made: **geometry edits** or **attribute edits** (or both). The following changes, what Who's On First calls a Significant Event, would require a new `wof:id` to be minted for a superseding feature and updates to a superseded feature.

- Cessation events (but when other feature(s) replace it with inception events)
- Changes to the `wof:placetype`
- Changes to the geometry, where more than 50% (area or length) is added or removed
- Moving a feature's location more than ten kilometers from it's original location

#### Moving a feature's location more than ten kilometers from it's original location

Similar to the Yugoslavia example, above, if a feature has it's geometry move more than ten kilometers or five miles from its original location, a new feature with a new `wof:id` would be created. 

If an error correction needed to occur to move Iceland, for example, fifty kilometers to the east (let's pretend it was imported incorrectly), the record for Iceland would receive a date (the date of it's error correction) in the `edtf:deprecated` field, an updated `mz:is_current` field, and the `wof:id` of the newly created Iceland record in it's `wof:superseded_by` field.

The new Iceland record would receive a new `wof:id`, and would have it's `wof:supersedes` field updated to include the `wof:id` of the original Iceland record. This new record would be our superseding features.

#### If any of the above are true:

We are required to do the following:

* Mint a new `wof:id`
* Link up supersedes values
* `is_current` field updates
* Mark the `edtf:cessation` field with the edit date

### Death

When one feature ceases and other feature(s), it is replaced with inception events.
A **superseded** feature will either need a `edtf:deprecated` or `edtf:cessation` date field update. This date is an essential attribute, as it identifies the specific date at which that feature was superseded (and when the superseding feature took over as the valid feature). When one of these field updates occurs, the superseding feature will always get a new `wof:id`.

* `edtf:deprecated` - Used when a feature was **never** correct to begin with. _Typically_ the field to update when dealing with an error correction.
 
* `edtf:cessation` - Used when a feature was correct at a point in time, but for one or more reasons is no longer correct.

## Examples

### Adding a new feature to Who's On First

An example of a new feature would be a venue record for a new restaurant in New York City. If said restaurant was opened in September 2016, Who's On First would not known about this feature previous to this date, which means a new `wof:id` would be created and attached to a venue record in the New York venues repository for inclusion into Who's On First. Note that since this feature was never in Who's On First prior to the creation of this new venue record, a new `wof:id` would be minted from Brooklyn Integers.

Another example could be a new military facility on a Pacific Island. Similar to the new venue record described above, this facility would receive a new `wof:id`, geometry, and attributes. This feature is an example of a completely new feature to Who's On First.

### Changes to the `wof:placetype`

If Who's on First incorrectly classified a set of localities as regions, said region records would become the superseded records, with new superseding locality records created in their place. The `mz:is_current` field, `wof:superseded_by`, and `edtf:cessation` date field would be updated for each of the superseded region records. Completely new features with new `wof:id`s, a corrected `wof:placetype` field, and updated `wof:supersedes` field would be created for the superseding locality records. 

In this case, since the correction was made on the `wof:placetype` field and other attribute field values were correct, all other correct attributes would be transferred to the superseding feature (zoom levels, geometries, concordances, hierarchies, etc).

### Changes to the geometry, where more than 50% (area or length) is added or removed

The Yugoslavia example, above, is a perfect example of a real-world geometry change causing a new `wof:id` to be minted. In this case, Yugoslavia was dissolved and split into several different countries (and a disputed area). The record for Yugoslavia would receive a date (the date of it's dissolution) in the `edtf:cessation` field, an updated `mz:is_current` field, and the `wof:id`s of the newly created countries in it's `wof:superseded_by` field.

The new countries, Slovenia, Croatia, Bosnia and Herzegovina, the Republic of Macedonia, Montenegro and Serbia which includes (Vojvodina and Kosovo), would each receive new `wof:id`s, and would have their `wof:supersedes` field updated to  include the `wof:id` of Yugoslavia. These would be our superseding features.

This superseding work would allow someone looking at, say, Montenegro, to see when it was created and what superseded feature it came from.

### Moving a feature's location more than ten kilometers from it's original location

Similar to the Yugoslavia example, above, if a feature has it's geometry move more than ten kilometers or five miles from its original location, a new feature with a new `wof:id` would be created. 

If an error correction needed to occur to move Iceland, for example, fifty kilometers to the east (let's pretend it was imported incorrectly), the record for Iceland would receive a date (the date of it's error correction) in the `edtf:deprecated` field, an updated `mz:is_current` field, and the `wof:id` of the newly created Iceland record in it's `wof:superseded_by` field.

The new Iceland record would receive a new `wof:id`, and would have it's `wof:supersedes` field updated to include the `wof:id` of the original Iceland record. This new record would be our superseding features.
