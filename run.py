from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import pandas, dotenv, os, uuid
dotenv.load_dotenv(".env")

app= Flask(__name__)
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
firebase_admin.initialize_app(credentials.Certificate("serviceAccountKey.json"), {
    'databaseURL': ''
})
db = firestore.client()

class uploadFile(FlaskForm):
    file=FileField("File")
    upload=SubmitField("Upload")

@app.route('/')
def home():
    # send_to_Gemini("entry0")
    return render_template('home.html')


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    form = uploadFile()
    if form.validate_on_submit():
        file = form.file.data
        data = pandas.read_csv(file)
        columns = data.columns
        for index, row in data.iterrows():
            ref = db.collection("inventory_updates").document(str(uuid.uuid4()))
            entry = {}
            for i in range(len(row)):   
                entry[columns[i]] = row[i]
            ref.set(entry)
        """
        TO DO 
        - retrieve data from apps script from firebase
        """
    return render_template('dashboard.html', form=form)

def send_to_Gemini(doc):
    inventory_updates = db.collection("inventory_updates").document(doc).get() 
    # inventory_updates has this format: {'Product': 'Apple', 'Cost/Unit': '50', 'Units': '2'}
    # just send this obj to gemini 
    
    # print(inventory_updates.to_dict())

if __name__ == '__main__':
    app.run()

# <!-- todo -->
# <!-- style dashboard, give data to gemini and generate response, create upload for csv and save to firebase  -->
# <!--  --> 

# apis
# https://www.youtube.com/watch?v=HiyfG0Kb0WM