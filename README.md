# Data Pipelines with Apache Airflow
Udacity Project 6: Building Data Pipelines with Apache Airflow


### **Introduction**
A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.


### **Project Overview**
To complete the project, we will need to create our own custom operators to perform tasks such as staging the data, filling the data warehouse, and running checks on the data as the final step.

Project template provides four empty operators that need to be implemented into functional pieces of a data pipeline. The template also contains a set of tasks that need to be linked to achieve a coherent and sensible data flow within the pipeline.

Provided with a helpers class that contains all the SQL transformations, that need to be executed it with custom operators.


### **Add Airflow Connections**

![Airflow2](/airflow2.png)


### **Project Template**

> The project template package contains three major components for the project:

>> The dag template has all the imports and task templates in place

>> The operators folder with operator templates

>> A helper class for the SQL transformations

The graph view finally look like:

![Airflow1](/airflow1.png)

### **Building the operators**
>> Build four different operators that will stage the data, transform the data, and run checks on data quality.
>> Utilize Airflow's built-in functionalities as connections and hooks as much as possible and let Airflow do all the heavy-lifting when it is possible.
>> All of the operators and task instances will run SQL statements against the Redshift database. 

> **Stage Operator**
>> The stage operator is expected to be able to load any JSON formatted files from S3 to Amazon Redshift. The operator creates and runs a SQL COPY statement based on the parameters provided. The operator's parameters should specify where in S3 the file is loaded and what is the target table.

>> The parameters should be used to distinguish between JSON file. Another important requirement of the stage operator is containing a templated field that allows it to load timestamped files from S3 based on the execution time and run backfills.

> **Fact and Dimension Operators**
>> With dimension and fact operators, we can utilize the provided SQL helper class to run data transformations. Most of the logic is within the SQL transformations and the operator is expected to take as input a SQL statement and target database on which to run the query against.

>> Dimension loads are often done with the truncate-insert pattern where the target table is emptied before the load. Fact tables are usually so massive that they should only allow append type functionality.

> **Data Quality Operator**
>> The final operator to create is the data quality operator, which is used to run checks on the data itself. The operator's main functionality is to receive one or more SQL based test cases along with the expected results and execute the tests. For each the test, the test result and expected result needs to be checked and if there is no match, the operator should raise an exception and the task should retry and fail eventually.

>> For example one test could be a SQL statement that checks if certain column contains NULL values by counting all the rows that have NULL in the column. We do not want to have any NULLs so expected result would be 0 and the test would compare the SQL statement's outcome to the expected result.

### **Project Datasets**
> Two datasets that reside in S3. Here are the S3 links for each:

>> Song data: s3://udacity-dend/song_data

>> Log data: s3://udacity-dend/log_data

> **Song Dataset**

The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset.

> song_data/A/B/C/TRABCEI128F424C983.json

> song_data/A/A/B/TRAABJL12903CDCF1A.json

And below is an example of what a single song file, TRAABJL12903CDCF1A.json, looks like.

>> {'artist_id': {0: 'AR8IEZO1187B99055E'},
 'artist_latitude': {0: nan},
 'artist_location': {0: ''},
 'artist_longitude': {0: nan},
 'artist_name': {0: 'Marc Shaiman'},
 'duration': {0: 149.86404},
 'num_songs': {0: 1},
 'song_id': {0: 'SOINLJW12A8C13314C'},
 'title': {0: 'City Slickers'},
 'year': {0: 2008}}


> **Log Dataset**

The second dataset consists of log files in JSON format generated by this event simulator based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations, partitioned by year and month...

> For example, here are filepaths to two files in this dataset.
>> log_data/2018/11/2018-11-12-events.json

>> log_data/2018/11/2018-11-13-events.json

And below is an example of what the data in a log file, 2018-11-12-events.json, looks like.

>> {'artist': {0: 'Sydney Youngblood', 1: 'Gang Starr'},
 'auth': {0: 'Logged In', 1: 'Logged In'},
 'firstName': {0: 'Jacob', 1: 'Layla'},
 'gender': {0: 'M', 1: 'F'},
 'itemInSession': {0: 53, 1: 88},
 'lastName': {0: 'Klein', 1: 'Griffin'},
 'length': {0: 238.07955, 1: 151.92771},
 'level': {0: 'paid', 1: 'paid'},
 'location': {0: 'Tampa-St. Petersburg-Clearwater, FL',
  1: 'Lake Havasu City-Kingman, AZ'},
 'method': {0: 'PUT', 1: 'PUT'},
 'page': {0: 'NextSong', 1: 'NextSong'},
 'registration': {0: 1540558108796.0, 1: 1541057188796.0},
 'sessionId': {0: 954, 1: 984},
 'song': {0: "Ain't No Sunshine", 1: 'My Advice 2 You (Explicit)'},
 'status': {0: 200, 1: 200},
 'ts': {0: 1543449657796, 1: 1543449690796},
 'userAgent': {0: '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2"',
  1: '"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"'},
 'userId': {0: '73', 1: '24'}}


### **Schema for Song Play Analysis**

#### **Fact Table**

> **songplays** - records in log data associated with song plays i.e. records with page NextSong
>> - songplay_id
>> - start_time
>> - user_id
>> - level
>> - song_id
>> - artist_id
>> - session_id
>> - location
>> - user_agent


#### **Dimension Tables**

> **users - users in the app**
>> - user_id
>> - first_name
>> - last_name
>> - gender
>> - level

> **songs** - songs in music database
>> - song_id
>> - title
>> - artist_id
>> - year
>> - duration

> **artists** - artists in music database
>> - artist_id
>> - name
>> - location
>> - latitude
>> - longitude

> **time** - timestamps of records in songplays broken down into specific units
>> - start_time
>> - hour
>> - day
>> - week
>> - month
>> - year
>> - weekday
