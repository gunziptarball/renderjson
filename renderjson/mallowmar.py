"""
Mallowmar
=========

I have no idea what else to call this right now.  Brain dump time.  Here's some
stuff to import for these tests

>>> import csv
>>> import tabulate
>>> import yaml
>>> from pprint import pprint

Let's look at a file, delimited with pipes and the first row serving as the
header.

>>> with open('tests/data/cars.txt') as f:
...     source_data = tuple(csv.DictReader(f, delimiter='|'))

It's got some stuff about cars I've owned over the years

>>> print(tabulate.tabulate(source_data[0].items()))
---------  ------------------------
Make       Ford
Model      LTD
Year       1985
Cool Car   Yes
Comment    I miss this car so much.
Year Sold  2018
---------  ------------------------

I want to to take this and convert it into something other than a bunch of
strings.  Something that would look like this
>>> desired_output = {
...     'Comment': 'I miss this car so much.',
...     'Cool Car': True,
...     'Make': 'Ford',
...     'Model': 'LTD',
...     'Year': '1985',
...     'Year Sold': '2018'
... }

So I'm trying to make a function that magically does this based on a JSON Schema
living here...

>>> with open('tests/data/cars-config.yaml') as config_file:
...     schema = yaml.safe_load(config_file)

I've already defined what I want the types to be based on the schema for
validating...but I also want it to drive how it's transformed.

>>> import jsonschema
>>> jsonschema.validate(source_data[0], schema)  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
jsonschema.exceptions.ValidationError: ...nope.

My desired output is valid

>>> jsonschema.validate(desired_output, schema)
>>> actual_output = transform(source_data[0], schema)
>>> from hamcrest import assert_that, has_entries
>>> if actual_output != desired_output:
...     assert_that(actual_output, has_entries(desired_output))
... else:
...     print("Noice!")
Noice!



"""
import typing as t

JSONFriendly = t.Union[str, int, bool, None, t.List["_Simple"], t.Dict[str, "_Simple"]]

_TYPE_MAPPING: t.Dict[str, t.Type] = {
    "string": str,
    "number": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}

_TRU_VALUES = ("Yes", "yes", "True", "true", "1", "Y")


def transform(source_data: JSONFriendly, mallow_config: JSONFriendly) -> JSONFriendly:
    class Properties(t.TypedDict):
        type: str

    # Horrible code to get test to pass
    if mallow_config["type"] != "object" or not isinstance(source_data, dict):
        raise NotImplementedError("only object supported right now")
    properties: t.Dict[str, Properties] = mallow_config["properties"]
    result: t.Dict[str, JSONFriendly] = {}
    for original_key, source_value in source_data.items():

        target_type_name = properties.get(original_key, {"type": "string"})["type"]
        if target_type_name == "boolean":
            result[original_key] = source_value in _TRU_VALUES
        elif target_type_name == "string":
            result[original_key] = source_value
        else:
            raise NotImplementedError(f"Doesn't support {target_type_name}")
    return result
