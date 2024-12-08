import streamlit as st
import sqlite3
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go


#0. Defining the functions: to get data, to set up visualizations
def get_data_all_users(db_path="data.db"):
    query = f'''SELECT 
                    company_name,
                    energy_usage_emission,
                    waste_emission,
                    travel_emission,
                    energy_usage_emission + waste_emission + travel_emission as overall_emission,
                    date(response_date) as response_date 
                FROM results_summary'''
    with sqlite3.connect(db_path) as conn:
        data = pd.read_sql(query, conn)
    return data 

def plot_pie_chart(values, labels):
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{p:.1f}%  \n({v:d} kgCO2)'.format(p=pct,v=val)
        return my_autopct                       
    
    fig, ax = plt.subplots(figsize=(3, 2.2))
    ax.pie(
        values, labels=labels, autopct=make_autopct(values),
        startangle=90, textprops={'fontsize': 4.6},
        colors=sns.color_palette('coolwarm')
    )
    return fig

def plot_box_charts(data):
    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.1)
    fig.add_trace(go.Box(y=data['energy_usage_emission'], name="Energy kgCO2"), row=1, col=1)
    fig.add_trace(go.Box(y=data['waste_emission'], name="Waste kgCO2"), row=1, col=2)
    fig.add_trace(go.Box(y=data['travel_emission'], name="Travel kgCO2"), row=1, col=3)
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
    return fig

def plot_total_emission_distribution(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data, x='overall_emission', kde=True, color='lightskyblue')
    plt.xlabel('Overall Emission')
    plt.ylabel('Number of Companies')
    return fig

def plot_total_emission_by_company(data):
    fig = plt.figure(figsize=(10, 6))
    sns.barplot(x='company_name', y='overall_emission', data=data, palette='coolwarm', ci=None)
    plt.xlabel('Company Name')
    plt.ylabel('Overall Emission')
    return fig


#1. Overview visualizations
st.subheader('High-Level Overview', divider="gray")
data = get_data_all_users()

#1.1. Pie chart for the median values
median_emission_values = [
    round(data['energy_usage_emission'].median(), 2),
    round(data['waste_emission'].median(), 2),
    round(data['travel_emission'].median(), 2)
]
pie_chart = plot_pie_chart(median_emission_values, ['Energy Usage', 'Waste', 'Business Travel'])

st.write("###### Median value distribution across partner companies")
col1, col2, col3 = st.columns([0.25, 3, 0.25])  
with col2:
    st.pyplot(pie_chart, use_container_width=False)

#1.2. Box charts for each emission type
st.write("###### Distribution by emission type")
box_charts = plot_box_charts(data)
st.plotly_chart(box_charts)

#1.3. Total emission distribution plot 
st.write("###### Distribution of total emission across companies")
total_emission_distribution = plot_total_emission_distribution(data)
st.pyplot(total_emission_distribution)


#2. Overview visualizations
st.subheader('Companies Overview', divider="gray")

#2.1. Table data
st.write("###### Table with data of all companies")
st.dataframe(data, hide_index=True)

# 2.2. Total emissions by company
st.write("###### Total emissions per company")
total_emission_by_company = plot_total_emission_by_company(data)
st.pyplot(total_emission_by_company)