import argparse


class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Heleper format to exclude empty list on nargs +"""

    def _format_args(self, action, default_metavar):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_args(action, default_metavar)
        if action.nargs == '+':
            parts = ''
        return parts


def make_parser():
    """Return parser with arguments for program"""

    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description='Automatically restart namd dynamics.',
                                     epilog="Made by artotim",
                                     usage='%(prog)s -i <path/to/previous_run/> -o <path/to/restart_output/>',
                                     add_help=False,
                                     formatter_class=SubcommandHelpFormatter)
    required = parser.add_argument_group('Required')
    optional = parser.add_argument_group('Optional')

    required.add_argument('-i', '--input', metavar='', dest='previous', required=True,
                          help='Previous dynamic folder')
    required.add_argument('-o', '--output', metavar='', dest='restart', required=True,
                          help='Restart output folder')
    optional.add_argument("-h", "--help", action="help",
                          help="Show this help message and exit")
    optional.add_argument('-c', '--conf', metavar='',
                          help='Previous .conf file')
    optional.add_argument('-f', '--file-name', metavar='',
                          help='Set output files name')
    optional.add_argument('-r', '--run', metavar='',
                          help='Set run steps number')
    optional.add_argument('-a', '--add-options', metavar='', dest='options', default=[], action='append', nargs='+',
                          help='Additional options to include in .conf file')
    optional.add_argument('-e', '--namd-exe', default='namd', metavar='',
                          help='Path to namd executable')
    optional.add_argument('-N', '--no-namd', action='store_false', dest='namd',
                          help='Disable automatically running namd after end')
    optional.add_argument('-B', '--backup', action='store_true',
                          help='Save backups for restart files while running namd')
    optional.add_argument('-t', '--threads', default=1, type=int, metavar='',
                          help='Number of cores to run namd when automatically running (default: 1)')

    return parser
