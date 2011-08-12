from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
import facebook

# Grab the user model.
UserModel = User
if hasattr(settings, 'FACEBOOK_USER_MODEL'):
    parts = settings.FACEBOOK_USER_MODEL.split('.')
    module_name = '.'.join(parts[0:-1]) 
    
    module = __import__(module_name)
    for part in parts[1:]:
        module = getattr(module, part)
    UserModel = module

class FacebookBackend(ModelBackend):
    """ Authenticate a facebook user. """
    def authenticate(self, fb_uid=None, fb_graphtoken=None):
        """ If we receive a facebook uid then the cookie has already been validated. """
        if fb_uid:
            user, created = UserModel.objects.get_or_create(username=fb_uid)
            return user
        return None

class FacebookProfileBackend(ModelBackend):
    """ Authenticate a facebook user and autopopulate facebook data into the users profile. """
    def authenticate(self, fb_uid=None, fb_graphtoken=None):
        print "authenticate with fb_uid=%s and fb_graphtoken=%s" % (fb_uid, fb_graphtoken)
        """ If we receive a facebook uid then the cookie has already been validated. """
        if fb_uid and fb_graphtoken:
            user, created = UserModel.objects.get_or_create(username=fb_uid)
            print "user=%s, created=%s" % (user, created)
            if created:
                # It would be nice to replace this with an asynchronous request
                graph = facebook.GraphAPI(fb_graphtoken)
                me = graph.get_object('me')
                print "me=%s" % me
                if me:
                    print "first_name=%s" % me['first_name']
                    if me.get('first_name'): user.first_name = me['first_name']
                    if me.get('last_name'): user.last_name = me['last_name']
                    if me.get('email'): user.email = me['email']
                    user.save()

            return user
        return None
