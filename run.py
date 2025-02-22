from flask import Flask, render_template

import firebase_admin
from firebase_admin import credentials as cred
from firebase_admin import db

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()