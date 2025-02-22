from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials as cred
from firebase_admin import db
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import pandas,os
from werkzeug.utils import secure_filename

app= Flask(__name__)
app.config['SECRET_KEY']="123443525"
app.config['UPLOAD_FOLDER']="allfiles"

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
        data = pandas.read_csv(file)

        """
        
        for index, row in data.iterrows():
            data["Quan"]
product = data["Product"]
units = data["Units"]
cost_unit = data["Cost/Unit"]
total_cost = data["Total Cost"]

        """
        
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