# ex-chartbeat1
Chartbeat REST API extractor (Keboola Connection)

API documentation: http://support.chartbeat.com/docs/api.html 

This extractor is not public, to find it just put /kds.ex-cxense to the end of url (for example: https://connection.eu-central-1.keboola.com/..../extractors/kds.ex-chartbeat1)

## Configuration:

{
- "host": " ",
- "#apikey": " ",
- "user_id": " ",
- "limit": " ",
- "start": " ",         
- "end": " ",
- "metrics": " ",
- "subdomain": " ",
- "dimensions": "dimension1,dimension2,dimension3...",
- "tz": " ",
- "sort_column": " ",
- "sort_order": " ",
- "primary_key": [" "],
- "table_name": " "
}

## Configuration description:
* "host" - Host Domain, which is associated with Chartbeat account (_sf_async_config.domain);

* "#apikey" - API Key (get it here: https://chartbeat.com/signin/?next=/publishing/settings/api-keys/);

* "user_id" - an individual login seat’s user id number;

* "limit" - page limit (10 by default);

* "start", "end" - for "start" and "end" parameters it is important to insert numbers. For example "start": "-1", "end": "0" = download data from yesterday till today;

* "metrics" - custom metrics;

* "subdomain" - subdomain;

* "dimensions" - a filter, which allows to specify a needed variable;

* "tz" - timezone;

* "sort_column" - to sort the report by metric or dimension (must be paired with a "sort_order");

* "sort_order" - to sort by asc or desc;

* "primary_key" - PK or PKs of table in Keboola;

* "table_name" - table name.
