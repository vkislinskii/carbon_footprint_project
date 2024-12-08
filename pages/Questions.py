import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#0. Defining the functions
def get_user_inputs():
    company_name = st.text_input("Your company's name", key="company_name")
    with st.expander("Energy Usage Questions", expanded=True):
        electricity = st.number_input("What is your average monthly electricity bill in euros?", min_value=0, value=None, placeholder="Type a number...")
        gas = st.number_input('What is your average monthly gas bill in euros?', min_value=0, value=None, placeholder="Type a number...")
        fuel = st.number_input('What is your average monthly fuel bill for transportation in euros?', min_value=0, value=None, placeholder="Type a number...")

    with st.expander("Waste Questions", expanded=True):
        waste_amt = st.number_input('How much waste do you generate per month in kilograms?', min_value=0, value=None, placeholder="Type a number...")
        recycled_prc = st.slider('How much of that waste is recycled or composed (in percentage)?', 0, 100, 20)

    with st.expander("Business Travel Questions", expanded=True):
        travel_km = st.number_input('How many kilometers do your employees travel per year for business purposes?', min_value=0, value=None, placeholder="Type a number...")
        fuel_eff = st.slider('What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?', 1, 25, 7)

    return company_name, electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff

def calculate_emissions(electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff):
    energy_usage = round((electricity * 12 * 0.0005) + (gas * 12 * 0.0053) + (fuel * 12 * 2.32), 2)
    waste = round(waste_amt * 12 * (0.57-recycled_prc/100), 2)
    travel = round(travel_km * fuel_eff * 2.31, 2)
    return energy_usage, waste, travel

def save_user_value(company_name, electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff, response_date, energy_usage, waste, travel):
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO results_raw VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (company_name, electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff, response_date))
    cursor.execute('''INSERT OR REPLACE INTO results_summary VALUES (?, ?, ?, ?, ?)''', 
                   (company_name, energy_usage, waste, travel, response_date))
    conn.commit()  
    conn.close()   

def get_values(db_path="data.db"):
    query = ''' SELECT 
                    energy_usage_emission,
                    waste_emission,
                    travel_emission
                FROM results_summary'''
    with sqlite3.connect(db_path) as conn:
        data = pd.read_sql(query, conn)
    return data  

def generate_chart(data0, data1, labels, company_name):
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    axes[0].pie(data0, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('coolwarm'))
    axes[0].set_title(company_name)   
    axes[1].pie(data1, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('coolwarm'))
    axes[1].set_title("Median values for all our partner companies")
    return fig

def display_recommendations(energy_usage, waste, travel):
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


st.subheader('Questionnaire', divider="gray")

#1. getting information from the user
company_name, electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff = get_user_inputs()

if st.button("Submit Data"):
    if company_name:
        #2. Calculating emissions of the company
        energy_usage, waste, travel = calculate_emissions(electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff)

        #3. Saving the values 
        response_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_user_value(company_name, electricity, gas, fuel, waste_amt, recycled_prc, travel_km, fuel_eff, response_date, energy_usage, waste, travel)

        #4. Table data
        st.subheader("Comparison of yours and other companies' carbon footprints", divider="gray")
        st.write("###### Absolute values")
        total = round(energy_usage + waste + travel, 2)
        data = get_values()
        energy_usage_median = data['energy_usage_emission'].median()
        waste_median = data['waste_emission'].median()
        travel_median = data['travel_emission'].median()
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
            if row['Comparison'] == 'Difference':  
                return ['background-color: lightsteelblue'] * len(row)
            else:
                return [''] * len(row)
            
        chart_data = chart_data.style.apply(highlight_row, axis=1)
        st.dataframe(chart_data, hide_index=True)
        
        #5. Pie chart
        sizes = [energy_usage, waste, travel]
        sizes_median = [energy_usage_median, waste_median, travel_median]
        fig = generate_chart(sizes, sizes_median, ["Energy Usage", "Waste", "Business Travel"], st.session_state.company_name)
        st.pyplot(fig)

        #6. Recommendations
        st.write("##### Recommendations")
        display_recommendations(energy_usage, waste, travel)




    


    #4. submitting user's data, visualizing it and comparing it with our database's average