from flask import Flask, render_template,request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
import pandas, dotenv, os
import google.generativeai as genai

dotenv.load_dotenv(".env")

app= Flask(__name__)
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
API_KEY=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")


firebase_admin.initialize_app(credentials.Certificate("serviceAccountKey.json"), {
    'databaseURL': ''
})
db = firestore.client()

class uploadFile(FlaskForm):
    file=FileField("File")
    upload=SubmitField("Upload")

class chatting(FlaskForm):
    chat_prompt=StringField("Enter your question")
    submit=SubmitField("Submit")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fetchAll', methods=["GET"])
def fetchAll():
    docs = db.collection("inventory_updates").stream()
    # return json format of all the docs
    return {"data": [doc.to_dict() for doc in docs]}

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    form = uploadFile()
    form2 = chatting()
    if form.validate_on_submit():
        file = form.file.data
        data = pandas.read_csv(file)
        columns = data.columns
        for index, row in data.iterrows():
            ref = db.collection("inventory_updates").document(f"{row[0]}")
            entry = {}
            for i in range(len(row)):   
                entry[columns[i]] = row[i]
            ref.set(entry)
            
        """
        TO DO 
        - retrieve data from apps script from firebase
        """
    return render_template('dashboard.html', form=form, form2=form2)

@app.route('/chat', methods=["GET", "POST"])
def send_to_Gemini():
    form2= chatting()
    if (request.method == "POST"):
        if form2.validate_on_submit():
            prmpt= form2.chat_prompt.data
            print(prmpt)
            res = model.generate_content("prmpt")
            
    return redirect(url_for("dashboard", response = res.text))

    
    # inventory_updates = db.collection("inventory_updates").document(doc).get()
    res = model.generate_content("This is a python dictionary:", inventory_updates, "Based on the information provided - product_id,product_name,product_descp,product_image,og_inventory,og_supplier,og_supplier_info,og_cfoot,og_price- for the store I need you to search on google for canadian suppliers that can offer this product.")
    print(res.text)
    # inventory_updates has this format: {'Product': 'Apple', 'Cost/Unit': '50', 'Units': '2'}
    # just send this obj to gemini 
    

if __name__ == '__main__':
    app.run()

# apis
# https://www.youtube.com/watch?v=HiyfG0Kb0WM