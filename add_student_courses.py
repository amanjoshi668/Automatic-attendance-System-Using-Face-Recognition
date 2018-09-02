import sqlite3
import json
import csv
import pandas as pd  

def add_s_courses(id, courses):
	with open ('Data/details.json') as data_file:
		data = json.load(data_file)
	data[id]=courses
	with open('Data/details.json', 'w') as outfile:
		json.dump(data, outfile)

	conn=sqlite3.connect('student.db')
	cursor = conn.execute("select name from details where id =%d"%(int(id)))
	name=""
	for row in cursor:
		name = "\""+str(row[0])+"\""
	for x in courses:
		table_name = str("attendence"+str(x))
		print(table_name,id,name)
		conn.execute("insert into %s (id,name) values(%d,%s)"%(table_name,int(id),str(name)))
	conn.commit()
	conn.close()
	return