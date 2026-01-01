# Streamlit UI - Yad2 Semantic Search

Simple web interface for the Yad2 Semantic Search Engine.

## Features

- 🔍 Natural language search in Hebrew
- 🎯 Advanced filtering (price, rooms, location, features)
- 📊 Ranked results with similarity scores
- 🏠 Detailed listing information display
- 📱 Responsive layout

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

2. **Set API URL (optional):**
   ```bash
   # Default is http://localhost:8000
   export API_BASE_URL=http://localhost:8000
   ```

## Running

1. **Make sure the FastAPI backend is running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Streamlit:**
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Open your browser:**
   - Streamlit will automatically open at `http://localhost:8501`
   - Or navigate to the URL shown in the terminal

## Usage

1. Enter a search query in Hebrew (e.g., "דירה 2 חדרים בתל אביב")
2. Optionally set filters in the sidebar (price, rooms, location, features)
3. Click "חפש" (Search) button
4. Browse results with detailed listing information

## Configuration

The UI connects to the FastAPI backend. By default, it expects:
- API URL: `http://localhost:8000`
- API Endpoint: `/api/v1/search`

You can change the API URL by setting the `API_BASE_URL` environment variable.

