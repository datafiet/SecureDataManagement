import pickle
import jsonpickle
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
        return obj
        # raise TypeError('Not a dict or pairing group object')


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
        return obj
        # raise TypeError('Not a dict or pairing group object (str), but {}'.format(type(obj)))


def load(group, infile):
    """
    Recursively UNpickle a serialized dict of group objects or a single group object
    """

    root = pickle.load(infile)
    return _load(group, root)













def _dump2(group, obj):
    """
    Recursive helper function to pickle a dict of group objects or a single group object
    """

    if isinstance(obj, dict):
        return dict((k, _dump2(group, v)) for k, v in obj.items())
    elif isinstance(obj, pc_element):
        return group.serialize(obj)
    else:
        return obj
        # raise TypeError('Not a dict or pairing group object {}'.format(type(obj)))


def dump2(group, obj):
    """
    Recursively pickle a serialized dict of group objects or a single group object
    """
    return jsonpickle.encode(_dump2(group, obj))


def _load2(group, obj):
    """
    Recursive helper function to unpickle a dict of group objects or a single group object
    """

    if isinstance(obj, dict):
        return dict((k, _load2(group, v)) for k, v in obj.items())
    elif isinstance(obj, bytes):
        return group.deserialize(obj)
    else:
        return obj
        # raise TypeError('Not a dict or pairing group object (str), but {}'.format(type(obj)))


def load2(group, infile):
    """
    Recursively UNpickle a serialized dict of group objects or a single group object
    """

    root = jsonpickle.decode(infile)
    return _load2(group, root)
