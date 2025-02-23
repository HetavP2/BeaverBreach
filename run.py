from flask import Flask, render_template,request, redirect, url_for, session
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
import re  # Add this import at the top

def sanitize_gemini_response(response):
    # Remove any markdown code blocks
    response = re.sub(r'```json\s*|\s*```', '', response, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    response = response.strip()
    
    # Try to fix common JSON formatting issues
    try:
        # Parse and re-serialize to ensure valid JSON
        parsed = json.loads(response)
        return json.dumps(parsed)
    except json.JSONDecodeError:
        # If parsing fails, try to clean up common issues
        response = re.sub(r'[\n\r\t]', '', response)  # Remove newlines and tabs
        response = re.sub(r',\s*}', '}', response)     # Remove trailing commas
        return response


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
        # print(f"Error calling Gemini AI: {e}")
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

@app.route('/loading', methods=["GET", "POST"])
def loading():
    # data = request.args["data"]
    # columns = request.args["columns"]
    data_json = session.get('data', '[]')  # Get JSON from session
    columns = session.get('columns', [])  # Get column names

    # Convert JSON string back to DataFrame
    data = pandas.DataFrame.from_records(json.loads(data_json)) if data_json else pandas.DataFrame()


    for index, row in data.iterrows():
        # looping thru each
        doc_id = str(index)
        ref = db.collection("inventory_updates").document(f"{doc_id}")
        entry = {}
        for i in range(len(row)):   
            entry[columns[i]] = row[i]
        # do analysis on each
        # print(entry)
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
        shopping_results = shopping_results[:5]  # Keep only the first 3 results

        #2.) calculate carbon footprint for canadian supplier and american supplier
        # 3.) calculate change in cost price and profit margin

        prompt = f'''You are an expert on International US-Canada trade and are a business consultant. Below is information about a product:
        {entry}
        The product is currently being sourced suppliers from the US. The company is trying to source the product from Canada amid 25% tarrifs on all imports from the USA.

        Your task is to:
        1.) Find a Canadian supplier for the product. Below are the top 6 results from Google Shopping. Make sure you pick a supplier who is CANADIAN and manufactures from CANADA:
        {shopping_results}
        Determine which one out of the results is the best supplier for the product. Your decision should ensure the supplier manufactures in Canada and is cheaper. Provide a short 20-30 word explanation for your choice.
        2.) Calculate the carbon footprint of the Canadian supplier and the US supplier. Use tonnes of CO2e. the values should be 
        You should assume the business is located in Waterloo, Ontario, Canada. The carbon footprint should be in kgCO2e. Use the current information about the product to calculate both the carbon footprint from the original US Supplier and then the Canadian Supplier you have selected based on search results. If you do not have enough info, make a prediction based on the product type, distance from supplier, etc and give a numerical value
        3.) Calculate the change in cost price from switching to the Canadian Supplier and profit margin (as a percentage, based on the original selling price of the product). Try to show that the price has decreased and the profit margin has increased, as you account for the 25% increase in tarrifs for the american supplier.

        4.) Provide a specific explanation on what other factors (such as CBSA/USCBP, NAFTA, CUSMA, duty rates if applicable, etc) can affect the business's product amid the tarrifs. 
        Effective February 4, 2025, the government is imposing 25 per cent tariffs on $30 billion in goods imported from the United States (U.S.).

These tariffs only apply to goods originating from the U.S., which shall be considered as those goods eligible to be marked as a good of the U.S. in accordance with the Determination of Country of Origin for the Purposes of Marking Goods (CUSMA Countries) Regulations. Make sure to reference them in your short comments on other influencing factors.
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
product_id	product_name	product_descp	product_image	og_inventory	og_supplier_name	og_supplier_info	og_cfoot	og_price	location	og_cost og_carbon_footprint new_carbon_footprint new_cost new_profit_margin total_savings comments_on_other_factors comments_on_supplier_choice new_supplier_name

Make sure your ENTIRE response is ONLY a json response so that I can simply just do json.loads(your_response) to get the data. Do NOT apply any other markdown formatting or anything. Just return a json response.

        '''

        #3.) pass to gemini ai
        summary = call_gemini_ai(prompt)
        # Sanitize the response
        sanitized_summary = sanitize_gemini_response(summary)

        try:
            summary_dict = json.loads(sanitized_summary)  # Parse the sanitized response
            ref.set(summary_dict)  # Push the DICTIONARY to Firebase
            print("Firebase update successful")
        except json.JSONDecodeError as e:
            # print(f"JSON Error: {e}")
            # Fallback: Save raw text for debugging
            ref.set({"error": str(e), "raw_response": sanitized_summary})
        return redirect(url_for('analytics'))
    return render_template('loading.html')

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    form = uploadFile()
    if form.validate_on_submit():
        file = form.file.data
        data = pandas.read_csv(file)
        session['data'] = data.to_json(orient='records')
        session['columns'] = data.columns.tolist()

        return redirect(url_for('loading'))

        # print(data)
    return render_template('dashboard.html', form=form)

chat_his=[]
chat1 = model.start_chat(history=chat_his)
messages=[]

@app.route('/analytics', methods=["GET", "POST"])
def analytics():
    form2 = chatting()
    collection = db.collection("inventory_updates").get()
    all_rec=[]
    for row in collection:
        all_rec.append(row.to_dict())
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

    #     print(user_doc.to_dict())
    return render_template('analytics.html', all_rec=all_rec, form2=form2, chat_history = chat_his, messages=messages)
    
if __name__ == '__main__':
    app.run()

# apis
# https://www.youtube.com/watch?v=HiyfG0Kb0WM