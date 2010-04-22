import sys
import urllib2
from json import loads

base_url = "http://graph.facebook.com"

# from http://developers.facebook.com/docs/reference/api/user
connections = ["base", "home", "feed", "tagged", "posts", "picture",\
                "friends", "activities", "interests", "music", "books",
                "movies", "television", "likes", "photos", "albums",
                "videos", "groups", "statuses", "links", "notes",
                "events", "inbox", "outbox", "updates"]
# this not json, so don't parse it
not_json = ["picture",]

# some of the connections require you to be logged in and will 
# raise a 500 error, set this to True and those will be silently swallowed
swallow_not_allowed = True

# this catches if you search for a user who does not exist
class NotFound(Exception): pass
class NotAllowed(Exception): pass

class FacebookUser:
    def get(self, attr):
        """ Gets from facebook and parses if appropriate """
        if attr:
            url = "%s/%s/%s" % (base_url, self._name, attr)
        else:
            url = "%s/%s" % (base_url, self._name)
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            if attr:
                raise NotAllowed(e)
            else:
                raise NotFound(e)

        content = response.read()
        if attr not in not_json:
            content = loads(content)
        return content
    
    def __init__(self, name):
        """ Does an initial get of base data for the user """
        self._name = name
        self._data = {"base":self.get(None)}
    
    def __getattr__(self, attr):
        if attr in connections:
            if attr not in self._data:
                try:
                    self._data[attr] = self.get(attr)
                except NotAllowed:
                    if swallow_not_allowed:
                        self._data[attr] = None
                    else:
                        raise
            return self._data[attr]
        raise AttributeError, attr
    
if __name__=="__main__":
    if len(sys.argv) < 2:
        print "Syntax: fb.py name"
        sys.exit()
    
    # example
    name = sys.argv[1]
    fb = FacebookUser(name)
    print "User: %s" % name

    for connection in connections:
        print
        print connection
        print "-" * 40
        if connection in not_json:
            print getattr(fb, connection)[:30], "..."
        else:
            print getattr(fb, connection)
            