import os
import pathlib

from yoyo import read_migrations, get_backend

import app.db

# Get migrations folder from anywhere
migrations_path = pathlib.Path(app.db.__file__).parents[0] / 'migrations'


class Migrate:
    def __init__(self,
                 db_uri: str = os.environ["DATABASE_URL"],
                 migration_folder: str = read_migrations(str(migrations_path))):
        self.backend = get_backend(db_uri)
        self.migration_folder = migration_folder

    def apply(self):
        self.backend.apply_migrations(self.backend.to_apply(self.migration_folder))

    def rollback_all(self):
        self.backend.rollback_migrations(self.backend.to_rollback(self.migration_folder))

    def rollback_one(self):
        self.backend.rollback_one(self.migration_folder)

    def reapply(self):
        self.rollback_all()
        self.apply()
