
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
from flask import current_app as app
# from backend.forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm
from .models import *

controllers = Blueprint('controllers', __name__)

@controllers.route("/")
def home():
    return render_template("home.html")

