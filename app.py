import streamlit as st
from PIL import Image
import pyodbc
import datetime as dt
import pandas as pd


st.set_page_config(page_title= 'Premium Calculator',layout='wide', initial_sidebar_state='expanded')

image = Image.open('Avon.png')
st.image(image, use_column_width=False)

query = 'select distinct ClientName from tblClientMaster\
        where PolicyExpiryDate >= getdate()'

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
    conn.close()
    return active_clients

active_clients = get_data_from_sql()


def score_calculator(options, mlr, portfolio, pop, last_repriced, tenure, discount, female_pop, rate, industry):
    #Assign score based on the selected MLR of the client
    mlr_score = 0
    if mlr == '1 - 39':
        mlr_score = 0
    elif mlr == '40 - 70':
        mlr_score = 3
    elif mlr == 'Above 70':
        mlr_score = 7

    #Assign score based on the selected portfolio size of the client
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

    #Assign score based on the selected range of the client's active lives
    pop_score = 0
    if pop == '1 - 5000':
        pop_score = 4
    elif pop == '5001 - 10000':
        pop_score = 3
    elif pop == '10001 - 15000':
        pop_score = 2
    elif pop == '15001 - 20000':
        pop = 1
    elif pop == 'Above 20k Lives':
        pop_score = 0
    
    #Assign score based on the selected reprice category of the client
    reprice_score = 0
    if last_repriced == 'Never been Repriced':
        reprice_score = 4
    elif last_repriced == 'Above 3 years':
        reprice_score = 3
    elif last_repriced == '2 years':
        reprice_score = 2
    elif last_repriced == 'Last year':
        reprice_score = 1
    elif last_repriced == 'Long-standing(Never been repriced based on relationship and good MLR)':
        reprice_score = 0

    #Assign score based on the tenure of the client
    tenure_score = 0
    if tenure == 'Above 10 years':
        tenure_score = 1
    elif tenure == '8 - 10 years':
        tenure_score = 2
    elif tenure == '6 - 8 years':
        tenure_score = 3
    elif tenure == '3 - 5 years':
        tenure_score = 4
    elif tenure == '1 - 2 years':
        tenure_score = 0
    
    #Assign score based on whether the client is subscribed to a single plan and the discount history applied to the plan(s)
    discount_score = 0
    if options == 'Single Product' and discount == '2.5 - 5':
        discount_score = 0
    elif options == 'Single Product' and discount == '5.1 - 15.5':
        discount_score = 1
    elif options == 'Single Product' and discount == '15.6 - 30.5':
        discount_score = 2
    elif options == 'Single Product' and discount == '30.6 - 40.5':
        discount_score = 3
    elif options == 'Single Product' and discount == '40.6 - 50':
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

    #Assign score based on the population of female lives the client has
    female_pop_score = 0
    if female_pop == '0 - 10%':
        female_pop_score = 0
    elif female_pop == '11 - 20%':
        female_pop_score = 1
    elif female_pop == '21 - 30%':
        female_pop_score = 2
    elif female_pop == '31 - 40%':
        female_pop_score = 3
    elif female_pop == '41 - 50%':
        female_pop_score = 4
    elif female_pop == 'Above 50%':
        female_pop_score = 5
    #Assign score based on the population of male lives the client has
    # male_pop_score = 0
    # if male_pop == '20 - 30':
    #     male_pop_score = 2
    # elif male_pop == '30 - 40':
    #     male_pop_score = 3
    # elif male_pop == '40 and Above':
    #     male_pop_score = 5
    
    #Assign score based on the number of plans the client is subscribed to and the rate type applied to the plan(s)
    rate_score = 0
    if options == 'Single Product' and rate == 'Base Rate':
        rate_score = 3
    elif options == 'Single Product' and rate == 'Circulation Rate':
        rate_score = 2
    elif options == 'Multiple Product':
        rate_score = rate

    #Assign score based on the Industry category the client is in.
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


    #Calculate the final score and assign the corresponding reccommendation
    final_score = mlr_score + portfolio_score + pop_score + reprice_score + tenure_score + discount_score + female_pop_score  + rate_score + industry_score
    if final_score > 0 and final_score < 11:
        result = 'No Premium Increment'
    elif final_score > 10 and final_score < 21:
        result = '5% Premium Increment'
    elif final_score > 20 and final_score < 31:
        result = '10% Premium Increment'
    elif final_score > 30 and final_score < 41:
        result = '20% Premium Increment'
    elif final_score > 40:
        result = '30% Premium Increment'

    return final_score, result

#Create a title on the sidebar
st.sidebar.title('Premium Calculator')
#Create a radio button that enables the user to select the client category
options = st.sidebar.radio('Is the Client Single or Multi Product', options=['Single Product', 'Multiple Product'])

if options == 'Single Product':

    #Create a sidebar that enables the user to select the different metrics category of the client to be repriced.
    client = st.sidebar.selectbox(label='Select Client', options=active_clients)
    mlr = st.sidebar.selectbox(label='Client MLR Range', options=('1 - 39', '40 - 70', 'Above 70'))
    portfolio = st.sidebar.selectbox(label='Portfolio Size', options=('25,000 - 100,000', '100,001 - 1,000,000', '1M - 5M', '5M - 50M', '50M and Above'))
    pop = st.sidebar.selectbox(label='Lives Population', options=('1 - 5000', '5001 - 10000', '10001 - 15000', '15001 - 20000', 'Above 20K Lives'))
    last_repriced = st.sidebar.selectbox(label='Client Last Reprice Period', options =('Never been Repriced', 'Above 3 years', '2 years', 'Last year', 'Long-standing(Never been repriced based on relationship and good MLR)'))
    tenure = st.sidebar.selectbox(label='Client Tenure', options=('1 - 2 years', '3 - 5 years', '6 - 8 years', '8 - 10 years', 'Above 10 years'))
    discount = st.sidebar.selectbox(label='Previous Discount', options=('2.5 - 5', '5.1 - 15.5', '15.6 - 30.5', '30.6 - 40.5', '40.6 - 50'))
    female_pop = st.sidebar.selectbox(label='Female Population', options=('0 - 10%', '11 - 20%', '21 - 30%', '31 - 40%', '41 - 50%', 'Above 50%'))
    # male_pop = st.sidebar.selectbox(label='Male Population', options=('20 - 30', '30 - 40', '40 and Above'))
    rate = st.sidebar.selectbox(label='Applied Rate', options=('Base Rate', 'Circulation Rate'))
    industry = st.sidebar.selectbox(label='Industry', options=('Financial Services', 'Education', 'Manufacturing and FMCG', 'Real Estate', 'Hospitality', 'Healthcare and Pharmaceuticals', 'Oil and Gas', 'Agriculture', 'Power and Utlilities', 'Tech, Media and Telcos'))

#create a sidebar slider that enables user to select the number of plans the client is subscribed to and select the discount and base rate for each of these products
elif options == 'Multiple Product':
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
    pop = st.sidebar.selectbox(label='Lives Population', options=('1 - 5000', '5001 - 10000', '10001 - 15000', '15001 - 20000', 'Above 20K Lives'))
    last_repriced = st.sidebar.selectbox(label='Client Last Reprice Period', options =('Never been Repriced', 'Above 3 years', '2 years', 'Last year', 'Long-standing(Never been repriced based on relationship and good MLR)'))
    tenure = st.sidebar.selectbox(label='Client Tenure', options=('1 - 2 years', '3 - 5 years', '6 - 8 years', '8 - 10 years', 'Above 10 years'))
    female_pop = st.sidebar.selectbox(label='Female Population', options=('0 - 10%', '11 - 20%', '21 - 30%', '31 - 40%', '41 - 50%', 'Above 50%'))
    # client = st.sidebar.selectbox(label='Select Client', options=active_clients)
    # mlr = st.sidebar.selectbox(label='Client MLR Range', options=('1 - 39', '40 - 70', 'Above 70'))
    # portfolio = st.sidebar.selectbox(label='Portfolio Size', options=('25,000 - 100,000', '100,001 - 1,000,000', '1M - 5M', '5M - 50M', '50M and Above'))
    # pop = st.sidebar.selectbox(label='Lives Population', options=('1 - 1000', '1001 - 5000', '5001 - 10000', 'Above 10K Lives'))
    # last_repriced = st.sidebar.selectbox(label='Client Last Reprice Period', options =('Last Year', '2 Years ago', '3 years and Above'))
    # tenure = st.sidebar.selectbox(label='Client Tenure', options=('1 - 3 years', '4 - 5 years', '6 - 10years'))
    # female_pop = st.sidebar.selectbox(label='Female Population', options=('20 - 30', '30 - 40', '40 and Above'))
    # male_pop = st.sidebar.selectbox(label='Male Population', options=('20 - 30', '30 - 40', '40 and Above'))
    industry = st.sidebar.selectbox(label='Industry', options=('Financial Services', 'Education', 'Manufacturing and FMCG', 'Real Estate', 'Hospitality', 'Healthcare and Pharmaceuticals', 'Oil and Gas', 'Agriculture', 'Power and Utlilities', 'Tech, Media and Telcos'))

    

final_score, result = score_calculator(options,mlr, portfolio, pop, last_repriced, tenure, discount, female_pop, rate, industry)
final_score = round(final_score,2)
st.header('RECOMMENDATION')
st.subheader(client + ' has a total score of ' + str(final_score) + '. It is therefore recommended that their premium should be repriced at ' + result)



