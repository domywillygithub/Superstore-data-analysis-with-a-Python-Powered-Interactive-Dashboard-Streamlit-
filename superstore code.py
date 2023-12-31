import streamlit as st
import plotly.express as px
import pandas as pd 
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title='Superstore Dashboard', page_icon = ':bar_chart:', layout = 'wide')
st.title(':bar_chart: Mega Superstore Sales Dashboard')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)


# fl =st.file_uploader(":black_joker: Upload file", type = (['csv','xlsx','txt','xls']))
# if fl is not None:
#     filename = fl.name
#     st.write(filename)
#     df = pd.read_csv(filename,encoding="ISO-8859-1")
# else:
#     os.chdir(r'C:\Users\domyw\OneDrive\Desktop\codes') 
#     df = pd.read_csv('Sample - Superstore.csv',encoding = "ISO-8859-1") 
  
df = pd.read_csv('Sample - Superstore.csv',encoding = "ISO-8859-1")
col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])

#Getting min and max date

startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date', startDate))

with col2:
    date2 = pd.to_datetime(st.date_input('End Date', endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.image('superstore.jpg', caption = 'DWM Mega Superstore, \nUl. Wroblewskiego 87 \nWroclaw, Poland')

#choose a region
st.sidebar.header('Choose a filter: ')
region = st.sidebar.multiselect('Pick a Region: ', df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

#create for state
state = st.sidebar.multiselect('Pick State: ', df2['State'].unique())
if not state:
    df3= df2.copy()
else:
    df3 = df2[df2['State'].isin(state)] 

# create for city
city = st.sidebar.multiselect('Pick City: ', df3['City'].unique())

#Filter the data based on region, state and city 
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df  = df[df['State'].isin(state)]
elif state and city:
    filtered_df  = df3[df['State'].isin(state) & df3['City'].isin(city)]
elif region and city:
    filtered_df  = df3[df['State'].isin(state) & df3['City'].isin(city)]
elif region and state:
    filtered_df  = df3[df['Region'].isin(region) & df3['State'].isin(state)]
elif city:
    filtered_df  =df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]

category_df = filtered_df.groupby(by=['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader('Sales by Category')
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text = ['${:,.2f}'.format(x) for x in category_df['Sales']],
                   template = 'seaborn') 
    st.plotly_chart(fig, use_container_width=True,height=200)

with col2:
    st.subheader('Sales by Region')  
    fig = px.pie(filtered_df, values='Sales', names = 'Region', hole = 0.5) 
    fig.update_traces(text = filtered_df['Region'],textposition = 'outside')
    st.plotly_chart(fig,use_container_width=True)


cl1, cl2 = st.columns(2)
with cl1:
    with st.expander('Category_viewData'):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name= 'Category.csv',mime = 'text/csv',
        help = 'click here to downloand the data as CSV file')

with cl2:
    with st.expander('Region_viewData'):
        region_df = filtered_df.groupby(by = 'Region', as_index=False)['Sales'].sum()
        st.write(region_df.style.background_gradient(cmap='Oranges'))
        csv = region_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name= 'Region.csv',mime = 'text/csv',
        help = 'click here to downloand the data as CSV file')

filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
st.subheader('Time Series Analytics')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x= 'month_year', y='Sales', labels = {'Sales': 'Amount'}, height = 400, width = 1200, template= 'gridon')
st.plotly_chart(fig2, use_container_width=True)

with st.expander('Time series data view'):
    st.write(linechart.T.style.background_gradient(cmap='Greens'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = 'Time series.csv',mime='text/csv')

# creating a tree map based on region, category and sub-category
st.subheader('Hierarchial view of sales using TreeMap')
fig3 = px.treemap(filtered_df, path = ['Region', 'Category', 'Sub-Category'], values = 'Sales', hover_data = ['Sales'],
                  color = 'Sub-Category')

fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Sales by Segment')
    fig = px.pie(filtered_df, values = 'Sales', names='Segment', template = 'plotly_dark')
    fig.update_traces(text  = filtered_df['Segment'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

sub_category_df = filtered_df.groupby(by=['Sub-Category'])['Sales'].sum().sort_values(ascending=True)
print(sub_category_df)

with chart2:
    st.subheader('Sales by Sub-Category')
    formatted_sales = ['${:,.2f}'.format(x) for x in sub_category_df]  
    fig = px.bar(sub_category_df, y=sub_category_df.index, x=formatted_sales,
                  text=formatted_sales, template='seaborn', orientation="h", color_discrete_sequence=['darkblue'],  # Set all bars to dark blue
                 height=600,width = 800) 
    fig.update_layout(
        xaxis_title="Total Sales",
        yaxis_title="Sub-Category",
        margin=dict(l=50, r=20, t=30, b=50), 
         yaxis=dict(showgrid=False) 
    )
    st.plotly_chart(fig, use_container_width=True, height=200)
    # fig = px.bar(filtered_df, values = 'Sales', names='Category', template = 'gridon')
    # fig.update_traces(text  = filtered_df['Category'], textposition = 'inside')
    # st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff 
st.subheader(":point_right: Monthly Sub-Category Sales Summary")
with st.expander('Summary_Table'):
    df_sample = df[0:5][['Region','State','City','Category','Sales','Profit','Quantity']]
    fig = ff.create_table(df_sample, colorscale='Cividis')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("Monthly Sub-Category Table")
    filtered_df['month'] = filtered_df['Order Date'].dt.month_name()
    sub_category_year = pd.pivot_table(data = filtered_df, values = 'Sales', index = ['Sub-Category'],
                                          columns = 'month')
    st.write(sub_category_year.style.background_gradient(cmap = 'Blues'))

#create a scatter plot
data1 = px.scatter(filtered_df, x = 'Sales', y = 'Profit', size = 'Quantity')
data1['layout'].update(title='Relationship between Sales and Profits using a Scatter Plot',
                       titlefont = dict(size=28), xaxis = dict(title='Sales',titlefont = dict(size=19)),
                       yaxis = dict(title='Profit',titlefont = dict(size=19)))

st.plotly_chart(data1, use_container_width=True)

with st.expander('View complete dataset'):
    st.write(filtered_df.style.background_gradient(cmap='Blues'))

#download complete  dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name = 'dataset.csv', mime = 'text/csv')
