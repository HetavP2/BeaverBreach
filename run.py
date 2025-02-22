from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials as cred
from firebase_admin import db
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import pandas 
impo

app= Flask(__name__)
app.config['SECRET_KEY']="shhh"

class uploadFile(FlaskForm):
    file=FileField("File")
    upload=SubmitField("Upload")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    form = uploadFile()
    if form.validate_on_submit():
        file = form.file.data
        
        # file.save
        print(file)
        data = pandas.read_csv(file)
        """
        TO DO 
        - add data to firebase 
        - retrieve data from apps script from firebase
        """
    return render_template('dashboard.html', form=form)


if __name__ == '__main__':
    app.run()

# <!-- todo -->
# <!-- style dashboard, give data to gemini and generate response, create upload for csv and save to firebase  -->
# <!--  --> 

# apis
# https://www.youtube.com/watch?v=HiyfG0Kb0WM