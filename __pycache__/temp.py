import face_recognition
import cv2
import sys
import sqlite3
import csv
import json
import pandas as pd  

def convert_date(string):
	if string.find("-")!=-1:
	 	temp = string.split('-')
	 	x = str(temp[2])+"_"+str(temp[1])+"_"+str(temp[0])
	 	return x
	return string

def take_attendence(date, filename, course):
	conn = sqlite3.connect('student.db')
	print('opened succesfully')


	id_name = {}
	known_face_encodings = []
	known_face_id = []
	known_face_name = []

	path = "Faces/"

	table_name = "attendence"+course
	cursor = conn.execute("select id from %s"%(table_name))
	ids = []
	for row in cursor:
		ids.append(row[0])

	cursor = conn.execute("select * from details")
	for row in cursor:
		if row[0] in ids:
			known_face_id.append(row[0])
			id_name[row[0]] = row[1]
			known_face_name.append(row[1])
			image1 = face_recognition.load_image_file(str(path+str(row[2])))
			image2 = face_recognition.load_image_file(str(path+str(row[3])))
			image3 = face_recognition.load_image_file(str(path+str(row[4])))
			temp = []
			temp.append(face_recognition.face_encodings(image1)[0])
			temp.append(face_recognition.face_encodings(image2)[0])
			temp.append(face_recognition.face_encodings(image3)[0])
			known_face_encodings.append(temp)

	video_capture = cv2.VideoCapture(filename)

	found_ids = []
	count = 0
	while video_capture.isOpened():
		if count%100!=0:
			continue
		ret, frame = video_capture.read()
		if frame is None:
			break
		rgb_small_frame = frame[:, :, ::-1]

		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

		for face_encoding in face_encodings:
			found = []
			for count,person in enumerate(known_face_encodings):
				matches = face_recognition.compare_faces(person, face_encoding, tolerance=0.75)
				matched = 0
				for x in matches:
					if x:
						matched = matched+1
				if x>=2:
					found_id = int(known_face_id[count])
					if found_id not in found_ids:
						found_ids.append(found_id)
						found.append(count)
					break
			for x in found:
				del(known_face_id[x])
				del(known_face_encodings[x])


	date = "\""+date+"\""
	print(found_ids)
	conn.execute("alter table %s\
		add %s INT default 0" %(table_name, date))

	conn.commit()

	for x in found_ids:
		conn.execute("update %s set total_attendence = total_attendence+1 where id=%d"%(table_name,int(x)))
		conn.execute("update %s set %s = 1 where id=%d"%(table_name,date,int(x)))

	conn.commit()

	df = pd.read_sql_query("select * from %s"%(table_name),conn)
	df1 = df.pop('total_attendence')
	df['total_attendence'] = df1
	head = df.columns

	new_head = []
	for x in head:
		new_head.append(convert_date(x))

	df.columns = new_head
	
	csv_file = "CSV/"+table_name+".csv"
	df.to_csv(csv_file, index=False)

	json_file = "Data/"+table_name+".json"
	with open (json_file) as data_file:
		data = json.load(data_file)
	cursor = conn.execute("select id, total_attendence from %s"%(table_name))
	dictionary = {}
	for row in cursor:
		dictionary[row[0]]=row[1]
	for (i,x) in enumerate(data['students']):
		if x['id'] in dictionary:
			data['students'][i]['attendence']=dictionary[x['id']]
			del(dictionary[x['id']])
	for x in dictionary:
		temp={}
		temp['id']=x
		temp['attendence']=dictionary[x]
		data['students'].append(temp)

	with open(json_file, 'w') as outfile:
		json.dump(data, outfile)

	conn.close()