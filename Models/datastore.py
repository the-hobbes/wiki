# Authors:
#   Phelan
# 
# this file collects all of the datastore entities needed by the blog. 
from google.appengine.ext import db
import Handlers.hashing as hashing
import Handlers.common

class User(db.Model):
    '''
        user entity.
        @classmethod are decorators. This particular one means that you can call these methods on the class itself, not 
        instances (objects) of this class. User.by_id, for example. So, 'cls' is kind of like 'self'.

        These are procedural lookups, not GQL ones
    '''
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    # datastore interactions related to users
    def users_key(group = 'default'):
        # this creates the ancestor element in the database to store all the users
        return db.Key.from_path('users', group)

    @classmethod
    def by_id(cls, uid):
        # looks up user by id
        uKey = db.Key.from_path('users', 'default')
        return User.get_by_id(uid, parent = uKey)

    @classmethod
    def by_name(cls, name):
        # looks up user by name. basically select * from user where name == name, and get() returns first instance
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        # this one actually creates a new user object, based on the inputs
        # However, doesn't actually store it
        h = hashing.Hasher()
        uKey = db.Key.from_path('users', 'default')
        
        pw_hash = h.makePwHash(name, pw)
        return User(parent = uKey,
                            name = name,
                            pw_hash = pw_hash,
                            email = email)

    @classmethod
    def login(cls, name, pw):
        h = hashing.Hasher()
        # do an actual login. first, lookup the user in the datastore
        u = cls.by_name(name)
        if u and h.validatePassword(name, pw, u.pw_hash):
            # if the user exists in the datastore and the password hashes to the right value, return the user object
            return u

class Wiki(db.Model):
    '''
        wikiPage entity. 
    '''
    title = db.StringProperty(required = True)
    text = db.StringProperty(required = True)
    dateTime = db.DateTimeProperty(auto_now_add = True)

    def wiki_key(group = 'default'):
        # this creates the ancestor element in the database to store all the wiki's
        return db.Key.from_path('wiki', group)

    @classmethod
    def by_id(cls, uid):
        # looks up user by id
        wKey = db.Key.from_path('wiki', 'default')
        return Wiki.get_by_id(uid, parent = wKey)

    @classmethod
    def by_title(cls, title):
        # looks up user by name. basically select * from user where name == name, and get() returns first instance
        w = Wiki.all().filter('title =', title).get()
        return w
