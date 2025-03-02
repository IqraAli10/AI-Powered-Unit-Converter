import streamlit as st
import requests
import google.generativeai as genai
import os
import plotly.express as px  # Importing Plotly for graph visualization

# Set Gemini API Key (Replace 'your-api-key' with your actual key)
API_KEY = "AIzaSyATmW-HObq5S2IufiwRknzkPskF0Pi9na4"
genai.configure(api_key=os.environ["API_KEY"])

# Function to fetch real-time exchange rates
def get_exchange_rate(from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url).json()
    return response['rates'].get(to_currency, None)

# Function to perform unit conversion with additional unit types
def convert_units(value, from_unit, to_unit):
    conversion_factors = {  # Added more unit types for conversion
        ('kg', 'lb'): 2.20462,
        ('lb', 'kg'): 0.453592,
        ('cm', 'inch'): 0.393701,
        ('inch', 'cm'): 2.54,
        ('km', 'mile'): 0.621371,
        ('mile', 'km'): 1.60934,
        ('C', 'F'): lambda c: (c * 9/5) + 32,
        ('F', 'C'): lambda f: (f - 32) * 5/9,
        ('m', 'ft'): 3.28084,  # Meters to Feet
        ('ft', 'm'): 0.3048,    # Feet to Meters
        ('l', 'gallon'): 0.264172,  # Liters to Gallons
        ('gallon', 'l'): 3.78541,     # Gallons to Liters
        ('m/s', 'km/h'): 3.6,          # Meters per second to Kilometers per hour
        ('km/h', 'm/s'): 0.277778       # Kilometers per hour to Meters per second
    }  # Closing the conversion_factors dictionary
    
    if (from_unit, to_unit) in conversion_factors:
        factor = conversion_factors[(from_unit, to_unit)]
        return factor(value) if callable(factor) else value * factor
    elif from_unit in ['USD', 'EUR', 'GBP'] and to_unit in ['USD', 'EUR', 'GBP']:
        return value * get_exchange_rate(from_unit, to_unit)
    else:
        return None

# AI Explanation Function
def get_ai_explanation(query):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    return response.text

# Function to create a graph visualization
def create_graph(data):
    fig = px.line(data, x='x_values', y='y_values', title='Unit Conversion Visualization')
    st.plotly_chart(fig)

# Streamlit UI
st.title("AI-Powered Advanced Unit Converter")

st.sidebar.header("Conversion Options")
value = st.sidebar.number_input("Enter value:", min_value=0.0, format="%.4f")
from_unit = st.sidebar.selectbox("From Unit:", ['kg', 'lb', 'cm', 'inch', 'km', 'mile', 'C', 'F', 'USD', 'EUR', 'GBP'])
to_unit = st.sidebar.selectbox("To Unit:", ['kg', 'lb', 'cm', 'inch', 'km', 'mile', 'C', 'F', 'USD', 'EUR', 'GBP'])

if st.sidebar.button("Convert"):    
    # Example data for graph visualization
    data = {
        'x_values': [1, 2, 3, 4],
        'y_values': [convert_units(value, from_unit, to_unit) for value in [1, 2, 3, 4]]  # Sample conversion results
    }
    create_graph(data)  # Call the graph creation function

    result = convert_units(value, from_unit, to_unit)
    if result is not None:
        st.success(f"{value} {from_unit} = {result:.4f} {to_unit}")
        explanation = get_ai_explanation(f"Convert {value} {from_unit} to {to_unit} and explain the process.")
        st.info(explanation)
    else:
        st.error("Conversion not supported!")

# AI Chat Assistant with History
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # Initialize chat history in session state

st.subheader("Ask AI About Unit Conversions")
user_question = st.text_input("Enter your question:", key="user_question_input", value="")  # Unique key added

if st.button("Ask AI"):
    ai_response = get_ai_explanation(user_question)
    st.write(ai_response)
    
    # Store the question and response in chat history
    st.session_state.chat_history.append({"question": user_question, "response": ai_response})
    
    # Clear the input field
    # No longer clear the input field here


# Display chat history
if st.sidebar.button("Show Chat History"):
    st.sidebar.subheader("Chat History")
    for entry in st.session_state.chat_history:
        st.sidebar.write(f"Q: {entry['question']}")
        st.sidebar.write(f"A: {entry['response']}")
        st.sidebar.write("---")  # Added separator for better readability

# Dark Mode Toggle
if st.sidebar.checkbox("Dark Mode"):
    st.markdown("""
        <style>
            body { background-color: #121212; color: white; }
        </style>
    """, unsafe_allow_html=True)
