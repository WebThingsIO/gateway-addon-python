"""Wrapper around the gateway's database."""

import json
import os
import sqlite3


_DB_PATHS = [
    os.path.join(os.path.expanduser('~'),
                 'mozilla-iot',
                 'gateway',
                 'db.sqlite3'),
    os.path.join(os.path.expanduser('~'),
                 '.mozilla-iot',
                 'config',
                 'db.sqlite3'),
    os.path.join('.', 'db.sqlite3'),               # if cwd is the gateway dir
    os.path.join('..', '..', '..', 'db.sqlite3'),  # if cwd is the add-on dir
]

if 'MOZIOT_HOME' in os.environ:
    _DB_PATHS.append(
        os.path.join(os.environ['MOZIOT_HOME'], 'config', 'db.sqlite3'))

if 'MOZIOT_DATABASE' in os.environ:
    _DB_PATHS.append(os.environ['MOZIOT_DATABASE'])


class Database:
    """Wrapper around gateway's settings database."""

    def __init__(self, package_name, path=None):
        """
        Initialize the object.

        package_name -- the adapter's package name
        path -- optional path to the database
        """
        self.package_name = package_name
        self.path = path
        self.conn = None

        if self.path is None:
            for p in _DB_PATHS:
                if os.path.isfile(p):
                    self.path = p
                    break

    def open(self):
        """Open the database."""
        if self.path is None:
            return False

        self.conn = sqlite3.connect(self.path)
        return True

    def close(self):
        """Close the database."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def load_config(self):
        """Load the package's config from the database."""
        if not self.conn:
            return None

        key = 'addons.{}'.format(self.package_name)
        c = self.conn.cursor()
        c.execute('SELECT value FROM settings WHERE key = ?', (key,))
        data = c.fetchone()
        c.close()

        if not data:
            return None

        data = json.loads(data[0])

        if 'moziot' not in data or 'config' not in data['moziot']:
            return None

        return data['moziot']['config']

    def save_config(self, config):
        """Save the package's config in the database."""
        if not self.conn:
            return False

        key = 'addons.{}'.format(self.package_name)
        c = self.conn.cursor()
        c.execute('SELECT value FROM settings WHERE key = ?', (key,))
        data = c.fetchone()
        c.close()

        if not data:
            return False

        data = json.loads(data[0])

        if 'moziot' not in data:
            data['moziot'] = {}

        data['moziot']['config'] = config

        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                  (key, json.dumps(data)))
        self.conn.commit()
        c.close()

        return True
