# importing required libraries
#importing all directories needed
import os
import sys, pyspark, json
from pyspark import SparkContext
import numpy as np
import csv
import matplotlib.pyplot as plt

import pyspark.sql.types as tp

from pyspark.sql import SQLContext, SparkSession
from pyspark.sql import SparkSession,Row,Column
from pyspark.streaming import StreamingContext

from pyspark.sql.functions import col

from pyspark.sql.functions import *

from pyspark.sql.types import FloatType

import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import lit,monotonically_increasing_id, row_number
from pyspark.sql import Window
import datetime
import pandas as pd



sc = SparkContext("local[2]", "Crime")
#spark = SparkSession(sc)
ssc = StreamingContext(sc, 1)
sql_context=SQLContext(sc)


def dfto(data):
	if data.isEmpty():
		return
	s = SparkSession(data.context)
	data = data.collect()[0]
	#converting data into dataframe for easy usage
	cols = [f"feature{j}" for j in range(len(data[0]))]
	colm = ['Dates','Category','Descript', 'DayOfWeek', 'PdDistrict', 'Resolution', 'Address','X', 'Y']
	df = s.createDataFrame(data, colm)
	df.show()
	df = df.withColumn('X', df['X'].cast(FloatType()))
	df = df.withColumn('Y', df['Y'].cast(FloatType()))
        
        
	df.groupBy("Category").count().orderBy(col("count").desc()).show()
	
	df.groupBy("Descript").count().orderBy(col("count").desc()).show()
	
	df.select(min('Dates').alias('first_record_date'),max('Dates').alias('latest_record_date')).show(truncate=False)
	
	
	df = df.withColumn('date_time', to_timestamp('Dates','yyyy-MM-dd HH:mm:ss'))\
       .withColumn('month', trunc('date_time', 'YYYY')) #adding a month column to be able to view stats on a monthly basis
       
	df.select(['Dates','date_time', 'month'])\
      	.show()
	
	
	type_arrest_date = df.groupBy(['Resolution', 'month'])\
                     .count()\
                     .orderBy(['month', 'count'])
	print()
	type_arrest_date.show()
	
	
	type_arrest_pddf = pd.DataFrame(type_arrest_date.rdd.map(lambda l: l.asDict()).collect())
	
	
	type_arrest_pddf['yearpd'] = type_arrest_pddf['month'].apply(lambda dt: datetime.datetime.strftime(pd.Timestamp(dt), '%Y'))
	#type_arrest_pddf['arrest'] = type_arrest_pddf['arrest'].apply(lambda l: l=='True')
	type_arrest_pddf['arrest'] = type_arrest_pddf['Resolution'].apply(lambda l:"ARREST" in l)
	print(type_arrest_pddf)
	
	
	#What time of the day are ciminal the busiest?
	
	df_hour = df.withColumn('hour',hour(df['date_time']))
	hourly_count = df_hour.groupBy('hour').count().cache()
	hourly_total_count = hourly_count.groupBy('hour').sum('count')
	
	hourly_count_pddf = pd.DataFrame(hourly_total_count.select(hourly_total_count['hour'], hourly_total_count['sum(count)'].alias('count'))\
                                .rdd.map(lambda l: l.asDict())\
                                 .collect())

	print(hourly_count_pddf)
	
	
	#df.select('PdDistrict').distinct().count()
	
	#What are the top disctricts where crime occurred?
	
	df.groupBy(['PdDistrict']).count().orderBy('count', ascending=False).show()
	
	#street_home_hour = location_hour.where((location_hour['PdDistrict'] == 'CENTRAL') | (location_hour['PdDistrict'] == 'NORTHERN'))
	#a data frame with location descriptions and counts of recorded crimes, and hours...
	#street_home_hour_pddf = pd.DataFrame(street_home_hour.rdd.map(lambda row: row.asDict()).collect())
	#street_home_hour_pddf = street_home_hour_pddf.sort_values(by='hour')
	
	#print(street_home_hour_pddf)
	
	categorydf = pd.DataFrame(df_hour.groupBy(['Category', 'hour']).count().orderBy('hour').rdd.map(lambda row: row.asDict()).collect())
	print(categorydf)
	
	
	#dom = domestic_hour[domestic_hour['Category==NON-CRIMINAL'] == 'True']['count']
	#non_dom = domestic_hour[domestic_hour['Category==NON-CRIMINAL'] == 'False']['count']

	#either_dom = domestic_hour.groupby(by=['hour']).sum()['count']

	#dom_keys = domestic_hour[domestic_hour['domestic'] == 'False']['hour']
        
	df_dates = df_hour.withColumn('week_day', dayofweek(df_hour['date_time']))\
                 .withColumn('year_month', month(df_hour['date_time']))\
                 .withColumn('month_day', dayofmonth(df_hour['date_time']))\
                 .withColumn('date_number', datediff(df['date_time'], to_date(lit('2001-01-01'), format='yyyy-MM-dd')))\
                 .cache()

	df_dates.select(['Dates', 'month', 'hour', 'week_day', 'year_month', 'month_day', 'date_number']).show(20, truncate=False)
	
	week_day_crime_counts = df_dates.groupBy('week_day').count()
	week_day_crime_counts_pddf = pd.DataFrame(week_day_crime_counts.orderBy('week_day').rdd.map(lambda e: e.asDict()).collect())
	print(week_day_crime_counts_pddf)
	
	
	
	month_day_crime_counts = df_dates.groupBy('month_day').count()
	month_day_crime_counts_pddf = pd.DataFrame(month_day_crime_counts.orderBy('month_day').rdd.map(lambda e: e.asDict()).collect())
	month_day_crime_counts_pddf.sort_values(by='count', ascending=False).head(10)
	
	
	month_day_crime_counts_pddf = month_day_crime_counts_pddf.sort_values(by='month_day', ascending=True)
	print(month_day_crime_counts_pddf)
	
	
	df_dates_community_areas = df_dates.na.drop(subset=['address']).groupBy('address').count()
	df_dates_community_areas.orderBy('count', ascending=False).show(10)
	
	top_crime_types = df_dates.select('Category').groupBy('Category').count().rdd.map(lambda row: row.asDict()).takeOrdered(10, key=lambda l: 1/l['count'])

	top_busy_areas =  df_dates_community_areas.rdd.map(lambda row: row.asDict()).takeOrdered(10, key=lambda l: 1/l['count'])
	
	top_crime_types_lst = [dc['Category'] for dc in top_crime_types]
	top_busy_areas_lst = [dc['address'] for dc in top_busy_areas]
	
	
	
	print(top_crime_types_lst)
	print(top_busy_areas_lst)
       
	#df_hour = df.withColumn('hour', hour(df['date_time']))
	
	
	#week_day_crime_counts = df_dates.groupBy('week_day').count()
	
		

def mapdat(data):
    lstrecord = list()
    js_dat=json.loads(data)
    for record in js_dat:
        tup = tuple(js_dat[record].values())
        lstrecord.append(tup)
    return lstrecord 	

lines = ssc.socketTextStream("localhost",6100).map(mapdat).foreachRDD(dfto)

ssc.start() 
#ssc.awaitTermination(100)
#ssc.stop()
ssc.awaitTermination()

