# Intelligent Chatbot System

## Overview
This project is a context-aware chatbot built using Python, Flask, and MySQL. It leverages Finite Automata for structured conversation management, integrates real-time APIs for dynamic data, handles mathematical queries, and provides a user-friendly web interface.

## Features
- **Finite Automata-Based State Management:** Maintains structured and logical conversation flow.
- **Real-Time API Integration:** Fetches live weather updates (OpenWeatherMap) and calculates distances (OpenCage).
- **Database Querying:** Retrieves predefined responses from a MySQL database for common queries.
- **Mathematical Computations:** Safely evaluates arithmetic expressions entered by users.
- **Regex-Based Query Parsing:** Extracts important details from user inputs for precise responses.
- **Web Interface:** Developed with Flask, allowing smooth user interaction via forms.

## Project Structure
- `app.py` — Main chatbot API handling state management, API calls, database querying, and response generation.
- `form.py` — Flask-based web interface for user interaction.
- `mysqlsetup.py` — MySQL database setup and sample data population script.

## Technologies Used
- **Python 3**
- **Flask** (Web framework)
- **MySQL** (Database for response storage)
- **OpenWeatherMap API** (Weather data)
- **OpenCage Geocoding API** (Distance calculations)
- **Regex** (Query parsing)
- **Finite Automata Concepts** (State management)

## Setup Instructions
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/chatbot-system.git
    cd chatbot-system
    ```

2. Install required Python libraries:
    ```bash
    pip install flask mysql-connector-python requests
    ```

3. Setup the MySQL database:
    - Create a new database.
    - Run the `mysqlsetup.py` script to create tables and populate sample data.

4. Configure API keys:
    - Update `app.py` with your OpenWeatherMap and OpenCage API keys.

5. Run the application:
    ```bash
    python form.py
    ```
    Access the chatbot at `http://localhost:5000`.

## Accuracy and Performance
- Structured queries achieve 90-95% accuracy.
- Free-form queries achieve 80-85% accuracy.
- Real-time APIs and optimized database handling ensure fast and reliable responses.

Contributors: Aasavari Khire, Yash Khose, Drashi Manoria, Utkarsh Garg
