import streamlit as st
from PIL import Image
import pyodbc
import datetime as dt
import pandas as pd


st.set_page_config(page_title= 'Premium Calculator',layout='wide', initial_sidebar_state='expanded')

image = Image.open('utilization_image.png')
st.image(image, use_column_width=False)

query = 'SELECT  DISTINCT Name\
        FROM dimClient'

@st.cache_data(ttl = dt.timedelta(hours=24))
def get_data_from_sql():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
        +st.secrets['server']
        +';DATABASE='
        +st.secrets['database']
        +';UID='
        +st.secrets['username']
        +';PWD='
        +st.secrets['password']
        )
    
    active_clients = pd.read_sql(query, conn)
    return active_clients

active_clients = get_data_from_sql()


def score_calculator(options, mlr, portfolio, pop, last_repriced, tenure, discount, female_pop, male_pop, rate, industry):
    mlr_score = 0
    if mlr == '1 - 39':
        mlr_score = 0
    elif mlr == '40 - 70':
        mlr_score = 3
    elif mlr == 'Above 70':
        mlr_score = 7

    portfolio_score = 0
    if portfolio == '25,000 - 100,000':
        portfolio_score = 4
    elif portfolio == '100,001 - 1,000,000':
        portfolio_score = 3
    elif portfolio == '1M - 5M':
        portfolio_score = 2
    elif portfolio == '5M - 50M':
        portfolio_score = 1
    elif portfolio == '50M and Above':
        portfolio_score = 0

    pop_score = 0
    if pop == '1 - 1000':
        pop_score = 5
    elif pop == '1001 - 5000':
        pop_score = 3
    elif pop == '5001 - 10000':
        pop_score = 2
    elif pop == 'Above 10k Lives':
        pop_score = 0
    
    reprice_score = 0
    if last_repriced == 'Last Year':
        reprice_score = 0
    elif last_repriced == '2 Years ago':
        reprice_score = 3
    elif last_repriced == '3 years and Above':
        reprice_score = 7

    tenure_score = 0
    if tenure == '1 - 3 years':
        tenure_score = 5
    elif tenure == '4 - 5 years':
        tenure_score = 3
    elif tenure == '6 - 10 years':
        tenure_score = 2

    discount_score = 0
    if options == 'Single Product' and discount == '1 - 10':
        discount_score = 0
    elif options == 'Single Product' and discount == '11 - 20':
        discount_score = 1
    elif options == 'Single Product' and discount == '21 - 30':
        discount_score = 2
    elif options == 'Single Product' and discount == '31 - 40':
        discount_score = 3
    elif options == 'Single Product' and discount == '41 - 50':
        discount_score = 4
    elif options == 'Multiple Product' and discount > 0 and discount < 11:
        discount_score = 0
    elif options == 'Multiple Product' and discount > 10 and discount < 21:
        discount_score = 1
    elif options == 'Multiple Product' and discount > 20 and discount < 31:
        discount_score = 2
    elif options == 'Multiple Product' and discount > 30 and discount < 41:
        discount_score = 3
    elif options == 'Multiple Product' and discount > 40 and discount < 51:
        discount_score = 4

    female_pop_score = 0
    if female_pop == '20 - 30':
        female_pop_score = 2
    elif female_pop == '30 - 40':
        female_pop_score = 3
    elif female_pop == '40 and Above':
        female_pop_score = 5

    male_pop_score = 0
    if male_pop == '20 - 30':
        male_pop_score = 2
    elif male_pop == '30 - 40':
        male_pop_score = 3
    elif male_pop == '40 and Above':
        male_pop_score = 5
    
    rate_score = 0
    if options == 'Single Product' and rate == 'Base Rate':
        rate_score = 3
    elif options == 'Single Product' and rate == 'Circulation Rate':
        rate_score = 2
    elif options == 'Multiple Product':
        rate_score = rate

    industry_score = 0
    if industry == 'Financial Services':
        industry_score = 0.5
    elif industry == 'Education':
        industry_score = 0.5
    elif industry == 'Manufacturing and FMCG':
        industry_score = 2
    elif industry == 'Real Estate':
        industry_score = 1
    elif industry == 'Hospitality':
        industry_score = 0.5
    elif industry == 'Healthcare and Pharmaceuticals':
        industry_score = 0.5
    elif industry == 'Oil and Gas':
        industry_score = 2
    elif industry == 'Agriculture':
        industry_score = 0.5
    elif industry == 'Power and Utlilities':
        industry_score = 1
    elif industry == 'Tech, Media and Telcos':
        industry_score = 1.5



    final_score = mlr_score + portfolio_score + pop_score + reprice_score + tenure_score + discount_score + female_pop_score + male_pop_score + rate_score + industry_score
    if final_score > 0 and final_score < 11:
        result = 'No Premium Increment'
    elif final_score > 10 and final_score < 31:
        result = '5% Premium Increment'
    elif final_score > 30 and final_score < 51:
        result = '10% Premium Increment'
    elif final_score > 50 and final_score < 71:
        result = '20% Premium Increment'
    elif final_score > 70:
        result = '30% Premium Increment'

    return final_score, result

st.sidebar.title('Premium Calculator')
options = st.sidebar.radio('Is the Client Single or Multi Product', options=['Single Product', 'Multiple Product'])

if options == 'Single Product':

    client = st.sidebar.selectbox(label='Select Client', options=active_clients)
    mlr = st.sidebar.selectbox(label='Client MLR Range', options=('1 - 39', '40 - 70', 'Above 70'))
    portfolio = st.sidebar.selectbox(label='Portfolio Size', options=('25,000 - 100,000', '100,001 - 1,000,000', '1M - 5M', '5M - 50M', '50M and Above'))
    pop = st.sidebar.selectbox(label='Lives Population', options=('1 - 1000', '1001 - 5000', '5001 - 10000', 'Above 10K Lives'))
    last_repriced = st.sidebar.selectbox(label='Client Last Reprice Period', options =('Last Year', '2 Years ago', '3 years and Above'))
    tenure = st.sidebar.selectbox(label='Client Tenure', options=('1 - 3 years', '4 - 5 years', '6 - 10years'))
    discount = st.sidebar.selectbox(label='Previous Discount', options=('1 - 10', '11 - 20', '21 - 30', '31 - 40', '41 - 50'))
    female_pop = st.sidebar.selectbox(label='Female Population', options=('20 - 30', '30 - 40', '40 and Above'))
    male_pop = st.sidebar.selectbox(label='Male Population', options=('20 - 30', '30 - 40', '40 and Above'))
    rate = st.sidebar.selectbox(label='Applied Rate', options=('Base Rate', 'Circulation Rate'))
    industry = st.sidebar.selectbox(label='Industry', options=('Financial Services', 'Education', 'Manufacturing and FMCG', 'Real Estate', 'Hospitality', 'Healthcare and Pharmaceuticals', 'Oil and Gas', 'Agriculture', 'Power and Utlilities', 'Tech, Media and Telcos'))

if options == 'Multiple Product':
    num_of_products = st.sidebar.slider(label='Total Number of Products', min_value=2, max_value=7)
    if num_of_products == 2:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        discount = (product1 + product2)/2
        rate = (rate_score1 + rate_score2)/2

    elif num_of_products == 3:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        product3 = st.sidebar.slider(label='Product 3 Discount', min_value=0,max_value=50)
        rate3 = st.sidebar.radio(label='Product 3 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate3 == 'Base Rate':
            rate_score3 = 3
        elif rate3 == 'Circulation Rate':
            rate_score3 = 2
        discount = (int(product1) + int(product2) + int(product3))/3
        rate = (rate_score1 + rate_score2 + rate_score3)/3

    elif num_of_products == 4:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        product3 = st.sidebar.slider(label='Product 3 Discount', min_value=0,max_value=50)
        rate3 = st.sidebar.radio(label='Product 3 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate3 == 'Base Rate':
            rate_score3 = 3
        elif rate3 == 'Circulation Rate':
            rate_score3 = 2
        product4 = st.sidebar.slider(label='Product 4 Discount', min_value=0,max_value=50)
        rate4 = st.sidebar.radio(label='Product 4 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate4 == 'Base Rate':
            rate_score4 = 3
        elif rate4 == 'Circulation Rate':
            rate_score4 = 2
        discount = (int(product1) + int(product2) + int(product3) + int(product4))/4
        rate = (rate_score1 + rate_score2 + rate_score3 + rate_score4)/4

    elif num_of_products == 5:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        product3 = st.sidebar.slider(label='Product 3 Discount', min_value=0,max_value=50)
        rate3 = st.sidebar.radio(label='Product 3 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate3 == 'Base Rate':
            rate_score3 = 3
        elif rate3 == 'Circulation Rate':
            rate_score3 = 2
        product4 = st.sidebar.slider(label='Product 4 Discount', min_value=0,max_value=50)
        rate4 = st.sidebar.radio(label='Product 4 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate4 == 'Base Rate':
            rate_score4 = 3
        elif rate4 == 'Circulation Rate':
            rate_score4 = 2
        product5 = st.sidebar.slider(label='Product 5 Discount', min_value=0,max_value=50)
        rate5 = st.sidebar.radio(label='Product 5 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate5 == 'Base Rate':
            rate_score5 = 3
        elif rate5 == 'Circulation Rate':
            rate_score5 = 2
        discount = (product1 + product2 + product3 + product4 + product5)/5
        rate = (rate_score1 + rate_score2 + rate_score3 +rate_score4 + rate_score5)/5

    elif num_of_products == 6:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        product3 = st.sidebar.slider(label='Product 3 Discount', min_value=0,max_value=50)
        rate3 = st.sidebar.radio(label='Product 3 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate3 == 'Base Rate':
            rate_score3 = 3
        elif rate3 == 'Circulation Rate':
            rate_score3 = 2
        product4 = st.sidebar.slider(label='Product 4 Discount', min_value=0,max_value=50)
        rate4 = st.sidebar.radio(label='Product 4 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate4 == 'Base Rate':
            rate_score4 = 3
        elif rate4 == 'Circulation Rate':
            rate_score4 = 2
        product5 = st.sidebar.slider(label='Product 5 Discount', min_value=0,max_value=50)
        rate5 = st.sidebar.radio(label='Product 5 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate5 == 'Base Rate':
            rate_score5 = 3
        elif rate5 == 'Circulation Rate':
            rate_score5 = 2
        product6 = st.sidebar.slider(label='Product 6 Discount', min_value=0,max_value=50)
        rate6 = st.sidebar.radio(label='Product 6 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate6 == 'Base Rate':
            rate_score6 = 3
        elif rate6 == 'Circulation Rate':
            rate_score6 = 2
        discount = (product1 + product2 + product3 + product4 + product5 + product6) /6
        rate = (rate_score1 + rate_score2 + rate_score3 +rate_score4 + rate_score5 + rate_score6)/6

    elif num_of_products == 7:
        product1 = st.sidebar.slider(label='Product 1 Discount', min_value=0,max_value=50)
        rate1 = st.sidebar.radio(label='Product 1 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate1 == 'Base Rate':
            rate_score1 = 3
        elif rate1 == 'Circulation Rate':
            rate_score1 = 2
        product2 = st.sidebar.slider(label='Product 2 Discount', min_value=0,max_value=50)
        rate2 = st.sidebar.radio(label='Product 2 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate2 == 'Base Rate':
            rate_score2 = 3
        elif rate2 == 'Circulation Rate':
            rate_score2 = 2
        product3 = st.sidebar.slider(label='Product 3 Discount', min_value=0,max_value=50)
        rate3 = st.sidebar.radio(label='Product 3 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate3 == 'Base Rate':
            rate_score3 = 3
        elif rate3 == 'Circulation Rate':
            rate_score3 = 2
        product4 = st.sidebar.slider(label='Product 4 Discount', min_value=0,max_value=50)
        rate4 = st.sidebar.radio(label='Product 4 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate4 == 'Base Rate':
            rate_score4 = 3
        elif rate4 == 'Circulation Rate':
            rate_score4 = 2
        product5 = st.sidebar.slider(label='Product 5 Discount', min_value=0,max_value=50)
        rate5 = st.sidebar.radio(label='Product 5 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate5 == 'Base Rate':
            rate_score5 = 3
        elif rate5 == 'Circulation Rate':
            rate_score5 = 2
        product6 = st.sidebar.slider(label='Product 6 Discount', min_value=0,max_value=50)
        rate6 = st.sidebar.radio(label='Product 6 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate6 == 'Base Rate':
            rate_score6 = 3
        elif rate6 == 'Circulation Rate':
            rate_score6 = 2
        product7 = st.sidebar.slider(label='Product 7 Discount', min_value=0,max_value=50)
        rate7 = st.sidebar.radio(label='Product 7 Rate', options=('Base Rate', 'Circulation Rate'))
        if rate7 == 'Base Rate':
            rate_score7 = 3
        elif rate7 == 'Circulation Rate':
            rate_score7 = 2
        discount = (product1 + product2 + product3 + product4 + product5 + product6 + product7) /7
        rate = (rate_score1 + rate_score2 + rate_score3 +rate_score4 + rate_score5 + rate_score6 + rate_score7)/7
       

    client = st.sidebar.selectbox(label='Select Client', options=active_clients)
    mlr = st.sidebar.selectbox(label='Client MLR Range', options=('1 - 39', '40 - 70', 'Above 70'))
    portfolio = st.sidebar.selectbox(label='Portfolio Size', options=('25,000 - 100,000', '100,001 - 1,000,000', '1M - 5M', '5M - 50M', '50M and Above'))
    pop = st.sidebar.selectbox(label='Lives Population', options=('1 - 1000', '1001 - 5000', '5001 - 10000', 'Above 10K Lives'))
    last_repriced = st.sidebar.selectbox(label='Client Last Reprice Period', options =('Last Year', '2 Years ago', '3 years and Above'))
    tenure = st.sidebar.selectbox(label='Client Tenure', options=('1 - 3 years', '4 - 5 years', '6 - 10years'))
    female_pop = st.sidebar.selectbox(label='Female Population', options=('20 - 30', '30 - 40', '40 and Above'))
    male_pop = st.sidebar.selectbox(label='Male Population', options=('20 - 30', '30 - 40', '40 and Above'))
    industry = st.sidebar.selectbox(label='Industry', options=('Financial Services', 'Education', 'Manufacturing and FMCG', 'Real Estate', 'Hospitality', 'Healthcare and Pharmaceuticals', 'Oil and Gas', 'Agriculture', 'Power and Utlilities', 'Tech, Media and Telcos'))



final_score, result = score_calculator(options,mlr, portfolio, pop, last_repriced, tenure, discount, female_pop, male_pop, rate, industry)
st.header('RECOMMENDATION')
st.subheader(client + ' has a total score of ' + str(final_score) + '. It is therefore recommended that their premium should be repriced at ' + result)



