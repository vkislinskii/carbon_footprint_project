import streamlit as st
import sqlite3
from datetime import datetime

st.text_input("Your company's name", key="company_name")

with st.expander("Energy Usage", expanded=True):
    electricity_bill = st.slider("What is your average monthly electricity bill in euros?", 0, 1000, 100)
    gas_bill = st.slider('What is your average monthly gas bill in euros?', 0, 1000, 100)
    fuel_bill = st.slider('What is your average monthly fuel bill for transportation in euros?', 0, 1000, 100)

    energy_usage = round((electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32), 3)
    st.write("#### Energy's part in your carbot footprint is ", energy_usage, "kgCO2")

with st.expander("Waste", expanded=True):
    waste_amt = st.slider('How much waste do you generate per month in kilograms?', 0, 100, 50)
    recycled_prc = st.slider('How much of that waste is recycled or composed (in percentage)?', 0.0, 1.0, 0.2)

    waste = round(waste_amt * 12 * (0.57-recycled_prc), 3)
    st.write("#### Waste's part in your carbot footprint is", waste, "kgCO2")

with st.expander("Business Travel", expanded=True):
    travel_km = st.slider('How many kilometers do your employees travel per year for business purposes?', 0, 1000, 100)
    fuel_eff = st.slider('What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?', 0, 25, 7)
    travel = round(travel_km * 1/fuel_eff * 2.31, 3)
    st.write("#### Travel's part in your carbot footprint is ", travel, "kgCO2")

response_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_user_value(company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date))
    conn.commit()  # Save the changes
    conn.close()   # Close the connection

if st.button('Submit my data and see analytics') and st.session_state.company_name:
    save_user_value(st.session_state.company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date)






