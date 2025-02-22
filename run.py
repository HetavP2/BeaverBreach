from flask import Flask, render_template,request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore 
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
import pandas, dotenv, os
import google.generativeai as genai
from werkzeug.utils import secure_filename
from serpapi import GoogleSearch
import requests
import json


dotenv.load_dotenv(".env")

app= Flask(__name__)
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
API_KEY=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

def call_gemini_ai(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": text
            }]
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini AI: {e}")
        return "Summary unavailable due to error."

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
        file = form.file.data
        data = pandas.read_csv(file)
        columns = data.columns
        print(data)
        for index, row in data.iterrows():
            # looping thru each
            ref = db.collection("inventory_updates").document(f"{row[index]}")
            entry = {}
            for i in range(len(row)):   
                entry[columns[i]] = row[i]
            # do analysis on each
            print(entry)
            #1.) pass to serp shopping api to find Canadian supplier
            params = {
            "engine": "google_shopping",
            "q": entry["product_name"]+" nearby manufactured in Canada",
            "api_key": "fb780cada7255e9b5a6b8ba072632893e11060b8d6799bb877f8bb2072e43a74",
            "gl": "ca",
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            shopping_results = results.get("shopping_results", [])  # Ensure it's a list
            shopping_results = shopping_results[:3]  # Keep only the first 3 results

            #2.) calculate carbon footprint for canadian supplier and american supplier
            # 3.) calculate change in cost price and profit margin

            prompt = f'''You are an expert on International US-Canada trade and are a business consultant. Below is information about a product:
            {entry}
            The product is currently being sourced suppliers from the US. The company is trying to source the product from Canada amid 25% tarrifs on all imports from the USA.

            Your task is to:
            1.) Find a Canadian supplier for the product. Below are the top 3 results from Google Shopping:
            {shopping_results}
            Determine which one out of the results is the best supplier for the product. Provide a short 20-30 word explanation for your choice.
            2.) Calculate the carbon footprint of the Canadian supplier and the US supplier.
            You should assume the business is located in Waterloo, Ontario, Canada. The carbon footprint should be in kgCO2e. Use the current information about the product to calculate both the carbon footprint from the original US Supplier and then the Canadian Supplier you have selected based on search results.
            3.) Calculate the change in cost price from switching to the Canadian Supplier and profit margin (as a percentage, based on the original selling price of the product). Try to show increased profit margin.

            4.) Provide a specific explanation on what other factors (such as CBSA/USCBP, NAFTA, CUSMA, duty rates if applicable, etc) can affect the business's product amid the tarrifs. 
            Effective February 4, 2025, the government is imposing 25 per cent tariffs on $30 billion in goods imported from the United States (U.S.).

These tariffs only apply to goods originating from the U.S., which shall be considered as those goods eligible to be marked as a good of the U.S. in accordance with the Determination of Country of Origin for the Purposes of Marking Goods (CUSMA Countries) Regulations.
"Tariff Item/Article #

Harmonized System (HS) Heading

Indicative Description"

6309.00.10

Worn clothing and other worn articles.

Used textile articles for use in the manufacture of wiping rags
6309.00.90

Worn clothing and other worn articles.

Other
6217.10.00

Other made up clothing accessories; parts of garments or of clothing accessories, other than those of heading 62.12.

6117.90.90

Other made up clothing accessories, knitted or crocheted; knitted or crocheted parts of garments or of clothing accessories.

return a json response that is an extension of the original product data with the following fields:
product_id	product_name	product_descp	product_image	og_inventory	og_supplier	og_supplier_info	og_cfoot	og_price	location	og_cost og_carbon_footprint new_carbon_footprint new_cost new_profit_margin total_savings comments_on_other_factors comments_on_supplier_choice

Make sure your ENTIRE response is ONLY a json response so that I can simply just do json.loads(your_response) to get the data.

            '''

            #3.) pass to gemini ai
            summary = call_gemini_ai(prompt)
            print(summary)
            # summary_dict = json.loads(summary)  # Parse the response into a dictionary
            # print(summary_dict)
            # ref.set(summary)
        return redirect(url_for('analytics'))
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