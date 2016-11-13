from jinja2 import Markup


class MomentJs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, f):
        return Markup("<script>"
                      "document.write(moment(\"%s\").%s);"
                      "</script>" %
                      (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), f))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def from_now(self):
        return self.render("fromNow()")
