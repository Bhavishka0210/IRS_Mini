import streamlit as st
import google.generativeai as palm
import os
from ics import Calendar, Event
from datetime import datetime, timedelta
import json

palm.configure(api_key=os.getenv("PALM_API_KEY"))
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name

# Streamlit app title and user input
st.title("Travel Itinerary Generator")

city = st.text_input("Enter the city you're visiting:")
start_date = st.date_input("Select the start date for your trip:", value=datetime.today())

# Set the maximum end date to 30 days after the start date
max_end_date = start_date + timedelta(days=30)

# User selects the end date of the trip
end_date = st.date_input("Select the end date for your trip:", 
                         value=start_date + timedelta(days=1),  # Default to the next day
                         min_value=start_date, 
                         max_value=max_end_date)

# Calculate the number of days between start_date and end_date
days = (end_date - start_date).days

# User preferences checkboxes
art = st.checkbox("Art")
museums = st.checkbox("Museums")
outdoor = st.checkbox("Outdoor Activities")
indoor = st.checkbox("Indoor Activities")
kids_friendly = st.checkbox("Good for Kids")
young_people = st.checkbox("Good for Young People")

# Generate itinerary button
if st.button("Generate Itinerary"):
    # Create a prompt based on user input
    prompt = f"You are a travel expert. Give me an itinerary for {city}, for {days} days, assuming each day starts at 10 am and ends at 8 pm with a buffer of 30 minutes between each activity. I like to"
    
    if art:
        prompt += " explore art,"
    if museums:
        prompt += " visit museums,"
    if outdoor:
        prompt += " engage in outdoor activities,"
    if indoor:
        prompt += " explore indoor activities,"
    if kids_friendly:
        prompt += " find places suitable for kids,"
    if young_people:
        prompt += " discover places suitable for young people,"

    prompt += """ Limit the length of the output JSON string to 1200 characters. Generate a structured JSON representation for the travel itinerary.

    {
      "days": [
        {
          "day": 1,
          "activities": [
            {
              "title": "Activity 1",
              "description": "Description of Activity 1",
              "link": "https://example.com/activity1",
              "start_time": "10:00 AM",
              "end_time": "12:00 PM",
              "location": "https://maps.google.com/?q=location1"
            },
            {
              "title": "Activity 2",
              "description": "Description of Activity 2",
              "link": "https://example.com/activity2",
              "start_time": "02:00 PM",
              "end_time": "04:00 PM",
              "location": "https://maps.google.com/?q=location2"
            }
          ]
        }
      ]
    }

    Ensure that each day has a 'day' field and a list of 'activities' with 'title', 'description', 'start_time', 'end_time', and 'location' fields. Keep descriptions concise.
    """

    # Call the OpenAI API
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=3000,
    )

    # Extract and display the generated itinerary
    itinerary = completion.result.strip()
    itinerary = itinerary[7:-3]
    itinerary_json = json.loads(itinerary)

    for day in itinerary_json["days"]:
        st.header(f"Day {day['day']}")
        for activity in day["activities"]:
            st.subheader(activity["title"])
            st.write(f"Description: {activity['description']}")
            st.write(f"Location: {activity['location']}")
            st.write(f"Time: {activity['start_time']} - {activity['end_time']}")
            st.write(f"Link: {activity['link']}")
            st.write("\n")

    # Calendar download functionality
    def get_download_link(content, filename):
        """Generates a download link for the given content."""
        b64_content = content.encode().decode("utf-8")
        href = f'<a href="data:text/calendar;charset=utf-8,{b64_content}" download="{filename}">Download {filename}</a>'
        return href

    cal = Calendar()
    start_date = datetime.now() + timedelta(days=1)

    for day, activities in enumerate(itinerary_json.get("days", []), start=1):
        for activity in activities.get("activities", []):
            event = Event()
            event.name = activity.get("title", "")
            event.description = activity.get("description", "")
            event.location = activity.get("location", "")
            event.begin = start_date + timedelta(
                days=day - 1, 
                hours=int(activity.get("start_time", "10:00 AM").split(":")[0]), 
                minutes=int(activity.get("start_time", "10:00 AM").split(":")[1][:2])
            )
            event.end = start_date + timedelta(
                days=day - 1, 
                hours=int(activity.get("end_time", "08:00 PM").split(":")[0]), 
                minutes=int(activity.get("end_time", "08:00 PM").split(":")[1][:2])
            )
            cal.events.add(event)

    cal_content = str(cal)

    # Create a download link
    st.success("Itinerary ready to export!")
    st.markdown(get_download_link(cal_content, "Itinerary.ics"), unsafe_allow_html=True)
