import sys
from os.path import dirname, abspath
parent_dir = dirname(abspath(__file__))
if parent_dir not in sys.path:
	sys.path.append(parent_dir)
from . import getData
