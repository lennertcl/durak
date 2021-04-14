from flask import render_template
from . import main

@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html")

@main.route("/rules")
def rules():
    return render_template("rules.html")
