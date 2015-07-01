#!/usr/bin/env python

import os

from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db


application = create_app(os.getenv('DM_ENVIRONMENT') or 'development')
manager = Manager(application)
manager.add_command("runserver", Server(host="0.0.0.0", port=8888))
migrate = Migrate(application, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
