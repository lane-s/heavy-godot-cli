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

        if not self.extract_heavy_source():
            return

        self.copy_base_module()
        self.analyze_heavy_source()
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
            return False
        except zipfile.BadZipFile:
            print(self.BAD_ZIP_FILE+" "+self.PLEASE_INPUT_ZIP_FILE)
            return False
        except:
            print(self.UNEXPECTED_ERROR, sys.exec_info()[0])
            return

        self.module_dir = os.path.join(os.getcwd(), self.DEFAULT_MODULE_DIR_NAME)
        if os.path.exists(self.module_dir):
            print(self.TEMP_EXISTS)
            return False

        os.makedirs(self.module_dir)

        zip_ref.extractall(self.module_dir)
        zip_ref.close()
        return True
    
    """ Copy all of the base module code into the new module directory """
    def copy_base_module(self):
        base_files = os.listdir(self.base_module_dir)
        for file_name in base_files:
            file_path = os.path.join(self.base_module_dir, file_name)
            if os.path.isfile(file_path):
                shutil.copy(file_path, self.module_dir)
    
    """ Analyze the heavy source code to find the values for all the variables we need to resolve in the base module code """
    def analyze_heavy_source(self):
        self.get_names_from_source()
        self.generate_in_event_methods()
        self.generate_parameter_control_methods()
        self.generate_documentation()

    """ Get the heavy patch name from the source and use it to determine the module name, class names, and related symbols """
    def get_names_from_source(self):
        source_files = os.listdir(self.module_dir)
        patch_name_regex = re.compile("(Heavy_.*?)\.(cpp|hpp)")
        patch_name = None

        for file_name in source_files:
            match = patch_name_regex.match(file_name)
            if match is not None:
                patch_name = match.group(1)
        
        if patch_name is None:
            print("Cannot find heavy patch in supplied source code")
            cleanup_temp()
            return
        
        self.variables['module_name'] = patch_name.lower()+"_module"
        self.variables['patch_classname'] = patch_name
        self.variables['audio_stream_classname'] = patch_name+"_AudioStream"
        self.variables['audio_playback_classname'] = patch_name+"_AudioStreamPlayback"
        self.variables['header_symbol'] = self.variables['module_name'].upper()+"_H"

    """ Generate code to pass events between the heavy patch and the Godot AudioStream """
    def generate_in_event_methods(self):
        patch_header_path = os.path.join(self.module_dir, self.variables['patch_classname'] + '.hpp')
        patch_header_file = open(patch_header_path, 'r')

        in_events = self.get_enum_vals(patch_header_file, 'EventIn')

        in_event_declaration_stub_path = os.path.join(self.stubs_dir, 'inevent_declaration.cpp')
        in_event_declaration_stub_file = open(in_event_declaration_stub_path, 'r')

        in_event_definition_stub_path = os.path.join(self.stubs_dir, 'inevent_definition.cpp')
        in_event_definition_stub_file = open(in_event_definition_stub_path, 'r')

        bind_method_stub_path = os.path.join(self.stubs_dir, 'bind_method.cpp')
        bind_method_stub_file = open(bind_method_stub_path, 'r')

        in_event_method_declarations = []
        in_event_method_definitions = []
        in_event_binds = ['\n']

        for in_event in in_events:
            self.variables['method_name'] = 'trigger_'+in_event.lower()+"_event"
            self.variables['event_name'] = in_event
            in_event_method_declarations.append(self.resolve_variables(in_event_declaration_stub_file))
            in_event_method_definitions.append(self.resolve_variables(in_event_definition_stub_file))
            in_event_binds.append(self.resolve_variables(bind_method_stub_file))

        self.variables['in_event_method_declarations'] = '\n'.join(in_event_method_declarations)
        self.variables['in_event_method_definitions'] = '\n'.join(in_event_method_definitions)
        self.variables['in_event_binds'] = '\n'.join(in_event_binds)

        patch_header_file.close()
        in_event_declaration_stub_file.close()
        in_event_definition_stub_file.close()
            

    """ Returns a list of possible values for the enum of the given name in the given file """
    def get_enum_vals(self, file, enum_name):
        vals = []

        file.seek(0, 0)
        lines = file.readlines()

        enum_start_regex = re.compile('enum\s*' + enum_name + '\s*:\s*hv_uint32_t\s*\{') #Match line like 'enum ParameterIn : hv_uint32_t {'
        enum_val_regex = re.compile('(.+?)\s*=\s*[A-F0-9x]+') #Match line like 'ENUM_NAME = 0xFFFFFF,'
        enum_end_regex = re.compile('\}\s*;') #Match end of clause i.e. '};'

        reading_enum = False

        for line in lines:
            if reading_enum:
                if enum_end_regex.match(line.strip()) is not None:
                    return vals
                else:
                    match = enum_val_regex.match(line.strip())
                    if match is not None:
                        vals.append(match.group(1))
            elif enum_start_regex.match(line.strip()) is not None:
                reading_enum = True
                continue

        return vals

    """ Generate code to expose heavy patch parameters through the Godot AudioStream """
    def generate_parameter_control_methods(self):
        pass

    """ Generate documentation for the new Godot module """
    def generate_documentation(self):
        pass

    """ Transform the base module code into a wrapper for the supplied heavy source code by resolving all variables in the base module and renaming base files"""
    def transform_base_module(self):
        self.resolve_all_variables()
        self.rename_files()

    def resolve_all_variables(self):
        wrapper_file_names = ['base.cpp', 'base.h', 'register_types.h', 'register_types.cpp']

        for wrapper_file_name in wrapper_file_names:
            file_path = os.path.join(self.module_dir, wrapper_file_name)
            wrapper_file = open(file_path, 'r+')

            resolved_text = self.resolve_variables(wrapper_file)

            wrapper_file.seek(0, 0)
            wrapper_file.write(resolved_text)            
            wrapper_file.truncate(len(resolved_text))
            wrapper_file.close()


    def rename_files(self):
        new_module_dir = os.path.join(self.module_dir, os.path.join(os.pardir, self.variables['module_name']))

        os.rename(self.module_dir, new_module_dir)
        self.module_dir = os.path.abspath(new_module_dir)

        base_src_regex = re.compile("(base).(cpp|h)")

        source_files = os.listdir(self.module_dir)
        for file_name in source_files:
            match = base_src_regex.match(file_name)
            if match is not None:
                file_path = os.path.join(self.module_dir, file_name)
                new_file_name = file_name[:match.start(1)] + self.variables['module_name'] + file_name[match.end(1):]
                new_file_path = os.path.join (self.module_dir, new_file_name)
                os.rename(file_path, new_file_path)

    """ Replace all of the expressions of the form $(var) with the value of var stored in the variables dictionary """
    def resolve_variables(self, input_file):
        resolved = []

        input_file.seek(0, 0)
        lines = input_file.readlines()

        var_regex = "\$\((.*?)\)" #Match expressions like '$(var_name)'
        def var_repl(match):
            return self.variables[match.group(1)]

        for i, line in enumerate(lines):
            resolved_line = re.sub(var_regex, var_repl, line)
            resolved.append(resolved_line)
        
        return '\n'.join(resolved)

    """ Cleanup and finish """
    def finish(self):
        if self.options['--clean']:
            os.remove(self.zipfile_path)
        print("Module generation complete. The heavy patch '"+self.variables['patch_classname']+"' has been wrapped up as the Godot module '"+self.variables['module_name']+"'")

    """ Remove the temporary folder if the wrap failed prematurely """
    def cleanup_temp(self):
        shutil.rmtree(self.module_dir)



    

