# Breakout_LLM_assesement

## Project Overview
This Flask-based web application enables intelligent data filtering using natural language prompts. By leveraging AI (Groq API), users can easily analyze CSV files through intuitive, conversational filtering.

## Features
- CSV file upload
- AI-powered natural language data filtering
- Interactive column selection
- Real-time data visualization
- CSV download functionality

## Prerequisites
- Python 3.8+
- Groq API Key

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/nikhilyadav09/Breakout_LLM_assesement.git
cd your-project-directory
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Groq API Key
1. Create a `.env` file in project root
2. Add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Application
```bash
python app.py
```

## Usage Guide
1. Upload a CSV file
2. Select a column
3. Enter a natural language prompt like:
   - "Show rows where price is greater than 100"
   - "Find entries with rating less than 3"
4. View filtered results
5. Download filtered data as CSV

## Example Prompts
- "Show me rows where time_spent is more than 20"
- "Filter data with rating equal to 4"
- "Select entries where price is less than 50"

## Error Handling
- Supports various comparison operators
- Provides clear error messages
- Handles type conversion automatically

## Technology Stack
- Flask
- Pandas
- Groq AI
- Python

## Troubleshooting
- Ensure CSV has numeric columns
- Use clear, simple language in prompts
- Check internet connection for AI processing


