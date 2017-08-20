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
	print('\nenter path to replace "' + include_path + '" in "' + os.path.relpath(file_path) + '":')
	print('(press enter to leave unchanged)')
	val = input('path: ')
	if val.strip() == '':
		print('leaving unchanged\n')
		return None
	else:
		print('')
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
	print('\nselect header to replace "' + include_path + '" in "' + os.path.relpath(file_path) + '":')
	rel_options = [ os.path.relpath(i, file_path) for i in options]
	print('  0: ' + include_path + ' (unchanged)')
	for i in range(0, len(rel_options)):
		print('  ' + str(i + 1) + ': ' + rel_options[i])
	print('  ' + str(len(rel_options) + 1) + ': [show all headers]')
	print('  ' + str(len(rel_options) + 2) + ': [enter other]')
	val = input('enter selection: ')
	if val == 'q':
		print('aborted')
		exit(0)
	try:
		val = int(val) - 1
	except ValueError:
		print('leaving unchanged\n')
		return None
	print('')
	if val == -1:
		return None
	elif val >= 0 and val < len(rel_options):
		return rel_options[val]
	elif val == len(rel_options):
		return get_any_header_from_user(file_path, include_path, headers)
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
			return get_choice_from_user(file_path, include_path, headers[name], headers) if not automatic else None
		else:
			new = os.path.relpath(headers[name], os.path.dirname(file_path))
			return new if new != include_path else None
	else:
		new = get_any_header_from_user(file_path, include_path, headers) if not automatic else None
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
			if not quiet:
				print('replacing \'' + sections[i] + '\' with \'' + fixed + '\'')
			sections[i] = fixed
		sections[i] = '#include "' + sections[i] + '"'
		i += 2
	return ''.join(sections) if fixed_something else None

def get_all_sources(base):
	return get_all_files_with_extension(base, source_ext)

def prompt_for_file(path):
	print('\nsave changes to \'' + os.path.relpath(path) + '\'? (Yes, No, YYes to all, Quit)')
	val = input('[Y/n/yy/q]: ').lower()
	print('')
	if val == '' or val == 'y' or val == 'yes':
		return True
	elif val == 'n' or val == 'no':
		return False
	elif val == 'yy' or val == 'yes to all':
		global warn
		warn = False
		return True
	elif val == 'q' or val == 'quit':
		print('aborted')
		exit(0)
	else:
		print('please enter y, n, a or q')
		return prompt_for_file(path)

def fix_file(path, headers):
	if not quiet:
		print('checking \'' + os.path.relpath(path) + '\'')
	f = open(path, 'r')
	text = f.read()
	f.close()
	fixed_text = fix_text(path, text, headers)
	if fixed_text != None:
		if not warn or automatic or prompt_for_file(path):
			if not quiet:
				print('saving changes')
			f = open(path, 'w')
			f.write(fixed_text)
			f.close()
		elif not quiet:
			print('changes not saved')

def show_help():
	print('Include Fixer - a tool for automatically fixing broken #includes in C and C++ code')
	print('usage: include_fixer [options] [root directory]')
	print('options:')
	print('-h    - show this help info')
	print('-q    - quiet mode')
	print('-a    - automatic mode (don\'t prompt for input)')
	print('WARNING: this script will permanently modify files in the base directory and sub directories. it is highly recommended that you back up your code before running it.')

def parse_args():
	global base_path
	for i in range(1, len(sys.argv)):
		arg = sys.argv[i]
		if arg == '-h' or arg == '--help':
			show_help()
			exit(0)
		elif arg == '-q':
			global quiet
			quiet = True
		elif arg == '-a':
			global automatic
			automatic = True
		elif arg.startswith('-'):
			print('invalid arg \'' + arg + '\'')
			show_help()
			exit(-1)
		else:
			if base_path == None:
				base_path = arg
			else:
				print('can not have multiple base paths')
				exit(-1)
	if base_path == None:
		base_path = '.'
	base_path = os.path.abspath(base_path)
	#if os.path.relpath(os.path.dirname(sys.argv[0])) == os.path.relpath(base_path):
	#	global warn
	#	warn = False

def warn_at_start():
	if warn and not automatic:
		print('WARNING: this script will permanently modify files in \'' + base_path + '\' and sub directories.\nit is highly recommended that you back up your code before running it.')
		print('(this warning is disabled if this script is located in the project root)')
		val = input('continue? [Y/n]: ')
		if val != '' and val != 'Y' and val != 'y':
			print('aborted')
			exit(0)


parse_args()

if not quiet:
	print('detecting files...')

headers = get_header_dict(base_path)
sources = get_all_sources(base_path)

if not quiet:
	print('found ' + str(len(headers)) + ' headers and ' + str(len(sources) - len(headers)) + ' implementation files')

# this is no longer needed because now it prompts for every file
#warn_at_start()

for i in get_all_sources(base_path):
	fix_file(i, headers)

if not quiet:
	print('task complete, exiting.')
