import time
import types

import locust
import locust.events
import locust.exception
import clickhouse_driver


class ClickhouseResponse:
    def __init__(self, resp, elapsed, name, is_insert=False, exc=None):
        self.resp = resp
        self.is_insert = is_insert
        self.exc = exc
        self._failed = False
        self.event = dict(
            request_type='INSERT' if self.is_insert else 'SELECT',
            name=name,
            response_time=elapsed,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not self._failed:
            return self.failure(exc_val)
        if self.exc and not self._failed:
            return self.failure(self.exc)
        return self.success()

    def failure(self, exc):
        locust.events.request_failure.fire(
            exception=locust.exception.CatchResponseError(exc)
            if isinstance(exc, str)
            else exc,
            **self.event
        )
        self._failed = True

    def success(self):
        locust.events.request_success.fire(
            response_length=0 if self.is_insert else len(self.resp), **self.event
        )


class ClickHouseLocust(locust.Locust):
    clickhouse_settings = {}
    query_to_name_cut_threshold = 32

    def __init__(self):
        super().__init__()
        if self.host is None:
            raise locust.exception.LocustError('No host configured')

        self._ch = clickhouse_driver.Client(self.host, **self.clickhouse_settings)
        self.client = self

    def query(self, query, params=None, name=None, **kwargs):
        is_insert = isinstance(params, (list, tuple, types.GeneratorType))
        name = name or query[: self.query_to_name_cut_threshold]

        start = time.time()
        try:
            resp = self._ch.execute(query, params=params, **kwargs)
            return ClickhouseResponse(
                resp=resp,
                elapsed=self._ch.last_query.elapsed/1000.0,  # seconds to milliseconds
                name=name,
                is_insert=is_insert,
            )
        except Exception as e:
            return ClickhouseResponse(
                resp=None,
                elapsed=(time.time() - start)/1000.0,  # seconds to milliseconds
                name=name,
                is_insert=is_insert,
                exc=e,
            )
