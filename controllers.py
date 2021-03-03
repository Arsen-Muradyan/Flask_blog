from flask import Flask, render_template, request, redirect
from flask import url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import models
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
import re
import os
from functools import wraps

def index():
  return render_template('index.html')
