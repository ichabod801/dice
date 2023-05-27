"""
__init__.py

The interface for tracking my dice collection.

Constants:
COLORS: The color abbreviations used in the codes. (dict of str: str)
FLAG_MENU: The lines for menu choices about flags. (tuple of str)
FLAGS: The names of the flag features of the dice. (tuple of str)
SIZES: The size abbreviations used in the codes. (dict of str: str)

Classes:
Die: A unique die type within the collection. (object)
Lou: An interface for tracking my dice collection. (cmdr.Cmdr)

Functions:
encode: Translate the features of a die to a code for the die. (str)
go: Run the dice collection interface. (Lou)
"""

import collections
import os

import cmdr
import ick_text as txt

from . import filter_funcs

COLORS = {'BLA': 'black', 'BLU': 'blue', 'BRA': 'brass', 'BRO': 'brown', 'GOL': 'gold', 'GRA': 'gray', 
	'GRE': 'green', 'OFF': 'off white', 'ORA': 'orange', 'OTH': 'other', 'PIN': 'pink', 'PUR': 'purple', 
	'RED': 'red', 'SIL': 'silver', 'TAN': 'tan', 'TRA': 'transparent', 'WHI': 'white', 'YEL': 'yellow'}

FLAG_MENU = ('A: Faces that are not 1 to {0}.', 'B: Faces that are 1-{0} but not pips or arabic numerals.',
	'C: A non-standard shape.', 'D: A material besides plasic or resin.', 
	'E: Different symbols for the 1 or the {0}.')

FLAGS = ('art_pip', 'material', 'odd_shape', 'odd_pip', 'odd_face')

SIZES = {'S': 'small', 'M': 'medium', 'L': 'large', 'H': 'huge', 'G': 'gigantic'}

class Die(object):
	"""
	A unique die type within the collection. (object)

	Attributes:
	art_pip: A flag for unusual max and/or min pip. (bool)
	code: The code storing the die's features. (str)
	color: The color of the die. (str)
	count: The number of dice of this type. (int)
	faces: The number of unique faces on the die. (int)
	material: A flag for a non-plastic material. (bool)
	odd_face: A flag for the faces not being 1 to the number of sides. (bool)
	odd_pip: A flag for pips that are not dots or numbers. (bool)
	odd_shape: A flag for a non-platonicish shape. (bool)
	sides: The number of sides on the die. (int)
	size: The size of the die. (str)

	Methods:
	table_row: A text representation where everything lines up in columns. (str)

	Overridden Methods:
	__init__
	__add__
	__radd__
	__repr__
	__str__
	"""

	def __init__(self, code, count):
		"""
		Parse the die data. (None)

		Parameters:
		code: The code storing the die's features. (str)
		count: The number of dice of this type. (int)
		"""
		# Store the given parameters
		self.code = code
		self.count = count
		# Parse the code.
		self.color = COLORS[code[:3]]
		self.size = SIZES[code[3]]
		self.sides = int(code[4:7])
		self.faces = int(code[7:10])
		flags = int(code[-2:])
		for power, attribute in enumerate(FLAGS):
			setattr(self, attribute, bool(flags & (2 ** power)))

	def __add__(self, other):
		"""
		Addition by count. (int)

		Parameters:
		other: The item to add to. (Die or int)
		"""
		if isinstance(other, Die):
			return self.count + other.count
		elif isinstance(other, int):
			return self.count + other
		else:
			return NotImplemented

	def __radd__(self, other):
		"""
		Right-handed addition by count. (int)

		Parameters:
		other: The item to add to. (Die or int)
		"""
		return self + other

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return f'Die({self.code!r}, {self.count})'

	def __str__(self):
		"""Human readable text representation. (str)"""
		text = f'{self.size} {self.color} d{self.sides}'
		if self.faces != self.sides:
			text = f'{text}/{self.faces}'
		flags = [flag.replace('_', ' ') for flag in FLAGS if getattr(self, flag)]
		if flags:
			text = '{} ({})'.format(text, ', '.join(flags))
		return text

	def data(self):
		"""Data storage text representation. (str)"""
		return '{}\t{}\n'.format(self.code, self.count)

	def table_row(self):
		"""A text representation where everything lines up in columns. (str)"""
		text = f'{self.count:<3} {self.size:<8} {self.color:<11} d{self.sides:<3}/d{self.faces:<3}'
		flag_bits = [flag.replace('_', ' ') if getattr(self, flag) else ' ' * len(flag) for flag in FLAGS]
		text = '{} {}'.format(text, ' '.join(flag_bits))
		return text

class Lou(cmdr.Cmdr):
	"""
	An interface for tracking my dice collection. (cmdr.Cmdr)

	Attributes:
	changes: What changes have been made to the data. (str)
	current: The current subset of the whole collection. (list of Die)
	dice: The dice in the collection. (list of Die)
	loc: The file system location of this file. (str)
	new_rows: Any new rows added to the data. (list of Die)
	subsets: Temporarily stored subsets of the dice. (dict of str: list)

	Class Attributes:
	filter_funcs: Functions for filtering dice. (dict of str:callable)

	Methods:
	do_add: Add dice to the collection. (None)
	do_add7: Add a standard seven die set to the collection. (None)
	do_count: Count the current subset of dice by a feature of those dice. (None)
	do_load: Load a previously stored subset. (None)
	do_quit: Leave the dice collection interface. (True)
	do_save: Save the current collection. (None)
	do_store: Store the current subset. (None)
	do_subset: Make a subset of the current set of dice. (sub)
	do_table: Print a table of the current subset. (None)
	filter: Filter a set of dice. (list of Die)
	load_data: Load the stored dice data. (None)
	print_count: Print the count of the current subset. (None)

	Overridden Methods:
	__repr__
	preloop
	"""

	aliases = {'q': 'quit', 'sub': 'subset'}
	prompt = 'DICE:: '

	def __repr__(self):
		"""Debugging text representation. (str)"""
		return '<In honor of Lou Zocchi>'

	def do_add(self, arguments):
		"""
		Add dice to the collection.

		Small: Noticeably smaller than standard
		Medium: Standard Size
		Large: Larger than Standard d20, but rollable
		Huge: Too big to roll reasonably
		Gargantuan: Just silly
		"""
		# Get the dice features from the user.
		color = txt.input_menu('What color are the dice? ', list(COLORS.values()))
		size = txt.input_menu('What size are the dice? ', list(SIZES.values()))
		sides = txt.input_int('How many sides do the dice have? ', low = 1)
		face_query = f'How many unique faces do the dice have (return for {sides})? '
		faces = txt.input_int(face_query, low = 1, default = sides)
		# Get the flags with one input.
		menu = '\n'.join(FLAG_MENU).format(sides)
		while True:
			print(menu)
			choices = input('Enter any of the above items that fit the dice: ')
			try:
				flags = sum([2 ** 'abcde'.index(letter) for letter in choices.lower()])
			except IndexError:
				print('Please only enter the letters A throug E.')
			else:
				break
		# Get the quantity from the user.
		count = txt.input_int('How many of these dice are you adding to the collection? ', low = 1)
		# Get the code for the dice to be entered.
		code = encode(color, size, sides, faces, flags)
		# Look for matching dice already in the collection.
		matches = [die for die in self.dice if die.code == code]
		# Enter the dice.
		if matches:
			matches[0].count += count
			self.changes = True
		else:
			self.dice.append(Die(code, count))
			self.new_rows.append(self.dice[-1])
		# Let the user know the updated count.
		print()
		print(f'You now have {sum(self.dice)} dice.')

	def do_add7(self, arguments):
		"""
		Add a standard seven die set to the collection.
		"""
		# Get the dice color from the user.
		color = txt.input_menu('What color are the dice? ', list(COLORS.values()))
		for sides in (4, 6, 8, 10, 100, 12, 20):
			# Get the code for the dice to be entered.
			if sides == 100:
				code = encode(color, 'M', 10, 10, 16)
			else:
				code = encode(color, 'M', sides, sides, 0)
			# Look for matching dice already in the collection.
			matches = [die for die in self.dice if die.code == code]
			# Enter the dice.
			if matches:
				matches[0].count += 1
				self.changes = True
			else:
				self.dice.append(Die(code, 1))
				self.new_rows.append(self.dice[-1])
		# Let the user know the updated count.
		print()
		print(f'You now have {sum(self.dice)} dice.')

	def do_count(self, arguments):
		"""
		Count the current subset of dice by a feature of those dice.

		The argument is a feature of the dice: color, size, sides, faces, odd-face, 
		odd-pip, odd-shape, material, or art-pip.
		"""
		# Parse the arguments.
		feature = arguments.lower().replace('-', '_')
		# Validate the feature.
		try:
			getattr(self.current[0], feature)
		except AttributeError:
			print(f'Invalid die feature: {arguments!r}.')
			return
		# Calculate the counts.
		counts = collections.defaultdict(int)
		for die in self.current:
			value = getattr(die, feature)
			counts[value] += die.count
		# Display the counts.
		max_len = max([len(str(value)) for value in counts.keys()])
		template = '{{:>{}}} {{}}'.format(max_len)
		for value, count in counts.items():
			print(template.format(value, count))

	def do_load(self, arguments):
		"""
		Load a previously stored subset.

		The argument is the name of the subset to be loaded. Using the argument 'all'
		will load all of the dice.
		"""
		if arguments.lower() == 'all':
			self.current = self.dice[:]
		else:
			self.current = self.subsets[arguments]
		self.print_count()

	def do_quit(self, arguments):
		"""
		Leave the dice collection. (q)
		"""
		if self.changes or self.new_rows:
			if txt.input_yes_no('Changes to the collection have been made. Do you wish to save them? '):
				self.do_save('')
		return True

	def do_save(self, arguments):
		"""
		Save the current collection.
		"""
		if self.changes:
			with open(os.path.join(self.loc, 'dice.dat'), 'w') as dice_file:
				for die in self.dice:
					dice_file.write(die.data())
			self.changes = False
			rows = len(self.dice)
			s = '' if rows == 1 else 's'
			print(f'{rows} row{s} were written to the stored data.')
		elif self.new_rows:
			rows = len(self.new_rows)
			with open(os.path.join(self.loc, 'dice.dat'), 'a') as dice_file:
				while self.new_rows:
					dice_file.write(self.new_rows.pop().data())
			s = '' if rows == 1 else 's'
			print(f'{rows} row{s} were added to the stored data.')
		else:
			print('No changes have been made to the collection.')

	def do_store(self, arguments):
		"""
		Store the current subset.

		Stored subsets are discarded when this system is closed.
		"""
		self.subsets[arguments] = self.current

	def do_subset(self, arguments):
		"""
		Make a subset of the current set of dice. (sub)

		Use color, flag, or size words to subset by color or size, dX to subset by X 
		sides, and fX to subset by X unique faces.
		"""
		self.current = self.filter(self.current, arguments)

	def do_table(self, arguments):
		"""
		Print a table of the current subset.
		"""
		for die in self.current:
			print(die.table_row())

	def filter(self, base, arguments):
		"""
		Filter a set of dice. (list of Die)

		Parameters:
		base: The set of dice to filter. (list of Die)
		arguments: The criteria for filtering the dice. (str)
		"""
		# Run the filters
		output = base[:]
		for word in arguments.lower().split():
			# Handle aliases from the code.
			word = COLORS.get(word.upper(), word)
			word = SIZES.get(word.upper(), word)
			# Filter the basic attributes.
			if word in COLORS.values():
				output = [die for die in output if die.color == word]
			elif word in SIZES.values():
				output = [die for die in output if die.color == word]
			elif word.startswith('d') and word[1:].isnumeric():
				output = [die for die in output if die.sides == int(word[1:])]
			elif word.startswith('f') and word[1:].isnumeric():
				output = [die for die in output if die.faces == int(word[1:])]
			else:
				# Filter the flag attributes and filter functions.
				flag_word = word.replace('-', '_')
				if flag_word in FLAGS:
					output = [die for die in output if getattr(die, flag_word)]
				elif flag_word[0] == '!' and flag_word[1:] in FLAGS:
					output = [die for die in output if not getattr(die, flag_word[1:])]
				elif flag_word in self.filters:
					output = list(filter(self.filters[flag_word], output))
				else:
					# Print a warning for unrecognized filters.
					print(f'Unrecognized filter criteria: {word}.')
		self.current = output
		self.print_count()
		return output

	def load_data(self):
		"""Load the stored dice data. (None)"""
		self.dice = []
		with open(os.path.join(self.loc, 'dice.dat')) as dice_file:
			for line in dice_file:
				code, count = line.split('\t')
				self.dice.append(Die(code, int(count)))
		self.dice.sort(key = lambda die: die.code)

	def preloop(self):
		"""Prepare the command loop. (None)"""
		self.loc = os.path.dirname(os.path.abspath(__file__))
		self.load_data()
		self.current = self.dice[:]
		self.subsets = {}
		self.filters = {name[3:]: func for name, func in filter_funcs.__dict__.items() if callable(func)}
		print('Welcome to your dice collection.')
		print(f'You have {sum(self.dice)} dice.')
		print()
		self.changes = False
		self.new_rows = []

	def print_count(self):
		"""Print the count of the current subset. (None)"""
		total = sum(self.current)
		to_be = 'is' if total == 1 else 'are'
		d_word = 'die' if total == 1 else 'dice'
		print(f'There {to_be} {total} {d_word} in the current subset.')

def encode(color, size, sides, faces, flags):
	"""
	Translate the features of a die to a code for the die. (str)

	Parameters:
	color: The color of the die. (str)
	size: The size of the die. (str)
	sides: The number of sides on the die. (int)
	faces: The number of unique faces on the die. (int)
	flags: The binary flags for the die. (int)
	"""
	# Get the color code.
	color_code = color[:3].upper()
	if color_code not in COLORS:
		raise ValueError(f'Cannot encode the color {color!r}.')
	# Get the size code.
	size_code = size[0].upper()
	if size_code not in SIZES:
		raise ValueError(f'Cannot encode the size {size!r}.')
	# Generate the code.
	return f'{color_code}{size_code}{sides:03}{faces:03}{flags:02}'

def go():
	"""Run the dice collection interface. (Lou)"""
	lou = Lou()
	lou.cmdloop()
	return lou
