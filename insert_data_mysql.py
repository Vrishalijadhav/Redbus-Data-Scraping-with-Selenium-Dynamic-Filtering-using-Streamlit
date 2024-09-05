import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'BLANK@321',  # Update your MySQL password here
    'database': 'redbus_db'
}

def create_mysql_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def upload_to_mysql(csv_file):
    # Read CSV data into a DataFrame
    df = pd.read_csv(csv_file)

    # Replace NaN values with None for MySQL compatibility
    df = df.where(pd.notnull(df), None)
    
    # Create MySQL connection
    connection = create_mysql_connection()
    if connection is None:
        print("Failed to connect to MySQL. Exiting upload.")
        return

    try:
        cursor = connection.cursor()

        # Creating the table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS bus_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Route_Name VARCHAR(255),
            Route_Link VARCHAR(255),
            Bus_Name VARCHAR(255),
            Bus_Type VARCHAR(255),
            Date DATE,
            Departing_Time VARCHAR(50),
            Duration VARCHAR(50),
            Reaching_Time VARCHAR(50),
            Star_Rating VARCHAR(10),
            Price VARCHAR(50),
            Seat_Availability VARCHAR(50)
        )
        '''
        cursor.execute(create_table_query)

        # Insert the data into the MySQL table row by row
        for _, row in df.iterrows():
            try:
                insert_query = '''
                INSERT INTO bus_details (Route_Name, Route_Link, Bus_Name, Bus_Type, Date, 
                                         Departing_Time, Duration, Reaching_Time, Star_Rating, 
                                         Price, Seat_Availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                data_tuple = (row['Route_Name'], row['Route_Link'], row['Bus_Name'], row['Bus_Type'],
                              row['Date'], row['Departing_Time'], row['Duration'], row['Reaching_Time'],
                              row['Star_Rating'], row['Price'], row['Seat_Availability'])

                # Execute the query for each row
                cursor.execute(insert_query, data_tuple)

            except Error as e:
                print(f"Error inserting row: {e}")
                continue  # Skip the row that caused an error

        # Commit the transaction after all rows have been inserted
        connection.commit()
        print("Data uploaded to MySQL successfully!")

    except Error as err:
        print(f"Error uploading data to MySQL: {err}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

# Path to your CSV file
csv_file = 'all_states_bus_details.csv'

# Upload CSV data to MySQL
upload_to_mysql(csv_file)
