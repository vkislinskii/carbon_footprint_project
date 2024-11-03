import streamlit as st

st.write('''#### Hey! \n Let's calculate your carbot footprint''')

with st.expander("Why does my company need this?"):
    st.write('Carbon reporting is a key aspect of measuring individuals and organisations impact on the environment, to help mitigate climate crisis.\n')
    st.write('It is under EU law that member states must report their estimated carbon footprints.')

st.page_link("pages/page2_questions.py", label='Go to questions')