#!/usr/bin/env python

from google.appengine.api import datastore


def create_foreign_key(kind, key_is_id=False):
    def generate_foreign_key_lambda(value):
        if key_is_id:
            value = int(value)
        if not value:    # ADDED
            return None  # ADDED
        return datastore.Key.from_path(kind, value)
    return generate_foreign_key_lambda
