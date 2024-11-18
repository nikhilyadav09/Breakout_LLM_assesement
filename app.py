from flask import Flask, request, render_template, send_file
import pandas as pd
import os
import io
from groq import Groq
import re

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Groq client
client = Groq(api_key="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")

# Global variables
df = None
columns = []
filtered_data = None

def parse_prompt_with_groq(prompt, columns):
    """
    Use Groq to interpret the user's prompt and extract filtering conditions
    
    Args:
        prompt (str): User's natural language prompt
        columns (list): Available columns in the DataFrame
    
    Returns:
        dict: Parsed condition with column, operator, and value
    """
    try:
        # Prepare a structured prompt for the AI
        full_prompt = f"""
        Interpret the following user prompt and extract the filtering condition.
        Available columns are: {columns}
        
        Extract these details:
        1. Which column to filter
        2. What comparison operator to use (>, <, ==, >=, <=)
        3. What value to compare against
        
        Prompt: {prompt}
        
        Respond in this exact JSON format:
        {{
            "column": "column_name",
            "operator": "comparison_operator",
            "value": numeric_value
        }}
        
        If you cannot determine the condition, return an error message.
        """

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        
        response = chat_completion.choices[0].message.content
        
        # Try to parse JSON-like response
        import json
        try:
            parsed_condition = json.loads(response)
            return parsed_condition
        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            column_match = re.search(r'"column"\s*:\s*"([^"]+)"', response)
            operator_match = re.search(r'"operator"\s*:\s*"([^"]+)"', response)
            value_match = re.search(r'"value"\s*:\s*(\d+(?:\.\d+)?)', response)
            
            if column_match and operator_match and value_match:
                return {
                    "column": column_match.group(1),
                    "operator": operator_match.group(1),
                    "value": float(value_match.group(1))
                }
            
            raise ValueError("Could not parse condition from AI response")
    
    except Exception as e:
        print(f"Error parsing prompt: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    global df, columns, filtered_data

    if request.method == 'POST':
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename.endswith('.csv'):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                df = pd.read_csv(filepath)
                
                # Convert all columns to numeric where possible
                for col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except Exception as e:
                        print(f"Could not convert {col} to numeric: {e}")
                
                columns = df.columns.tolist()
                return render_template('index.html', columns=columns)
            else:
                return render_template('index.html', error="Only CSV files are supported.")
        
        elif 'column' in request.form and 'prompt' in request.form:
            try:
                # Parse prompt using Groq
                parsed_condition = parse_prompt_with_groq(request.form['prompt'], columns)
                
                if not parsed_condition:
                    return render_template('index.html', 
                                           columns=columns, 
                                           error="Could not interpret your prompt. Please rephrase.")
                
                # Validate parsed condition
                selected_column = parsed_condition['column']
                operator = parsed_condition['operator']
                value = parsed_condition['value']
                
                # Validate column exists
                if selected_column not in df.columns:
                    return render_template('index.html', 
                                           columns=columns, 
                                           error=f"Column '{selected_column}' not found in data.")
                
                # Apply filtering
                if operator == '<':
                    filtered_data = df[df[selected_column] < value]
                elif operator == '>':
                    filtered_data = df[df[selected_column] > value]
                elif operator == '==':
                    filtered_data = df[df[selected_column] == value]
                elif operator == '>=':
                    filtered_data = df[df[selected_column] >= value]
                elif operator == '<=':
                    filtered_data = df[df[selected_column] <= value]
                else:
                    return render_template('index.html', 
                                           columns=columns, 
                                           error="Unsupported comparison operator.")
                
                # Render results
                return render_template('index.html', 
                                       columns=columns, 
                                       table_data=filtered_data.to_dict(orient='records'), 
                                       table_headers=filtered_data.columns.tolist())
            
            except Exception as e:
                return render_template('index.html', 
                                       columns=columns, 
                                       error=f"Error processing your request: {str(e)}")

    return render_template('index.html', columns=columns)

@app.route('/download')
def download_filtered_data():
    global filtered_data
    if filtered_data is not None:
        # Create a CSV in memory
        output = io.StringIO()
        filtered_data.to_csv(output, index=False)
        
        # Create a send_file response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='filtered_data.csv'
        )
    return "No filtered data available", 400

if __name__ == "__main__":
    print("INFO: Starting Flask app in debug mode.")
    app.run(debug=True)
