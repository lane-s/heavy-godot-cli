"""
heavy-godot
 
Usage:
  heavy-godot create_module [ZIPPED_HEAVY_SOURCE]
  heavy-godot -h | --help
  heavy-godot --version
 
Options:
  -h --help                         Show this screen.
  --version                         Show version.
 
Examples:
  heavy-godot hello
 
Help:
  For help using this tool, please open an issue on the Github repository:
"""
 
 
from inspect import getmembers, isclass
 
from docopt import docopt
 
from . import __version__ as VERSION
 
 
def main():
    """Main CLI entrypoint."""
    import heavygodot.commands
    options = docopt(__doc__, version=VERSION)
 
    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for k, v in options.items():
        if hasattr(heavygodot.commands, k):
            module = getattr(heavygodot.commands, k)
            commands = getmembers(module, isclass)
            command = [command[1] for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()