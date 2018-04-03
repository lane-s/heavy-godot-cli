# heavygodot/commands/wrap.py
"""The wrap command."""
 
 
from json import dumps
 
from .base import Base
import sys
from collections import defaultdict
import os
import zipfile
import shutil
import re
 
class Wrap(Base):

    """Create a godot module from the supplied heavy source files"""
    def run(self):
        self.initialize()
        self.extract_heavy_source()
        self.copy_base_module()
        self.analyze_source()
        self.transform_base_module()
        self.finish()

    PLEASE_INPUT_ZIP_FILE = "Please supply the path to the zipped heavy C++ source code"
    FILE_NOT_FOUND = "Input file not found."
    BAD_ZIP_FILE = "Bad zip file."
    UNEXPECTED_ERROR = "Unexpected error: "
    TEMP_EXISTS = "Temp directory 'module_name' already exists. Please remove and run wrap again"

    DEFAULT_MODULE_DIR_NAME = "heavy_godot_module"
    BASE_MODULE_DIR_NAME = "base_module"
    STUBS_DIR_NAME = "stubs"

    def initialize(self):
        self.variables = defaultdict(str)
        self.var_regex = "\$\((.*?)\)" #Match expressions like '$(var_name)'

        self.base_module_dir = os.path.join(os.path.dirname(__file__), self.BASE_MODULE_DIR_NAME)
        self.stubs_dir = os.path.join(self.base_module_dir, self.STUBS_DIR_NAME) 

    """ Extract the input source files into a new directory """
    def extract_heavy_source(self):
        zipfile_name = self.options['ZIPPED_HEAVY_SOURCE']
        if zipfile_name is None:
            print(self.PLEASE_INPUT_ZIP_FILE)
            return

        self.zipfile_path = os.path.join(os.getcwd(), zipfile_name)
        try:
            zip_ref = zipfile.ZipFile(self.zipfile_path, 'r')
        except FileNotFoundError:
            print(self.FILE_NOT_FOUND+" "+self.PLEASE_INPUT_ZIP_FILE)
            return
        except zipfile.BadZipFile:
            print(self.BAD_ZIP_FILE+" "+self.PLEASE_INPUT_ZIP_FILE)
            return
        except:
            print(self.UNEXPECTED_ERROR, sys.exec_info()[0])
            return

        self.module_dir = os.path.join(os.getcwd(), self.DEFAULT_MODULE_DIR_NAME)
        if os.path.exists(self.module_dir):
            print(self.TEMP_EXISTS)
            return

        os.makedirs(self.module_dir)

        zip_ref.extractall(self.module_dir)
        zip_ref.close()

        if self.options['--clean']:
            os.remove(self.zipfile_path)
    
    """ Copy all of the base module code into the new module directory """
    def copy_base_module(self):
        base_files = os.listdir(self.base_module_dir)
        for file_name in base_files:
            file_path = os.path.join(self.base_module_dir, file_name)
            if os.path.isfile(file_path):
                shutil.copy(file_path, self.module_dir)
    
    """ Analyze the heavy source code to find the values for all the variables we need to resolve in the base module code """
    def analyze_source(self):
        pass

    """ Transform the base module code into a wrapper for the supplied heavy source code """
    def transform_base_module(self):
        pass

    """ Replace all of the expressions of the form $(var) with the value of var stored in the variables dictionary """
    def resolve_variables(self, input_file):
        resolved = []
        lines = input_file.readlines()

        for i, line in enumerate(lines):
            resolved_line = line
            for match in re.finditer(self.var_regex, resolved_line):
                var_name = match.group(1)
                if var_name in self.variables:
                    resolved_line[match.start(1):match.end(1)] = self.variables[var_name]
                else:
                    print("Unresolved variable $("+var_name+") in "+input_file.name+" at line "+str(i)) 
            
            resolved.append(resolved_line)
        
        return resolved

    """ Clean up and exit"""
    def finish(self):
        print("Module generation complete. The heavy patch '"+"x"+"' has been wrapped up as the Godot module '"+"y"+"'")


    

