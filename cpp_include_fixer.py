import os

def get_subdirs(base_path):
	contents_list = os.listdir(base_path)
	output_list = []
	for thing in contents_list:
		path = os.path.join(base_path, thing)
		if os.path.isdir(path):
			output_list.append(path)
	return output_list

def get_subdirs_recursive(base_path):
	first_level_subdirs = get_subdirs(base_path)
	all_subdirs = [base_path]
	for i in first_level_subdirs:
		all_subdirs += get_subdirs_recursive(i)
	return all_subdirs

sub_dirs = get_subdirs_recursive('dummy')

print(sub_dirs)

