from unittest.mock import patch

from django.core.management import call_command
from django.db import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    @patch('django.db.utils.ConnectionHandler.__getitem__', return_value=True)
    def test_wait_for_db_ready(self, gi):
        gi.return_value = True
        call_command('wait_for_db')
        self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    @patch('django.db.utils.ConnectionHandler.__getitem__',
           side_effect=[OperationalError] * 5 + [True])
    def test_wait_for_db_ready_after_5_attempts(self, gi, ts):
        call_command('wait_for_db')
        self.assertEqual(gi.call_count, 6)
