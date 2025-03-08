from flask import redirect
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info
from config.db import engine, Base
from routes.feedback import feedback_bp

# Swagger Info
info = Info(title="Feedback API", version="1.0.0", description="Feedback API for Collecting User Feedback and Analyzing Sentiments")

# Initialize Flask app
app = OpenAPI(__name__, info=info)

# Enable CORS
CORS(app)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Register the Blueprint with OpenAPI
app.register_api(feedback_bp)

# Root route to redirect to the OpenAPI documentation
@app.route("/")
def home():
    """Redireciona para a documentação da API."""
    return redirect("/openapi")

# Execute the app
if __name__ == "__main__":
    app.run(debug=True)
