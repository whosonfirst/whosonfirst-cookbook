# Assigning Cessation and Deprecated Dates

When updating a record in Who's On First that is no longer current, it is important to differentiate between cessation and deprecated dates. Each have a specific meaning and usage in Who's On First.

## Definitions

### edtf:cessation

An EDTF date string indicating when a place ceased to exist as a political entity or social construct in "popular" culture.

### edtf:deprecated

An EDTF date string indicating when a Who's On First record was officially deprecated, for example if the record references a place considered to be invalid.

## Usage

Let's say we're updating Who's On First neighbourhood records for San Francisco, CA. An existing neighbourhood record could have a geometry that includes areas that are not typically referred to as part of that neighbourhood or an incorrect `wof:placetype`.
In those cases, an `edtf:deprecated` date should be added to the record, as the record was never correct to begin with. 

However, if Who's On First had a record for, say, the Barbary Coast neighbourhood, this record would need an `edtf:cessation` date. 
The difference with the Barary Coast record update is that the Barbary Coast at one point was a valid, known neighbourhood that ceased to exist in time. It was replaced by the neighbourhoods of Chinatown, North Beach, and Jackson Square.

Just because Who's On First decides a record belongs at a different placetype or should have a different geometry, does not mean that the record ceased to exist; it was simply categorized incorrectly.

**Remember**: cessation dates have a specific meaning; it represents the date that a place ceased to exist or was replaced by something else. Deprecated dates should be used when it has been decided that a place was never represented correctly to begin with.

## Simply put...

The `edtf:deprecated` property should be used as a default when updating a record that is no longer current. Use the `edtf:cessation` property only if the record has a "hard" end date.

## See also

- https://github.com/whosonfirst/whosonfirst-dates
