#! /bin/python3

import os
import re

header_ext = ['h', 'hpp']
source_ext = ['c', 'cpp', 'h', 'hpp']

def split_ext(path):
	i = path.rsplit('.', 1)
	return (i[0], i[1]) if len(i) == 2 else (i[0], '')

def get_contents_of_dir(base):
	return [ os.path.abspath(os.path.join(base, i)) for i in os.listdir(base) ]

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
		return include_path
	else:
		return val

def get_choice_from_user(file_path, include_path, options):
	print('\nselect path to replace "' + include_path + '" in "' + file_path + '":')
	rel_options = [ os.path.relpath(i, file_path) for i in options]
	print('1. [enter other]')
	print('2. ' + include_path + ' (unchanged)')
	for i in range(0, len(rel_options)):
		print(str(i + 3) + '. ' + rel_options[i])
	val = int(input('enter selection: ')) - 3
	if val == -2:
		return get_path_from_user(file_path, include_path)
	elif val == -1:
		return include_path
	elif val >= 0 and val < len(rel_options):
		return rel_options[val]
	else:
		print('invalid input')
		return get_choice_from_user(file_path, include_path, options)

def fix_include(file_path, include_path, headers):
	name = split_ext(os.path.basename(include_path))[0]
	if name in headers:
		if type(headers[name]) == type([]):
			for i in headers[name]:
				if include_path == i:
					return include_path
			return get_choice_from_user(file_path, include_path, headers[name])
		else:
			return os.path.relpath(headers[name], file_path)
	else:
		return get_path_from_user(file_path, include_path)

def fix_text(file_path, text, headers):
	sections = re.split('#include[\s\t]*\"(.*)\"', text)
	i = 1
	while i < len(sections):
		sections[i] = '#include "' + fix_include(file_path, sections[i], headers) + '"'
		i += 2
	return ''.join(sections)

def get_all_sources(base):
	return get_all_files_with_extension(base, source_ext)

def fix_file(path, headers):
	f = open(path, 'r')
	text = f.read()
	f.close()
	fixed_text = fix_text(path, text, headers)
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
