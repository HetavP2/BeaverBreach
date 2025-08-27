# BeaverBreach

A powerful web application that combines data analytics, AI-powered insights, and secure authentication to deliver interactive dashboards and visualizations.

## 🚀 Features

- **AI-Powered Analytics**
  - Integration with Google's Gemini AI for intelligent data insights
  - Natural language processing for data analysis
  - Automated summary generation from data sources

- **Interactive Dashboards**
  - Real-time data visualization
  - Customizable analytics views
  - Responsive design for all devices

- **Secure Firebase Backend**
  - Google Firebase authentication and database
  - Secure data storage and retrieval
  - Real-time updates and synchronization

- **Modern UI with TailwindCSS**
  - Clean, responsive interface
  - Consistent design language
  - Optimized user experience

- **Advanced Search Integration**
  - SerpAPI integration for enhanced search capabilities
  - Data enrichment from external sources

## 🔧 Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Flask** - Web framework
- **Firebase Admin** - Authentication and database
- **Google Gemini AI** - Natural language processing and AI insights
- **Pandas** - Data manipulation and analysis

### Frontend
- **HTML5/Jinja2** - Templating and structure
- **TailwindCSS** - Styling and responsive design
- **JavaScript** - Client-side interactivity

### APIs & Services
- **Google Gemini API** - AI capabilities
- **Firebase Firestore** - Database services
- **SerpAPI** - Search engine results processing

## 📂 Project Structure

```
BeaverBreach/
├── .venv/                  # Virtual environment
├── static/                 # Static assets
│   ├── css/                # CSS files
│   └── images/             # Image resources
├── templates/              # HTML templates
│   ├── analytics.html      # Analytics page
│   ├── base.html           # Base template
│   ├── dashboard.html      # Dashboard page
│   ├── home.html           # Home page
│   └── loading.html        # Loading screen
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── serviceAccountKey.json  # Firebase credentials
├── sources.txt             # Reference sources
└── tailwind.config.js      # TailwindCSS configuration
```

## 📋 Prerequisites

- Python 3.x
- pip (Python package manager)
- Google account for Gemini AI API and Firebase
- Node.js and npm (for TailwindCSS build)

## 🛠️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/BeaverBreach.git
cd BeaverBreach
```

### 2. Set up a virtual environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory with the following:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Set up Firebase
- Create a Firebase project at [firebase.google.com](https://firebase.google.com)
- Download your service account key and save it as `serviceAccountKey.json` in the project root

### 6. Run the application
```bash
python run.py
```

### 7. Access the application
Open your browser and navigate to:
```
http://localhost:5000
```

## 📈 Usage

1. **Home Page**: Start at the landing page to learn about BeaverBreach's capabilities
2. **Dashboard**: View your main metrics and KPIs
3. **Analytics**: Dive deeper into your data with AI-powered insights
4. **Data Upload**: Upload your data files for analysis
5. **AI Chat**: Interact with the AI to get specific insights about your data

