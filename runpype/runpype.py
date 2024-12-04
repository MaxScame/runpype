from collections import defaultdict
import json
import logging
from queue import Queue
from typing import Any, Callable


class ContextDict(dict):
    """
    Dictionary that calls a callback from the pipeline if the data has changed.

    Args:
        parent (Pype): pipeline object
    """

    def __init__(self, parent=None) -> None:
        super().__init__()
        self.parent = parent

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        self.parent.update(key)


class Context:
    """
    Pipeline Context.
    """

    def __init__(self, parent=None) -> None:
        self._ctx = ContextDict(parent)

    def set(self, key: str, value: Any) -> None:
        self._ctx[key] = value

    def is_exist(self, key) -> bool:
        if self._ctx.get(key, None):
            return True
        return False

    def get(self, key: str) -> Any:
        if key not in self._ctx:
            raise Exception(f'Key "{key}" not found in context')
        return self._ctx[key]


class Task:
    """
    Task with internal fields.
    """
    def __init__(
        self, key: str, name: str, func: Callable[[Context], Any], require: set[str]
    ) -> None:
        self.key = key
        self.name = name
        self.func = func
        self.require = require
        self.require_count = len(require) if require else 0


class Pype:
    """
    Functions pipeline with auto recalculate if values changed.
    """

    def __init__(self, name: str, context: Context = None) -> None:
        """
        Args:
            name (str): pipeline name
        """
        self.name = name or "Default pipeline"
        self.context = context or Context(self)
        self.queue = None
        self.logger = logging.getLogger(__name__)
        self.tasks: list[Task] = []
        self.task_keys: set[str] = set()
        self.ordered_tasks: list[Task] = None
        self._links = defaultdict(set)

    def add(
        self,
        key: str,
        name: str,
        func: Callable[[Context], Any],
        require: set[str] = None,
    ) -> None:
        """
        Add new task in pipeline.

        Args:
            key (str): task key
            name (str): small result description
            func (Callable[[Context], Any]): task function
            requirements (set[str], optional): task dependencies keys
        """
        if key in self.task_keys:
            raise Exception(f'Key "{key}" already added')
        else:
            self.tasks.append(Task(key, name, func, require))
            self.task_keys.add(key)
            if require is not None:
                self.chain_task_links(key, require)

        self.logger.info(f'Added task "{name}" with key "{key}" (require: {require})')

    def add_task(
        self,
        *,
        key: str,
        name: str,
        require: set[str] = None,
    ) -> Callable[..., None]:
        """
        Add new task in pipeline.

        Args:
            key (str): task key
            name (str): small result description
            requirements (set[str], optional): task dependencies keys
        """
        def wrapper(func) -> None:
            self.add(key, name, func, require)
        return wrapper

    def chain_task_links(self, addicted_key: str, requirements: set[str]) -> None:
        """
        Link tasks by key.

        Args:
            addicted_key (str): dependent task key
            requirements (set[str]): keys to the tasks required for calculation
        """
        for arg in requirements:
            self.link_keys(arg, addicted_key)

    def create_exec_queue(self) -> None:

        task_count = len(self.tasks)
        self.queue = Queue(task_count)

        sorted_tasks_by_req_count: list[Task] = sorted(
            self.tasks, key=lambda x: x.require_count
        )
        self.ordered_tasks: list[Task] = []

        # Append tasks with null-req first
        for task in sorted_tasks_by_req_count:
            if task.require_count == 0:
                self.ordered_tasks.append(task)

        while len(self.ordered_tasks) < task_count:
            for task in sorted_tasks_by_req_count:
                processed_tasks = {t.key for t in self.ordered_tasks}
                if task.require:
                    if len(task.require - processed_tasks):
                        continue
                    else:
                        if task.key in processed_tasks:
                            continue
                        self.ordered_tasks.append(task)
                        processed_tasks.add(task.key)
        for t in self.ordered_tasks:
            self.queue.put(t)

    def run(self) -> None:
        """
        Run pipeline.
        """
        self.create_exec_queue()
        self.logger.info("Starting pipeline execution..")
        while not self.queue.empty():
            task = self.queue.get()
            self.context.set(task.key, task.func(self.context))
            self.queue.task_done()

    def link_keys(self, tracking_key: str, addicted_key: str) -> None:
        """
        Linking a chain key to another key.
        If the master key is changed, the dependent link will be recalculated.

        Args:
            tracking_key (str): master key
            addicted_key (str): dependent key
        """
        self._links[tracking_key].add(addicted_key)

    def update(self, key: str) -> None:
        """
        When the value is changed, the calculation of all dependencies is called up

        Args:
            key (str): task key
        """
        if len(self._links[key]):
            self.logger.debug(f'Key "{key}" updated. Rerun...')
            for link in self._links[key]:
                if self.context.is_exist(link):
                    self.context.set(
                        link, self.get_task_by_key(link).func(self.context)
                    )

    def get_task_by_key(self, key: str) -> Task | None:
        """
        Get task object by key.

        Args:
            key (str): task key

        Returns:
            Task | None: task object or None, if it doesn't exist
        """
        for t in self.tasks:
            if key == t.key:
                return t

    @property
    def data(self) -> ContextDict:
        """
        Get context data.

        Returns:
            ContextDict: context dict
        """
        return self.context._ctx

    def __getitem__(self, key: str) -> Any:
        """
        Returns a value from the data by key

        Args:
            key (str): task key

        Raises:
            KeyError: if there is no key, an exception is raised

        Returns:
            Any: value
        """
        return self.context.get(key)

    def __setitem__(self, key: str, value: str) -> Any:
        self.context.set(key, value)

    def __repr__(self) -> str:
        return json.dumps(self.context._ctx, indent=4)
