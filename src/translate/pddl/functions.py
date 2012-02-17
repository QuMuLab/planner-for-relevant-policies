import pddl_types


def parse_functions(seq):
    # seq is ":functions" block without the leading ":functions" tag.
    result = pddl_types.parse_typed_list(
        seq, constructor=Function.parse, default_type="number")
    for function in result:
        if function.result_type != "number":
            raise SystemExit(
                "function with bad result type (only \"number\" supported): %s"
                % function)
    return result


class Function(object):
    def __init__(self, name, parameters, result_type):
        self.name = name
        self.parameters = parameters
        self.result_type = result_type

    @classmethod
    def parse(cls, alist, result_type):
        name = alist[0]
        parameters = pddl_types.parse_typed_list(alist[1:], only_variables=True)
        return cls(name, parameters, result_type)

    def __str__(self):
        return "%s(%s): %s" % (
            self.name, ", ".join(map(str, self.parameters)), self.result_type)
