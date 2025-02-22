from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import pandas, dotenv, os

dotenv.load_dotenv(".env")

app= Flask(__name__)
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
firebase_admin.initialize_app(credentials.Certificate("serviceAccountKey.json"), {
    'databaseURL': ''
})
db = firestore.client()

# Add data to Firestore
doc_ref = db.collection("proposedchange").document("user1")
# doc_ref.set({"name": "Alice", "email": "alice@example.com"})
print(db)

# Retrieve data
# user_doc = db.collection("users").document("user1").get()
# if user_doc.exists:
#     print(user_doc.to_dict())

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
        columns_list = data.columns
        for index, row in data.iterrows():
            print(index, row)
        
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