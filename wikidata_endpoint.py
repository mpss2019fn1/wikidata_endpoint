import queue

from wikidata_request_executor import WikidataRequestExecutor


class WikidataEndpoint:

    def __init__(self, config):
        self._config = config
        self._executor_pool = queue.Queue()
        self._initialize_executor_pool()
        self.execution_blocked_until = None

    def _initialize_executor_pool(self):
        for i in range(self._config.concurrent_requests()):
            self._executor_pool.put(WikidataRequestExecutor(self))

    def return_executor(self, executor):
        if executor in self._executor_pool:
            return

        self._executor_pool.put(executor)

    def request(self):
        return self._executor_pool.get(block=True)

    def config(self):
        return self._config
