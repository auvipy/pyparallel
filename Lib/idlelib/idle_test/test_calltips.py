import unittest
import idlelib.CallTips as ct
CTi = ct.CallTips()  # needed for get_entity test in 2.7
import types


# Test Class TC is used in multiple get_argspec test methods
class TC(object):
    'doc'
    tip = "(ai=None, *args)"
    def __init__(self, ai=None, *b): 'doc'
    __init__.tip = "(self, ai=None, *args)"
    def t1(self): 'doc'
    t1.tip = "(self)"
    def t2(self, ai, b=None): 'doc'
    t2.tip = "(self, ai, b=None)"
    def t3(self, ai, *args): 'doc'
    t3.tip = "(self, ai, *args)"
    def t4(self, *args): 'doc'
    t4.tip = "(self, *args)"
    def t5(self, ai, b=None, *args, **kw): 'doc'
    t5.tip = "(self, ai, b=None, *args, **kwds)"
    def t6(no, self): 'doc'
    t6.tip = "(no, self)"
    def __call__(self, ci): 'doc'
    __call__.tip = "(self, ci)"
    # attaching .tip to wrapped methods does not work
    @classmethod
    def cm(cls, a): 'doc'
    @staticmethod
    def sm(b): 'doc'

tc = TC()

signature = ct.get_arg_text  # 2.7 and 3.x use different functions
class Get_signatureTest(unittest.TestCase):

    def test_builtins(self):
        # 2.7 puts '()\n' where 3.x does not, other minor differences

        # Python class that inherits builtin methods
        class List(list): "List() doc"
        # Simulate builtin with no docstring for default argspec test
        class SB:  __call__ = None

        def gtest(obj, out):
            self.assertEqual(signature(obj), out)

        gtest(list, "()\nlist() -> new empty list")
        gtest(List, '()\n' + List.__doc__)
        gtest(list.__new__,
               'T.__new__(S, ...) -> a new object with type S, a subtype of T')
        gtest(list.__init__,
               'x.__init__(...) initializes x; see help(type(x)) for signature')
        append_doc =  "L.append(object) -- append object to end"
        gtest(list.append, append_doc)
        gtest([].append, append_doc)
        gtest(List.append, append_doc)

        gtest(types.MethodType, '()\ninstancemethod(function, instance, class)')
        gtest(SB(), '')


    def test_functions(self):
        def t1(): 'doc'
        t1.tip = "()"
        def t2(a, b=None): 'doc'
        t2.tip = "(a, b=None)"
        def t3(a, *args): 'doc'
        t3.tip = "(a, *args)"
        def t4(*args): 'doc'
        t4.tip = "(*args)"
        def t5(a, b=None, *args, **kwds): 'doc'
        t5.tip = "(a, b=None, *args, **kwds)"

        for func in (t1, t2, t3, t4, t5, TC):
            self.assertEqual(signature(func), func.tip + '\ndoc')

    def test_methods(self):
        for meth in (TC.t1, TC.t2, TC.t3, TC.t4, TC.t5, TC.t6, TC.__call__):
            self.assertEqual(signature(meth), meth.tip + "\ndoc")
        self.assertEqual(signature(TC.cm), "(a)\ndoc")
        self.assertEqual(signature(TC.sm), "(b)\ndoc")

    def test_bound_methods(self):
        # test that first parameter is correctly removed from argspec
        for meth, mtip  in ((tc.t1, "()"), (tc.t4, "(*args)"), (tc.t6, "(self)"),
                            (TC.cm, "(a)"),):
            self.assertEqual(signature(meth), mtip + "\ndoc")
        self.assertEqual(signature(tc), "(ci)\ndoc")

    def test_no_docstring(self):
        def nd(s): pass
        TC.nd = nd
        self.assertEqual(signature(nd), "(s)")
        self.assertEqual(signature(TC.nd), "(s)")
        self.assertEqual(signature(tc.nd), "()")

    def test_non_callables(self):
        for obj in (0, 0.0, '0', b'0', [], {}):
            self.assertEqual(signature(obj), '')

class Get_entityTest(unittest.TestCase):
    # In 3.x, get_entity changed from 'instance method' to module function
    # since 'self' not used. Use dummy instance until change 2.7 also.
    def test_bad_entity(self):
        self.assertIsNone(CTi.get_entity('1/0'))
    def test_good_entity(self):
        self.assertIs(CTi.get_entity('int'), int)

class Py2Test(unittest.TestCase):
    def test_paramtuple_float(self):
        # 18539: (a,b) becomes '.0' in code object; change that but not float
        def f((a,b), c=0.0): pass
        self.assertEqual(signature(f), '(<tuple>, c=0.0)')

if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
