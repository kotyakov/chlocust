from chlocust.client import ClickhouseClient
from chlocust.types import ValuesIn


def test_escape_values_in():
    c = ClickhouseClient('foo')
    query_tmpl = '%(test_me)s'
    query = c.substitute_params(query_tmpl, {'test_me': ValuesIn([1, 2, 3])})
    assert query == '1,2,3'
