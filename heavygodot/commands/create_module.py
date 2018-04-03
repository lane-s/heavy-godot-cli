# heavygodot/commands/create_module.py
"""The create_module command."""
 
 
from json import dumps
 
from .base import Base
import os
 
class CreateModule(Base):
    """Create a godot module from the supplied heavy source files"""
 
    def run(self):
        print(self.options)

        file_name = self.options['ZIPPED_HEAVY_SOURCE']
        file_path = os.path.join(os.getcwd(), file_name)
        infile = open(file_path, "r")

        lines = infile.readlines()
        for l in lines:
            print(l)