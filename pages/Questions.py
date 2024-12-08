import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#1. getting information from the user
st.text_input("Your company's name", key="company_name")

with st.expander("Energy Usage Questions", expanded=True):
    electricity_bill = st.number_input("What is your average monthly electricity bill in euros?", min_value=0, value=None, placeholder="Type a number...")
    gas_bill = st.number_input('What is your average monthly gas bill in euros?', min_value=0, value=None, placeholder="Type a number...")
    fuel_bill = st.number_input('What is your average monthly fuel bill for transportation in euros?', min_value=0, value=None, placeholder="Type a number...")

    if pd.isna(electricity_bill) + pd.isna(gas_bill) + pd.isna(fuel_bill) == False:
        energy_usage = round((electricity_bill * 12 * 0.0005) + (gas_bill * 12 * 0.0053) + (fuel_bill * 12 * 2.32), 2)
        st.write("#### Energy's part in your carbot footprint is ", energy_usage, "kgCO2")

with st.expander("Waste Questions", expanded=True):
    waste_amt = st.number_input('How much waste do you generate per month in kilograms?', min_value=0, value=None, placeholder="Type a number...")
    recycled_prc = st.slider('How much of that waste is recycled or composed (in percentage)?', 0, 100, 20)

    if pd.isna(waste_amt) == False:
        waste = round(waste_amt * 12 * (0.57-recycled_prc/100), 2)
        st.write("#### Waste's part in your carbot footprint is", waste, "kgCO2")

with st.expander("Business Travel Questions", expanded=True):
    travel_km = st.number_input('How many kilometers do your employees travel per year for business purposes?', min_value=0, value=None, placeholder="Type a number...")
    fuel_eff = st.slider('What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?', 1, 25, 7)

    if pd.isna(travel_km) == False:
        travel = round(travel_km * fuel_eff * 2.31, 2)
        st.write("#### Travel's part in your carbot footprint is ", travel, "kgCO2")

response_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#2. defining functions for saving and getting user's data
def save_user_value(company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date, energy_usage, waste, travel):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO results_raw VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date))
    cursor.execute('''INSERT OR REPLACE INTO results_summary VALUES (?, ?, ?, ?, ?)''', 
                   (company_name, energy_usage, waste, travel, response_date))
    conn.commit()  
    conn.close()   

def get_values(type):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    if type == 'energy':
        cursor.execute('''  SELECT AVG(energy_usage_emission)
                        FROM    (SELECT
                                    energy_usage_emission
                                FROM results_summary
                                ORDER BY energy_usage_emission
                                LIMIT 2 - (SELECT COUNT(*) FROM results_summary) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results_summary))    
                   ''')
    elif type == 'waste':
        cursor.execute('''  SELECT AVG(waste_emission)
                        FROM    (SELECT
                                    waste_emission
                                FROM results_summary
                                ORDER BY waste_emission
                                LIMIT 2 - (SELECT COUNT(*) FROM results_summary) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results_summary))    
                   ''')
    elif type == 'travel':
        cursor.execute('''  SELECT AVG(travel_emission)
                        FROM    (SELECT
                                    travel_emission
                                FROM results_summary
                                ORDER BY travel_emission
                                LIMIT 2 - (SELECT COUNT(*) FROM results_summary) % 2 -- odd 1, even 2
                                OFFSET (SELECT (COUNT(*) - 1) / 2
                                        FROM results_summary))    
                   ''')
    result = cursor.fetchone()     
    conn.close()  
    return round(result[0], 2) if result else None 

check_variable = pd.isna(electricity_bill) + pd.isna(gas_bill) + pd.isna(fuel_bill) + pd.isna(waste_amt) + pd.isna(travel_km)

if st.button('Submit my data', type='primary') and st.session_state.company_name and check_variable == False:
    #3. creating dataframe with entered data
    total = round(energy_usage + waste + travel, 2)
    energy_usage_median = get_values('energy')
    waste_median = get_values('waste')
    travel_median = get_values('travel')
    total_median = round(energy_usage_median + waste_median + travel_median, 2)

    energy_usage_diff = str(round((energy_usage / energy_usage_median - 1) * 100, 2)) + " %"
    waste_diff = str(round((waste / waste_median - 1) * 100, 2)) + " %"
    travel_diff = str(round((travel / travel_median - 1) * 100, 2)) + " %"
    total_diff = str(round((total / total_median - 1) * 100, 2)) + " %"

    chart_data = pd.DataFrame(
        {
            "Comparison": [st.session_state.company_name, "Median", "Difference"],
            "Energy Usage": [str(energy_usage), str(energy_usage_median), energy_usage_diff],
            "Waste": [str(waste), str(waste_median), waste_diff],
            "Business Travel": [str(travel), str(travel_median), travel_diff],
            "Total": [str(total), str(total_median), total_diff]
        }
        )

    def highlight_row(row):
        if row['Comparison'] == 'Difference':  # Highlight row with index 1
            return ['background-color: lightsteelblue'] * len(row)
        else:
            return [''] * len(row)


    #4. submitting user's data, visualizing it and comparing it with our database's average
    save_user_value(st.session_state.company_name, electricity_bill, gas_bill, fuel_bill, waste_amt, recycled_prc, travel_km, fuel_eff, response_date, energy_usage, waste, travel)

    st.write("##### Comparison of yours and other companies' carbon footprints")
    st.write("###### Absolute values")

    chart_data = chart_data.style.apply(highlight_row, axis=1)
    st.dataframe(chart_data, hide_index=True)
    
    st.write("###### Shares of carbon footprint components")
    labels = ['Energy Usage', 'Waste', 'Business Travel'] #chart_data.iloc[0] #chart_data['Comparison'] #'Energy Usage', 'Hogs', 'Dogs', 'Logs'
    sizes = [energy_usage, waste, travel]
    sizes_median = [energy_usage_median, waste_median, travel_median]

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('coolwarm'))
    axes[0].set_title(f"{st.session_state.company_name}")
    #ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    axes[1].pie(sizes_median, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('coolwarm'))
    axes[1].set_title("Median values for all our partner companies")
    
    st.pyplot(fig)

    st.write("##### Recommendations")    
    if energy_usage <= 5000:
        st.write(f"**You have low energy related emissions, {energy_usage} kgCO2.**")
        st.write("*Great job!* Your energy consumption is efficient. Maintain current practices by conducting periodic energy audits to ensure no inefficiencies creep in.")
    elif energy_usage <= 15000:
        st.write(f"**You have moderate energy related emissions, {energy_usage} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Switch to renewable energy.* Opt for green energy contracts or install on-site solar panels.")
        st.write("2. *Upgrade infrastructure.* Use LED lighting, energy-efficient HVAC systems, and appliances with high energy-star ratings.")
        st.write("3. *Reduce idle energy.* Implement smart controls for lighting and machinery, ensuring devices are off when not in use.")
    else:
        st.write(f"**You have high energy related emissions, {energy_usage} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Conduct an energy audit.* Pinpoint high-consumption areas and reduce wasteful practices.")
        st.write("2. *Insulate and retrofit.* Improve building insulation and consider energy-efficient retrofits like double-glazed windows.")
        st.write("3. *Electrify transportation.* Replace fossil-fuel-powered generators or vehicles with electric alternatives.")
    st.write("Energy related emissions state benchmarks")
    energy_df = pd.DataFrame(
        {
            "Level": ["Low", "Moderate", "High"],
            "Left limit, kgCO2": ["0", "5000.1", "15000.1"],
            "Right limit, kgCO2": ["5000", "15000", "∞"]
        }
        )
    st.dataframe(energy_df, hide_index=True) 

    if waste <= 1000:
        st.write(f"**You have low waste related emissions, {waste} kgCO2.**")
        st.write("*Excellent work!* Your waste management practices are exemplary. Keep monitoring and look for ways to further minimize waste.")
    elif waste <= 3000:
        st.write(f"**You have moderate waste related emissions, {waste} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Boost recycling.* Expand recycling initiatives and educate employees on proper waste segregation.")
        st.write("2. *Reduce single-use items.* Eliminate disposable plastics in favor of reusable or biodegradable options.")
        st.write("3. *Implement waste reduction policies.* Encourage double-sided printing, paperless offices, and composting.")
    else:   
        st.write(f"**You have high waste related emissions, {waste} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Conduct a waste audit.* Analyze waste streams to identify excessive or inefficient practices.")
        st.write("2. *Collaborate on sustainability.* Work with suppliers to minimize packaging or switch to sustainable options.")
        st.write("3. *Pursue zero waste initiatives.* Implement a circular economy approach by finding ways to repurpose waste.")
    st.write("Waste related emissions state benchmarks")
    waste_df = pd.DataFrame(
        {
            "Level": ["Low", "Moderate", "High"],
            "Left limit, kgCO2": ["0", "1000.1", "3000.1"],
            "Right limit, kgCO2": ["1000", "3000", "∞"]
        }
        )
    st.dataframe(waste_df, hide_index=True) 

    if travel <= 10000:
        st.write(f"**You have low travel related emissions, {travel} kgCO2.**")
        st.write("*Fantastic!* Your travel-related emissions are well under control. Maintain virtual meetings and promote energy-conscious travel behaviors.")
    elif travel <= 25000:
        st.write(f"**You have moderate travel related emissions, {travel} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Optimize travel plans.* Plan efficient routes and consolidate trips to minimize fuel use.")
        st.write("2. *Shift travel modes.* Use public transport, carpooling, or cycling for shorter distances.")
        st.write("3. *Adopt hybrid options.* Use hybrid vehicles or fuel-efficient car rentals for business trips.")
    else:
        st.write(f"**You have high travel related emissions, {travel} kgCO2. You can use this tips to reduce them:**")
        st.write("1. *Electrify business travel.* Transition to electric vehicles and promote train travel over flights for short distances.")
        st.write("2. *Limit non-essential travel.* Shift to virtual meetings and reduce the need for in-person travel.")
        st.write("3. *Offset emissions.* Invest in carbon credits or green initiatives to neutralize the travel-related impact.")
    
    st.write("Waste related emissions state benchmarks")
    travel_df = pd.DataFrame(
        {
            "Level": ["Low", "Moderate", "High"],
            "Left limit, kgCO2": ["0", "10000.1", "25000.1"],
            "Right limit, kgCO2": ["10000", "25000", "∞"]
        }
        )
    st.dataframe(travel_df, hide_index=True)