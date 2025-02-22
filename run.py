from flask import Flask, render_template,request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
import pandas, dotenv, os
import google.generativeai as genai
from werkzeug.utils import secure_filename


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
    chat_prompt=StringField("What's on your mind today?")
    submit=SubmitField("Submit")

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/loading')
def loading():
    return render_template('loading.html')


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    form = uploadFile()
    if form.validate_on_submit():
        file=request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOADFOLDER"], filename)
        file.save(file_path)  # Save file temporarily
        
        # Upload file to Gemini AI
        uploaded_file = genai.upload_file(file_path)
        print(f"File uploaded successfully! File ID: {uploaded_file.name}")
   
        # file = form.file.data
        # file.read()
        # data = pandas.read_csv(file)
        # columns = data.columns
        # for index, row in data.iterrows():
        #     ref = db.collection("inventory_updates").document(f"{row[1]}")
        #     entry = {}
        #     for i in range(len(row)):   
        #         entry[columns[i]] = row[i]
        #     ref.set(entry)
        # return redirect(url_for('analytics'))
    return render_template('dashboard.html', form=form)

chat_his=[]
chat1 = model.start_chat(history=chat_his)
messages=[]

@app.route('/analytics', methods=["GET", "POST"])
def analytics():
    form2 = chatting()
    if (request.method == "POST"):
        if form2.validate_on_submit():
            message = form2.chat_prompt.data
            messages.append(message)
            res = chat1.send_message(message, stream=True)
            for chunk in res:
                pass
                # print(chunk.text, end="", flush=True)
                # print(chunk.candidates[0].content.role)
            # print(res)
            chat_his.append(res)
            return redirect(url_for('analytics'))

    return render_template('analytics.html', form2=form2, chat_history = chat_his, messages=messages)
    
if __name__ == '__main__':
    app.run()

# apis
# https://www.youtube.com/watch?v=HiyfG0Kb0WM