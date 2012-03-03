#!/usr/bin/env python
import cgi
import datetime
import string
import urllib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from django.core.validators import email_re

from bebannered_model import *
from bebannered_helpers import ShowTemplate
from bebannered_helpers import HashPassword

class ReCaptchaHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""<html><body><form action='' method='post'><script type="text/javascript"
     src="http://www.google.com/recaptcha/api/challenge?k=6LdAUcESAAAAAOPx40aHJ1W9kWtaE_behEvWeKz6 ">
  </script>
  <noscript>
     <iframe src="http://www.google.com/recaptcha/api/noscript?k=6LdAUcESAAAAAOPx40aHJ1W9kWtaE_behEvWeKz6"
         height="300" width="500" frameborder="0"></iframe><br>
     <textarea name="recaptcha_challenge_field" rows="3" cols="40">
     </textarea>
     <input type="hidden" name="recaptcha_response_field"
         value="manual_challenge">
  </noscript></form></body></html>""")
  def post(self):
    def encode_if_necessary(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s
    params = urllib.urlencode ({
            'privatekey': encode_if_necessary('6LdAUcESAAAAAJAQIvTK1Y4TlbgRYUVyhtzii075'),
            'remoteip' :  encode_if_necessary(self.request.remote_addr),
            'challenge':  encode_if_necessary(self.request.get('recaptcha_challenge_field')),
            'response' :  encode_if_necessary(self.request.get('recaptcha_response_field')),
            })
    rcap = urlfetch.fetch('http://www.google.com/recaptcha/api/verify?' + params,method='POST',deadline=10).content
    if string.split(rcap,"\n")[0] == "true":
      self.response.out.write('yay')
    else:
      self.response.out.write('nay')
    


#maybe change name to bebannered_api
class PreferencesPostHandler(webapp.RequestHandler):
  def post(self,userid):
    user = db.Key(userid)
    allprefs = self.request.arguments()
    def filter_loc(x): return string.split(x,'.')[0] == 'location'
    def filter_vend(x): return string.split(x,'.')[0] == 'vendor'
    def get_end(x): return string.split(x,'.')[1]
    vendorprefs = set(map(get_end,filter(filter_vend,allprefs)))
    locationprefs = set(map(get_end,filter(filter_loc,allprefs)))
    self.response.out.write(vendorprefs)
    
    #can use ancestor instead
    currentprefs = UserPreference.all().filter('user = ',user)
    cprefs = set(str(pref.preference.key()) for pref in currentprefs)
    
    currentlocs = UserDealArea.all().filter('user = ',user)
    clocs = set(str(loc.dealarea.key().name()) for loc in currentlocs)
    
    #adds
    for vpref in vendorprefs:
      if not vpref in cprefs:
        newpref = UserPreference()
        newpref.user = user
        newpref.preference = db.Key(vpref)
        newpref.put()
    
    for lpref in locationprefs:
      if not lpref in clocs:
        newloc = UserDealArea()
        newloc.user = user
        newloc.dealarea = db.Key.from_path('DealArea',lpref)
        newloc.put()
    
    for cpref in currentprefs:
      if not str(cpref.preference.key()) in vendorprefs:
        cpref.delete()
    
    for cloc in currentlocs:
      if not str(cloc.dealarea.key().name()) in locationprefs:
        cloc.delete()
    
    self.redirect("/")

#Users
class UserHandler(webapp.RequestHandler):
  def post(self):
    user = User()
    #username already taken etc.
    
    #validation
    user.username = self.request.get('email')
    user.email = self.request.get('email')
    
    if email_re.match(user.email)==None:
      self.redirect("/error/3")
      return
    
    rawpass = self.request.get('password')
    
    if rawpass != self.request.get('confirm-password'):
      self.redirect("/error/4")
      return 

    if User.all().filter('username = ',user.username).count(1) > 0:
      self.redirect("/error/5")
      return
    
    if rawpass == user.username:
      self.redirect("/error/6")
      return
    
    if len(rawpass) < 6:
      self.redirect("/error/7")
      return
    
    password = HashPassword(self.request.get('password'))
    user.password = password
    user.put()
    self.response.headers.add_header('Set-Cookie', 'user=%s' % user.username.encode())
    self.response.headers.add_header('Set-Cookie', 'user_id=%s' % str(user.key().id()))
    self.response.headers.add_header('Set-Cookie', 'user_key=%s' % str(user.key()))
    self.redirect("/preferences")

class LoginHandler(webapp.RequestHandler):
  #implement double hash at some point
  def post(self):
    username = self.request.get('username')
    redirect = self.request.get('redirect')
    if self.request.cookies.get('user','') == username:
      #check cookies here
      if redirect != '':
        self.redirect(str(redirect))
      else:
        self.redirect("/preferences")
      return

    userqry = User.all().filter('username = ',username).fetch(1)
    if len(userqry) < 1:
      self.redirect("/error/101")
      return
    else:
      user = userqry[0]
      password = HashPassword(self.request.get('password'))
      if user.password != password:
        self.redirect("/error/102")
        return
      else:
        #check cookies here
        self.response.headers.add_header('Set-Cookie', 'user=%s' % username.encode())
        self.response.headers.add_header('Set-Cookie', 'user_id=%s' % str(user.key().id()))
        self.response.headers.add_header('Set-Cookie', 'user_key=%s' % str(user.key()))
        if redirect != '':
          self.redirect(str(redirect))
        else:
          self.redirect("/preferences")

class LogoutHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Set-Cookie', 'user=')
    self.response.headers.add_header('Set-Cookie', 'user_id=')
    self.response.headers.add_header('Set-Cookie', 'user_key=')
    self.redirect("/")

class ChangePasswordHandler(webapp.RequestHandler):
    def get(self):
        ShowTemplate(self,'templates/change_password.html',None)
    
    def post(self):
        userid = self.request.cookies.get('user_key','')
        if userid is None:
            self.redirect('/')
            return
        user_key = db.Key(userid)
        user = User.get(user_key)
        rawpass = self.request.get('password')
        if not user:
          self.redirect('/')
        old_pass = HashPassword(self.request.get('current_password'))
        if old_pass != user.password:
          self.redirect('/error/220')
          return
        if rawpass != self.request.get('confirm-password'):
          self.redirect("/error/204")
          return    
        if rawpass == user.username:
          self.redirect("/error/206")
          return
        if len(rawpass) < 6:
            self.redirect("/error/207")
            return
    
        user.password = HashPassword(rawpass)
        user.put()
        self.redirect("/")

class ProductHandler(webapp.RequestHandler):
  def get(self):
    self.redirect("/")
