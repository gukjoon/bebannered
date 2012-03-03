#!/usr/bin/env python
from google.appengine.ext import db
from geomodel.geomodel import GeoModel


class Preference(db.Model):
    adility_id = db.IntegerProperty()
    name = db.StringProperty()
    cookie = db.StringProperty()
    parent_preference = db.SelfReferenceProperty()

class Vendor(db.Model):
    adility_id = db.IntegerProperty()
    url = db.StringProperty()
    name = db.StringProperty()
    description = db.TextProperty()
    category = db.ReferenceProperty(Preference)

class Location(GeoModel):
    combo_id = db.StringProperty()
    vendor = db.ReferenceProperty(Vendor)
    address = db.StringProperty()

class DealArea(db.Model):
    adility_name = db.StringProperty()
    full_name = db.StringProperty()

class Deal(db.Model):
    adility_id = db.IntegerProperty()
    title = db.StringProperty()
    vendor = db.ReferenceProperty(Vendor)
    image = db.StringProperty()
    startdate = db.DateProperty()
    enddate = db.DateProperty()
    revenue = db.FloatProperty()
    price = db.FloatProperty()
    value = db.FloatProperty()
    quantity = db.IntegerProperty()
    fineprint = db.TextProperty()
    dealarea = db.ReferenceProperty(DealArea)
    active = db.BooleanProperty(default=False)

class User(db.Model):
    username = db.StringProperty()
    email = db.EmailProperty()
    password = db.BlobProperty()

class UserPreference(db.Model):
    user = db.ReferenceProperty(User)
    preference = db.ReferenceProperty(Preference)

class UserDealArea(db.Model):
    user = db.ReferenceProperty(User)
    dealarea = db.ReferenceProperty(DealArea)

class OrderedDeal(db.Model):
    deal = db.ReferenceProperty(Deal)
    user = db.ReferenceProperty(User)
    code = db.StringProperty()
    display = db.StringProperty()
    orderkey = db.IntegerProperty()
    paid = db.BooleanProperty()
    status = db.StringProperty()
    token = db.StringProperty()
