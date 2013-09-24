# pyjiong

License: GPLv3

A very small python3 module for working with pleco/skritter-style lists and Chinese. Right now there's no setup script so it can't be installed, just copy the pyjiong folder into your working directory.

## Usage

- convert pinyin formats (numbers and tone marks) (tools.py)
- get only chinese characters from a string (tools.py)
- read cedict/unihan files (filesupport.py)
- mix/diff two lists (chlist.py), have a look at the example frequencyHSK to see how to sort a list of HSK words in the order of a frequency list

## Todo

- better tests
- better docs
- more functionality as needed, see ideas ;-)

## Ideas

- make it a python package
- compare lists, get similarity measure
- add support for tatoeba files
- introduce a way to print flashcards/sheets from lists using jinja2 and wkhtmltopdf or other solutions
