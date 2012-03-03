#!/usr/bin/env python
import cgi
import datetime

from google.appengine.ext import webapp

from bebannered_helpers import *

#pages
class MainPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/index.html',None)

class SplashPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/coming.html',None)

class AboutPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/about.html',None)

class PrivacyPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/privacy.html',None)

class ErrorPage(webapp.RequestHandler):
  def get(self,errorcode):
    try:
      code = int(errorcode)
    except Exception:
      code = 0
    # 0 - 99 is the error code
    # 100 - 900 is the page to display
    
    pages = {0: 'signup',
             1: 'signin',
             2: 'chpass'}
    
    errors = {0: "An error has occured",
              #login errors
              1: "User not found!",
              2: "Your password is incorrect!",
              #registration errors
              3: "Invalid email.",
              4: "Your passwords don't match",
              5: "Username already exists",
              6: "Password is the same as your e-mail. Do better",
              7: "Password is too short. Passwords should be a minimum of 6 characters.",
              #other errors
              8: "You are not authorized to see this deal!",
              #Password changing errors
              20: "The original password was not correct!"}
    page = int(code/100)
    error = int(code%100)
    template_values = {}
    if error in errors:
      template_values['error_message'] =  errors[error]
    else:
      template_values['error_message'] = errors[error]
    if page in pages:
      template_values[pages[page]] = True
      
    ShowTemplate(self,'templates/error.html',template_values)
    

class DealsPage(webapp.RequestHandler):
  def get(self):
    userid = self.request.cookies.get('user_key','')
    dt1 = datetime.datetime.now()
    if userid!='':
      template_values = {'deals' : GetDeals(userid)}
    else:
      if self.request.get('page'):
        myoffset = (int(self.request.get('page')) - 1) * 20
        nextpage = int(self.request.get('page')) + 1
      else:
        myoffset = 0
        nextpage = 2
      template_values = {'deals' : GetDeals(None,offset=myoffset),'nextpage' : nextpage}
    dt2 = datetime.datetime.now()
    ShowTemplate(self,'templates/deals.html',template_values)

class HowItWorksPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/howitworks.html',None)

#not logged in
class SignInPage(webapp.RequestHandler):
  def get(self):
    #display already signed in page
    args = { }
    redirect = self.request.get('redirect')
    if redirect != '':
      args['redirect'] = redirect
    ShowTemplate(self,'templates/signin.html', args)

class SignUpPage(webapp.RequestHandler):
  def get(self):
    ShowTemplate(self,'templates/signup.html',None)


#only logged in
class PreferencesPage(webapp.RequestHandler):
  def get(self):
    userid = self.request.cookies.get('user_key','')
    if userid!='':
      template_values = {'preferences' : GetPreferences(userid),
                         'dealareas' : GetDealAreas(userid),
                         'mydeals' : GetMyDeals(userid)}
      ShowTemplate(self,'templates/preferences.html',template_values)
    else:
      self.redirect("/signin")

class LandingPageHandler(webapp.RequestHandler):
  def get(self,dealid):
    if self.request.cookies.get('user_id',''):
      template_values = GetDealInfo(dealid)
      if template_values:
        ShowTemplate(self,'templates/landingpage.html',template_values)
      else:
        self.redirect("/")
    else:
      #make sure to redirect and also redirect registration
      self.redirect("/signin?redirect=/landingpage/%s" % str(dealid))

class StaticLandingPage(webapp.RequestHandler):
  def get(self):
    template_values = {'key':'123',
     'title':'Example',
     'image':'http://subdomain-dev-9961.adilitydemo.com/system/illustrations/9001/original/1630310.jpg?1267982663',
     'price':'39.99',
     'value':'200.0',
     'locations':[{'address':'3956 Rivermark Plaza, Santa Clara, CA 95054',
                   'latitude':'37.395117',
                   'longitude':'-121.945931'},
                  {'address':'39070 Aronaunt Way, Fremont, CA 94538',
                   'latitude':'37.5449423',
                   'longitude':'-121.9898997'}],
     'center':{'lat':'37.5898562',
               'long':'-121.9952563'},
     'savings':'80.01%',
     'quantity':'250',
     'fineprint':'Blah blah blah fineprint',
     'vendor':'The Salon at PureBeauty',
     'url':'http://www.purebeauty.com/',
     'checkouturl' : 'https://sandbox.google.com/checkout/api/checkout/v2/checkoutForm/Merchant/308159225824435',
     'checkoutimg' : 'https://sandbox.google.com/checkout/buttons/buy.gif?merchant_id=308159225824435&amp;w=117&amp;h=48&amp;style=white&amp;variant=text&amp;loc=en_US'}
    ShowTemplate(self,'templates/landingpage.html',template_values)
     
                   
    

class PixelHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'image/gif'
    self.response.out.write('e404')
