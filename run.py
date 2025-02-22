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
        columns = data.columns
        for index, row in data.iterrows():
            ref = db.collection("inventory_updates").document(f"entry{index}")
            ref.set({
               str(columns[0]): str(row[0]),
               str(columns[1]): str(row[1]),
               str(columns[2]): str(row[2]),
            })
        
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