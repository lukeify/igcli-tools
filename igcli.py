import sys
import inspect
import pyclbr
import importlib
import toolkit
from InstagramDataService import InstagramDataService
from Opt import Opt

def get_toolkit():
    """
    A set of available tools that the igcli toolkit provides.

    Returns:
        A set of the tools available.
    """
    return {'like-count'}


def get_opts(argv):
    """
    Fetches the operands provided to the igcli tool at runtime.

    Args:
        argv: A list of arguments provided to the program from sys.argv when the
                script was executed.

    Returns:
        A dictionary of argument key value pairs, with a tool guaranteed as one
        of the keys in the dictionary.
    """
    opts = {}

    # parse the tool to be used
    if len(argv) >= 2 and argv[1] in get_toolkit():
        opts[Opt.Tool] = argv[1]
    else:
        raise Exception("Please provide one of the following igcli tools as the first parameter: {}", get_toolkit())

    argv = argv[2:]

    while argv:
        if argv[0][0] == "-":
            # Lookup name of option enum by value provided
            opts[Opt[Opt(argv[0]).name]] = argv[1]
        argv = argv[1:]

    return opts


def gather_opts(options, requirements):
    """
    Gathers the options requested by the tool to run, and ensures that all mandatory options requested by the calling
    tool are present in the options dictionary.

    Args:
        requirements: A dictionary with mandatory and optional sets of options as requested by the calling tool.

    Returns:
        The requested arguments as a dictionary.

    Raises:
        Exception: If a mandatory argument as requested by the calling tool is not present.
    """

    # Intersect the options available, and the mandatory options requested by the calling tool. If the intersection has
    # less options than the mandatory set, they cannot be satisfied to throw an Exception.
    intersected_mandatory_options = requirements['mandatory'] & set(options.keys())
    if intersected_mandatory_options != requirements['mandatory']:
        raise Exception("Please provide the mandatory arguments")

    # Perform the same function, but with the optional options and without the satisfaction check
    intersected_optional_options = requirements['optional'] & set(options.keys())

    # Union the mandatory and optional requested options
    returned_opt_keys = intersected_mandatory_options.union(intersected_optional_options)

    return dict((opt_key, options[opt_key]) for opt_key in returned_opt_keys)


# Run application
if __name__ == '__main__':
    opts = get_opts(sys.argv)

    igds = InstagramDataService()

    tool_name = opts[Opt.Tool].title().replace("-", "") + "Tool"
    module_name = importlib.import_module("toolkit.{}".format(tool_name))
    Tool = getattr(module_name, tool_name)

    tool = Tool(igds)
    options = gather_opts(opts, tool.requested_options())

    # Execute the application
    result = tool.run(options)

    print(result)
