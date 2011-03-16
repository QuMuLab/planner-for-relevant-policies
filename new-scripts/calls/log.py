redirects = {'stdout': open('run.log', 'a'), 'stderr': open('run.err', 'a')}
properties_file = open('properties', 'a')


def add_property(name, value):
    properties_file.write('%s = %s\n' % (name, repr(value)))
    properties_file.flush()

def save_returncode(command_name, value):
    add_property('%s_returncode' % command_name.lower(), str(value))
    error = 0 if value == 0 else 1
    add_property('%s_error' % command_name.lower(), error)
