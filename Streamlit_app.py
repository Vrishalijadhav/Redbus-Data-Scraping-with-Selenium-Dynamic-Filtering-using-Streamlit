#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime

# Connect to MySQL database
def get_connection():
    return pymysql.connect(host='localhost', user='root', passwd='BLANK@321', database='redbus_db')

# Function to fetch route names starting with a specific letter, arranged alphabetically
def fetch_route_names(connection):
    query = "SELECT DISTINCT Route_Name FROM bus_details ORDER BY Route_Name"
    route_names = pd.read_sql(query, connection)['Route_Name'].tolist()
    return route_names

# Function to fetch data from MySQL based on selected Route_Name, price sort order, and date filter
def fetch_data(connection, route_name, price_sort_order, start_date, end_date):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = '''
    SELECT * FROM bus_details 
    WHERE Route_Name = %s 
    AND Date BETWEEN %s AND %s
    ORDER BY Star_Rating DESC, Price {}
    '''.format(price_sort_order_sql)
    df = pd.read_sql(query, connection, params=(route_name, start_date, end_date))
    return df

# Function to filter data based on Star_Rating and Bus_Type
def filter_data(df, star_rating, bus_type):
    filtered_df = df[df['star_rating'].isin(star_rating) & df['bus_type'].isin(bus_type)]
    return filtered_df

# Main Streamlit app
def main():
    st.header('Easy and Secure Online Bus Tickets Booking')

    connection = get_connection()

    try:
        # Sidebar - Input for starting letter and route name search
        route_names = fetch_route_names(connection)
        route_search = st.sidebar.text_input('Search Route Name', '')
        filtered_route_names = [name for name in route_names if route_search.upper() in name.upper()]

        if filtered_route_names:
            selected_route = st.sidebar.selectbox('Select Route Name', filtered_route_names)
        
            # Sidebar - Date range input
            start_date = st.sidebar.date_input('Start Date', datetime.today())
            end_date = st.sidebar.date_input('End Date', datetime.today())

            # Sidebar - Selectbox for sorting preference
            price_sort_order = st.sidebar.selectbox('Sort by Price', ['Low to High', 'High to Low'])

            # Fetch data based on selected Route_Name, date range, and price sort order
            data = fetch_data(connection, selected_route, price_sort_order, start_date, end_date)

            if not data.empty:
                # Display data table with a subheader
                st.write(f"### Data for Route: {selected_route}")
                st.write(data)

                # Filter by Star_Rating and Bus_Type
                star_rating = data['star_rating'].unique().tolist()
                selected_ratings = st.multiselect('Filter by star rating', star_rating)

                bus_type = data['bus_type'].unique().tolist()
                selected_bus_type = st.multiselect('Filter by bus type', bus_type)

                if selected_ratings and selected_bus_type:
                    filtered_data = filter_data(data, selected_ratings, selected_bus_type)
                    # Display filtered data table with a subheader
                    st.write(f"### Filtered Data for Star Rating: {selected_ratings} and Bus Type: {selected_bus_type}")
                    st.write(filtered_data)
            else:
                st.write(f"No data found for Route: {selected_route} with the specified filters.")
        else:
            st.write("No routes found matching the search criteria.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
