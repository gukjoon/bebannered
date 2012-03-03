import os
import datetime
import hashlib

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from bebannered_model import *

#ehhhhh
def ShowTemplate(webapp, template_file, template_values):
  #reset cookies
  user = webapp.request.cookies.get('user','')
  userid = webapp.request.cookies.get('user_id','')
  userkey = webapp.request.cookies.get('user_key','')
  if userid != '':
    cookies = [cookie.preference.cookie for cookie in UserPreference.all().filter('user = ',db.Key(userkey))]
  else:
    cookies = []
  
  add_template = {'user' : user, 'userid' : userid, 'userkey' : userkey, 'cookies': cookies}
  if type(template_values) is dict:
    template_values.update(add_template)
  else:
    template_values = add_template
  path = os.path.join(os.path.dirname(__file__), template_file)
  webapp.response.out.write(template.render(path, template_values))

def GetPreferences(userid):
  userpreferences = [userpref.preference.name for userpref in UserPreference.all().filter('user = ', db.Key(userid))]
  #do we want to do extra work here or just add in key?
  preferences = [(preference.name, preference.key(), preference.name in userpreferences,
                  [(subpref.name, subpref.key(), subpref.name in userpreferences) for subpref in Preference.all().filter('parent_preference = ',preference)])
                 for preference in Preference.all().filter('parent_preference = ',None)]
  
  return preferences

def GetDealAreas(userid):
  userareas = [userarea.dealarea.full_name for userarea in UserDealArea.all().filter('user = ',db.Key(userid))]
  dealareas = [[dealarea.full_name,dealarea.adility_name,dealarea.full_name in userareas] for dealarea in DealArea.all()]
  return dealareas


def GetMyDeals(userid):
  
  #return [{'deal_title': mydeal.deal.title, 'code': mydeal.code, 'token': mydeal.token, 'vendor': mydeal.deal.vendor.name}
  return [{'key': str(mydeal.key()), 'title': mydeal.deal.title, 'vendor': mydeal.deal.vendor.name, 'display': mydeal.display}
          for mydeal in OrderedDeal.all().filter('user = ',db.Key(userid)).filter('paid = ',True)]


def GetDeals(userid,offset=0):
  if userid==None:
    dealqry = Deal.all().filter('active = ',True).filter('enddate >= ', datetime.datetime.now())
    #dealqry = Deal.all().filter('enddate >= ', datetime.datetime.now())
    return {'All' : [{'title':deal.title,'id':str(deal.key())} for deal in dealqry.fetch(limit=20,offset=offset)]}
  else:
    dealdict = {}
    userprefs = [userpref.preference for userpref in UserPreference.all().filter('user = ',db.Key(userid))]
    userlocations = set([userdealarea.dealarea.adility_name for userdealarea in UserDealArea.all().filter('user = ',db.Key(userid))])
    
    for userpref in userprefs:
      templist = []
      for vendor in Vendor.all().ancestor(userpref):
        dealqry = Deal.all().ancestor(vendor).filter('active = ',True)
        for deal in dealqry:
          if deal.dealarea.adility_name in userlocations:
            templist.append({'vendor' : vendor.name,
                             'title' : deal.title,
                             'id' : deal.key()})
      dealdict[userpref.name] = templist
    return dealdict
    
def GetDealInfo(dealid):
  #too much reference walking!
  deal = db.get(dealid)
  if not deal:
    return None
  #deal with no locations case
  locations = [{'latitude' : location.location.lat, 'longitude': location.location.lon ,'address' : location.address} for location in Location.all().filter('vendor = ',deal.vendor)]
  lats = [location['latitude'] for location in locations]
  longs = [location['longitude'] for location in locations]
  center = {'lat': (max(lats) - min(lats))/2 + min(lats),
            'long': (max(longs) - min(longs))/2 + min(longs)}
  #set currency formatting to USD
  return {'key' : deal.adility_id,
          'gae_key' : deal.key(),
          'deal_area' : deal.dealarea.full_name,
          'title' : deal.title,
          'image' : deal.image,
          'price' : "%1.2f" % deal.price,
          'value' : "%1.2f" % deal.value,
          #geo shit
          'locations' : locations,
          'center' : center,
          'savings': "%1.0f" % round((1- (deal.price/deal.value)) * 100,0) + "%",
          'quantity' : deal.quantity,
          'fineprint' : deal.fineprint,
          'vendor' : deal.vendor.name,
          'url' : deal.vendor.url,
          'vendor_desc' : deal.vendor.description,
          'category' : deal.vendor.category.name,
          #adjust checkout urls here. TODO: use DEV flag
          'checkouturl' : 'https://sandbox.google.com/checkout/api/checkout/v2/checkoutForm/Merchant/308159225824435',
          'checkoutimg' : 'https://sandbox.google.com/checkout/buttons/buy.gif?merchant_id=308159225824435&amp;w=117&amp;h=48&amp;style=white&amp;variant=text&amp;loc=en_US'}

def HashPassword(password):
  return hashlib.md5(password).digest()