import time
import signal
import subprocess


class TestEntrypoint:
    def test_poetry_entrypoint_is_set(self):
        process = subprocess.Popen(
            [
                "poetry",
                "run",
                "poi-map",
                "--help",
            ]
        )

    def test_poetry_entrypoint_runs(self):
        process = subprocess.Popen(
            ["poetry", "run", "poi-map", "tests/test-data/local_execution/config.json"]
        )
        time.sleep(2)
        process.send_signal(signal.SIGINT)
