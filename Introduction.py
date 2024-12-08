import streamlit as st

st.write('''#### Welcome to the carbon footprint calculator.''')

with st.expander("Why does my company need this?"):
    st.write("It's important due to several social, regulatory, and economic factors:")
    st.write('###### 1. Regulatory Compliance')
    st.write("Germany, as part of the European Union, has strong regulations and ambitious goals for reducing greenhouse gas emissions.")
    st.write('''EU regulations, like the [Corporate Sustainability Reporting Directive (CSRD)](https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en), 
             require companies to disclose their environmental impact, including their carbon emissions.
             ''')
    st.write('###### 2. Consumer Demand')
    st.write("Consumers in Germany are highly eco-conscious, so reducing emissions can enhance customer loyalty and brand image.")
    st.write('###### 3. Competitive Advantage')
    st.write("Companies that demonstrate strong environmental credentials attract eco-conscious investors, partners and talent.")
    st.write('###### 4. Cost Savings')
    st.write("Measuring carbon emissions helps companies reveal inefficiencies and wasteful practices, leading to cost-saving opportunities.")

st.write('''Ready to take some action?\nLet's calculate your company's carbon footprint!''')
st.page_link("pages/Questions.py", label='Go to questions', icon="😍")
st.page_link("pages/Summary.py", label='Go to summary', icon="📈")

