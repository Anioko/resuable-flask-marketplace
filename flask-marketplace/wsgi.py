import sys, os

activate_this = '/home/ubuntu/flask-marketplace/venv/bin/activate_this.py'
with open(activate_this) as f:
 exec(f.read(), dict(__file__=activate_this))

sys.path.insert(0, '/home/ubuntu/flask-marketplace/marketplace/')
from manage import app as application
