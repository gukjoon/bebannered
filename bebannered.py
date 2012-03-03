#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import wsgiref.handlers

from google.appengine.ext import webapp

from bebannered_pages import *
from bebannered_handlers import *

application = webapp.WSGIApplication([
    #('/.*', SplashPage),
  ('/', MainPage),
  ('/howitworks', HowItWorksPage),
  ('/about',AboutPage),
  ('/privacy',PrivacyPage),
  ('/error/(.*)',ErrorPage),
  
  ('/recaptcha',ReCaptchaHandler),
  
  
  #only shown when logged out
  ('/signin',SignInPage),
  ('/signup',SignUpPage),
  #only shown when logged in
  ('/deals',DealsPage),
  ('/preferences',PreferencesPage),
  
  ('/landingpage/(.*)',LandingPageHandler),
  ('/fakelp',StaticLandingPage),
  #('/cookie',PixelHandler),
  
  #API
  ('/register',UserHandler),
  ('/login',LoginHandler),
  ('/logout',LogoutHandler),
  ('/changePassword', ChangePasswordHandler),
  #Sets preferences for a user
  ('/preferences/(.*)',PreferencesPostHandler)
  
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
