from unittest import main, TestCase
from flask.ext.webtest import TestApp
import json
from api import app

class MyTests(TestCase):

    def setUp(self):
        self.app = app
        self.w = TestApp(self.app)

    def test_base_url_returns_response(self):
        r = self.w.get('/')
        self.assertFalse(r.flashes)
