# gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"  # Bind to a specific IP and port
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
threads = 2  # Number of threads per worker
timeout = 120  # Workers silent for more than this many seconds are killed and restarted
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log errors to stdout
capture_output = True  # Redirect stdout/stderr to specified log files
