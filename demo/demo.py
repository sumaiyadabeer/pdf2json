import json
import tabula
from collections import OrderedDict

import pymongo

from tkinter import *
from tkinter import filedialog
import tkinter as tk




def remove_empty_cells(data):
	#print(len(data))
	for i in range(len(data)-1,-1,-1):
	    if data[i]["text"] == "":
	    	#print("poping............"+ str(i))
	    	data.pop(i)
	    	#break

	#print(data)
	return data


def remove_neglegible_cells(data):
	#print(len(data))
	for i in range(len(data)-1,-1,-1):
	    if float(data[i]["width"]) <1.0:
	    	#print("poping............"+ str(i))
	    	data.pop(i)
	    	#break

	#print(data)
	return data
def in_range(cl,cr,pl,pr):
	if cl >=pl and cl<=pr and cr >=pl and cr<=pr:
		return True
	else:
		return False

def Is_nested(h1,h2):
	h1=remove_empty_cells(h1)
	h2=remove_empty_cells(h2)

	#make critaria more refined
	if len(h1) == len(h2):
		return False
	else:
		return True



def read_pdf():
	global path1
	table_list=[]
	path=filedialog.askopenfilename(filetypes=(("PDF", ".pdf"), ("All files", "*.*")))
	path1=path
	tabula.convert_into(path1, "jsontable.json", lattice=True, output_format="json", pages='all')
	greetings_disp =tk.Text(master=window,height=1,width=len("pdf file:"+path1) ,fg="midnight blue")
	greetings_disp.grid(column=0,row=3)
	greetings_disp.insert(tk.END , "pdf file:"+path1)


def see_pdf():
	obj  = json.load(open("jsontable.json"))
	message="loaded PDF: "+str(path1)+ "\n found "+str(len(obj))+" table/tables"
	greetings_disp =tk.Text(master=window,height=3,width=len("loaded PDF: "+str(path1)),fg="midnight blue")
	greetings_disp.grid(column=0,row=5)
	greetings_disp.insert(tk.END , message)


def convert_to_json():
	obj  = json.load(open("jsontable.json"))
	print(len(obj))
	#table_list = []
	for i in range(len(obj)):
		print(i)

		data = obj[i]["data"]
		name=remove_empty_cells(data[0])
		Table = table(Is_nested(data[1],data[2]),name[0]["text"])

		parent = remove_empty_cells(data[1])
		if Table.is_nested:
			child=remove_empty_cells(data[2])
			value_index=3
		else:
			child = []
			value_index=2
		Table.get_attribute(parent,child)
		#Table.print_class()

		#value 
		for row in range(value_index,len(data)):
			value= []
			filter_value = remove_neglegible_cells(data[row])
			for i in filter_value:
				value.append(i["text"])
			#print(value)

			Table.get_values(value)

		Table.store_values()
		Table.print_class()
		table_list.append(Table)


	message="Successfully converted to json "+"\nfind these files in data directory:\n     "
	for i in table_list:
		message = message+ i.name +"\n     "

	greetings_disp =tk.Text(master=window,height =min(50, len(table_list)+2),width=len("loaded PDF: "+str(path1)),fg="midnight blue")
	greetings_disp.grid(column=0,row=7)
	greetings_disp.insert(tk.END , message)


def db_insert():
	myclient=pymongo.MongoClient("mongodb://localhost:27017/")
	mydb= myclient["pdf2json"]
	message = "starting server at 'mongodb://localhost:27017/'\ndatabse created:pdf2json\ncollections created:\n      "
	for i in table_list:
		message = message+ i.name +"\n      "
		mycol = mydb[i.name]
		x=mycol.insert(i.values)
		print(x)
	greetings_disp =tk.Text(master=window,height =min(50, len(table_list)+3),width=len("starting server at 'mongodb://localhost:27017/'"),fg="midnight blue")
	greetings_disp.grid(column=0,row=9)
	greetings_disp.insert(tk.END , message)



class table():
	is_nested = False
	name = ""
	attribute_list = []
	values = []

	def __init__(self,Is_Nest,Name):
		self.is_nested = Is_Nest
		self.name = Name
		self.attribute_list = []
		self.values = []


	def store_values(self):
		open("./data/"+self.name+".json", "w").write(json.dumps(self.values, indent=4, separators=(',', ': ')))


	def print_class(self):
		print(self.is_nested)
		print(self.name)
		print(self.attribute_list)
		print(self.values)



	def get_attribute(self,parent,child):
		result = OrderedDict()
		#result_list = []
		for p in parent:
			self.attribute_list.append(p["text"])
			childDict = OrderedDict()
			child_list=[]
			for c in child:
				print(c)
				lc= float(c["left"])
				wc= float(c["width"])
				lp= float(p["left"])
				wp= float(p["width"])

				if in_range(lc,lc+wc, lp, lp+wp+0.0001):
					childDict[c["text"]]= None
					child_list.append(c["text"])
					print(c["text"]+" is added" )
					#print(c["text"]+ "----------->"+ p["text"])

			result[p["text"]]= childDict
			#result_list.append(child_list)
			self.attribute_list.append(child_list)
			if len(childDict)==0:
				self.attribute_list.pop()
				result[p["text"]]= None
		#return result,  result_list





	def get_values(self, value):
		#handle valus by comapring no of possible attribute and remove the extra cells
		result = {}
		count = 0
		var=0
		#print(value)
		for i in range(len(self.attribute_list)):
			print(self.attribute_list[i])
			if var>0:
				var= var-1
				print("skipping")
				continue
			child={}
			if(i < len(self.attribute_list)-1):
				print("now handling last attribute")
				print(i,len(self.attribute_list))
				if(isinstance(self.attribute_list[i], (str)) and isinstance(self.attribute_list[i+1], (list))):
					for j in self.attribute_list[i+1]:
						child[j]= value[count]
						count = count+1
						
				
			if len(child) == 0:
				#print( self.attribute_list[i], child)
				#print(value[count])
				print(self.attribute_list[i], value[count] ,i)
				result[self.attribute_list[i]] = value[count]
				count = count+1
				
			if len(child) > 0:
				var=1
				#print("nested",i)
				#print( self.attribute_list[i], child)
				result[self.attribute_list[i]] = child

		
			#print(result)

		self.values.append(result)




		
window = tk.Tk()
window.title("Graphical Interface")
wd=str(window.winfo_screenwidth()-260)+"x"+str(window.winfo_screenheight()-200)
window.geometry(wd)

table_list=[]



labelfont=('Arial', 40, 'bold')
label1 = tk.Label(text="  PDF2JSON   ", anchor='n', font=labelfont , fg="midnight blue" , bg="mint cream")
label1.grid(column=0,row=0)

greetings_disp =tk.Text(master=window,height=1,width=200,fg="midnight blue")
greetings_disp.grid(column=0,row=1)
greetings_disp.insert(tk.END , "prototype for Techgium")

#buttons

button1 = tk.Button(text="READ PDF" , command= read_pdf , bg="powder blue")
button1.grid(column=0,row=2)

button2 = tk.Button(text="PEEK PDF" , command=see_pdf , bg="powder blue")
button2.grid(column=0,row=4)

button3 = tk.Button(text="Convert Table/s to JSON file" , command= convert_to_json , bg="powder blue")
button3.grid(column=0,row=6) #disable this button after once and enable only if new pdf is uploaded

button4 = tk.Button(text="Database INFO" , command= db_insert, bg="powder blue")
button4.grid(column=0,row=8)

window.mainloop()
