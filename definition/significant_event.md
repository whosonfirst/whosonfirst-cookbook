##What is a Significant Event?

As the world is in a state of constant change, Who's On First (WOF) records are constantly changing, too. With most record changes, a simple property update and update to the`wof:lastmodified` property field is sufficient. However, if a **Significant Event** takes place, additional work is needed. 

So, what exactly is a **Significant Event** and how is it defined?

- Changing a point feature's location more than 10km
- Changing a polygon feature's area more than 50
- Changing a feature's `wof:name` without storing the original `wof:name` as an alternative name
- Changing a feature's `wof:name` due to the original `wof:name` being wrong to begin with
- Giving a feature a new `wof:parent_id`
- Giving a feature a new `wof:placetype`
- Updating a feature's `wof:hierarchy` to include an updated `wof:id`
- Replacing or superseding a record (end of life event)

If a WOF record is updated due to a **Significant Event**, the following work is required:

- The feature's raw data (GeoJSON) should be duplicated into a new feature with a new `wof:id`.
- The newly duplicated feature receives a `wof:supersedes` value equal to that of the existing feature's `wof:id`.
- The existing feature receives a `wof:superseded_by` value equal to that of the new feature's `wof:id`.
- The existing feature receives a `mz:is_current` value equal to `0`.
- If the existing feature was never correct to begin with, it will receive a new date _(YYYY-MM-DD)_ in the `edtf:deprecated` property. Otherwise, the `edtf:cessation` property will be given a date _(YYYY-MM-DD)_. This `edtf` date should equal the date when the feature was edited.

It is important to note that this list, as written today, may be incomplete or unable to capture the subtleties and demands of real-life. Additionally, we expect a decent amount of churn in Who's On First during the early days of the project which may require us to bend the rules in certain cases. However, this churn should settle as the database grows in size and allow us to possibly refine these rules.

Our [Who's On First Life Cylce Document](https://github.com/whosonfirst/whosonfirst-cookbook/blob/master/definition/wof:id_lifecycle.md) has more detailed information about **Significant Events** in relation to the `wof:id`.

Questions? Drop us an [email](stephen.epps@mapzen.com).
