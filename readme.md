# Include Fixer

Include Fixer is a utility that automatically fixes broken relative #includes in C and C++ source and headers. It makes it easy to reorganize projects large and small without manually changing every relative #include. For example, 

## Usage
```
usage: ./include_fixer.py [options] [root directory]
options:
-h    - show help
-q    - quiet mode
-a    - automatic mode (don't prompt for input)
```

WARNING: this script modifies your files, and so there is a non zero chance it will cause damage due to either defect or user error. It is recommended that you use version control and be especially careful with the `-a` flag, as it will then automatically modify files without prompt.
