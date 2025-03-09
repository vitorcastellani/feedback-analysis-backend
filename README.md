# Feedback Analysis API

![Python](https://img.shields.io/badge/Python-3.12-4)
![Flask](https://img.shields.io/badge/Flask-3.1.0-blue.svg)
![Flask-CORS](https://img.shields.io/badge/Flask--CORS-5.0.1-blue.svg)
![Flask-OpenAPI3](https://img.shields.io/badge/Flask--OpenAPI3-4.1.0-blue.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-2.10.6-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.38-blue.svg)
![SQLAlchemy-Utils](https://img.shields.io/badge/SQLAlchemy--Utils-0.41.2-blue.svg)
![Python-dotenv](https://img.shields.io/badge/Python--dotenv-1.0.1-blue.svg)
![Pytest](https://img.shields.io/badge/Pytest-8.3.5-blue.svg)
![VaderSentiment](https://img.shields.io/badge/VaderSentiment-3.3.2-blue.svg)
![Langdetect](https://img.shields.io/badge/Langdetect-1.0.9-blue.svg)
![Deep Translator](https://img.shields.io/badge/Deep--Translator-1.11.4-blue.svg)

## 📌 Project Overview
The **Feedback Analysis API** is a simple MVP designed to collect, store, and analyze user feedback. This project is part of the **Postgraduate Software Engineering Program at PUC-RIO** and was developed by **Vitor Fernando Castellani**.

The API provides functionalities to:
- Store user feedback messages.
- Retrieve feedback entries.
- Perform sentiment analysis using Natural Language Processing (NLP).
- Store the sentiment analysis results.
- Utilize SQLite as the database for easy deployment and testing.

## 🚀 How to Run the Project
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/vitorcastellani/feedback-analysis-backend.git
cd feedback-analysis-backend
```

### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
```

### 3️⃣ Activate the Virtual Environment
- **Windows:**
```sh
venv\Scripts\activate
```
- **Mac/Linux:**
```sh
source venv/bin/activate
```

### 4️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 5️⃣ Run the API
```sh
python app.py
```
Or using Flask directly:
```sh
flask run
```

The API will be available at: `http://127.0.0.1:5000`

## 🧪 Running the Tests
To execute all the unit and integration tests, run:
```sh
pytest -v
```
By default, a test database (`test.sqlite`) will be created in the `database/` folder, separate from the production database (`production.sqlite`).

## 📂 Database Information
The API uses **SQLite** as the database engine.
- In production mode, the database file will be: `database/production.sqlite`.
- For integration tests, the database file will be: `database/test.sqlite`.

---
Developed by **Vitor Fernando Castellani** - PUC-RIO Software Engineering Postgraduate Program