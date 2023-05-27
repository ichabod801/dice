"""
filter_funcs.py

Filter functions for dice.

Functions:
is_odd_sided: Filter function for dice with an odd number of sides. (bool)
is_platonic: Filter function for platonic solids. (bool)
is_standard: Filter function for standard dice. (bool)
"""

def is_odd_sided(die):
	"""Filter function for dice with an odd number of sides. (bool)"""
	return die.sides % 2

def is_platonic(die):
	"""Filter function for platonic solids. (bool)"""
	return die.sides in (4, 6, 8, 12, 20) and not die.odd_shape

def is_standard(die):
	"""Filter function for standard dice. (bool)"""
	value = die.size == 'medium' and die.sides in (4, 6, 8, 10, 12, 20) and not die.odd_shape
	value = value and (die.sides == 10 or not die.odd_face)
	return value
