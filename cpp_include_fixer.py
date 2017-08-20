import os

def get_contents_of_dir(base_path):
	return [ os.path.join(base_path, i) for i in os.listdir(base_path) ]

def get_subdirs(base_path):
	contents_list = get_contents_of_dir(base_path)
	output_list = []
	for path in contents_list:
		if os.path.isdir(path):
			output_list.append(path)
	return output_list

def get_subdirs_recursive(base_path):
	first_level_subdirs = get_subdirs(base_path)
	all_subdirs = [base_path]
	for i in first_level_subdirs:
		all_subdirs = all_subdirs + get_subdirs_recursive(i)
	return all_subdirs

def path_has_extension(path, extensions):
	for extension in extensions:
		if path.endswith('.' + extension):
			return True
	return False

def get_all_files_with_extension(base_path, extensions):
	dirs = get_subdirs_recursive(base_path)
	out_files = []
	for directory in dirs:
		contents = get_contents_of_dir(directory)
		for i in contents:
			if os.path.isfile(i) and path_has_extension(i, extensions):
				out_files.append(i)
	return out_files
	
files = get_all_files_with_extension('dummy', ['h', 'hpp'])

print(files)
