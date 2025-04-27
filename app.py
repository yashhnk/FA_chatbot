from flask import Flask, request, jsonify
import mysql.connector
import datetime
import re
import os
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from urllib.parse import quote
import ast

# Load environment variables
load_dotenv()

# Finite Automata States
class ChatState:
    START = "START"
    WEATHER = "WEATHER"
    TRAVEL = "TRAVEL"
    MATH = "MATH"
    TIME_DATE = "TIME_DATE"
    GENERAL = "GENERAL"
    WEATHER_LOCATION = "WEATHER_LOCATION"
    TRAVEL_DESTINATION = "TRAVEL_DESTINATION"

# Finite Automata Transition Table
TRANSITION_TABLE = {
    ChatState.START: {
        'weather': ChatState.WEATHER,
        'temperature': ChatState.WEATHER,
        'forecast': ChatState.WEATHER,
        'climate': ChatState.WEATHER,
        'travel': ChatState.TRAVEL,
        'flight': ChatState.TRAVEL,
        'train': ChatState.TRAVEL,
        'bus': ChatState.TRAVEL,
        'distance': ChatState.TRAVEL,
        'from': ChatState.TRAVEL,
        'to': ChatState.TRAVEL,
        'calculate': ChatState.MATH,
        'math': ChatState.MATH,
        'time': ChatState.TIME_DATE,
        'date': ChatState.TIME_DATE,
        'day': ChatState.TIME_DATE,
        'today': ChatState.TIME_DATE,
        'default': ChatState.GENERAL
    },
    ChatState.WEATHER: {
        'in': ChatState.WEATHER_LOCATION,
        'for': ChatState.WEATHER_LOCATION,
        'at': ChatState.WEATHER_LOCATION,
        'default': ChatState.WEATHER
    },
    ChatState.TRAVEL: {
        'from': ChatState.TRAVEL_DESTINATION,
        'to': ChatState.TRAVEL_DESTINATION,
        'between': ChatState.TRAVEL_DESTINATION,
        'and': ChatState.TRAVEL_DESTINATION,
        'default': ChatState.TRAVEL
    },
    ChatState.TIME_DATE: {
        'default': ChatState.START
    },
    ChatState.MATH: {
        'default': ChatState.START
    },
    ChatState.GENERAL: {
        'default': ChatState.START
    }
}


# Flask App Initialization
app = Flask(__name__)

# Database setup function
def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD", "Yyaasshhnk#@2511"),
        database="chatbot_db"
    )
    cursor = conn.cursor()

    tables = {
        "weather": """
            CREATE TABLE IF NOT EXISTS weather (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_pattern VARCHAR(255) NOT NULL,
                response TEXT NOT NULL
            )
        """,
        "maths": """
            CREATE TABLE IF NOT EXISTS maths (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_pattern VARCHAR(255) NOT NULL,
                response TEXT NOT NULL
            )
        """,
        "travel": """
            CREATE TABLE IF NOT EXISTS travel (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_pattern VARCHAR(255) NOT NULL,
                response TEXT NOT NULL
            )
        """,
        "general_convo": """
            CREATE TABLE IF NOT EXISTS general_convo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_pattern VARCHAR(255) NOT NULL,
                response TEXT NOT NULL
            )
        """,
        "time_date": """
            CREATE TABLE IF NOT EXISTS time_date (
                id INT AUTO_INCREMENT PRIMARY KEY,
                input_pattern VARCHAR(255) NOT NULL,
                response TEXT NOT NULL
            )
        """
    }

    for table_name, table_query in tables.items():
        try:
            cursor.execute(table_query)
        except mysql.connector.Error as err:
            print(f"Error creating table {table_name}: {err}")

    conn.commit()
    return conn, cursor

# FA State Manager
class StateMachine:
    def __init__(self):
        self.current_state = ChatState.START
        self.context = {}

    def transition(self, user_input):
        user_input_lower = user_input.lower()
        next_state = None

        # Debugging: Print the current state
        print(f"[DEBUG] Current state: {self.current_state}")

        # Check if the current state exists in TRANSITION_TABLE
        if self.current_state not in TRANSITION_TABLE:
            print(f"[ERROR] State '{self.current_state}' not found in TRANSITION_TABLE. Resetting to START.")
            self.current_state = ChatState.START
            return self.current_state  # Exit early to avoid KeyError

        # Process input
        for _ in range(2):  # Allow two passes
            for trigger, target_state in TRANSITION_TABLE[self.current_state].items():
                if trigger in user_input_lower and trigger != 'default':
                    next_state = target_state
                    break

            if next_state is None:
                next_state = TRANSITION_TABLE[self.current_state].get('default', ChatState.START)

            print(f"[DEBUG] Transitioning to: {next_state}")

            self.current_state = next_state

        return self.current_state




def extract_location(user_input):
    patterns = [
        r'weather in ([a-zA-Z\s]+)',
        r'weather (?:for|at|like in) ([a-zA-Z\s]+)',
        r'what\'?s the weather (?:in|for|at) ([a-zA-Z\s]+)',
        r'how is the weather in ([a-zA-Z\s]+)',
        r'tell me (?:the )?weather (?:for|in|at) ([a-zA-Z\s]+)',
        r'(?:forecast|temperature) (?:for|in|at) ([a-zA-Z\s]+)'
    ]
    
    user_input_lower = user_input.lower()
    for pattern in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            return match.group(1).strip()
    return None

# Fetch weather from API
def get_weather_from_api(location):
    if not location:
        return "Please specify a location for the weather forecast. Example: 'What's the weather in London?'"

    weather_api_key = os.getenv("WEATHER_API_KEY", "80f6afe8d2ee43b104b0b19c857a79ad")
    
    try:
        place_encoded = quote(location)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={place_encoded}&appid={weather_api_key}&units=metric"
        
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            error_msg = data.get("message", "Unknown error")
            return f"Sorry, I couldn't find weather information for {location}. ({error_msg})"

        weather_desc = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        return (f"The weather in {location.capitalize()} is {weather_desc}. "
                f"Temperature: {temperature}°C, "
                f"Humidity: {humidity}%, "
                f"Wind Speed: {wind_speed} m/s")

    except requests.exceptions.RequestException as e:
        return f"Failed to connect to weather service. Please try again later."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"


def extract_places(user_input):
    # Match multiple patterns including missing prepositions
    patterns = [
        r'(?:from|between)\s+(.+?)\s+(?:to|and)\s+(.+)',  # "from X to Y" / "between X and Y"
        r'(.+?)\s+(?:to|and)\s+(.+?)\s+(?:distance|far)',  # "X to Y distance"
        r'(?:distance|far)\s+(?:from|between)\s+(.+?)\s+(?:to|and)\s+(.+)'  # "distance from X to Y"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            return (match.group(1).strip(), match.group(2).strip())
    return None

# Get distance using OpenCage API
def get_distance_from_api(place1, place2):
    opencage_api_key = os.getenv("OPENCAGE_API_KEY", "718e2ad086b843759caebfd45f6fd61d")
    
    try:
        def get_coordinates(place):
            url = f"https://api.opencagedata.com/geocode/v1/json?q={quote(place)}&key={opencage_api_key}"
            response = requests.get(url)
            data = response.json()
            
            if not data.get('results'):
                return None
            # Get highest confidence result
            best_result = max(data['results'], key=lambda x: x.get('confidence', 0))
            return best_result['geometry']

        coords1 = get_coordinates(place1)
        coords2 = get_coordinates(place2)

        if not coords1:
            return f"Could not find location: {place1}"
        if not coords2:
            return f"Could not find location: {place2}"

        distance = geodesic((coords1["lat"], coords1["lng"]), 
                         (coords2["lat"], coords2["lng"])).km
                         
        return (f"Distance between {place1.title()} and {place2.title()} "
                f"is approximately {round(distance, 2)} km.")

    except Exception as e:
        return f"Error calculating distance: {str(e)}"

# Math Expression Evaluator
# Math Expression Evaluator - Fixed Version
def calculate_math_expression(user_input):
    try:
        # Extract math expression using regex
        math_expression = re.search(
            r'((?:\d+|\().*?(?:\d+|\)))',  # Match from first number or ( to last number or )
            user_input.replace(" ", "")
        )
        
        if not math_expression:
            return "Please provide a valid mathematical expression like '5+3' or 'calculate 10/2'"

        expression = math_expression.group(1)
        
        # Enhanced safety check
        if not re.match(r'^[-+*/()\d.\s]+$', expression):
            return "Invalid characters in mathematical expression"

        # Restricted evaluation environment
        allowed_chars = {'+', '-', '*', '/', '(', ')', '.', ' '}
        sanitized = ''.join([c for c in expression if c in allowed_chars or c.isdigit()])
        
        result = eval(sanitized, {"_builtins_": None}, {})
        return f"The answer is {round(result, 4) if isinstance(result, float) else result}."
    
    except Exception as e:
        return f"Calculation error: {str(e)}. Please check your input format."

def get_response(user_input, cursor):
    state_machine = StateMachine()
    state = state_machine.transition(user_input)
    
    # Weather handling
    if state in [ChatState.WEATHER, ChatState.WEATHER_LOCATION]:
        location = extract_location(user_input)
        if not location:
            return "Could you clarify the location for the weather forecast? Example: 'weather in London'"
        return get_weather_from_api(location)

    # Travel/distance handling
    elif state in [ChatState.TRAVEL, ChatState.TRAVEL_DESTINATION]:
        places = extract_places(user_input)
        if not places or not all(places):
            return "Please provide both locations in format: 'distance from <start> to <destination>'"
            
        if places[0].lower() == places[1].lower():
            return "Start and destination locations cannot be the same."
            
        return get_distance_from_api(*places)

    # Math handling
    elif state == ChatState.MATH:
        # First try direct calculation
        try:
            return calculate_math_expression(user_input)
        except:
            # If that fails, try extracting numbers and operators
            numbers = re.findall(r'\d+', user_input)
            operators = re.findall(r'[+\-*/]', user_input)
            
            if len(numbers) < 2 or not operators:
                return "Please provide a valid expression like '5+3' or 'calculate 10 divided by 2'"
            
            expression = f"{numbers[0]}{operators[0]}{numbers[1]}"
            return calculate_math_expression(expression)

    # Time/date handling
    elif state == ChatState.TIME_DATE:
        now = datetime.datetime.now()
        if re.search(r'\btime\b', user_input.lower()):
            return f"Current time: {now.strftime('%H:%M:%S %Z')}"
        elif re.search(r'\bdate\b', user_input.lower()):
            return f"Today's date: {now.strftime('%A, %B %d, %Y')}"
        elif re.search(r'\bday\b', user_input.lower()):
            return f"Today is: {now.strftime('%A')}"
        return "I couldn't understand the date/time request."


    # General fallback
    try:
        cursor.execute("SELECT response FROM general_convo WHERE input_pattern = %s", 
                      (user_input,))
        if result := cursor.fetchone():
            return result[0]
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    
    return "I'm not sure how to respond to that. Could you rephrase your question?"

# Flask API route
@app.route("/get_response", methods=["POST"])
def get_response_api():
    try:
        conn, cursor = setup_database()
        user_input = request.json.get("user_input", "").strip()
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        response = get_response(user_input, cursor)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
@app.route("/")
def home():
    return "Chatbot is running. Use the appropriate route to talk to it.."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
