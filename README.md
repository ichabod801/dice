# Code and Data for Ichabod's Dice Collection

This is Python code and some data related to my dice collection. Much of this is going to change moving forward. When I got to 2,000 dice I decided to roll them all. When I rolled them all I discovered that I actually have 2,058 dice. So I need to redo the database, which will be a sizeable project in and of itself. But I haven't even figured out how I want to do that yet.

Details on the individual files are below.

## `__init__.py`

This is a command-line interface for maintaining the database recording my dice collection. It's based on cmdr.py, which is my extension of cmd.py, and which is not up on Github. If you are really that interested, contact me.

## dice.dat

This is the data file for my dice collection database. The format is a Die ID string and a count of dice matching that string, separated by a tab. The format for the Die ID string is CCCZSSSFFFBB, with the parts being:

* CCC: A three letter alphabetic code for the color.
* Z: A one letter alphabetic code for the size of the die.
* SSS: A three digit number of sides for the die.
* FFF: A three digit number of unique faces for the die.
* BB: A two digit numbe of the binary flags for the die (special symbol for 1 or N, odd material, odd shape, not pips or standard numbers, not numbered 1 to N)

For more details, see the constants in the `__init__.py` file.

I don't have a lot of faith in this file any more. And, yeah, I probably could have used SQLite or something similar for this. But programming is no fun if you don't get to constantly reinvent the wheel.

## dice_xl.dat

This is the original data file converted from the Excel spreadsheet I used to store the data in.

## filter_funcs.py

These are functions used by `__init__.py` for filtering the collection.

## roll_check.py

These are functions for cleaning the data for rolling all the dice and generating summary statistics based on those rolls.

## rolls_alpha.py

This is the data for the non-numeric rolls. It's tab delimited. The first field is the text rolled or a description of the symbol rolled. The second field is how many times that was rolled *at the same time*. The dice were generally rolled in handfuls, so the same result can come up multiple times in different handfuls.

## rolls_numeric.py

This is the data for the numeric rolls. It's tab delimited, with the first field the number rolled and the second number the number of times it was rolled *at the same time*. The dice were generally rolled in handfuls, so the same result can come up multiple times in different handfuls.