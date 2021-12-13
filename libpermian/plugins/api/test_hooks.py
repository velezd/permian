import unittest
from time import sleep
from libpermian.plugins.api.hooks import make, callback_on, threaded_callback_on
from libpermian.hooks.register import HOOKS, CALLBACKS

hook_function = None

class TestHooksApi(unittest.TestCase):
    OLD_HOOKS = []
    OLD_CALLBACKS = []

    @classmethod
    def setUpClass(cls):
        cls.OLD_HOOKS = HOOKS.copy()
        cls.OLD_CALLBACKS = CALLBACKS.copy()
        global hook_function
        @make
        def hook_function():
            pass

    @classmethod
    def tearDownClass(cls):
        HOOKS = cls.OLD_HOOKS
        CALLBACKS = cls.OLD_CALLBACKS
        global hook_function
        del hook_function

    def setUp(self):
        self.called = False
        self.called_threaded = False

    def test_make(self):
        self.assertIn(hook_function, HOOKS)

    def test_callback_on(self):
        @callback_on(hook_function)
        def callback_function():
            self.called = True

        self.assertFalse(self.called)
        hook_function()
        self.assertTrue(self.called)

    def test_threaded_callback_on(self):
        @threaded_callback_on(hook_function)
        def callback_function_threaded():
            sleep(0.1)
            self.called_threaded = True

        self.assertFalse(self.called_threaded)
        hook_function()
        self.assertFalse(self.called_threaded)
        sleep(0.2)
        self.assertTrue(self.called_threaded)
