---
layout: page
category: blog
title: Concordances with Wikipedia data
excerpt: Collecting and analyzing Wikipedia data to extract useful information.
image: https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/Image.PNG
authors: [okavvada]
tags: [data, whosonfirst]
---

![Wikipedia Concordances Main Image](https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/Image.PNG)
_Photo Illustration:
[Mapzen](https://mapzen.com/)_

_Photo Credit: 
[Wikipedia](https://www.wikipedia.org/), [Stay Connected](https://theinnovationenterprise.com/summits/global-sports-innovation-summit-boston/stay-connected)_

We recently [tweeted](https://twitter.com/alloftheplaces/status/748202320677109760) that Who's on First was holding hands with Wikipedia entries. Today we will talk about who that work was completed.

Our vision is to be able to make a unique connection between our [Who's on First](https://whosonfirst.mapzen.com/) data and the corresponding Wikipedia page. Who's on First is our own gazetteer of places, where all the data have a unique identifier number and a list of properties. We use Who's on First data for many Mapzen services as it can provide the **labelling**, **searching** and **browsing** capabilities.

Wikipedia is an internet encyclopedia which is collaboratively built by its users. It is currently a huge source of information as it involves more than 5,000,000 articles covering many subjects and disciplines. The benefit of Wikipedia is that it has come to be one of the most popular websites, constantly evolving and one of the largest general reference works. Making our Who's on First data able to connect to the large pool of information in Wikipedia and to allow the two datasets to “hold hands” has added benefit to our maps as you can now view interesting Wikipedia information as you browse through our map. 

A map is essentially a compilation of a variety of data; Having good quality data on a map might seem obvious but it is a struggle to provide quality control and updates, especially when working with open data. 
 
 
### Wikipedia Structure
The first step is to understand the structure of Wikipedia’s database. Wikipedia has a web service [API](http://readwrite.com/2013/09/19/api-defined/) that provides access to its main wiki features, data and meta-data, namely the [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page). An API is essentially a tool that allows applications to talk to each other in a structured way.

To make things a little more helpful (or complicated! (your choice)), Wikipedia has a separate project called [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) that acts as a central storage space (secondary database) for all the structured data Wikipedia handles. We are introducing Wikidata as in this structured data format, each Wikipedia entry (you can think of this as a Wikipedia page) is assigned a unique number which is extremely helpful as it provides a connection between all the different Wikipedia's (country specific, and they are a lot… 282 of them!). For example, [Spain](https://en.wikipedia.org/wiki/Spain) would be the English Wikipedia page for Spain and [España](https://es.wikipedia.org/wiki/Espa%C3%B1a) would be the Spanish version of the same city. As a result, in order to find the specific city in the Wikipedia of your choice, you would need to know the language initials of the Wikipedia page along with the title of the page in that language. 

To concentrate all the information from the different Wikipedia's on a single Who's on First entry, the `Wikidata ID` number is required. This value would point to the Wikidata web page which for the Spain example would be [Spain](http://www.wikidata.org/wiki/Q29) and would have entries for both of the articles mentioned above. As you can imagine, in the map making world, where it involves information from many different countries and in many different languages having a uniquely identifiable number for each entry is highly valuable.


###Wikipedia Titles
The ultimate goal of this work was to find a way to connect our data with Wikipedia and extract useful information from Wikipedia for each of our entries. We wanted to get the original Wikipedia titles of our places (for example the borough that is called “Bronx” in our database is named “The Bronx” in Wikipedia or “Queenstown” locality is named “Queenstown, New Zealand” in Wikipedia etc), the Wikidata ID of each entry, the Wikipedia url and all the localized language translations of each place. In addition, we wanted to get population data for the administrative places, elevation from the sea level, area and latitude and longitude coordinates. The entire code structure can be found in this [Repository](https://github.com/mapzen-data/wikipedia-notebooks).

The first step of making the concordance with Wikipedia data was to identify a connection point. Wikipedia allows you to search its database for a place name and returns the closest Wikipedia page title. We used this API query to identify the potential original Wikipedia page title for all the administrative places in our database using the Who's on First name as the key input argument. 

A sample python request using the <code>requests</code> python package for the original Wikipedia titles (`wk:page`) is shown below:
    request_API = ("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&srprop=title&srlimit=1&format=json" %name)
    result_request=requests.get(request_API)

This worked relatively well but as you can imagine for the ambiguous cases, where multiple results could match, Wikipedia sometimes returned page titles that were not the ones we were looking for. We looked through the results and applied several cleanup steps to identify which ones were correct and which ones were not. 

In the table below you can see a selected subset of the results that we got from Wikipedia `wk:page` for each Who's on First `name`. 

<img width="480" alt="Subset of original Wikipedia concordances" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/original.png">
<p class='caption'>Subset of original Wikipedia concordances.</p>

We used several approaches to sanity check the results and only keep the correct ones so we would not input wrong Wikipedia concordances to our Who's on First database. This involved a classification process of all entries to whether we thought of the result name matched the input name. The entire code for the data clean up can be found in the [IPython notebook](https://github.com/mapzen-data/wikipedia-notebooks/blob/master/Jupyter_notebooks_with_analysis/Find_original_wikipedia_title_and_wordcount.ipynb).

The first approach involved identifying and discarding any Wikipedia titles that were included in a "blacklist". This "blacklist" consisted of page titles that included numbers or any of the words, timeline, birthday, political, environmental or music which would probably point to aggregate Wikipedia pages that were not of interest to us.  This would help eliminate false Wikipedia concordances such as the ones listed below.

<img width="520" alt="Wrong Wikipedia concordances" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/lists_music.png">
<p class='caption'>Wrong Wikipedia concordances.</p>

Another easy fix was to try and find results that were not referring to the same placetype even though their names might match. Such examples would be entries that did not have the word “Airport” or “Facility” in both the input name as well as the returned Wikipedia page. On the other hand, if the words “District” of “Municipality” were included in the returned result, they were classified as correct as we were looking for administrative places. Wikipedia sometimes returned the disambiguation page as a page title result which was disregarded. 

<img width="500" alt="Wikipedia concordances referring to different placetypes" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/airport.png">
<p class='caption'>Wikipedia concordances referring to different placetypes.</p>

For the remaining results, we calculated the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) of the input name and the result name which is a metric for quantifying the difference between two [strings](https://en.wikipedia.org/wiki/String_(computer_science)). This value would be used as a metric for dissimilarities between the two names. To avoid misclassifying occurrences that involved some kind of hierarchical order for example (Scottsville vs. Scottsville, Kentucky), we calculated a separate the Levenshtein distance between the Wikipedia result and the name after joining it with its corresponding region or country. 

The Levenshtein distance metric provided insight on which entries were probably correct, thus their names were as similar as possible. We allowed entries that matched 100% with the Levenshtein distance metric but we were flexible enough to accept up to 30% dissimilarities (see “Tafaraoui Airport” example). Dissimilarities more that 80% of the strings were marked as not correct. Below you can identify some examples that were classified with the use of the Levenshtein distance.

<img width="960" alt="Wikipedia concordances and their Levenshtein distances" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/leve.png">

Each of the Who's on First entries has a placetype associated with it that describes its hierarchy. The semi-automatic classification involved checking for placetypes in the Who's on First data and the results from the Wikipedia page. The placetypes between Who's on First and Wikipedia should match else the Wikipedia title was considered as wrong. In some cases multiple Who's on First entries would share a name but have different placetypes associated with them (see example of China in the table below). For those cases the Wikipedia title was connected to the Who's on First entry with the higher ranking of a placetype in the hierarchy of places (for example, country > locality > neighborhood).

<img width="420" alt="Wikipedia concordances with placetype fixes" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/placetype.png">

The final technique was to manually classify the entries as correct or not by going through the ones not yet classified especially in the areas where we had personal knowledge. The Slavic and Greek languages were classified by hand as it was impossible to find a point of connection between the different alphabets. A snippet of our data and their final classification is shown in the table below. 

<img width="580" alt="Subset of Wikipedia concordances after clean up" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/final.png">

After cleaning up the data gathered from Wikipedia we ended up with about 155,000 of entries with Wikipedia titles classified as correct, 24,000 were uncertain and 81,000 were classified as wrong.

###Wikidata IDs
Having identified the correct Wikipedia page title for most of our entries we then requested the Wikidata ID for each page in our dataset. This returned a unique identifier for each entry that had an original Wikipedia title. These values are extremely useful as they provide a point of connection between all the different Wikipedias in the 282 different languages where the data is stored in a structured way. A sample python request using the <code>requests</code> python package for the Wikidata IDs (`wd:id`) is shown below:

    request_API = ("https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&titles=%s&format=json" %name)
    result_request=requests.get(request_API)

We also requested the word count of each web page from the Wikipedia API. This will help generate a quantifiable metric for assessing the importance of each place and will be described in a future post. A sample python request using the <code>requests</code> python package for the `wordcount` is shown below:

    request_API= ("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&srprop=wordcount&srlimit=1&format=json" %name)
    result_request=requests.get(request_API)

A subset of our Who's on First data with the corresponding Wikidata IDs is shown below.

<img width="620" alt="Wikipedia concordances with Wikidata IDs" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/wd_ids.png">

###Wikipedia languages 
Another important feature we were interested in getting from Wikipedia was different names in many languages  for each WHo's on First place. Wikipedia has been designed in many different languages and also gives aliases to names for localized languages. This information would be valuable on a map and a search engine. Some entries would have many Wikipedia aliases which would mean that consecutive API calls had to be made to get all the aliases for each place as each return only gave us a certain number of aliases at a time. 

The average number of language aliases that each place would have was 15 but some places could have up to 266. A sample python request using the <code>requests</code> python package for the languages is shown below:

    request_API= ("https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=langlinks&format=json" %name)
    result_request=requests.get(request_API)

 See an example of different language aliases below for Yosemite Valley.

<img width="200" alt="Wikipedia languages" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/language.png">

###Wikipedia demographics and location data
For the administrative places, it would be great if we could add more information on population, elevation from sea level and location coordinates. Since this data cannot be directly accessed from the MediaWiki API requests, we used the Wikidata query service through [SPARQL API](https://query.wikidata.org/). By using SPARQL we were able to get population, elevation and location data for some administrative places in Wikipedia.

The bottleneck of this process is that Wikipedia categories are not well defined so it is hard to search for all administrative places as they can be under many different categories. We searched for the most prominent ones like countries, regions, counties, cities, towns, villages, neighborhoods, airports and archaeological sites and then by using the Wikidata IDs joined them to our administrative places in the Who's on First. 

We were able to add population data to about 5,500 of our places, elevation to 10,000 and latitude and longitude to about 26,000. 

<img width="960" alt="Wikipedia concordances with population data" src="https://mapzen-assets.s3.amazonaws.com/images/Wikipedia-data-blog/populations.png">


###We love our data! (but it can always be improved...) 
Wikipedia is a huge source of information and we are proud to have our Who's on First gazetteer "holding hands" with more of it. It is still a work in progress and as new data is coming in we need to update our concordances to stay up to date. You can get a glimpse of the connection with Wikipedia by using our [Spelunker](https://mapzen.com/blog/spelunker-jumping-into-who-s-on-first/). Lists of all the Who's on First places with [concordances](https://whosonfirst.mapzen.com/spelunker/concordances/) for many of the open data projects, with [Wikidata concordances](https://whosonfirst.mapzen.com/spelunker/concordances/wikidata/#6/48.953/26.622) and with [Wikipedia concordances](https://whosonfirst.mapzen.com/spelunker/concordances/wikipedia/#3/63.78/23.49). By using our Wikipedia connection we were able to add additional properties to Who's on First such as preferred names, wikidata ID and links to the Wikipedia url. See [Italy](https://whosonfirst.mapzen.com/spelunker/id/85633253/#5/41.546/12.560), were all the local names are under the tab `names` and the Wikipedia concordances under `wof` - `concordances`. We wish to use this data for other types of analyses as well, such as a ranking method of feature importance to help mapping and search. We will keep you posted!
