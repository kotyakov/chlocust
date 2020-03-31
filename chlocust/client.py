import clickhouse_driver
from clickhouse_driver.util.escape import escape_param

from .types import ValuesIn


class ClickhouseClient(clickhouse_driver.Client):
    def substitute_params(self, query, params):
        if not isinstance(params, dict):
            raise ValueError('Parameters are expected in dict form')

        escaped = {}
        for key, value in params.items():
            escaped[key] = (
                ','.join(map(str, value))
                if isinstance(value, ValuesIn)
                else escape_param(value)
            )
        return query % escaped
