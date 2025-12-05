# CURRENT TASK: Add predicted curve graphing and ADD USER ID ADDITION TO FILE UPLOADING

import streamlit as st

# Webpage Settings
st.set_page_config(page_title="EZ Income Tracker", layout="wide", initial_sidebar_state="expanded", page_icon="logo.png")

# Initializing constant variables
requiredlibraries = [
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "sklearn"
]
totaltitles = ["Month No.", "Month", "Year", "Total Revenue", "Total Expenses", "Total Tax", "Net Income"]
pages = ["Home", "Add an Entry", "Your Income Data", "Edit an Entry", "Analyze Your Data"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Importing libraries/modules
import os
import time
from datetime import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn

from sklearn.linear_model import LinearRegression as lreg
from sklearn.model_selection import train_test_split as tts

pd.set_option("display.max_columns", None, "display.max_rows", None)

def isNum(num: str):
    
    try:
        num = float(num)
    
    except:
        
        try:
            num = int(num)

        except:
            return False
        
    return True

def cleanDF(df: pd.DataFrame):
    
    try:

        for col in df.columns:
            if "Unnamed:" in col and "(Revenue)" not in col and "(Expense)" not in col and "(Tax)" not in col:
                df.drop(col, axis='columns', inplace=True)

        print(f"User {st.session_state.userid}'s data was cleaned successfully.")

    except:
        print(f"ERROR: Could not clean User {st.session_state.userid}'s data.")

    return df

def cleanData(data: dict):
    
    try:

        for col in data:
            if "Unnamed:" in col and "(Revenue)" not in col and "(Expense)" not in col and "(Tax)" not in col:
                del data[col]

        print(f"User {st.session_state.userid}'s data was cleaned successfully.")

    except:
        print(f"ERROR: Could not clean User {st.session_state.userid}'s data.")

    return data

def saveEntries(df, id):

    df = cleanDF(df)

    try:

        write = str(df.to_csv())
        open(f"data_{id}.csv", "w").write(write)
        print(f"\nSaved User {id}'s data sucessfully.")

    except:
        print(f"\nERROR: Could not save User {id}'s data.")

def sortAccounts(df: pd.DataFrame):

    newdata = {}

    for col in df.columns:
        if col in totaltitles or col[-9:] == "(Revenue)" or col[-5:] == "(Tax)":
            newdata[col] = df[col]

    for col in df.columns:
        if col[-9:] == "(Expense)":
            newdata[col] = df[col]
    
    newdf = pd.DataFrame().from_dict(newdata)
    return cleanDF(newdf)

def colSelector(defaultval: bool = True):
    
    showCols = []

    selectall = st.checkbox("Select All", value=defaultval)

    for col in st.session_state.userdata.columns:
        
        if st.checkbox(col, value=selectall):
            showCols.append(col)

    return showCols

if "userdata" not in st.session_state or "userid" not in st.session_state or "currentids" not in st.session_state:

    st.session_state.currentids = []

    try:
        st.session_state.userdata = pd.read_csv("data.csv")

    except:
        
        st.session_state.userdata = pd.DataFrame()

        for title in totaltitles:
            st.session_state.userdata[title] = []
            
    import users

    st.session_state.currentids = users.userids
    st.session_state.userid = st.session_state.currentids[-1] + 1


sidebar = st.sidebar

# REMOVE AFTER RELEASE
if sidebar.button("Push to GitHub"):
    os.system("git add .")
    os.system("git commit -m \"Remote Update\"")
    os.system("git push origin main")        

st.sidebar.title(":green[EZ] Income Tracker")

page = st.sidebar.radio("**Navigation:**", pages)

if sidebar.button("Refresh Page"):
    sidebar.success("Page refreshed successfully!")
    
if len(st.session_state.userdata) > 0:

    if type(st.session_state.userdata) == dict:
        st.session_state.userdata = pd.DataFrame().from_dict(st.session_state.userdata)

    st.session_state.userdata = cleanDF(st.session_state.userdata)
    download = sidebar.download_button("Download Data", st.session_state.userdata.to_csv(index=False), file_name="data.csv")

if page == "Home":

    st.title(":green[EZ] Income Tracker")
    st.write("Welcome to **:green[EZ] Income Tracker.** This website will help you with **all** of your income tracking needs, with **data management**, **analysis**, **visualization** and **prediction features** that make budgeting **quick**, **easy** and **secure**. Make sure to create entries **every month** for the **best** results.")
    st.write("**If you have used this website before**, upload your **`data.csv`** file from your **last session** to the box **below**. If this is your first time, head to the **`Add an Entry`** page to get started. Once you're done, make sure to **save your data** by hitting the **`Download Data`** button on the sidebar **to the left**.")

    datafile = st.file_uploader("**Upload your data file below:**", accept_multiple_files=False, type=["csv"])

    if datafile and st.button("Upload File"):
        
        try:

            df = pd.read_csv(datafile)
            lendata = len(st.session_state.userdata)

            st.success("Data file uploaded successfully!")

            if st.session_state.userid not in st.session_state.currentids and lendata > 0:

                import users

                st.session_state.currentids = users.userids
                st.session_state.userid = st.session_state.currentids[-1] + 1
                st.session_state.currentids.append(st.session_state.userid)
                write = f"userids = {st.session_state.currentids}"

                try:
                    open("users.py", "w").write(write)
                    print(f"\nAdded User {st.session_state.userid} successfully and saved IDs to file.")
                except:
                    print(f"\nCould not add User {st.session_state.userid}.")

            df = cleanDF(df)
            st.session_state.userdata = df
            saveEntries(st.session_state.userdata, st.session_state.userid)


        except:
            st.error("There was an issue in uploading your file. Please try again.")

else:

    st.title(page)
    
    now = dt.now()
    currentmonth = now.strftime("%B")
    currentyear = int(now.strftime("%Y"))
    monthindex = 0
    lendata = len(st.session_state.userdata)

    for m in range(len(months)):
            
        if currentmonth == months[m]:
            monthindex = m
            break

    st.session_state.userdata = sortAccounts(st.session_state.userdata)    

    if lendata > 0:
        currentmonthno = list(st.session_state.userdata["Month No."])[-1]+1
    
    else:
        currentmonthno = 1

    if page == "Add an Entry":

        st.write(":grey[**Note:** For the month number to update, you may need to refresh the page after adding an entry if you plan on adding multiple entries.]")

        existingrevs = []
        existingexps = []
        existingtaxes = []

        for col in st.session_state.userdata.columns:

            if "(Revenue)" == col[-9:]:
                existingrevs.append(col)

            elif "(Expense)" == col[-9:]:
                existingexps.append(col)

            elif "(Tax)" == col[-5:]:
                existingtaxes.append(col)

        revenue = {}
        expenses = {}
        tax = {}

        revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=len(existingrevs), min_value=0)
        expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=len(existingexps), min_value=0)

        st.write("---")
        st.header("Time of Entry")

        c1, c2, c3 = st.columns(3)
    
        try:
            monthno = c1.number_input("**Month No.**", min_value=currentmonthno, step=1)

        except:
            monthno = c1.number_input("**Month No.**", min_value=1, step=1)


        month = c2.selectbox("**Month**", months, index=monthindex)
        year = c3.number_input("**Year**", currentyear, step=1)

        if revenuecount == 0 and expensecount == 0:
            st.write("---")
            st.subheader("**Use the sidebar on the left to add accounts.**")

        if revenuecount > 0:
            
            st.write("---")
            st.header("Revenue Sources")

            c1, c2, c3 = st.columns(3)
            
            unnamedaccounts = 0

            for i in range(revenuecount):

                accname = ""

                if (i < len(existingrevs)):
                    accname = existingrevs[i][:-10]

                if accname[:23] == "Unnamed Revenue Account":
                    unnamedaccounts += 1

                name = c1.text_input(f"**Revenue Source {i+1}:**", value=accname)

                if name == "":
                    
                    unnamedaccounts += 1
                    revenuecol = f"Unnamed Revenue Account {unnamedaccounts} (Revenue)"
                    taxcol = f"Unnamed Revenue Account {unnamedaccounts} (Tax)"

                else:
                    revenuecol = f"{name} (Revenue)"
                    taxcol = f"{name} (Tax)"

                if revenuecol in revenue:
                    revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                else:
                    revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                if taxcol in tax:
                    tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                else:
                    tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                revenue[revenuecol] = round(revenue[revenuecol], 2)
                tax[taxcol] = round(tax[taxcol], 2)

        if expensecount > 0:
            
            st.write("---")
            st.header("Expenses")

            c1, c2 = st.columns(2)

            unnamedaccounts = 0

            for i in range(expensecount):

                accname = ""

                if (i < len(existingexps)):
                    accname = existingexps[i][:-10]
                
                if accname[:23] == "Unnamed Expense Account":
                    unnamedaccounts += 1

                name = c1.text_input(f"**Expense {i+1}:**", value=accname)

                if name == "":
                    unnamedaccounts += 1
                    expensecol = f"Unnamed Expense Account {unnamedaccounts} (Expense)"

                else:
                    expensecol = f"{name} (Expense)"
                    
                if expensecol in expenses:
                    expenses[expensecol] += c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                else:
                    expenses[expensecol] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                expenses[expensecol] = round(expenses[expensecol], 2)


        totalrevenue = sum(revenue.values())
        totalexpenses = sum(expenses.values())
        totaltax = sum(tax.values())

        c1, c2, c3 = st.columns(3)

        netincome = totalrevenue - totalexpenses - totaltax


        revenuestr = f"{round(totalrevenue, 2)}"

        if ("." in revenuestr and len(revenuestr) > 1 and len(revenuestr.split(".")[1]) == "1"):
            revenuestr += "0"

        if (totalrevenue == 0):
            revenuestr = f"(0.00)"

        expensestr = f"{round(totalexpenses, 2)}"

        if ("." in expensestr and len(expensestr) > 1 and len(expensestr.split(".")[1]) == "1"):
            expensestr += "0"

        if (totalexpenses == 0):
            expensestr = f"0.00"        


        taxstr = f"{round(totaltax, 2)}"

        if (len(taxstr) > 1 and len(taxstr.split(".")[1]) == "1"):
            taxstr += "0"

        if (totaltax == 0):
            taxstr = f"0.00"        


        netincomestr = f"{np.abs(round(netincome, 2))}"

        if ("." in netincomestr and len(netincomestr.split(".")[1]) == 1):
            netincomestr += "0"

        if netincome < 0:
            netincomestr = f"({netincomestr})"

        if (netincome == 0):
            netincomestr = f"(0.00)"        


        totalvals = {
        
            "Month No.": [monthno],
            "Month": [month],
            "Year": [str(year)],
            "Total Revenue": [totalrevenue],
            "Total Expenses": [totalexpenses],
            "Total Tax": [totaltax],
            "Net Income": [netincome]
        
        }

        totalvalsstr = {
        
            "Month No.": [monthno],
            "Month": [month],
            "Year": [str(year)],
            "Total Revenue": [f"$ {revenuestr}"],
            "Total Expenses": [f"$ ({expensestr})"],
            "Total Tax": [f"$ ({taxstr})"],
            "Net Income": [f"$ {netincomestr}"]
        
        }

        for revenueacc, taxacc in zip(revenue.keys(), tax.keys()):

            totalvals[revenueacc] = [revenue[revenueacc]]
            totalvals[taxacc] = [tax[taxacc]]

            revenuestr = f"{round(revenue[revenueacc], 2)}"

            if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                revenuestr += "0"

            if (totalrevenue == 0):
                revenuestr = f"(0.00)"

            taxstr = f"{round(tax[taxacc], 2)}"

            if ("." in taxstr and len(taxstr.split(".")[1]) == 1):
                taxstr += "0"

            if (tax[taxacc] == 0):
                taxstr = f"0.00"
            
            totalvalsstr[revenueacc] = [f"$ {revenuestr}"]
            totalvalsstr[taxacc] = [f"$ ({taxstr})"]

        for acc in expenses:

            expensestr = f"{round(expenses[acc], 2)}"

            if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                expensestr += "0"

            if (expenses[acc] == 0):
                expensestr = f"0.00"

            totalvals[acc] = [expenses[acc]]
            totalvalsstr[acc] = [f"$ ({expensestr})"]

        totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

        st.write("---")
        st.header("Entry Preview")
        st.dataframe(totalvalsstr, hide_index=True, use_container_width=True)

        if sidebar.button("Add an Entry"):
                
            if st.session_state.userid not in st.session_state.currentids and lendata > 0:

                import users

                st.session_state.currentids = users.userids
                st.session_state.userid = st.session_state.currentids[-1] + 1
                st.session_state.currentids.append(st.session_state.userid)
                write = f"userids = {st.session_state.currentids}"

                try:
                    open("users.py", "w").write(write)
                    print(f"\nAdded User {st.session_state.userid} successfully and saved IDs to file.")
                except:
                    print(f"\nCould not add User {st.session_state.userid}.")

            try:
            
                data = {}

                for col in st.session_state.userdata.columns:

                    data[col] = []

                    for val in st.session_state.userdata[col]:
                        data[col].append(val)

                    if col not in totalvals:
                        data[col].append(0)

                for acc in totalvals:
                        
                    if acc not in data:
                        if len(data["Month No."]) > 1:
                            data[acc] = [0 for i in range(len(data["Month No."])-1)]
                        else:
                            data[acc] = []
                
                    data[acc].append(totalvals[acc][0])

                data = cleanData(data)
                newdf = pd.DataFrame().from_dict(data)
                saveEntries(newdf, st.session_state.userid)

                print(f"\nEntry created sucessfully for User {st.session_state.userid}.")

            except:
                print(f"\nERROR: Entry could not be created for User {st.session_state.userid}.")

            st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
            st.session_state.userdata = cleanDF(st.session_state.userdata)

            sidebar.success("Entry created successfully.")

    elif page == "Your Income Data":

        if lendata == 0:
            st.subheader("Please add an entry before attempting to view your entries.")            

        else:

            showColsExpander = sidebar.expander("**Selected Columns**")

            with showColsExpander:
                showCols = colSelector()

            st.session_state.userdata = cleanDF(st.session_state.userdata)

            interpolationExpander = sidebar.expander("**Interpolate Missing Data**")

            with interpolationExpander:

                st.write("Interpolate data for months that were missed in the recording process. Choose the month to interpolate, and we'll predict what the values for that month could have been based on your previous and following entry.")

                intmonths = list(st.session_state.userdata["Month No."].astype(int))
                maxval = max(intmonths)
                missingmonths = []

                for num in range(1, maxval):
                    if num not in intmonths:
                        missingmonths.append(num)

                if len(missingmonths) == 0:
                    st.success("**You don't have any missing data!**")

                else:

                    targetmonth = st.selectbox("**Target Month:**", missingmonths)

                    previndex = 0
                    nextindex = 0

                    prevmonth = 1
                    nextmonth = maxval

                    newvals = {}
                    cols = [c for c in st.session_state.userdata.columns]

                    newvals["Month"] = st.selectbox("**Month**", months, index=monthindex)
                    newvals["Year"] = st.number_input("**Year**", currentyear, step=1)

                    for i in range(len(st.session_state.userdata)):

                        val = int(st.session_state.userdata.iloc[i, 0])
                        
                        if val < targetmonth:
                            previndex = i
                            prevmonth = st.session_state.userdata.iloc[previndex, 0]

                        if val > targetmonth and nextmonth != 0:
                            nextindex = i
                            nextmonth = st.session_state.userdata.iloc[nextindex, 0]

                    prevgap = targetmonth - prevmonth
                    nextgap = nextmonth - targetmonth
                    totalgap = prevgap + nextgap

                    newvals["Month No."] = targetmonth

                    for c in range(3, len(cols)):

                        if cols[c][-5:] == "(Tax)" or cols[c] == "Total Tax":

                            prevtax = float(st.session_state.userdata.iloc[previndex, c])
                            nexttax = float(st.session_state.userdata.iloc[nextindex, c])

                            if cols[c][-5:] == "(Tax)":
                                revcol = cols[c][:-5]+"(Revenue)"
                            else:
                                revcol = "Total Revenue"

                            prevrev = st.session_state.userdata.loc[previndex, revcol]
                            nextrev = st.session_state.userdata.loc[nextindex, revcol]

                            prevtaxrate = prevtax / prevrev
                            nexttaxrate = nexttax / nextrev

                            newtaxrate = prevtaxrate + ( (nexttaxrate - prevtaxrate) / totalgap * prevgap )
                            newrev = newvals[revcol]
                            newval = newvals[revcol] * newtaxrate

                        else:

                            prevval = float(st.session_state.userdata.iloc[previndex, c])
                            nextval = float(st.session_state.userdata.iloc[nextindex, c])

                            newval = prevval + ( (nextval - prevval) / totalgap * prevgap )

                        if isNum(str(newval)):
                            newval = round(newval, 2)

                        newvals[cols[c]] = newval

                    data = {}

                    for col in st.session_state.userdata:

                        data[col] = [val for val in st.session_state.userdata[col]]
                        data[col].insert(nextindex, newvals[col])
                    
                    if st.button("Add Interpolated Data"):

                        newdf = pd.DataFrame()

                        for col in data:
                            newdf[col] = data[col]

                        saveEntries(newdf, st.session_state.userid)

                        st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                        st.session_state.userdata = cleanDF(st.session_state.userdata)
                    
                        lendata = len(st.session_state.userdata)

                        st.success("Interpolated data added successfully. You may have to refresh the page for your data to update.")

            if showCols == []:
                st.subheader("Please select a column to view.")

            else:

                startentry = sidebar.number_input("Starting Entry Number", 1, lendata, value=1)-1
                endentry = sidebar.number_input("Ending Entry Number", startentry, lendata, value=lendata)
                
                displaydf = pd.DataFrame()

                displaydf["Entry No."] = [i+1 for i in range(endentry-startentry)]

                for col in showCols:
                    displaydf[col] = st.session_state.userdata[col].iloc[startentry:endentry]                    

                st.dataframe(displaydf, use_container_width=True, hide_index=True)

                if st.expander("**:red[DANGER ZONE]**").button("**:red[Clear ALL Entries]**", use_container_width=True):
                    
                    newdata = {}

                    for title in totaltitles:
                        newdata[title] = []

                    st.session_state.userdata = pd.DataFrame.from_dict(newdata)

                    saveEntries(st.session_state.userdata, st.session_state.userid)
                    st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                    st.session_state.userdata = cleanDF(st.session_state.userdata)

    elif page == "Edit an Entry":

        if lendata == 0:
            st.subheader("Please add an entry before attempting to edit your entries.")

        else:

            existingrevs = []
            existingexps = []
            existingtaxes = []

            for col in st.session_state.userdata.columns:

                if "(Revenue)" == col[-9:]:
                    existingrevs.append(col)

                elif "(Expense)" == col[-9:]:
                    existingexps.append(col)

                elif "(Tax)" == col[-5:]:
                    existingtaxes.append(col)

            revenue = {}
            expenses = {}
            tax = {}

            revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=len(existingrevs), min_value=len(existingrevs))
            expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=len(existingexps), min_value=len(existingexps))

            st.write("---")
            st.header("Time of Entry")

            c1, c2, c3 = st.columns(3)
        
            for m in range(len(months)):
                    
                if currentmonth == months[m]:
                    monthindex = m
                    break

            monthno = c1.number_input("**Editing Entry (Month No.):**", min_value=1, max_value=lendata, value=lendata)
            month = c2.selectbox("**Month**", months, index=monthindex)
            year = c3.number_input("**Year**", currentyear, step=1)


            if revenuecount > 0:
                
                st.write("---")
                st.header("Revenue Sources")

                c1, c2, c3 = st.columns(3)
                
                unnamedaccounts = 0

                for i in range(revenuecount):

                    accname = ""

                    if (i < len(existingrevs)):
                        accname = existingrevs[i][:-10]

                    if accname[:23] == "Unnamed Revenue Account":
                        unnamedaccounts += 1

                    name = c1.text_input(f"**Revenue Source {i+1}:**", value=accname)

                    if name == "":
                        
                        unnamedaccounts += 1
                        revenuecol = f"Unnamed Revenue Account {unnamedaccounts} (Revenue)"
                        taxcol = f"Unnamed Revenue Account {unnamedaccounts} (Tax)"

                        if revenuecol in revenue:
                            revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                        else:
                            revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                        if taxcol in tax:
                            tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                        else:
                            tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                    else:

                        revenuecol = f"{name} (Revenue)"
                        taxcol = f"{name} (Tax)"

                        if revenuecol in revenue:
                            revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                        else:
                            revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                        if taxcol in tax:
                            tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                        else:
                            tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                    revenue[revenuecol] = round(revenue[revenuecol], 2)
                    tax[taxcol] = round(tax[taxcol], 2)

            if expensecount > 0:
                
                st.write("---")
                st.header("Expenses")

                c1, c2 = st.columns(2)

                unnamedaccounts = 0

                for i in range(expensecount):

                    accname = ""

                    if (i < len(existingexps)):
                        accname = existingexps[i][:-10]
                    
                    if accname[:23] == "Unnamed Expense Account":
                        unnamedaccounts += 1

                    name = c1.text_input(f"**Expense {i+1}:**", value=accname)

                    if name == "":
                        unnamedaccounts += 1
                        expensecol = f"Unnamed Expense Account {unnamedaccounts} (Expense)"

                    else:
                        expensecol = f"{name} (Expense)"
                        
                    if expensecol in expenses:
                        expenses[expensecol] += c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                    else:
                        expenses[expensecol] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                    expenses[expensecol] = round(expenses[expensecol], 2)


            totalrevenue = sum(revenue.values())
            totalexpenses = sum(expenses.values())
            totaltax = sum(tax.values())

            c1, c2, c3 = st.columns(3)

            netincome = totalrevenue - totalexpenses - totaltax


            revenuestr = f"{round(totalrevenue, 2)}"

            if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                revenuestr += "0"

            if (totalrevenue == 0):
                revenuestr = f"(0.00)"

            expensestr = f"{round(totalexpenses, 2)}"

            if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                expensestr += "0"

            if (totalexpenses == 0):
                expensestr = f"0.00"        


            taxstr = f"{round(totaltax, 2)}"

            if (len(taxstr.split(".")[1]) == 1):
                taxstr += "0"

            if (totaltax == 0):
                taxstr = f"0.00"        


            netincomestr = f"{np.abs(round(netincome, 2))}"

            if ("." in netincomestr and len(netincomestr.split(".")[1]) == 1):
                netincomestr += "0"

            if netincome < 0:
                netincomestr = f"({netincomestr})"

            if (netincome == 0):
                netincomestr = f"(0.00)"        


            totalvals = {
            
                "Month No.": [monthno],
                "Month": [month],
                "Year": [str(year)],
                "Total Revenue": [totalrevenue],
                "Total Expenses": [totalexpenses],
                "Total Tax": [totaltax],
                "Net Income": [netincome]
            
            }

            totalvalsstr = {
            
                "Month No.": [monthno],
                "Month": [month],
                "Year": [str(year)],
                "Total Revenue": [f"$ {revenuestr}"],
                "Total Expenses": [f"$ ({expensestr})"],
                "Total Tax": [f"$ ({taxstr})"],
                "Net Income": [f"$ {netincomestr}"]
            
            }

            for revenueacc, taxacc in zip(revenue.keys(), tax.keys()):

                totalvals[revenueacc] = [revenue[revenueacc]]
                totalvals[taxacc] = [tax[taxacc]]

                revenuestr = f"{round(revenue[revenueacc], 2)}"

                if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                    revenuestr += "0"

                if (totalrevenue == 0):
                    revenuestr = f"(0.00)"

                taxstr = f"{round(tax[taxacc], 2)}"

                if ("." in taxstr and len(taxstr.split(".")[1]) == 1):
                    taxstr += "0"

                if (tax[taxacc] == 0):
                    taxstr = f"0.00"
                
                totalvalsstr[revenueacc] = [f"$ {revenuestr}"]
                totalvalsstr[taxacc] = [f"$ ({taxstr})"]

            for acc in expenses:

                expensestr = f"{round(expenses[acc], 2)}"

                if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                    expensestr += "0"

                if (expenses[acc] == 0):
                    expensestr = f"0.00"

                totalvals[acc] = [expenses[acc]]
                totalvalsstr[acc] = [f"$ ({expensestr})"]

            totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

            st.write("---")
            st.header("Entry Preview")
            st.dataframe(totalvalsstr, hide_index=True, use_container_width=True)

            if sidebar.button("Save Entry"):
                    
                try:
                
                    data = {}

                    for col in st.session_state.userdata.columns:

                        data[col] = []

                        for val in st.session_state.userdata[col]:
                            data[col].append(val)

                    for acc in totalvals:
                            
                        if acc not in data:
                            if len(data["Month No."]) > 1:
                                data[acc] = [0 for i in range(len(data["Month No."])-1)]
                            else:
                                data[acc] = []
                    
                        data[acc][monthno-1] = totalvals[acc][0]

                    data = cleanData(data)
                    newdf = pd.DataFrame().from_dict(data)
                    saveEntries(newdf, st.session_state.userid)

                    st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                    st.session_state.userdata = cleanDF(st.session_state.userdata)

                    st.success(f"\nSaved the entry successfully.")

                except:
                    st.error(f"\nERROR: Entry could not be saved for User {st.session_state.userid}.")

    elif page == "Analyze Your Data":

        st.write("Here, you can generate **graphs**, make **predictions**, view **trends**, and look at your data **as a whole**. Before you begin, it's **highly recommended** that you ensure there is **no missing data**, or any missing data has been **interpolated** on the **Your Income Data** page. To get started, just select what you want to do **below**:")

        userchoice = st.radio("**What do you want to do?**", ["Generate Graphs", "Predict Data"])
        layout = st.radio("**Viewing Layout:**", ["Vertical", "Horizontal"])

        st.write("---")
        
        if lendata > 1:

            if layout == "Vertical":

                c1 = False
                c2 = False

            else:

                c1, c2, c3 = st.columns([10, 80, 10])

                c2.subheader("Divider Position (% towards the right side of the screen)")
                divamount = c2.slider("Divider Position", min_value=10, max_value=90, value=50, label_visibility="collapsed")

                if divamount < 10:
                    divamount = 10

                if divamount > 90:
                    divamount = 90

                st.write("---")

                c1, c2 = st.columns([divamount, 100-divamount])

            showColsExpander = sidebar.expander("**Dataset Columns to Show**")

            with showColsExpander:
                showCols = colSelector()

            displaydata = pd.DataFrame()
            displaydata["Entry No."] = [i+1 for i in range(len(st.session_state.userdata["Month No."]))]

            for col in showCols:
                displaydata[col] = st.session_state.userdata[col]
        
            if userchoice == "Generate Graphs":

                cols = [c for c in st.session_state.userdata.columns if c not in ["Month No.", "Month", "Year"]]
                monthnos = [int(m) for m in st.session_state.userdata["Month No."]]

                if len(cols) < 10:
                    maxcols = len(cols)
                else:
                    maxcols = 10

                gtypes = ["Scatter Plot", "Line Plot", "Linear Regression Plot", "Bar Plot"]
                gtype = sidebar.selectbox("**Graph Type:**", gtypes)
                numcols = sidebar.number_input("**Number of Columns to Plot:**", min_value=1, max_value=maxcols)

                startentry = sidebar.number_input("**Starting Entry to Plot:**", min_value=1, max_value=lendata-1)-1
                endentry = sidebar.number_input("**Ending Entry to Plot:**", min_value=startentry, max_value=lendata, value=lendata)

                darkbg = sidebar.checkbox("Graph Dark Mode", value=True)
                predictdata = sidebar.checkbox("Graph Predicted Data", value=False)

                if darkbg:
                    plt.style.use("dark_background")
                else:
                    plt.style.use("classic")

                fig, ax = plt.subplots()
                ax.set_xticks(np.arange(0, np.max(monthnos)+1, 1))

                plt.xlabel("Month No.")
                plt.ylabel(f"Amount ($)")

                selectedcols = []

                if numcols > 0:
                    sidebar.header("Columns to :green[Plot]:")

                x = list(st.session_state.userdata["Month No."])[startentry:endentry]

                for i in range(numcols):

                    selectedcol = sidebar.selectbox(f"**Column {i+1}:**", [col for col in cols if col not in selectedcols])
                    y = list(st.session_state.userdata[selectedcol])[startentry:endentry]

                    # COMPLETE THIS PART
                    if predictdata and len(ycols) == 0:
                        st.subheader("Please add accounts to your entries to predict account data.")
                    
                    elif predictdata:
                    
                        cols = st.session_state.userdata.columns
                        ycols = [c for c in cols if c not in totaltitles]

                        predsettings = sidebar.expander("**Prediction Settings:**", expanded=True)
                        predmonth = predsettings.number_input("**Number of Months to Predict:**", min_value=1, step=1, max_value=10)
                        startentry = predsettings.number_input("**Starting Entry to Use For Prediction:**", min_value=1, max_value=len(displaydata["Entry No."])-1, step=1)
                        endentry = predsettings.number_input("**Ending Entry to Use For Prediction:**", min_value=startentry+1, max_value=len(displaydata["Entry No."]), value=len(displaydata["Entry No."]), step=1)

                        x = st.session_state.userdata["Month No."][startentry-1:endentry]
                        y = st.session_state.userdata[ycols].iloc[startentry-1:endentry]

                        xtrain, xtest, ytrain, ytest = tts(x, y, test_size=0.2, random_state=40)
                        xtrain, xtest = xtrain.values.reshape(-1, 1), xtest.values.reshape(-1, 1)
                        lr = lreg().fit(xtrain, ytrain)

                        pred = lr.predict([[predmonth]])
                        preddict = {}

                        preddict["Month No."] = [predmonth]
                        preddict["Month"] = ["N/A"]
                        preddict["Year"] = ["N/A"]

                        for title in totaltitles:
                            if title not in ["Month No.", "Month", "Year"]:
                                preddict[title] = 0                 


                        for i in range(len(ycols)):
                            preddict[ycols[i]] = round(pred[0][i], 2)

                        for col in [c for c in preddict if c not in ["Month No.", "Month", "Year"]]:

                            preddict[col] = [preddict[col]]

                            if col[-9:] == "(Revenue)":
                                preddict["Total Revenue"][0] += preddict[col][0]

                            if col[-9:] == "(Expense)":
                                preddict["Total Expenses"][0] += preddict[col][0]
                                
                            if col[-5:] == "(Tax)":
                                preddict["Total Tax"][0] += preddict[col][0]

                        preddict["Net Income"] += (preddict["Total Revenue"][0] - preddict["Total Tax"][0] - preddict["Total Expenses"][0])

                        preddf = pd.DataFrame.from_dict(preddict)

                    selectedcols.append(selectedcol)
                    
                    if gtype == "Scatter Plot":
                        sn.scatterplot(x=x, y=y)

                    elif gtype == "Line Plot":
                        sn.lineplot(x=x, y=y)

                    elif gtype == "Linear Regression Plot":
                        sn.regplot(x=x, y=y)

                    elif gtype == "Bar Plot":
                        sn.barplot(x=x, y=y)
                
                if c2:
                    c2.header("Graph Display")
                    c2.pyplot(fig)
                else:
                    st.header("Graph Display")
                    st.pyplot(fig)

            else:
                
                cols = st.session_state.userdata.columns
                ycols = [c for c in cols if c not in totaltitles]

                if len(ycols) == 0:
                    st.subheader("Please add accounts to your entries to predict account data.")

                else:

                    predsettings = sidebar.expander("**Prediction Settings:**", expanded=True)
                    predmonth = predsettings.number_input("**Month to Predict:**", min_value=st.session_state.userdata["Month No."].iloc[-1]+1, step=1)
                    startentry = predsettings.number_input("**Starting Entry to Use For Prediction:**", min_value=1, max_value=len(displaydata["Entry No."])-1, step=1)
                    endentry = predsettings.number_input("**Ending Entry to Use For Prediction:**", min_value=startentry+1, max_value=len(displaydata["Entry No."]), value=len(displaydata["Entry No."]), step=1)

                    x = st.session_state.userdata["Month No."][startentry-1:endentry]
                    y = st.session_state.userdata[ycols].iloc[startentry-1:endentry]

                    xtrain, xtest, ytrain, ytest = tts(x, y, test_size=0.2, random_state=40)
                    xtrain, xtest = xtrain.values.reshape(-1, 1), xtest.values.reshape(-1, 1)
                    lr = lreg().fit(xtrain, ytrain)

                    pred = lr.predict([[predmonth]])
                    preddict = {}

                    preddict["Month No."] = [predmonth]
                    preddict["Month"] = ["N/A"]
                    preddict["Year"] = ["N/A"]

                    for title in totaltitles:
                        if title not in ["Month No.", "Month", "Year"]:
                            preddict[title] = 0                 


                    for i in range(len(ycols)):
                        preddict[ycols[i]] = round(pred[0][i], 2)

                    for col in [c for c in preddict if c not in ["Month No.", "Month", "Year"]]:

                        preddict[col] = [preddict[col]]

                        if col[-9:] == "(Revenue)":
                            preddict["Total Revenue"][0] += preddict[col][0]

                        if col[-9:] == "(Expense)":
                            preddict["Total Expenses"][0] += preddict[col][0]
                            
                        if col[-5:] == "(Tax)":
                            preddict["Total Tax"][0] += preddict[col][0]

                    preddict["Net Income"] += (preddict["Total Revenue"][0] - preddict["Total Tax"][0] - preddict["Total Expenses"][0])

                    preddf = pd.DataFrame.from_dict(preddict)

                    if c2:
                        c2.header("Data Prediction")
                        c2.dataframe(pd.DataFrame.from_dict(preddict), use_container_width=True, hide_index=True)

                    else:
                        st.header("Data Prediction")
                        st.dataframe(preddf, use_container_width=True, hide_index=True)

                    if sidebar.button("Add Predicted Entry"):
                            
                        try:
                        
                            data = {}

                            for col in st.session_state.userdata.columns:

                                data[col] = []

                                for val in st.session_state.userdata[col]:
                                    data[col].append(val)

                                if isNum(preddict[col][0]):
                                    newval = round(preddict[col][0], 2)
                                else:
                                    newval = preddict[col][0]

                                data[col].append(newval)


                            data = cleanData(data)
                            newdf = pd.DataFrame().from_dict(data)
                            saveEntries(newdf, st.session_state.userid)

                            print(f"\nEntry created sucessfully for User {st.session_state.userid}.")

                        except:
                            print(f"\nERROR: Entry could not be created for User {st.session_state.userid}.")

                        st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                        st.session_state.userdata = cleanDF(st.session_state.userdata)

                        sidebar.success("Entry created successfully.")


            if c1:
                
                c1.header("Your Data")
                c1.dataframe(displaydata, use_container_width=True, hide_index=True)

            else:
                st.write("---")
                st.header("Your Data")
                st.dataframe(st.session_state.userdata[showCols], use_container_width=True, hide_index=True)                

        else:
            st.subheader("Please enter more than one entry to analyze your data.")