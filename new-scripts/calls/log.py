redirects = {'stdout': open('run.log', 'w'), 'stderr': open('run.err', 'w')}
properties_file = open('properties', 'a')


def add_property(name, value):
    properties_file.write('%s = %s\n' % (name, repr(value)))
    properties_file.flush()

def save_returncode(command_name, value):
    add_property('%s_returncode' % command_name.lower(), value)
    # TODO: Do we want to mark errors here already?
    # TODO: Would it be better to save just one "fatal_error" for each run?
    error = 0 if value == 0 else 1
    add_property('%s_error' % command_name.lower(), error)
