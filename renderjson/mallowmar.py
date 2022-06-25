"""
Mallowmar
=========

I have no idea what else to call this right now.  Brain dump time.  Here's some
stuff to import for these tests

>>> import csv
>>> import tabulate

Let's look at a file, delimited with pipes and the first row serving
as the header.

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

"""
