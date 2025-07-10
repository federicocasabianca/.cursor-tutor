# MongoDB Materials Search

A web application for searching and managing educational materials in MongoDB. This application provides a modern interface for searching through materials and inserting new materials from a JSON dataset.

## Features

- Modern, responsive web interface
- Real-time search with relevance scoring
- Material insertion from JSON dataset
- Beautiful card-based results display
- MongoDB text search integration
- Loading states and error handling

## Project Structure

```
search-mongodb/
├── README.md
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html     # Web interface template
```

## Modular Structure (Recommended Refactor)

To keep the codebase maintainable and scalable, split the application into the following modules/blueprints:

- **app.py**: Main entry point. Handles app creation, configuration, and blueprint registration.
- **db.py**: Database connection logic and helpers for MongoDB.
- **search/**: Search-related routes and business logic.
  - `routes.py`: Search endpoints (e.g., `/search`, `/search/material/<id>`)
  - `service.py`: Search aggregation and ranking logic
- **typeahead/**: Typeahead suggestion endpoints and logic.
  - `routes.py`: `/typeahead` endpoint
  - `service.py`: Suggestion balancing, highlighting, and ranking
- **intents/**: Intent detection and taxonomy logic.
  - `routes.py`: Intent-related endpoints
  - `service.py`: Calls to external intent API, local taxonomy matching
- **taxonomy/**: Taxonomy loading and management.
  - `loader.py`: Loads and parses taxonomy CSVs
- **utils/**: Helper functions used across modules.
  - `highlight.py`: Text highlighting utilities
  - `helpers.py`: Miscellaneous helpers
- **templates/**: HTML templates for the web interface
- **static/**: (Optional) Static assets (CSS, JS, images)

**Each module/blueprint is responsible for a single concern, making the codebase easier to maintain, test, and extend.**

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your MongoDB connection details:
```
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=materials_db
COLLECTION_NAME=materials
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

### Searching Materials
- Enter search terms in the search box
- Results are displayed in cards with relevance scores
- Search works across title, description, material type, and author fields

### Inserting Materials
- Click the "Insert Materials from JSON" button to load materials from dataset.json
- Progress and results are shown via notifications

## Technical Details

- Built with Flask and MongoDB
- Uses Tailwind CSS for styling
- Implements MongoDB text search with scoring
- Responsive design for all device sizes
- Error handling and loading states

## Dependencies

- Flask 3.0.2
- PyMongo 4.6.1
- python-dotenv 1.0.1
- flask-cors 4.0.0

## Security Notes

- Never commit the `.env` file to version control
- Keep your MongoDB connection string secure
- Consider implementing IP whitelisting in MongoDB Atlas 