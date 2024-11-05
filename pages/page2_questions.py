import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

#1. getting information from the user
st.text_input("Your company's name", key="company_name")

with st.expander("Energy Usage", expanded=True):
    electricity_bill = st.number_input("What is your average monthly electricity bill in euros?", min_value=0, value=100)
    gas_bill = st.number_input('What is your average monthly gas bill in euros?', min_value=0, value=100)
    fuel_bill = st.number_input('What is your average monthly fuel bill for transportation in euros?', min_value=0, value=100)

    energy_usage = round((electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32), 2)
    st.write("#### Energy's part in your carbot footprint is ", energy_usage, "kgCO2")

with st.expander("Waste", expanded=True):
    waste_amt = st.number_input('How much waste do you generate per month in kilograms?', min_value=0, value=50)
    recycled_prc = st.slider('How much of that waste is recycled or composed (in percentage)?', 0, 100, 20)

    waste = round(waste_amt * 12 * (0.57-recycled_prc/100), 2)
    st.write("#### Waste's part in your carbot footprint is", waste, "kgCO2")

with st.expander("Business Travel", expanded=True):
    travel_km = st.number_input('How many kilometers do your employees travel per year for business purposes?', min_value=0, value=100)
    fuel_eff = st.slider('What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?', 0, 25, 7)
    travel = round(travel_km * 1/fuel_eff * 2.31, 2)
    st.write("#### Travel's part in your carbot footprint is ", travel, "kgCO2")

response_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#2. defining functions for saving and getting user's data
def save_user_value(company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date))
    conn.commit()  
    conn.close()   

def get_user_value(type):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    if type == 'energy':
        cursor.execute('''  SELECT AVG(x)
                        FROM    (SELECT
                                    (electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32) as x
                                FROM results
                                ORDER BY x
                                LIMIT 2 - (SELECT COUNT(*) FROM results) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results))    
                   ''')
    elif type == 'waste':
        cursor.execute('''  SELECT AVG(x)
                        FROM    (SELECT
                                    waste_amt * 12 * (0.57-recycled_prc/100) as x
                                FROM results
                                ORDER BY x
                                LIMIT 2 - (SELECT COUNT(*) FROM results) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results))    
                   ''')
    elif type == 'travel':
        cursor.execute('''  SELECT AVG(x)
                        FROM    (SELECT
                                    travel_km * 1/fuel_eff * 2.31 as x
                                FROM results
                                ORDER BY x
                                LIMIT 2 - (SELECT COUNT(*) FROM results) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results))    
                   ''')
    result = cursor.fetchone()     
    conn.close()  
    return round(result[0], 2) if result else None 

#3. creating dataframe with entered data
chart_data = pd.DataFrame(
    {
        "Comparison": [st.session_state.company_name, "Average"],
        "Energy Usage": [energy_usage, get_user_value('energy')],
        "Waste": [waste, get_user_value('waste')],
        "Business Travel": [travel, get_user_value('travel')]
    }
    )

#4. submitting user's data, visualizing it and comparing it with our database's average
if st.button('Submit my data', type='primary') and st.session_state.company_name:
    save_user_value(st.session_state.company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date)

    chart_data
    st.bar_chart(chart_data, x="Comparison", y=["Energy Usage", "Waste", "Business Travel"], stack=False)





