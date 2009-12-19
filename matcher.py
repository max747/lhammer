""" Matcher class """

import re

class Matcher:
    """Find patterns in the given data, you must feed data first and then
    you can do as many finds as you want"""
    def feed(self, data):
        self.data = data.replace('\n', '')

    def find(self, pattern):
        matches = re.findall(pattern, self.data)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        else:
            return matches
