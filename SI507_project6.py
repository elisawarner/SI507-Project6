#Sites

#ID (SERIAL)
#Name (VARCHAR up to 128 chars, UNIQUE)
#Type [e.g. "National Lakeshore" or "National Park"] (VARCHAR up to 128 chars)
#State_ID (INTEGER - FOREIGN KEY REFERENCING States)
#Location (VARCHAR up to 255 chars)
#Description (TEXT)
#States

#ID (SERIAL)
#Name (VARCHAR up to 40 chars, UNIQUE)

# Import statements
import psycopg2
import psycopg2.extras
import sys
import csv
from psycopg2 import sql
from config import *

DEBUG = False

# Write code / functions to set up database connection and cursor here.

def get_connection_and_cursor():
    try:
        if db_password != "":
            db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
            print("Success connecting to database")
        else:
            db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
    except:
        print("Unable to connect to the database. Check server and credentials.")
        sys.exit(1) # Stop running program if there's no db connection.

    db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

conn, cur = get_connection_and_cursor()


# Write code / functions to create tables with the columns you want and all database setup here.
def setup_database():
    # Invovles DDL commands
    # DDL --> Data Definition Language
    # CREATE, DROP, ALTER, RENAME, TRUNCATE

    conn, cur = get_connection_and_cursor()


    # DEBUG LINE:
    # cur.execute("DROP TABLE IF EXISTS States")

    cur.execute("""CREATE TABLE IF NOT EXISTS "States"(
        "ID" SERIAL PRIMARY KEY,
        "Name" VARCHAR(40) NOT NULL
    )""")


    # DEBUG LINE:
    # cur.execute("DROP TABLE IF EXISTS Sites")

    #### CREATE SITES TABLE ###
    cur.execute("""CREATE TABLE IF NOT EXISTS "Sites"(
        "ID" SERIAL PRIMARY KEY,
        "Name" VARCHAR(128) UNIQUE NOT NULL,
        "Type" VARCHAR(128),
        "State_ID" INTEGER,
        FOREIGN KEY ("State_ID") REFERENCES "States"("ID"),
        "Location" VARCHAR(255),
        "Description" TEXT
    )""")

    # Save changes
    conn.commit()

    print('Setup database complete')


# Write code / functions to deal with CSV files and insert data into the database here.

# creates a dictionary out of the data row
def get_site_dict(row_list, State_ID):
    return {
        'Name': row_list[0],
        'Type': row_list[2],
        'State_ID': State_ID,
        'Location': row_list[1],
        'Description': row_list[4]
    }

# inserts a column into the table
def insert(conn, cur, table, data_dict):
    column_names = data_dict.keys()
    # print(column_names)

    # generate insert into query string
    query = sql.SQL('INSERT INTO "{0}"({1}) VALUES({2}) ON CONFLICT DO NOTHING').format(
        sql.SQL(table),
        sql.SQL(', ').join(map(sql.Identifier, column_names)),
        sql.SQL(', ').join(map(sql.Placeholder, column_names))
    )
    query_string = query.as_string(conn)
    cur.execute(query_string, data_dict)

# the wrapper call function that will insert all the data into the tables and set up the database
def setup_wrapper():
	conn, cur = get_connection_and_cursor()
	# set up the database
	setup_database()
	# add values
	# Any new states to the list need to be added AT THE END of the list in order to keep the state_ids/foreign_keys consistent
	# Or delete the tables first and then redo
	list_of_participating_states = ['arkansas','california','michigan']
	for i in range(len(list_of_participating_states)):
		# Add states
		cur.execute("""INSERT INTO
       	    "States"("ID", "Name")
           	VALUES(%s, %s)
           	on conflict do nothing""",
           	(str(i+1), list_of_participating_states[i]))
		if DEBUG == True:
			print("State %s added to database" % (list_of_participating_states[i]))

		# Add specific sites
		file_name = list_of_participating_states[i] + '.csv'
		with open(file_name, 'r') as state_file:
			filereader = csv.reader(state_file, delimiter=',', quotechar='"')
			next(filereader)
			for row in filereader:
				insert(conn, cur, "Sites", get_site_dict(row, i+1))
				if DEBUG == True:
					print("Site %s in database" % (get_site_dict(row, i+1)['Name']))
	conn.commit()



# Make sure to commit your database changes with .commit() on the database connection.
# COMPLETED INSIDE WRAPPER FUNCTION AND SET UP CALLS


# Write code to be invoked here (e.g. invoking any functions you wrote above)
setup_wrapper() #All functions sequentially organized in wrapper call function

# Write code to make queries and save data in variables here.

# query the database for all of the locations of the sites. 
# (Of course, this data may vary from "Detroit, Michigan" to "Various States: AL, AK, AR, OH, CA, NV, MD" or the like. That's OK!)
# Save the resulting data in a variable called all_locations.

####### QUESTION: IS DICTIONARY FORMAT THE WAY IT SHOULD LOOK #######
cur.execute("""SELECT "Location" FROM "Sites" """)
all_locations = cur.fetchall()
print(all_locations)

##### QUESTION: MUST IT BE EXACTLY "beautiful" OR DOES "beautifully" COUNT? #####
# query the database for all of the names of the sites whose descriptions include the word beautiful. 
# Save the resulting data in a variable called beautiful_sites.
cur.execute("""SELECT "Name" FROM "Sites" WHERE "Description" like '%beautiful%'""")
beautiful_sites = cur.fetchall()
print(beautiful_sites)


# query the database for the total number of sites whose type is National Lakeshore. 
# Save the resulting data in a variable called natl_lakeshores.
cur.execute("""SELECT COUNT("ID") FROM "Sites" WHERE "Type" = 'National Lakeshore' """)
natl_lakeshores = cur.fetchall()
print(natl_lakeshores)

# query your database for the names of all the national sites in Michigan.
# Save the resulting data in a variable called michigan_names. You should use an inner join query to do this.
cur.execute("""SELECT "Sites"."Name", "States"."Name" AS "State_Name" FROM "Sites" INNER JOIN "States" ON "Sites"."State_ID" = "States"."ID" WHERE "States"."Name"='michigan' """)
michigan_names = cur.fetchall()
print(michigan_names)


# query your database for the total number of sites in Arkansas.
# Save the resulting data in a variable called total_number_arkansas. 
# You can use multiple queries + Python code to do this, one subquery, or one inner join query. HINT: You'll need to use an aggregate function!
cur.execute("""SELECT COUNT("Sites"."Name") FROM "Sites" INNER JOIN "States" ON "Sites"."State_ID" = "States"."ID" WHERE "States"."Name"='arkansas' """)
total_number_arkansas = cur.fetchall()
print(total_number_arkansas)
# We have not provided any tests, but you could write your own in this file or another file, if you want.
