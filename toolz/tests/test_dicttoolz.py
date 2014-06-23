from toolz.utils import raises
from toolz.dicttoolz import (merge, merge_with, valmap, keymap, update_in,
                             assoc, get_in, keyfilter, valfilter)


inc = lambda x: x + 1


iseven = lambda i: i % 2 == 0


class C():
    pass


def test_merge():
    assert merge({1: 1, 2: 2}, {3: 4}) == {1: 1, 2: 2, 3: 4}


def test_merge_iterable_arg():
    assert merge([{1: 1, 2: 2}, {3: 4}]) == {1: 1, 2: 2, 3: 4}


def test_merge_with():
    dicts = {1: 1, 2: 2}, {1: 10, 2: 20}
    assert merge_with(sum, *dicts) == {1: 11, 2: 22}
    assert merge_with(tuple, *dicts) == {1: (1, 10), 2: (2, 20)}

    dicts = {1: 1, 2: 2, 3: 3}, {1: 10, 2: 20}
    assert merge_with(sum, *dicts) == {1: 11, 2: 22, 3: 3}
    assert merge_with(tuple, *dicts) == {1: (1, 10), 2: (2, 20), 3: (3,)}

    assert not merge_with(sum)


def test_merge_with_iterable_arg():
    dicts = {1: 1, 2: 2}, {1: 10, 2: 20}
    assert merge_with(sum, *dicts) == {1: 11, 2: 22}
    assert merge_with(sum, dicts) == {1: 11, 2: 22}
    assert merge_with(sum, iter(dicts)) == {1: 11, 2: 22}


def test_valmap():
    assert valmap(inc, {1: 1, 2: 2}) == {1: 2, 2: 3}


def test_keymap():
    assert keymap(inc, {1: 1, 2: 2}) == {2: 1, 3: 2}


def test_valfilter():
    assert valfilter(iseven, {1: 2, 2: 3}) == {1: 2}


def test_keyfilter():
    assert keyfilter(iseven, {1: 2, 2: 3}) == {2: 3}


def test_assoc():
    assert assoc({}, "a", 1) == {"a": 1}
    assert assoc({"a": 1}, "a", 3) == {"a": 3}
    assert assoc({"a": 1}, "b", 3) == {"a": 1, "b": 3}

    # Verify immutability:
    d = {'x': 1}
    oldd = d
    assoc(d, 'x', 2)
    assert d is oldd

    # Test object support:
    c = C()
    assert assoc(c, "a", 1).__dict__ == {"a": 1}
    c.a = 1
    assert assoc(c, "a", 3).__dict__ == {"a": 3}
    assert assoc(c, "b", 3).__dict__ == {"a": 1, "b": 3}

    # Verify immutability:
    o = C()
    o.x = 1
    assoc(o, 'x', 2)
    assert o.x == 1


def test_update_in():
    assert update_in({"a": 0}, ["a"], inc) == {"a": 1}
    assert update_in({"a": 0, "b": 1}, ["b"], str) == {"a": 0, "b": "1"}
    assert (update_in({"t": 1, "v": {"a": 0}}, ["v", "a"], inc) ==
            {"t": 1, "v": {"a": 1}})
    # Handle one missing key.
    assert update_in({}, ["z"], str, None) == {"z": "None"}
    assert update_in({}, ["z"], inc, 0) == {"z": 1}
    assert update_in({}, ["z"], lambda x: x+"ar", default="b") == {"z": "bar"}
    # Same semantics as Clojure for multiple missing keys, ie. recursively
    # create nested empty dictionaries to the depth specified by the
    # keys with the innermost value set to f(default).
    assert update_in({}, [0, 1], inc, default=-1) == {0: {1: 0}}
    assert update_in({}, [0, 1], str, default=100) == {0: {1: "100"}}
    assert (update_in({"foo": "bar", 1: 50}, ["d", 1, 0], str, 20) ==
            {"foo": "bar", 1: 50, "d": {1: {0: "20"}}})
    # Verify immutability:
    d = {'x': 1}
    oldd = d
    update_in(d, ['x'], inc)
    assert d is oldd

    # Test object support:
    c = C()
    c.a = 0
    assert update_in(c, ["a"], inc).__dict__ == {"a": 1}
    c = C()
    c.a = 0
    c.b = 1
    assert update_in(c, ["b"], str).__dict__ == {"a": 0, "b": "1"}
    v = C()
    v.a = 0
    c = C()
    c.t = 1
    c.v = v
    assert update_in(c, ["v", "a"], inc).v.__dict__ == {"a": 1}

    # Handle one missing key.
    c = C()
    assert update_in(c, ["z"], str, None).__dict__ == {"z": "None"}
    assert update_in(c, ["z"], inc, 0).__dict__ == {"z": 1}
    assert update_in(c, ["z"], lambda x: x + "ar",
                         default="b").__dict__ == {"z": "bar"}

    # Allow AttributeError to be thrown if more than one missing key,
    # because we don't know what type of object to create for nesting.
    assert raises(AttributeError,
                  lambda: update_in(c, ["y", "z"], inc, default=0))

    # Verify immutability:
    o = C()
    o.x = 1
    update_in(o, ['x'], inc)
    assert o.x == 1


def test_get_in():
    # Test object support:
    o = C()
    a = C()
    a.b = 1
    o.a = a
    assert get_in(['a', 'b'], o) == 1
    assert get_in(['a', 'b', 'c'], o, 2) == 2
    assert raises(AttributeError,
                  lambda: get_in(['a', 'b', 'c'], o, no_default=True))
