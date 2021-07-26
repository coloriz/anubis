import logging
import shlex
import subprocess
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError, CancelledError

from .models import Job


class JobExecutor:
    _logger = logging.getLogger(__name__)

    def __init__(self, max_workers=1):
        self._logger.info('Job executor initialized.')
        self._pool = ThreadPoolExecutor(max_workers)
        self._fs = {}

    def submit(self, job: Job):
        future = self._pool.submit(self._execute, job)
        self._fs[job] = future
        # Remove the future object from the local store when it's done
        future.add_done_callback(lambda _: self._pop(job))
        future.add_done_callback(lambda f: self._after_execute(job, f))

    def cancel(self, job: Job) -> bool:
        future = self._fs.get(job)
        if future is None:
            return False
        return future.cancel()

    def _pop(self, job: Job):
        return self._fs.pop(job, None)

    @classmethod
    def _before_execute(cls, job: Job):
        job.set_state_running()
        job.save()

    @classmethod
    def _after_execute(cls, job: Job, future: Future):
        try:
            p = future.result()
            job.set_state_done(p.returncode, p.stdout, p.stderr)
        except TimeoutError:
            job.set_state_timeout()
        except CancelledError:
            job.set_state_cancelled()
        job.save()

    @classmethod
    def _execute(cls, job: Job):
        cls._before_execute(job)
        # Format subprocess args
        commander = job.commander
        command = commander.args_fmt.format_map({
            'id': shlex.quote(commander.id),
            'script': shlex.quote(job.script)
        })
        args = shlex.split(command)
        cls._logger.info(f'Running {job} with args: {args}')

        try:
            p = subprocess.run(args, capture_output=True, timeout=job.timeout, text=True)
        except subprocess.TimeoutExpired:
            cls._logger.info(f'Timeout expired! {job}')
            raise TimeoutError

        cls._logger.debug(f'Done {job}')
        return p
