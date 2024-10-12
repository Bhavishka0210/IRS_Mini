import streamlit as st
import pickle
from poi_trialmerged import FINAL
import pandas as pd
from streamlit_folium import folium_static
import folium

# Custom CSS for styling
streamlit_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;1,100&display=swap');

        .hotel-bold {
            font-weight: 600;
        }

        .hotel-font {
            font-size: 20px;
            background-color: #e6f9ff;
        }

        label.css-1p2iens.effi0qh3 {
            font-size: 18px;
        }

        p {
            font-size: 18px;
        }

        li {
            font-size: 18px;
        }
        #MainMenu {
            visibility: hidden;
        } 
        button.css-135zi6y.edgvbvh9 {
            font-size: 18px;
            font-weight: 600;
        }
    </style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

# Display the title and cover image
st.image('./data/Cover-Img.png')
st.title('Personalised Travel Recommendation and Planner')

# Load the pickle file
with open("lol.pkl", "rb") as pickle_in:
    load_lol = pickle.load(pickle_in)

def output_main(Type, Duration, Budget, TYPE, Ques):
    """Generate output based on user input parameters."""
    output, info, map = FINAL(Type, Duration, Budget, TYPE, Ques)
    return [output, info, map]

def main():
    @st.cache_data
    def get_data():
        return []

    # User input options
    lis1 = ['Adventure and Outdoors', 'Spiritual', 'City Life', 'Cultural', 'Relaxing']
    lis2 = ['Family', 'Friends', 'Individual']

    Type = st.multiselect("Vacation type according to priority:", lis1)
    Duration = st.slider("Duration (days)", min_value=1, max_value=40)
    Budget = st.slider("Budget (INR)", min_value=200, max_value=150000, step=500)

    col1, col2 = st.columns(2)
    TYPE = col1.selectbox("Who are you travelling with?", lis2)
    Ques = col2.radio("Is covering maximum places a priority?", ['Yes', "No"])

    cutoff = Budget / Duration

    if st.button("What do you recommend?"):
        try:
            RESULT = output_main(Type, Duration, Budget, TYPE, Ques)
        except Exception as e:
            st.error("An error occurred while generating recommendations. Please check your inputs.")
            return

        data = get_data()  
        data.append({"Type": Type, "Duration": Duration, "Budget": Budget, "TYPE": TYPE, "Ques": Ques})
        
        FINAL_DATA = pd.DataFrame(data)
        FINAL_DATA.to_csv('data/FinalData.csv', index=False)

        Output = RESULT[0]
        Info = RESULT[1]
        Map = RESULT[2]

        st.subheader('Your Inputs')
        st.write('{}'.format(Info[0]))
        col3, col4 = st.columns(2)
        for i in range(1, len(Info)-5):
            try: 
                col3.write('{}'.format(Info[i]))
            except:
                continue
        for i in range(4, len(Info)-2):
            try: 
                col4.write('{}'.format(Info[i]))
            except:
                continue
        st.write('{}'.format(Info[-2]))

        st.header('Suggested Itinerary')
        st.markdown('<p class="hotel-font"><span class="hotel-bold">Suggested Hotel/Accommodation:</span> {}<p>'.format(Info[-1]), unsafe_allow_html=True)

        if Output:
            for i in range(len(Output)):
                st.write(f"Day {i + 1}: {Output[i]}")
        else:
            st.write("No itinerary available.")

        # Display the map
        folium_static(Map)

if __name__ == '__main__':
    main()
