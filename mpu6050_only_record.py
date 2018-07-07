"""A GUI tool for recording MPU-6050 digital accelerometer and gyroscope readings on a Raspberry Pi.
Created by: Vijaykumar Walikar
Released under the MIT License
Copyright (c) 2018 Vijaykumar Walikar
"""

from tkinter import *
from tkinter import ttk
import csv
import time
import datetime
import threading
from mpu6050 import mpu6050


class PlotRecAccGyro():
	def __init__(self, parent):
		self.parent = parent
		self.parent.title('MPU6050 - Acceleration and Gyroscope')
		self.frame = Frame(self.parent)
		self.frame.pack(fill=BOTH, expand=1)
		self.parent.resizable(width = False, height = False)
		self.plot_trigger = True
		self.record_trigger = False
		
		self.var_all = IntVar()
		self.var_plot = IntVar()
		self.var_rec = IntVar()
		self.accgyro_chkbtn_state = []
		self.chkbtn_list = []
		
		# Call MPU6050 class
		self.mpu = mpu6050(0x68)
	
		# LabelFrame - Select components		
		self.labelframe_comp = LabelFrame(self.frame, text= 'Select components')
		self.labelframe_comp.grid(row=0,  column=0 , columnspan=3, sticky=N+E+W+S)
		self.labelframe_comp.grid_configure(padx=5, pady=5)

		# LabelFrame - Options to plot and record
		self.labelframe_opt = LabelFrame(self.frame, text= 'Options - Plot and Record')
		self.labelframe_opt.grid(row=0,  column=3 , columnspan=3, sticky=N+E+W+S)
		self.labelframe_opt.grid_configure(padx=5, pady=5)

		# Checkbuttons - Acceleration
		for i,j in enumerate(['Acc_x', 'Acc_y', 'Acc_z']):
			self.var_acc = IntVar()
			self.acc_chkbtn = Checkbutton(self.labelframe_comp, text=j, variable=self.var_acc, command=self.components_chk_func, padx=5, pady=5)
			self.acc_chkbtn.grid(row=i, column=0)
			self.accgyro_chkbtn_state.append(self.var_acc)
			self.chkbtn_list.append(self.acc_chkbtn)

		# Checkbuttons - Gyroscope
		for i,j in enumerate(['Gyro_x', 'Gyro_y', 'Gyro_z']):
			self.var_gyro = IntVar()
			self.gyro_chkbtn = Checkbutton(self.labelframe_comp, text=j, variable=self.var_gyro, command=self.components_chk_func, padx=5, pady=5)
			self.gyro_chkbtn.grid(row=i,  column=1)
			self.accgyro_chkbtn_state.append(self.var_gyro)
			self.chkbtn_list.append(self.gyro_chkbtn)

		# Checkbutton - All
		self.all_chkbtn = Checkbutton(self.labelframe_comp, text='All', variable=self.var_all, command=self.all_chk_func, padx=5, pady=5)
		self.all_chkbtn.grid(row=1, column=2)    

		# Button - Record to a file
		self.rec_chkbtn = ttk.Button(self.labelframe_opt, text='Start Recording', command=lambda: self.record_start_stop('rec_btn'))
		self.rec_chkbtn.grid(row = 1, column=0, sticky=N+E+W+S, padx=5, pady=10)
		self.rec_chkbtn.configure(state='disabled')
		
		# Label - File name
		self.rec_text = Label(self.labelframe_opt, text='to file (.csv)')
		self.rec_text.grid(row=1, column=1, sticky=N+E+W+S)
		
		# Entry - File name (Default name: SensorDataFile)
		self.file_name = ttk.Entry(self.labelframe_opt)
		self.file_name.insert(0,'SensorDataFile')
		self.file_name.grid(row=1, column=2, sticky=N+E+W+S, padx=5, pady=10)
		self.file_name.configure(state='disabled')

	# Function called on clicking on 'All' checkbutton
	def all_chk_func(self):
		if [i.get() for i in self.accgyro_chkbtn_state] != ([1]*6):
			[i.set(1) for i in self.accgyro_chkbtn_state]
			self.rec_chkbtn.configure(state='normal')
			self.file_name.configure(state='normal')
		else:
			[i.set(0) for i in self.accgyro_chkbtn_state]
			self.rec_chkbtn.configure(state='disabled')
			self.file_name.configure(state='disabled')
	
	# Function called on clicking on 'Record' checkbutton
	def rec_chk_func(self):
		if self.var_rec.get() == 1:
			self.file_name.configure(state='normal')
		else:
			self.file_name.configure(state='disabled')

	# Function called on clicking on acceleration or gyroscope checkbuttons		
	def components_chk_func(self):
		if (0 in [i.get() for i in self.accgyro_chkbtn_state]):
			self.var_all.set(0)
		else:
			self.var_all.set(1)
			
		if (1 in [i.get() for i in self.accgyro_chkbtn_state]):
			self.rec_chkbtn.configure(state='normal')
			self.file_name.configure(state='normal')
		else:
			self.rec_chkbtn.configure(state='disabled')
			self.file_name.configure(state='disabled')

	# Function called on clicking on 'Start writing' or 'Stop writing' button		
	def record_start_stop(self, btn_name):
		if self.rec_chkbtn['text'] == 'Start Recording':
			self.rec_chkbtn['text'] = 'Stop Recording'
			self.file_name.configure(state='disabled')		
			self.all_chkbtn.configure(state='disabled')
			for i in self.chkbtn_list:
				i.configure(state='disabled')
			self.record_trigger = True	
			print('Started recording sensor data...')
			thread_to_write_file = threading.Thread(target = self.record_to_file)
			thread_to_write_file.start()
		elif self.rec_chkbtn['text'] == 'Stop Recording':
			self.rec_chkbtn['text'] = 'Start Recording'
			self.file_name.configure(state='normal')
			self.all_chkbtn.configure(state='normal')
			for i in self.chkbtn_list:
				i.configure(state='normal')
			self.record_trigger = False
			print('Stopped recording sensor data...')
	
	# Thread called to record readings to a file
	def record_to_file(self):
		if self.file_name.get() != '':
			filename = self.file_name.get()
		else:
			filename = 'NoFileName'
		self.file_to_write = open(filename + '.csv', 'w')			# Open the file
		self.row_to_write = csv.writer(self.file_to_write, lineterminator='\n')
		column_titles = ['Date\n(YY:MM:DD)', 'Time\n(HH:MM:SS)', 'Time\n(µs)']
		column_titles = column_titles + [i for i,j in zip(['Ax\n(m/s^2)', 'Ay\n(m/s^2)', 'Az\n(m/s^2)', 'Gx\n(deg/s)', 'Gy\n(deg/s)', 'Gz\n(deg/s)'], [i.get() for i in self.accgyro_chkbtn_state]) if j==1]
		self.row_to_write.writerow(column_titles)
		while self.record_trigger:
			time.sleep(1)
			current_time = datetime.datetime.now()
			accel_data = self.mpu.get_accel_data()
			gyro_data = self.mpu.get_gyro_data()
			current_acc = [accel_data['x'], accel_data['y'], accel_data['z']]
			current_gyro = [gyro_data['x'], gyro_data['y'], gyro_data['z']]
			row = [current_time.strftime('%Y-%m-%d'), current_time.strftime('%H:%M:%S'), current_time.strftime('%f')]
			row = row + [i for i,j in zip(current_acc + current_gyro, [i.get() for i in self.accgyro_chkbtn_state]) if j==1]
			self.row_to_write.writerow(row)
		self.file_to_write.close()
			
if __name__ == '__main__': 
	root = Tk()
	plotrectool = PlotRecAccGyro(root)
	root.resizable(width = False, height = False)
	root.mainloop()