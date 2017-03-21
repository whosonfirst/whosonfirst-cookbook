# What is Required for S3 Import Files?

While we can never account for all edge cases, we _can_ develop an import strategy for the majority of issues.

Here is a brief rundown of what is required of `.geojson` files placed in the `whosonfirst.mapzen.com` S3 misc folder:

## We must **always** have the following attributes:

* **id**: _(`wof:id`)_
* **placetype**: _(`wof:placetype`)_
* **name**: _(`wof:name`)_
* **country**: _(ideally: `iso:country` / otherwise: `wof:country`)_
* **parent_id**: _(`wof:parent_id`)_

## We should **not** include the following:

* **Un-prefixed attribute headings** _(ex: `name`, `parent`, or `id`)_
* **Descendant ids** _(we don’t need to include child ids)_

## For one-off parenting issues:

If a record has more than one parent record, include one of the following values:

  * **`-1`** _(unknown, needs review)_
  * **`-2`** _(shrug, really complicated)_
  * **`-3`** _(contested, but not disputed.. used for placetypes below the locality level)_
  * **`-4`** _(multiple "legal" parents.. used for placetypes at the locality level or above)_
