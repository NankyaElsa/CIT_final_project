#plotly is used to draw the stcky chart

import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

import calendar
from datetime import datetime

import database as db  # Local import


#settings

incomes = ["Salary", "Blog", "Other Income"]
expenses = ["Rent", "Utilities", "Groceries","Car", "Other Expenses", "Saving"]
currency = "UGX"
page_title = "Income and Expense Tracker"
page_icon = ":moneybag:"  ## emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"

st.set_page_config(page_title = page_title, page_icon = page_icon, layout=layout)
st.title(page_title + " " + page_icon)  

#Hide Streamlit style so as to apply our own styles
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#Navigation menu
selected = option_menu (
    menu_title= None, 
    options=["Data Entry", "Data Visualization"], 
    icons=["pen", "bar-chart-fill"],  #icons https://icons.getbootstrap.com/
    orientation="horizontal"
    )
# for database
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods


#drop down values for selecting the period

years = [datetime.today().year, datetime.today().year + 1, datetime.today().year + 2, datetime.today().year + 3]
months = list(calendar.month_name[1:])

#input and save periods
if selected == "Data Entry":
    st.header(f"Data Entry in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key = "year")

        "---" #divider

        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)

        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)

        with st.expander("comment"):
            comment = st.text_area("", placeholder= "Enter a comment here...")

        "---"
        #creating a submit button
        submitted = st.form_submit_button("Save Data")
        if submitted:
            #capture the users input and store it in a nosql(deta) database
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}

            # Insert values into a database
            db.insert_period(period, incomes, expenses, comment)
            st.success(f"Data Saved!")

#plot periods using sankey charts
if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        #  Get periods from data base

        period = st.selectbox("Select Period:", get_all_periods())
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            #Get data from database
            period_data = db.get_period(period)
            comment = period_data.get("comment")
            incomes = period_data.get("incomes")
            expenses = period_data.get("expenses")
            #create metrics

            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col1.metric("Total Expense", f"{total_expense} {currency}")
            col1.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")

            #Create sankey chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)




    

    