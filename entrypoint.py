import multiprocessing
import os
import subprocess
import sys
import time

PYTHON = sys.executable


def _flask_db_current() -> bool:
    result = subprocess.run(
        [PYTHON, "-m", "flask", "db", "current"],
        capture_output=True,
    )
    return result.returncode == 0


def main() -> None:
    print("Starting DocStore API...", flush=True)

    print("Testing database connection...", flush=True)
    while not _flask_db_current():
        print("Database not ready - waiting...", flush=True)
        time.sleep(5)

    print("Running database migrations...", flush=True)
    subprocess.run([PYTHON, "-m", "flask", "db", "upgrade"], check=True)
    print("Migrations complete!", flush=True)

    print("Starting Gunicorn...", flush=True)
    workers = os.environ.get(
        "GUNICORN_WORKERS", str(2 * multiprocessing.cpu_count() + 1)
    )
    args = [
        PYTHON, "-m", "gunicorn",
        "--bind", "0.0.0.0:8080",
        "--workers", workers,
        "--worker-tmp-dir", "/dev/shm",
        "--control-socket", "/dev/shm/gunicorn.ctl",
        "--log-level", "info",
    ]
    if os.environ.get("DEBUG") == "true":
        args += ["--reload", "--reload-engine", "poll"]

    args.append("main:create_app()")
    os.execv(PYTHON, args)


if __name__ == "__main__":
    main()
