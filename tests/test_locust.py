from unittest import mock

import pytest
import clickhouse_driver

from chlocust import ClickHouseLocust


class TestClickhouseLocust:

    @pytest.fixture
    def ch_locust(self):
        clz = ClickHouseLocust
        clz.host = 'foo'
        return clz

    @pytest.fixture
    def mock_ch(self, monkeypatch):
        def _inner(ret_val=None, side_effect=None):
            m, em = mock.MagicMock(), mock.MagicMock(return_value=ret_val, side_effect=side_effect)
            m.attach_mock(em, 'execute')
            type(m).last_query = mock.PropertyMock(return_value=clickhouse_driver.client.QueryInfo())
            monkeypatch.setattr('clickhouse_driver.Client', mock.MagicMock(return_value=m))
            monkeypatch.setattr('locust.events.request_failure', mock.MagicMock())
            monkeypatch.setattr('locust.events.request_success', mock.MagicMock())
            return em
        return _inner

    def test_insert_ok(self, mock_ch, ch_locust):
        mock_ch()
        with ch_locust().query("foo", [1, 2, 3]) as resp:
            assert resp.is_insert is True
            assert resp.resp is None
            assert resp.exc is None
            assert resp.event == {'request_type': 'INSERT', 'name': 'foo', 'response_time': 0}

    def test_insert_failure(self, mock_ch, ch_locust):
        mock_ch(side_effect=Exception('lol'))
        with ch_locust().query("foo", [1, 2, 3]) as resp:
            assert resp.is_insert is True
            assert resp.resp is None
            assert resp.exc is not None and str(resp.exc) == 'lol'
            assert resp.event['request_type'] == 'INSERT'
            assert resp.event['name'] == 'foo'
            assert resp.event['response_time'] > 0

    def test_select_ok(self, mock_ch, ch_locust):
        mock_ch([(1,)])
        with ch_locust().query("foo", {'a': 1}) as resp:
            assert resp.is_insert is False
            assert resp.resp == [(1,)]
            assert resp.exc is None
            assert resp.event == {'request_type': 'SELECT', 'name': 'foo', 'response_time': 0}

    def test_select_failure(self, mock_ch, ch_locust):
        mock_ch(side_effect=Exception('kek'))
        with ch_locust().query("foo", {'a': 1}) as resp:
            assert resp.is_insert is False
            assert resp.resp is None
            assert resp.exc is not None and str(resp.exc) == 'kek'
            assert resp.event['request_type'] == 'SELECT'
            assert resp.event['name'] == 'foo'
            assert resp.event['response_time'] > 0
