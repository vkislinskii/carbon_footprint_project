import streamlit as st
import sqlite3
import pandas as pd
import plotly.figure_factory as ff 
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


#0. getting the data
def get_data_all_users():
    conn = sqlite3.connect("data.db")  
    cursor = conn.cursor()    
    query = f'''SELECT 
                    company_name,
                    energy_usage_emission,
                    waste_emission,
                    travel_emission,
                    energy_usage_emission + waste_emission + travel_emission as overall_emission,
                    date(response_date) as response_date 
                FROM results_summary'''
    data = pd.read_sql(query, conn)
    conn.close()
    return data 

data = get_data_all_users()

#1. Overview visualizations
st.subheader('High-Level Overview', divider="gray")
#1.1. Pie chart for the median values


energy_usage_median = round(data['energy_usage_emission'].median(), 2) 
waste_median = round(data['waste_emission'].median(), 2) 
travel_median = round(data['travel_emission'].median(), 2) 
labels = ['Energy Usage', 'Waste', 'Business Travel']
sizes_median = [energy_usage_median, waste_median, travel_median]

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.1f}%  \n({v:d} kgCO2)'.format(p=pct,v=val)
    return my_autopct

fig, axes = plt.subplots(figsize=(3, 2.2)) 
axes.pie(sizes_median, labels=labels, autopct=make_autopct(sizes_median), startangle=90, textprops={'fontsize': 4.6 }, colors=sns.color_palette('coolwarm'))
#plt.tight_layout()

st.write("###### Median value distribution across partner companies")
col1, col2, col3 = st.columns([0.25, 3, 0.25])  
with col2:
    st.pyplot(fig, use_container_width=False)



#1.2. Box charts for each emission type
fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.1)
fig.add_trace(go.Box(y=data['energy_usage_emission'], name="Energy kgCO2"), row=1, col=1)
fig.add_trace(go.Box(y=data['waste_emission'], name="Waste kgCO2"), row=1, col=2)
fig.add_trace(go.Box(y=data['travel_emission'], name="Travel kgCO2"), row=1, col=3)
fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))

st.write("###### Distribution by emission type")
st.plotly_chart(fig)


#1.3. Total emission distribution plot 
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(data, x='overall_emission', kde=True, color='lightskyblue')
plt.xlabel('Overall emission')
plt.ylabel('Number of companies')

st.write("###### Distribution of total emission across companies")
st.pyplot(fig)

#--------------------------------------
#2. Overview visualizations
st.subheader('Companies Overview', divider="gray")

st.write("###### Table with data of all companies")
st.dataframe(data, hide_index=True)




df_long = pd.melt(data, id_vars=['company_name'], value_vars=['energy_usage_emission', 'waste_emission', 'travel_emission'],
                  var_name='emission_type', value_name='emission_amount')

df_long2 = df_long
df_long2['total_emission'] = df_long.groupby('company_name')['emission_amount'].transform('sum')

# Calculate share of each emission type
df_long2['share'] = df_long['emission_amount'] / df_long['total_emission']

# Sort values to ensure proper stacking order
df_long2['emission_type'] = pd.Categorical(df_long['emission_type'], 
                                           categories=['energy_usage_emission', 'waste_emission', 'travel_emission'], 
                                           ordered=True)
df_long2 = df_long.sort_values(by=['company_name', 'emission_type'])


# 2.2. total emissions by company
st.write("###### Total emissions per company")
plt.figure(figsize=(10, 6))
sns.barplot(x='company_name', y='total_emission', data=df_long, palette='coolwarm', ci=None) #, hue='emission_type'
#plt.xticks(rotation=45)
st.pyplot(plt)