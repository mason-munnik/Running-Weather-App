import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

def configure():
    load_dotenv()

def get_weather_data(api_key, city_name):
    parameters = {'q': city_name, 'appid': api_key, 'units': 'metric'}
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(base_url, params=parameters)
        response.raise_for_status()
        weather_data = response.json()
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    
def display_weather_data(weather_data):
    if weather_data:
        city = weather_data["name"]
        country = weather_data['sys']['country']
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        print(f"\n--- Current Weather in {city}, {country} ---")
        print(f"Temperature: {temperature}°C")
        print(f"Feels like: {feels_like}°C")
        print(f"Description: {description.capitalize()}")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")
        print("--------------------------------------")
    else:
        print("No weather data to display.")

def format_weather_for_llm(weather_data):
    if not weather_data:
        return "Could not retrieve current weather data."
    
    city = weather_data['name']
    country = weather_data['sys']['country']
    temperature = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    description = weather_data['weather'][0]['description']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']

    weather_summary = (
        f'Current weather in {city}, {country}\n'
        f'Temperature: {temperature}°C (feels like: {feels_like})\n'
        f'Conditions: {description.capitalize()}\n'
        f'Humidity: {humidity}%\n'
        f'Wind Speed: {wind_speed} m/s'
    )
    return weather_summary

def get_gemini_response(prompt_text, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')

    try:
        response = model.generate_content(prompt_text)
        return response
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return "Couldn't generate response from Gemini"
    
if __name__ == "__main__":
    configure()

    owm_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not owm_api_key or not gemini_api_key:
        print("Error: Please set the OPENWEATHERMAP_API_KEY and GEMINI_API_KEY environment variables.")
    else:
        city_name = input("Enter the city name: ")
        weather_data = get_weather_data(owm_api_key, city_name)
        display_weather_data(weather_data)
        weather_summary_for_llm = format_weather_for_llm(weather_data)

        user_query = input("\nWhat would you like to ask Gemini about the weather?")
        full_prompt = (
            f"You are an AI assistant. Here is the current weather data:\n\n"
            f"{weather_summary_for_llm}\n\n"
            f"Please respond to the following request: \"{user_query}\""
        )
        print(f"\nSending to Gemini with prompt: --\n{full_prompt}\n--")

        gemini_response = get_gemini_response(full_prompt, gemini_api_key)
        print(f"\n--- Gemini's Response: ---\n{gemini_response}\n--------------------------")