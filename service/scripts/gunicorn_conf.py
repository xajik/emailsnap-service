import os
import signal


reload = True
loglevel = "debug"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
host = os.environ.get("HOST", "0.0.0.0")
port = os.environ.get("PORT", "80")
bind = [f"{host}:{port}"] 
forwarded_allow_ips = (
    "*"
)
worker_class = "uvicorn.workers.UvicornWorker"
threads = 1 
worker_connections = 1000
max_requests = 0  
max_requests_jitter = 0
timeout = 300 
graceful_timeout = 300
keepalive = 2
def worker_int(worker):
    os.kill(worker.pid, signal.SIGINT)