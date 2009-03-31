import simplejson as json

class BasecampObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "strftime"):
            return o.strftime("%Y-%m-%dT%H:%M:%S")
        return super(BasecampObjectEncoder, self).default(o)

if __name__ == "__main__":
    import unittest
    from basecampreporting.tests.test_serialization import *
    unittest.main()
