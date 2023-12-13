import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from company_data import nasdaq_dict

st.set_page_config(page_title='Nasdaq 100 Index',
                   layout='wide')

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
    equity = data_1.loc[data_1['Unnamed: 0'] == 'Stockholders Equity', data.columns[colll]].sum()
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

###Plot Functions###
##Gauges
def plot_gauges(
        company,asset_m=1, liabilities_m=1, prepaid_m=1,net_m=1,diluted_m=1,equity_m=1,price_m=1):

    fig = make_subplots(rows = 2, cols=3,
                        specs=([[{'type':'indicator'}, {'type': 'indicator'},{'type': 'indicator'}],
                                       [{'type':'indicator'}, {'type': 'indicator'},{'type': 'indicator'}]]))
    #Working Capital Ratio
    fig.add_trace(go.Indicator(
        value=working_capital_ratio(company, asset_m,liabilities_m),
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
        value=acid_test(company,asset_m,liabilities_m,prepaid_m),
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
        value= earning_per_share(company,net_m,diluted_m),
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
        value= price_earning_ratio(company,price_m,net_m,diluted_m),
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
        value=debt_to_equity(company,net_m,equity_m),
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
        value=return_on_equity(company,net_m,equity_m),
        mode='number+delta',
        delta={'position':'top',
               'reference':return_on_equity(company,colll=2)},
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font.size': 26},
        title={'text': 'Return On Equity',
               'font': {'size':28}}
    ), row=2, col=3)

    fig.update_layout(height = 250,
                      margin = {'l': 0, 'r':0, 't':15, 'b':0})

    st.plotly_chart(fig,use_container_width=True)

### Config Of Page###

col_1 , col_2 = st.columns((1,3))

with col_1:
    company_selected = st.selectbox(
        'Please select a company of your choice from the Nasdaq 100 Index',
        options= nasdaq_dict.keys()
    )
    company_selected_symbol = nasdaq_dict[company_selected]
    st.markdown(f'{company_selected} is selected for the charts')

with col_2:
    plot_gauges(company_selected_symbol)





