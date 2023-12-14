import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from company_data import nasdaq_dict
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(page_title='Nasdaq 100 Index',
                   layout='wide',
                   page_icon=':moneybag:')

@st.cache_data
def load_csv(path):
    data = pd.read_csv(path)
    return data

###Loading Nasdaq Data###

nasdaq_historic_df = load_csv('Nasdaq_Historical.csv')
nasdaq_weight_df = load_csv('Nasdaq_Index_Weight.csv')
nasdaq_company_stock_df = load_csv('Nasdaq_Stocks.csv')

weight_dict = nasdaq_weight_df.set_index('Symbol')['Weight'].to_dict()

###Mathemical Equations###
def working_capital_ratio(x,asset_m=1, liabilities_m=1, colll=1):
    data = load_csv(f'./Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    assets = data.loc[data['Unnamed: 0'] == 'Current Assets' ,data.columns[colll]].sum()
    liabilities = data.loc[data['Unnamed: 0'] == 'Current Liabilities', data.columns[colll]].sum()
    return (assets*asset_m)/(liabilities*liabilities_m)
def acid_test(x, asset_m=1,liabilities_m=1, prepaid_m=1,colll=1):
    data = load_csv(f'./Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    assets = data.loc[data['Unnamed: 0'] == 'Current Assets', data.columns[colll]].sum()
    prepaid = data.loc[data['Unnamed: 0'] == 'Prepaid Assets', data.columns[colll]].sum()
    liabilities = data.loc[data['Unnamed: 0'] == 'Current Liabilities', data.columns[colll]].sum()
    return ((assets* asset_m) - (prepaid*prepaid_m))/(liabilities * liabilities_m)
def earning_per_share(x, net_m=1,diluted_m=1,colll=1):
    data = load_csv(f'./Nasdaq_Financials/{x}_financials.csv')
    net = data.loc[data['Unnamed: 0'] == 'Net Income From Continuing Operation Net Minority Interest', data.columns[colll]].sum()
    diluted = data.loc[data['Unnamed: 0'] == 'Diluted Average Shares', data.columns[colll]].sum()
    return (net*net_m)/(diluted*diluted_m)
def debt_to_equity(x,liabilities_m=1,equity_m=1,colll=1):
    data = load_csv(f'./Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    liabilities = data.loc[data['Unnamed: 0'] == 'Current Liabilities', data.columns[colll]].sum()
    equity = data.loc[data['Unnamed: 0'] == 'Stockholders Equity', data.columns[colll]].sum()
    return (liabilities*liabilities_m)/(equity*equity_m)
def return_on_equity(x, net_m=1, equity_m=1,colll=1):
    data = load_csv(f'./Nasdaq_Financials/{x}_financials.csv')
    data_1 = load_csv(f'./Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    equity = data_1.loc[data_1['Unnamed: 0'] == 'Stockholders Equity', data_1.columns[colll]].sum()
    net = data.loc[data['Unnamed: 0'] == 'Net Income From Continuing Operation Net Minority Interest', data.columns[colll]].sum()
    return (net*net_m)/(equity*equity_m)
def price_earning_ratio(x, price_m=1, net_m=1,diluted_m=1,colll=1, year_select = 'current'):
    if year_select.lower() == 'current':
        price = nasdaq_company_stock_df.loc[(nasdaq_company_stock_df['Symbol'] == x ) & (nasdaq_company_stock_df['Date'] == '2023-11-30'), 'Close'].sum()
    else:
        price = nasdaq_company_stock_df.loc[(nasdaq_company_stock_df['Symbol'] == x) & (nasdaq_company_stock_df['Date'] == '2022-11-30'), 'Close'].sum()
    eps = earning_per_share(x,net_m,diluted_m,colll)
    if eps <= 0:
        return 0
    return (price*price_m)/eps

def operating_margin(x, colll=1):
    data = load_csv(f'./Nasdaq_Financials/{x}_financials.csv')
    operating = data.loc[data['Unnamed: 0'] == 'Operating Income', data.columns[colll]].sum()
    revenue = data.loc[data['Unnamed: 0'] == 'Total Revenue', data.columns[colll]].sum()
    return (operating/revenue)*100

def asset_turnover(x, colll=1):
    data = load_csv(f'./Nasdaq_Financials/{x}_financials.csv')
    data_1 = load_csv(f'./Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    revenue = data.loc[data['Unnamed: 0'] == 'Total Revenue', data.columns[colll]].sum()
    asset = data_1.loc[data_1['Unnamed: 0'] == 'Total Assetts', data_1.columns[colll]].sum()
    return revenue/asset

def liabilities_to_assets(x, colll=1):
    data = load_csv(f'/Nasdaq_BalanceSheet/{x}_balancesheet.csv')
    assets = data.loc[data['Unnamed: 0'] == 'Total Assets', data.columns[colll]].sum()
    liab = data.loc[data['Unnamed: 0'] == 'Total Liabilities Net Minority Interest', data.columns[colll]].sum()
    return liab/assets

def net_margins(x, colll=1):
    data = load_csv(f'./Nasdaq_Financials/{x}_financials.csv')
    revenue = data.loc[data['Unnamed: 0'] == 'Total Revenue', data.columns[colll]].sum()
    inc = data.loc[data['Unnamed: 0'] == 'Net Income', data.columns[colll]].sum()
    return inc/revenue

###Percental Changes###
def percental_change(selects):
    percentalchange = st.number_input(f'What Percental Change For {selects}?',
                                format='%.2f',
                                value=0.)
    return 1 + (percentalchange/100)

###Plot Functions###
##Gauges

def plot_gauges(
        company, name,asset_multi=1,
        liabilities_multi=1, prepaid_multi=1,net_multi=1,diluted_multi=1,equity_multi=1,price_multi=1):

    fig = make_subplots(rows = 2, cols=3,
                        specs=([[{'type':'indicator'}, {'type': 'indicator'},{'type': 'indicator'}],
                                       [{'type':'indicator'}, {'type': 'indicator'},{'type': 'indicator'}]]),
                        vertical_spacing=0,
                        horizontal_spacing=0)
    #Working Capital Ratio
    fig.add_trace(go.Indicator(
        value=working_capital_ratio(company, asset_m=asset_multi,liabilities_m=liabilities_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':working_capital_ratio(company,colll=2)},
        domain={'x':[0,1],'y':[0,1]},
        number={'font.size':26},
        title={'text': 'Working Capital Ratio',
               'font': {'size':28}}
    ),row=1, col=1)
    #Acid Test
    fig.add_trace(go.Indicator(
        value=acid_test(company,asset_m= asset_multi,liabilities_m=liabilities_multi,prepaid_m=prepaid_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':acid_test(company,colll=2)},
        domain={'x':[0,1],'y':[0,1]},
        number={'font.size':26},
        title={'text':'Acid Test',
               'font': {'size':28}}
    ),row=2, col=1)
    #Earnings Per Sare
    fig.add_trace(go.Indicator(
        value= earning_per_share(company,net_m=net_multi,diluted_m=diluted_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':earning_per_share(company,colll=2)},
        domain={'x':[0,1],'y':[0,1]},
        number={'font.size':26},
        title={'text':'Earn Per Share',
               'font': {'size':28}}
    ),row=1, col=2)
    #Price Earning Ratio
    fig.add_trace(go.Indicator(
        value= price_earning_ratio(company,price_m=price_multi,net_m=net_multi,diluted_m=diluted_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':price_earning_ratio(company,colll=2, year_select='last')},
        domain={'x':[0,1],'y':[0,1]},
        number={'font.size':26},
        title={'text':'Price Earning Ratio',
               'font': {'size':28}}
    ),row=2,col=2)
    #Debt To Equity
    fig.add_trace(go.Indicator(
        value=debt_to_equity(company,liabilities_m=liabilities_multi,equity_m=equity_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':debt_to_equity(company,colll=2)},
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font.size': 26},
        title={'text': 'Debt To Equity',
               'font': {'size':28}}
    ), row=1, col=3)
    #Return On Equity
    fig.add_trace(go.Indicator(
        value=return_on_equity(company,net_m=net_multi,equity_m=equity_multi),
        mode='number+delta',
        delta={'position':'top',
               'reference':return_on_equity(company,colll=2)},
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font.size': 26},
        title={'text': 'Return On Equity',
               'font': {'size':28}},
    ), row=2, col=3)

    fig.update_layout(height = 300,
                      margin = {'l': 0, 'r':0, 't':50, 'b':0},
                      title = f"{name}'s Financial Indicators",
                      paper_bgcolor = 'white')

    st.plotly_chart(fig,use_container_width=True)

def plot_line(company, company_name):
    line = nasdaq_company_stock_df[nasdaq_company_stock_df['Symbol'] == company]
    fig = go.Figure()

    for column in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        fig.add_trace(go.Scatter(x=line['Date'], y=line[column],
                                 mode = 'lines',
                                 name = column))
    fig.update_layout(margin = {'r':0,'l':0,'t':25,'b':0},
                      height = 600,
                      title = f'{company_name} Stocks From 2/12/2019 - 30/11/2023',
                      paper_bgcolor = 'white',
                      plot_bgcolor = 'white')
    st.plotly_chart(fig,use_container_width=True)

def plot_historical_line():
    fig = go.Figure()

    for column in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        fig.add_trace(go.Scatter(x=nasdaq_historic_df['Date'],
                                 y= nasdaq_historic_df[column],
                                 mode = 'lines',
                                 name = column))
    fig.update_layout(margin={'r': 0, 'l': 0, 't': 25, 'b': 0},
                      height=600,
                      title=f'Nasdaq Index From 2/12/2019 - 30/11/2023',
                      paper_bgcolor = 'white',
                      plot_bgcolor = 'white')
    st.plotly_chart(fig, use_container_width=True)

### Config Of Page###
header1, header2 = st.columns((1,1.3))
with header1:
    with st.container(border=True):
        st.markdown("""
        <style>
        .big-font {
            font-size:50px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<p class="big-font">Nasdaq-100 Visualisation</p>', unsafe_allow_html=True)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
col_1 , col_2 = st.columns((1,3))


with col_1:
    company_selected = st.selectbox(
        '**Please select a company of your choice from the Nasdaq 100 Index**',
        options= nasdaq_dict.keys())


    company_selected_symbol = nasdaq_dict[company_selected]
    st.markdown(f'{company_selected} is selected for the charts')
    mod = st.toggle('Modify Some Data For The Metrics')
    if mod:
        mod_selected = st.multiselect('Select What You Want To Modify',
                       ['Current Assets', 'Current Liabilities', 'Inventory Prepaid Expenses',
                        'Net Income', 'Diluted Average Shares', "Total Shareholders' Equity",
                        "Share Price"])
    else:
        mod_selected = False

with col_2:
    perc_asset_multi = 1
    perc_liabilities_multi = 1
    perc_prepaid_multi = 1
    perc_net_multi = 1
    perc_diluted_multi = 1
    perc_equity_multi = 1
    perc_price_multi = 1
    if mod_selected:
        if 'Current Assets' in mod_selected:
            perc_asset_multi = percental_change('Current Assets')

        if 'Current Liabilities' in mod_selected:
            perc_liabilities_multi = percental_change('Current_Liabilities')

        if 'Inventory Prepaid Expenses' in mod_selected:
            prepaid_multi = percental_change('Inventory Prepaid Expenses')

        if 'Net Income' in mod_selected:
            modified_net = percental_change('Net Income')

        if 'Diluted Average Shares' in mod_selected:
            diluted_multi = percental_change('Diluted Average Shares')

        if "Total Shareholders' Equity" in mod_selected:
            equity_multi = percental_change("Total Shareholders' Equity")

        if "Share Price" in mod_selected:
            price_multi = percental_change("Share Price")



    plot_gauges(company_selected_symbol, company_selected,asset_multi = perc_asset_multi,
        liabilities_multi = perc_liabilities_multi, prepaid_multi= perc_prepaid_multi,
                net_multi= perc_net_multi,diluted_multi=perc_diluted_multi,equity_multi=perc_equity_multi,
                price_multi=perc_price_multi)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    plot_historical_line()
with bottom_right:
    plot_line(company_selected_symbol, company_selected)






