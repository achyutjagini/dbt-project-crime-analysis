This README properly documents the technologies used (Spark, Kafka, MongoDB), datasets, streaming vs batch experiments, commands, results, and conclusion — everything missing in earlier versions.

🔍 Crime Data Analysis using Spark, Kafka & MongoDB
📁 Project Repository

Real-time & batch processing of crime datasets using Spark Streaming, Kafka event pipelines and MongoDB storage.

A DBT course project (UE19CS344) — Jan–May 2022
Team Members: Achyut Jagini (PES2UG19CS013) • Melavoy Nithin Reddy (PES2UG19CS230) • Koduru Bharath Subba Reddy (PES2UG19CS189) 

PES2UG19CS013_189_230-project r…

📌 Project Overview

This project focuses on analysing crime data using Apache Spark, Kafka, and MongoDB.
Two modes of data processing were implemented:

Mode	Description
Batch Processing	Crime CSV datasets processed directly through Spark
Real-Time Streaming	JSON crime events streamed using Kafka producer → consumer → Spark streaming job

The objective is to compare real-time streaming vs batch analytics performance and observe execution behaviour with changing window sizes.

🛠 Technologies Used
Technology	Purpose
Spark	Batch + streaming computation & querying
Kafka + Zookeeper	Real-time data production & consumption
Kafka CMAK UI	Kafka topic monitoring & cluster management
MongoDB	Storage of consumed crime events

Software list from project report 

PES2UG19CS013_189_230-project r…

:

Apache Spark

Kafka

Zookeeper

CMAK Kafka Dashboard

MongoDB

📥 Input Datasets
Dataset	Format	Used In
crime-train.csv, test.csv	CSV	Spark batch processing
police-department-calls-for-service.json	JSON	Kafka real-time streaming

Example JSON schema 

PES2UG19CS013_189_230-project r…

:

{
  "crime_id": "183653763",
  "original_crime_type_name": "Traffic Stop",
  "report_date": "2018-12-31T00:00:00.000",
  "offense_date": "2018-12-31T00:00:00.000",
  "call_time": "23:57",
  "address": "Geary Bl/divisadero St",
  "city": "San Francisco"
}

⚡ Real-Time Streaming Flow
Kafka Producer → Kafka Topic → Kafka Consumer → Spark Streaming → MongoDB

Start Zookeeper
cd /opt/kafka_2.13-3.1.0
sudo bin/zookeeper-server-start.sh config/zookeeper.properties

Start Kafka Broker
cd /opt/kafka_2.13-3.1.0
sudo JMX_PORT=8004 bin/kafka-server-start.sh config/server.properties

Start CMAK Dashboard
cd /opt/CMAK/target/universal/cmak-3.0.0.6
sudo bin/cmak -Dconfig.file=conf/application.conf -Dhttp.port=8080


Dashboard URL: http://127.0.0.1:8080

Produce & Consume Crime Events
python3 kafka_server.py      # producer
python3 consumer_server.py   # consumer


MongoDB receives records successfully 

PES2UG19CS013_189_230-project r…

.

📊 Spark Batch & Streaming Experiments
Streaming Window Results
Window Size	Total Execution Time
100	12:11:24 hrs
200	6:05:21 hrs

(Extracted from report graphs & time logs) 

PES2UG19CS013_189_230-project r…

Batch Execution

Performed using Spark submit:

/opt/spark/bin/spark-submit client.py 2>log.txt

📈 Observations — Batch vs Streaming
Mode	Pros	Cons
Batch	Faster overall	Not real-time
Streaming	Real-time insight & continuous consumption	Higher execution time, depends on window size

Larger streaming windows reduced runtime significantly.

🧾 Conclusion

The project successfully:

✔ Streamed crime events using Kafka + Spark Streaming
✔ Performed Spark SQL queries on data
✔ Stored processed records in MongoDB
✔ Compared batch vs streaming performance
✔ Demonstrated the impact of window sizes on streaming execution time
