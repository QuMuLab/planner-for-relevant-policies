
###################
# Save / Load csv files
################
def load_CSV(filename, delimiter = ','):
    """Load a csv file into a list of value arrays"""
    file_lines = read_file(filename)
    return [line.split(delimiter) for line in file_lines]

def save_CSV(data, filename, delimiter = ','):
    """
    Save a matrix of data as a csv file.
    
    data:        Array of arrays. Each element will be converted to a string
    filename:    Filename of the csv file to be created
    delimiter:   Optional parameter to specify the separator used
    """
    output = ''
    for line in data:
        output += delimiter.join([str(item) for item in line]) + "\n"
    
    write_file(filename, output)

def read_file(file_name):
    """Return a list of the lines of a file."""
    f = open(file_name, 'r')
    file_lines = [line.rstrip("\n") for line in f.readlines()]
    f.close()
    return file_lines

def write_file(file_name, contents):
    """Write the contents of a provided list or string to a file"""
    f = open(file_name, 'w')
    if contents.__class__.__name__ == 'list':
        f.write("\n".join(contents))
    else:
        f.write(contents)
    f.close()

def append_file(file_name, contents):
    """Append the contents of a provided list or string to a file"""
    f = open(file_name, 'a')
    if contents.__class__.__name__ == 'list':
        f.write("\n".join(contents))
    else:
        f.write(contents)
    f.close()
