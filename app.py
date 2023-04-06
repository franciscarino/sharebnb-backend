from sqlalchemy import or_
import os
from dotenv import load_dotenv

from flask import (Flask, request, jsonify)

from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

load_dotenv()
