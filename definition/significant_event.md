##What is a Significant Event?

As the world is in a state of constant change, Who's on First (WOF) records are constantly changing too. With most record changes, a simple property update and update to the`wof:lastmodified` property is sufficient. However, if a **Significant Event** takes place, additional work is needed. 

You might be asking yourself... what exactly is a **Significant Event**?

**Updates that qualify as a Significant Event:**

- Changes to the `wof:placetype`.
- Changes to the geometry, where more than 50% (area or length) is added or removed.
- Moving a feature's location more than (roughly) ten kilometers or five miles from it's original location.

**Some things that are grey areas:**

- Changing the `wof:parent_id` (updating the hierarchy).
- Disputed areas that are claimed by more than one parent id.
- Geometry changes that are less than 50% (area or length).
- Name changes that change the name, but not the spelling of the name.

If a WOF record is updated due to a **Significant Event**, a new record should be made and the following updates should be made:

#####Existing/Old Record
* Update the old record's `superseded_by` property to include the new record's wof:id.
* Add/update old record's the `edtf:cessation` field with the date of the new record's creation (format: _YYYY-MM-DD_).
* Add a new `"mz:is_current":0,` field (with the 0 value) to each record that was given a date value in the `edtf:cessation` field.

#####New Record
* Update the new record's `supersedes` property to include the old record's wof:id.

Questions? Drop us an [email](stephen.epps@mapzen.com).
