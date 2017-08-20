#! /bin/python3

import os
import re
import sys

header_ext = ['h', 'hpp']
source_ext = ['c', 'cpp', 'h', 'hpp']

base_path = None
quiet = False
automatic = False
warn = True

def split_ext(path):
	i = path.rsplit('.', 1)
	return (i[0], i[1]) if len(i) == 2 else (i[0], '')

def get_contents_of_dir(base):
	return [ os.path.abspath(os.path.join(base, i)) for i in os.listdir(base) if not i.startswith('.') ]

def get_subdirs(base):
	return [ i for i in get_contents_of_dir(base) if os.path.isdir(i) ]

def get_all_subdirs(base):
	return [base] + [i for j in get_subdirs(base) for i in get_all_subdirs(j)]
	
def has_extension(base, extensions):
	for extension in extensions:
		if base.endswith(extension):
			return True
	return False

def get_all_files(base):
	return [ path for subdir in get_all_subdirs(base) for path in get_contents_of_dir(subdir) if os.path.isfile(path) ]

def get_all_files_with_extension(base, extensions):
	return [ path for path in get_all_files(base) if has_extension(path, extensions) ]

def add_entry_to_headers(name, path, headers):
	if name in headers:
		if type(headers[name]) != type([]):
			headers[name] = [headers[name]]
		headers[name].append(path)
	else:
		headers[name] = path

def get_header_dict(base):
	headers = {}
	for path in get_all_files_with_extension(base, header_ext):
		name = split_ext(os.path.basename(path))[0]
		add_entry_to_headers(name, path, headers)
	return headers

def get_path_from_user(file_path, include_path):
	print('\nenter path to replace "' + include_path + '" in "' + file_path + '":')
	print('(press enter to leave unchanged)')
	val = input('path: ')
	if val.strip() == '':
		print('leaving unchanged\n')
		return None
	else:
		print('\n')
		return val

def get_any_header_from_user(file_path, include_path, headers):
	all_headers = []
	for key, val in headers.items():
		if type(val) == type([]):
			all_headers += val
		else:
			all_headers.append(val)
	return get_choice_from_user(file_path, include_path, all_headers, headers)

def get_choice_from_user(file_path, include_path, options, headers):
	print('\nselect header to replace "' + include_path + '" in "' + file_path + '":')
	rel_options = [ os.path.relpath(i, file_path) for i in options]
	print('  0: ' + include_path + ' (unchanged)')
	for i in range(0, len(rel_options)):
		print('  ' + str(i + 1) + ': ' + rel_options[i])
	print('  ' + str(len(rel_options) + 1) + ': [show all headers]')
	print('  ' + str(len(rel_options) + 2) + ': [enter other]')
	try:
		val = int(input('enter selection: ')) - 1
	except ValueError:
		print('leaving unchanged\n')
		return None
	print('')
	if val == -1:
		return None
	elif val >= 0 and val < len(rel_options):
		return rel_options[val]
	elif val == len(rel_options):
		get_any_header_from_user(file_path, include_path, headers)
	elif val == len(rel_options) + 1:
		return get_path_from_user(file_path, include_path)
	else:
		print('invalid input')
		return get_choice_from_user(file_path, include_path, options, headers)

def fix_include(file_path, include_path, headers):
	name = split_ext(os.path.basename(include_path))[0]
	if name in headers:
		if type(headers[name]) == type([]):
			for i in headers[name]:
				if os.path.relpath(i, file_path) == include_path:
					return None
			return get_choice_from_user(file_path, include_path, headers[name], headers)
		else:
			new = os.path.relpath(headers[name], file_path)
			return new if new != include_path else None
	else:
		new = get_any_header_from_user(file_path, include_path, headers)
		if new != None:
			add_entry_to_headers(name, new, headers)
		return new

def fix_text(file_path, text, headers):
	sections = re.split('#include[\s\t]*\"(.*)\"', text)
	fixed_something = False
	i = 1
	while i < len(sections):
		fixed = fix_include(file_path, sections[i], headers)
		if fixed != None:
			fixed_something = True
			sections[i] = fixed
		sections[i] = '#include "' + sections[i] + '"'
		i += 2
	return ''.join(sections) if fixed_something else None

def get_all_sources(base):
	return get_all_files_with_extension(base, source_ext)

def fix_file(path, headers):
	f = open(path, 'r')
	text = f.read()
	f.close()
	fixed_text = fix_text(path, text, headers)
	if fixed_text != None:
		f = open(path, 'w')
		f.write(fixed_text)
		f.close()

def show_help():
	print('Include Fixer - a tool for automatically fixing broken #includes in C and C++ code')
	print('usage: include_fixer [options] [root directory]')
	print('options:')
	print('-h    - show this help info')
	print('-q    - quiet mode')
	print('-a    - automatic mode (don\'t prompt for input)')
	print('WARNING: this script will permanently modify files in the base directory and sub directories. it is highly recommended that you back up your code before running it.')

def parse_args():
	if os.path.relpath(os.path.dirname(sys.argv[0])) == '.':
		global warn
		warn = False
	for i in range(1, len(sys.argv)):
		arg = sys.argv[i]
		if arg == '-h' or arg == '--help':
			show_help()
			exit(0)
		elif arg == 'q':
			global quiet
			quiet = True
		elif arg == 'a':
			global automatic
			automatic = True
		elif arg.startswith('-'):
			print('invalid arg \'' + arg + '\'')
			show_help()
			exit(-1)
		else:
			global base_path
			if base_path == None:
				base_path = arg
			else:
				print('can not have multiple base paths')
				exit(-1)
	if base_path == None:
		base_path = '.'

parse_args()

base_path = os.path.abspath(base_path)

if not quiet:
	print('detecting files...')

headers = get_header_dict(base_path)
sources = get_all_sources(base_path)

if not quiet:
	print('found ' + str(len(headers)) + ' headers and ' + str(len(sources) - len(headers)) + ' implementation files')

if warn:
	print('WARNING: this script will permanently modify files in \'' + base_path + '\' and sub directories.\nit is highly recommended that you back up your code before running it.')
	print('(this warning is disabled if this script is located in the project root)')
	val = input('continue? [Y/n]: ')
	if val != '' and val == 'Y' and val == 'y':
		print('aborted')
		exit(0)

for i in get_all_sources(base_path):
	fix_file(i, headers)

