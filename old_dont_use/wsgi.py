import sys, os
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir+"/healthcareprofessionals")
from manage import app as application

if __name__ == "__main__":
    application.run()
