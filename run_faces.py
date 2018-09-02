import find_faces
import cv2
import sys
import sqlite3
import csv
import json
import pandas as pd  
from sklearn import svm
from sklearn.externals import joblib
from PIL import Image,ImageDraw,ImageFont
import time
	
def convert_date(string):
	if string.find("-")!=-1:
	 	temp = string.split('-')
	 	x = str(temp[2])+"_"+str(temp[1])+"_"+str(temp[0])
	 	return x
	return string

def take_attendence(date, filename, course):
	threshold = 0.6
	conn = sqlite3.connect('student.db')
	print('opened succesfully')
	json_file = "Data/dictionary_reverse.json"
	json_rev_file = "Data/dictionary.json"
	with open (json_file) as data_file:
		dictionary = json.load(data_file)

	with open (json_rev_file) as data_file:
		dictionary_rev = json.load(data_file)

	table_name = "attendence"+course
	cursor = conn.execute("select id,name from %s"%(table_name))
	ids = []
	names = {}
	for row in cursor:
		ids.append(row[0])
		names[row[0]] = row[1]

	video_capture = cv2.VideoCapture(filename)

	found_ids = []
	count = -1
	model_name = 'models/trained_model.pkl'
	clf = joblib.load(model_name) 
	while video_capture.isOpened():
		ret, frame = video_capture.read()
		resolution = (768,1368)
		print(frame.shape)
		if frame is None:
			break
		count = count+1
		cv2.resize(frame,resolution)
		frame_other = frame
		if count%30==0:
			print(count)
			rgb_small_frame = frame[:, :, ::-1]
			face_locations = find_faces.face_locations(rgb_small_frame)
			face_recognized = 0


			#New code from here
			font = cv2.FONT_HERSHEY_DUPLEX
			for top, right, bottom, left in face_locations:
				 cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
			string = "Found "+str(len(face_locations))+" Faces in frame number "+str(count)
			cv2.putText(frame, string,(0,700), font, 1.0, (0, 0, 255), 1)
			face_names = []
			cv2.imshow('Video', frame)
			#new code ends here


			face_encodings = find_faces.face_encodings(rgb_small_frame, known_face_locations = face_locations)
			if len(face_encodings)>=1:
				result_all = clf.predict_proba(face_encodings)
				for result in result_all:
					result = list(result)
					index = result.index(max(result))
					if str(index) in dictionary_rev:
						id_no = dictionary_rev[str(index)]
						if id_no in ids:
							print(id_no)
							print(max(result))
							if max(result)>=threshold:
								face_names.append(names[id_no])
								if id_no not in found_ids:
									found_ids.append(id_no)
									face_recognized = face_recognized + 1
							else:
								face_names.append("Unidentified")



			#new code starts from here
			cv2.waitKey(5000)
			cv2.destroyAllWindows()
			for (top, right, bottom, left), name in zip(face_locations, face_names):
				cv2.rectangle(frame_other, (left, top), (right, bottom), (0, 0, 255), 2)
				cv2.rectangle(frame_other, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
				cv2.putText(frame_other, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
			string2 = "Identified "+str(face_recognized)+" Faces out of  "+str(len(face_locations))+" in Frame Number "+str(count)
			cv2.putText(frame_other, string2,(0,250), font, 1.0, (0, 255, 255), 1)
			cv2.imshow('Video', frame_other)
			cv2.waitKey(5000)
			cv2.destroyAllWindows()


			# new code ends here

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