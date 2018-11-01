import pickle

from charm.toolbox.pairinggroup import pc_element


def _dump(group, obj):
    """
    Recursive helper function to pickle a dict of group objects or a single group object
    """

    if isinstance(obj, dict):
        return dict((k, _dump(group, v)) for k, v in obj.items())
    elif isinstance(obj, pc_element):
        return group.serialize(obj)
    else:
        raise TypeError('Not a dict or pairing group object')


def dump(group, obj, outfile):
    """
    Recursively pickle a serialized dict of group objects or a single group object
    """
    pickle.dump(_dump(group, obj), outfile)


def _load(group, obj):
    """
    Recursive helper function to unpickle a dict of group objects or a single group object
    """

    if isinstance(obj, dict):
        return dict((k, _load(group, v)) for k, v in obj.items())
    elif isinstance(obj, bytes):
        return group.deserialize(obj)
    else:
        raise TypeError('Not a dict or pairing group object (str), but {}'.format(type(obj)))


def load(group, infile):
    """
    Recursively UNpickle a serialized dict of group objects or a single group object
    """

    root = pickle.load(infile)
    return _load(group, root)
