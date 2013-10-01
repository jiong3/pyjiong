# pyjiong

License: GPLv3

A very small python3 module for working with pleco/skritter-style lists and Chinese. Right now there's no setup script so it can't be installed, just copy the pyjiong folder into your working directory.

## Usage

- convert pinyin formats (numbers and tone marks) (tools.py)
- split pinyin into initial and final sound (tools.py)
- get only chinese characters from a string (tools.py)
- read cedict/unihan/tatoeba files (filesupport.py)
- mix/diff two lists (chlist.py), have a look at the example frequencyHSK to see how to sort a list of HSK words in the order of a frequency list

## Todo

- better tests
- better docs
- more functionality as needed, see ideas ;-)

## Ideas

- make it a python package
- compare lists, get similarity measure
- skritter api?
- introduce a way to print flashcards/sheets from lists using jinja2 and wkhtmltopdf or other solutions
