#! /bin/python3

# this may or may not work, was based on the include fixer code, I think it is supposed to recursivly open all code files and find text in them

import os
import re
import sys

# all the file types that may have code
code_ext = [
	'c', 'cpp', 'h', 'hpp', # C based
	'rs', 'java', 'swift', # compiled
	'py', 'sh', 'js', # scripting
	'md', 'txt', 'htm', 'html', 'css', # other
]

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
		if base.endswith('.'+extension):
			return True
	return False

def get_all_files(base):
	return [ path for subdir in get_all_subdirs(base) for path in get_contents_of_dir(subdir) if os.path.isfile(path) ]

def get_all_files_with_extension(base, extensions):
	return [ path for path in get_all_files(base) if has_extension(path, extensions) ]

def is_expr_in_file(path, expr):
	try:
		text = open(path).read()
		if expr in text:
			return True
		else:
			return False
	except:
		print('error reading ' + path)

"""
def show_help():
	print('Include Fixer - a tool for automatically fixing broken #includes in C and C++ code')
	print('usage: include_fixer [options] [root directory]')
	print('options:')
	print('-h    - show this help info')
	print('-q    - quiet mode')
	print('-a    - automatic mode (don\'t prompt for input)')
	print('WARNING: this script will permanently modify files in the specified directory and sub directories.\nit is highly recommended that you back up your code before running it.')
"""
"""
def parse_args():
	global base_path
	for i in range(1, len(sys.argv)):
		arg = sys.argv[i]
		if arg == '-h' or arg == '--help':
			show_help()
			exit(0)
		elif arg.startswith('-'):
			print('invalid arg \'' + arg + '\'')
			print('(use -h for help)')
			exit(-1)
		else:
			if base_path == None:
				base_path = arg
			else:
				print('can not have multiple root paths')
				print('(use -h for help)')
				exit(-1)
	if base_path == None:
		#base_path = '.'
		print('please specify a root path')
		print('(use -h for help)')
		exit(-1)
	base_path = os.path.abspath(base_path)
	#if os.path.relpath(os.path.dirname(sys.argv[0])) == os.path.relpath(base_path):
	#	global warn
	#	warn = False
"""

# parse_args()

if len(sys.argv) != 3:
	print('needs 2 args (base path and search term), got ' + str(len(sys.argv) - 1))
	exit(-1)

base_path = sys.argv[1]
search_expr = sys.argv[2]

files = get_all_files_with_extension(base_path, code_ext)

print('found ' + str(len(files)) + ' files, searching...')

for i in files:
	if is_expr_in_file(i, search_expr):
		print(i)

print('task complete, exiting.')
