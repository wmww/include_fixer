#! /bin/python3

import os
import re

header_ext = ['h', 'hpp']
source_ext = ['c', 'cpp', 'h', 'hpp']

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

def get_header_dict(base):
	headers = {}
	for path in get_all_files_with_extension(base, header_ext):
		name = split_ext(os.path.basename(path))[0]
		if name in headers:
			if type(headers[name]) != type([]):
				headers[name] = [headers[name]]
			headers[name].append(path)
		else:
			headers[name] = path
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
		return get_any_header_from_user(file_path, include_path, headers)

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

base = 'dummy'

headers = get_header_dict(base)

for i in get_all_sources(base):
	fix_file(i, headers)

#files = get_all_files_with_extension('dummy', ['h', 'hpp'])

#print(files)

#print(get_header_dict('dummy'))
