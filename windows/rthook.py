import os
import sys

if getattr(sys, 'frozen', False):
    # Add the _internal directory to PATH
    base_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(base_dir, '_internal')
    if os.path.isdir(internal_dir):
        os.environ['PATH'] = internal_dir + os.pathsep + os.environ.get('PATH', '')
