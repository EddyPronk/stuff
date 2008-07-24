import re

class MethodCall(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        f = getattr(fixture, self.name)
        actual = f()
        if type(actual)(str(cell)) == actual:
            cell.passed()
        else:
            cell.failed(actual)

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        setattr(fixture, self.name, type(getattr(fixture, self.name))(str(cell)))

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        action_name = res.group(1)
        return MethodCall(res.group(1))
    else:
        return SetAttribute(action_desc)
