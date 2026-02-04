import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
loglevel = "info"
accesslog = "-"
capture_output = True
timeout = 120
forwarded_allow_ips = "*"
