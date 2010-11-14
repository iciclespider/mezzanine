
import os
import sys

directory = os.path.dirname(os.path.abspath(__file__))
if directory in sys.path:
    sys.path.remove(directory)
directory = os.path.dirname(directory)
if directory in sys.path:
    sys.path.remove(directory)
sys.path.insert(0, directory)

import django
if django.VERSION[0] != 1 or django.VERSION[1] != 2:
    raise Exception('Django version "%s" is not 1.2.' % django.get_version())
import grappelli
if grappelli.VERSION != '2.2':
    raise Exception('Grappelli version "%s" is not 2.2.' % grappelli.VERSION)
