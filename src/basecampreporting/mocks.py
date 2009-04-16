import simplejson


from basecampreporting.etree import ET
from basecampreporting.basecamp import Basecamp
from basecampreporting.project import Project

class TestBasecamp(Basecamp):
    """Subclass of Basecamp which records network transactions.
       Transactions are serialized to JSON on disk and used in lieu
       of network usage on second and subsequent requests.
       Basecamp class found here: http://pypi.python.org/pypi/BasecampWrapper/0.1
       """
    def __init__(self, baseURL, username, password):
        self.__test_responses = { 'GET': {}, 'POST': {} }
        super(TestBasecamp, self).__init__(baseURL, username, password)
    
    def _request(self, path, data=None):
        try:
            result = self.__test_request_local(path, data)
        except KeyError:
            result = super(TestBasecamp, self)._request(path, data)
            self.__cache_result(path, data, result)
        return result

    def __cache_result(self, path, data, result):
        if data:
            data = ET.tostring(data)
            if not self.__test_responses['POST'].has_key(path):
                self.__test_responses['POST'][path] = {}
            self.__test_responses['POST'][path][data] = result
        else:
            self.__test_responses['GET'][path] = result
        return result

    def __test_request_local(self, path, data):
        if data:
            data = ET.tostring(data)
            try:
                return self.__test_responses['POST'][path][data]
            except KeyError:
                print "Cache miss: POST %s\n\t%s\n" % (path, data)
                raise
        try:
            return self.__test_responses['GET'][path]
        except KeyError:
            print "Cache miss: GET %s" % (path)
            print "Cache: %s" % (pprint.pformat(self.__test_responses['GET']))
            raise

    def load_test_fixtures(self, path):
        try:
            contents = file(path, 'r').read()
            self.__test_responses = simplejson.loads(contents)
            return self.__test_responses
        except IOError, e:
            print "Warning fixture file %s not found. No fixtures loaded." % (path)
            return False

    def save_test_fixtures(self, path):
        contents = simplejson.dumps(self.__test_responses, indent=4)
        file(path, 'w').write(contents)
        return contents

class TestProject(Project):
    """Mock of Project that reads data from fixtures."""
    def __init__(self, url, id, username, password, path_to_fixtures):
        super(TestProject, self).__init__(url, id, username, password, basecamp=TestBasecamp)
        self.bc.load_test_fixtures(path_to_fixtures)
