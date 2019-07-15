import sys
import math
import csv
import datetime
import time
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties
from collections import *
from pandas import *
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi


'''
Info:
	线性拟合函数，求出特征值,规定了y值不变的r为0
Args:
	x-自变量列表
	y-因变量列表
Returns:
	a-斜率
	b-截距
	r-线性相关性
Modify：
	2019/5/7
'''
def linefit(x, y):
	N = len(x)
	sx, sy, sxx, syy, sxy = 0, 0, 0, 0, 0
	for i in range(N):
		sx += x[i]
		sy += y[i]
		sxx += x[i] * x[i]
		syy += y[i] * y[i]
		sxy += x[i] * y[i]

	a = (sy * sx / N - sxy) / (sx * sx / N - sxx)
	b = (sy - a * sx) / N
	if syy - sy * sy / N == 0:
		r = 0
	else:
		r = abs(sy * sx / N - sxy) / math.sqrt((sxx - sx * sx / N) * (syy - sy * sy / N))
	return a, b, r


'''
Info:
	分析表格各个温度的线性拟合情况，并生成报告和拟合参数表格
Args:
	filename-原实验数据文件路劲
	df-因变量列表
	hnum-用来判断是整机台还是核心机，核心机比整机多一行
	txt-传入报告文本
Returns:
	txt-生成的线性分析报告
	df1-线性分析的表格
Modify：
	2019/5/7
'''
def linefit_analyze(filename, df, hnum, txt):
	aa = df.values

	num = np.array(aa)
	m, n = num.shape

	# 整机台会比核心机台多一列
	if hnum == 0:
		n -= 1

	bb = np.zeros((3, n - 1))
	# 矩阵转置这样之后线性拟合处理会比较方便
	cc = np.transpose(aa)

	# 每个温度测量值进行线性拟合
	for j in range(n - 1):
		bb[0][j], bb[1][j], bb[2][j] = linefit(cc[0], cc[j + 1])

	# 制作表头和索引
	with open(filename) as f:
		reader = csv.reader(f)
		for i in range(hnum + 1):
			header_row = next(reader)

	# 制作表头和索引
	index_tw = ['a', 'b', 'r']

	header_tw = []
	for i in range(n - 1):
		header_tw.append(header_row[i + 1])
	#df1是各个测点的a、b、r的表格
	df1 = pd.DataFrame(bb, index=index_tw, columns=header_tw)

	df1.to_csv(r'data\linefit_check_over.csv')

	# 统计温度上升下降不变的测点数量
	nplus = 0#用来统计斜率为正数量
	nminus = 0#用来统计斜率为负数量
	nzero = 0#用来统计斜率为0的数量
	nr = 0#统计线性相关性小于0.9的数量
	for i in range(n - 1):
		if bb[0][i] > 0:
			nplus += 1
		if bb[0][i] < 0:
			nminus += 1
		if bb[0][i] == 0:
			nzero += 1
		if bb[2][i] < 0.9:
			nr += 1

	# 判断整体线性拟合的好坏

	if nr > 0.2 * (n - 1):
		txt += '线性拟合超过20%的拟合结果较差\n'

	for i in range(n - 1):
		if bb[2][i] < 0.9:
			txt += header_tw[i] + '线性拟合结果较差\n'

	# 通过线性拟合来判断测点是否有问题
	if nplus < 0.8 * (n - 1) and nminus < 0.8 * (n - 1):

		txt += '温度变化趋势相同的测点没有超过80%，请查看数据是否正常\n'

	elif nplus > 0.8 * (n - 1):

		txt += '超过80%的测点温度都是上升趋势\n'

		if nminus != 0:
			for i in range(n - 1):
				if bb[0][i] < 0:
					txt += header_tw[i] + '测点温度是下降趋势\n'

		if nzero != 0:
			for i in range(n - 1):
				if bb[0][i] == 0:
					txt += header_tw[i] + '测点温度没有变化\n'

		if nminus == 0 and nzero == 0:
			txt += '测点温度没有下降或者不变的\n'

	elif nminus > 0.8 * (n - 1):

		txt += '超过80%的测点温度都是下降趋势\n'
		if nplus != 0:
			for i in range(n - 1):
				if bb[0][i] < 0:
					txt += header_tw[i] + '测点温度是上升趋势\n'

		if nzero != 0:
			for i in range(n - 1):
				if bb[0][i] == 0:
					txt += header_tw[i] + '测点温度没有变化\n'

		if nplus == 0 and nzero == 0:
			txt += '测点温度没有上升或者不变的\n'

	return txt,df1


# # 制作主界面
# class MainWindow(QMainWindow):
# 	def __init__(self, parent=None):
# 		super(MainWindow, self).__init__(parent)
# 		loadUi('linefit.ui', self)
# 		# self.setFixedSize(self.sizeHint())
# 		self.open_Button.clicked.connect(self.open_pre)
# 		self.linefit_Button.clicked.connect(self.linefit_start)
#
# 	def open_pre(self):
# 		filename, filetype = QFileDialog.getOpenFileName(self, '', r"data", "(*.csv)")
# 		self.lineEdit.setText(filename)
#
# 	def linefit_start(self):
# 		self.filename = self.lineEdit.text()
# 		filename_log = r'linefit_check_result.txt'
# 		curr_time = datetime.datetime.now()
# 		curr_time = curr_time.strftime("%Y-%m-%d %H:%M:%S")
# 		with open(filename_log, 'w') as file_object:
# 			txt = curr_time + '\n'
# 			file_object.write(txt)
#
# 		# 选择整机台即选择第几行为标题
# 		hnum = self.comboBox.currentIndex()
# 		try:
# 			# 导入实验数据
# 			df = pd.DataFrame(pd.read_csv(self.filename, header=hnum, low_memory=False))
# 			if hnum == 0 and df.columns[0] == 'TimeSpan':
# 				txt = linefit_analyze(self.filename, df, hnum, txt)
#
# 			elif hnum == 1 and df.columns[0] == 'TIME':
# 				txt = linefit_analyze(self.filename, df, hnum, txt)
#
# 			else:
# 				txt += '表格错误,请检查表格和车台选项'
# 		except Exception as e:
# 			txt += '请先选择数据'
#
# 		with open(filename_log, 'w') as file_object:
# 			file_object.write(txt + '\n')
#
# 			self.result_Browser.setText(txt)

class ExThread(QThread):
	trigger=pyqtSignal()
	def __init__(self, import_filename, widgetlist_2,\
				 excelexport_filename,data_clean,ex_sort):

		super(ExThread, self).__init__()
		self.working = True
		self.import_filename=import_filename
		self.widgetlist_2=widgetlist_2
		self.excelexport_filename=excelexport_filename
		self.data_clean=data_clean
		self.news_long=10**16
		self.num=0.01
		self.ex_sort=ex_sort

	def __del__(self):
		self.working = False
		self.wait()
		
	def run(self):
		#为处理数据量较大的采用分块读取
		data=pd.read_csv(self.import_filename,
						header=0,
						encoding='utf_8',
						engine='python',
						iterator=True)

		loop=True
		chunkSize=5000
		chunks=[]

		while loop:
			try:
				chunk=data.get_chunk(chunkSize)
				chunks.append(chunk)
			except StopIteration:
				loop=False

		data=pd.concat(chunks,ignore_index=True)
		df=pd.DataFrame(data)

		news=list(set(df.columns)-set(self.widgetlist_2))

		self.news_long=len(news)
		if self.news_long!=0:
			for i in range(self.news_long):

				del df[news[i]]
				self.num=i

		else:
			self.num=1
			self.news_long=2

		if self.data_clean!='':
			df=df[df!=self.data_clean]

		if self.ex_sort==True:
			df.sort_index(axis=1,ascending=True,inplace=True)

		df.to_excel(self.excelexpot_filename,index=None)
		self.num+=1

		self.trigger.emit()




class CsThread(QThread):
	trigger = pyqtSignal()
	def __init__(self, import_filename,
				 widgetlist_2, \
				 csvexport_filename,\
				 data_clean,ex_sort):
		super(CsThread, self).__init__()
		self.working = True
		self.import_filename=import_filename
		self.widgetlist_2=widgetlist_2
		self.csvexport_filename=csvexport_filename
		self.data_clean=data_clean
		self.news_long=10**16
		self.num=0.01
		self.ex_sort=ex_sort

		
		
	def __del__(self):
		self.working = False
		self.wait()
		
	def run(self):
		data=pd.read_csv(self.import_filename,\
						 header=0,\
						 encoding='utf_8',\
						 engine='pyhton',
						iterator=True)
		loop=True
		chunkSize=5000
		chunks=[]

		while loop:
			try:
				chunk=data.get_chunk(chunkSize)
				chunks.append(chunk)
			except StopIteration:
				loop=False

		data=pd.concat(chunks,ignore_index=True)
		df=pd.DataFrame(data)


		news=list(set(df.columns)-set(self.widgetlist_2))
		self.news_long=len(news)
		if self.news_long!=0:
			for i in range(self.news_long):

				del df[news[i]]
				self.num=i

		else:
			self.num=1
			self.news_long=2

		if self.data_clean!='':
			df=df[df!=self.data_clean]

		if self.ex_sort==True:
			df.sort_index(axis=1,ascending=True,inplace=True)
			
		df.to_csv(self.csvexport_filename, index=None)
		self.num+=1
		#reply = QMessageBox.information(self,'提示','已导出成功')
		# 线程相关代码
		self.trigger.emit()

class PlotThread(QThread):
	trigger=pyqtSignal()

	def __init__(self,import_filename,header_now,widgetlist_2):
		super(PlotThread,self).__init__()
		self.working=True
		self.import_filename=import_filename
		self.nn=0
		self.header_row=header_now
		self.widgetlist_2=widgetlist_2
		self.plot_ydir={}
		self.plot_x=[]
		self.num_col=[]

	def __del__(self):
		self.working=False
		self.wait()

	def run(self):

		if 'TimeSpan' not in self.header_row:
			reply=QMesssgeBox.information(self,'提示','数据表中无TimeSpan变量')
		else:
			for i in range(len(self.header_row)):
				if self.header_row[i] in self.widgetlist_2:
					self.num_col.append(i)

			if 'TimeSpan' not in self.widgetlist_2:
				self.num_col.append(self.header_row.index('TimeSpan'))
			data=pd.read_csv(self.import_filename,
							 header=0,
							 usecols=self.num_col,
							 encoding='utf_8',
							 engine='python',#主要是用c的话中文路径识别有些问题
							 iterator=True)
			loop=True
			chunkSize=5000
			chunks=[]
			while loop:
				try:
					chunk=data.get_chunk(chunkSize)
					chunks.append(chunk)

				except StopIteration:
					loop=False

			data=pd.concat(chunks,ignore_index=True)
			df=pd.DataFrame(data)

			self.nn=0
			self.plot_x=list(df['TimeSpan'])
			for i in self.widgetlist_2:

				self.nn+=1
				self.plot_ydir[i]=list(df[i])

		self.trigger.emit()




class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		loadUi('qt_cyres.ui', self)

		self.import_filename=''
		self.input_filename=''
		self.output_filename=''
		self.csvexport_filename=''
		self.excelexport_filename=''
		self.data_clean=''

		self.linefit_df=pd.DataFrame()
		self.linefit_df1=pd.DataFrame()
		self.header_row=[]
		self.widgetlist_1=[]
		self.widgetlist_2=[]

		self.linefit_step=False#判断是否线性拟合了
		self.step_1=False#判断是否导入数据了
		self.step_2=False#判断是否正在导入数据
		self.ex_sort=False#判断是否需要导出排序


		self.import_Button.clicked.connect(self.import_start)
		self.input_Button.clicked.connect(self.input_start)
		self.output_Button.clicked.connect(self.output_start)
		self.csvexport_Button.clicked.connect(self.csvexport_start)
		self.excelexport_Button.clicked.connect(self.excelexport_start)
		self.plot_Button.clicked.connect(self.plot_start)

		self.listWidget_1.setSelectionMode(QAbstractItemView.ExtendedSelection)#按住CTRL可多选
		self.listWidget_2.setSelectionMode(QAbstractItemView.ExtendedSelection)

		self.listWidget_1.itemDoubleClicked.connect(self.listDoubleClick_1)
		self.listWidget_2.itemDoubleClicked.connect(self.listDoubleClick_2)

		self.lineEdit_search.textChanged.connect(self.search_text_changed)
		#self.lineEdit.textChanged.connect(self.lineEdit_text_changed)

		#self.comboBox.currentTextChanged.connect(self.comboBox_text_changed)

		#以下的是用来做线性拟合用的
		# self.open_Button.clicked.connect(self.open_pre)
		# self.linefit_Button.clicked.connect(self.linefit_start)
		# self.lineplta_Button.clicked.connect(self.lineplta_start)
		# self.linepltb_Button.clicked.connect(self.linepltb_start)
		# self.linepltr_Button.clicked.connect(self.linepltr_start)
		self.checkBox_1.stateChanged.connect(self.export_change)


	#用来判断是否需要导出排序
	def export_change(self,state):
		if state==Qt.Checked:
			self.ex_sort
		else:
			self.ex_sort=False

	def import_start(self):
		
		self.step_1=True
		self.widgetlist_1=[]
		self.widgetlist_2=[]
		
		
		self.import_filename,filetype=QFileDialog.getOpenFileName(self,'',r"data","(*.csv)")
		
		try:
			with open(self.import_filename) as f:
				reader=csv.reader(f)
				for i in range(1):
					self.header_row=next(reader)

			self.lineEdit_import_1.setText(self.import_filename)
			self.listWidget_1.clear()
			self.listWidget_2.clear()
			self.lineEdit_search.clear()
			self.widgetlist_1=list(filter(None,self.header_row))
			
			
			#header_tw=[]
			#for i in range(n-1):
				#header_tw.append(header_row[i+1])
			
			if self.widgetlist_1 is not None and len(self.widgetlist_1) > 0:
				#self.listWidget = QListWidget(self)
				for item in self.widgetlist_1:
					self.listWidget_1.addItem(item)
				#if MultiSelection:
				self.listWidget_1.sortItems()
				#self.listWidget_1.setSelectionMode(QAbstractItemView.ExtendedSelection)#按住CTRL可多选
				#self.listWidget_1.itemClicked.connect(self.listItemClick)
				#self.listWidget_1.itemDoubleClicked.connect(self.listItemDoubleClick)
		except Exception as e:
			if self.import_filename!='':
				reply = QMessageBox.information(self,'提示','文件无法打开')
			
	
	def input_start(self):
		if self.step_1!=True:
			reply = QMessageBox.information(self,'提示','请先导入实验数据再导入模板')
		else:
			self.widgetlist_1=list(filter(None,self.header_row))
			self.input_filename,filetype=QFileDialog.getOpenFileName(self,'',r"data","(*.csv)")
			try:
				with open(self.input_filename) as f:
					reader=csv.reader(f)
					values_0=[]
					
					for row in reader:
						values_0.append(row[0])
				nio=True
				extra=set(values_0)-(set(self.widgetlist_1)&set(values_0))
			except Exception as e:
				if self.input_filename!='':
					reply = QMessageBox.information(self,'提示','文件无法打开')
				nio=False
				
			if nio==True:
				
				if len(values_0)!=len(set(values_0)):
					rep=dict(Counter(values_0))
					re={key: value for key, value in rep.items()if value>1}
					reply = QMessageBox.information(self,'提示','模板中有重复变量'+str(re))
					
				if extra!=set():
					reply = QMessageBox.information(self,'提示','模板中有额外变量'+str(extra))
					
				if len(values_0)==len(set(values_0)) and extra==set():
					self.widgetlist_2=values_0
					self.lineEdit_search.clear()
					self.listWidget_2.clear()
					for item in self.widgetlist_2:
						self.listWidget_2.addItem(item)
					self.listWidget_2.sortItems()
					for item in self.widgetlist_2:
						self.widgetlist_1.remove(item)
					self.listWidget_1.clear()
					for item in self.widgetlist_1:
						self.listWidget_1.addItem(item)
					self.listWidget_1.sortItems()
	
	
	def output_start(self):

		if self.widgetlist_2!=[]:
			self.output_filename,filetype=QFileDialog.getSaveFileName(self,'',r"form","(*.csv)")
			outer=Series(self.widgetlist_2)
			if self.output_filename!='':
				outer.to_csv(self.output_filename,index=None)
				reply = QMessageBox.information(self,'提示','已导出模板')
		else:
			reply=QMessageBox.information(self,'提示','导出模板为空，请重新选择')

	def listDoubleClick_1(self):

		text_list = self.listWidget_1.selectedItems()

		for item in text_list:
			self.widgetlist_1.remove(item.text())
			self.widgetlist_2.append(item.text())
		
		for item in text_list:
			qIndex =self.listWidget_1.indexFromItem(item)
			self.listWidget_1.takeItem(qIndex.row())
			
		self.listWidget_2.clear()
		for item in self.widgetlist_2:
			self.listWidget_2.addItem(item)
		self.listWidget_2.sortItems()
		

	def listDoubleClick_2(self):
		text_list = self.listWidget_2.selectedItems()

		for item in text_list:
			self.widgetlist_2.remove(item.text())
			self.widgetlist_1.append(item.text())
		for item in text_list:
			qIndex =self.listWidget_2.indexFromItem(item)
			self.listWidget_2.takeItem(qIndex.row())
			
		self.search_text_changed()
		self.listWidget_1.sortItems()
		
		
	
	def search_text_changed(self):
		
		txt=self.lineEdit_search.text()
		temp_list=[]
		self.listWidget_1.clear()
		for i in self.widgetlist_1:
			if txt in i:
				temp_list.append(i)
				
		for item in temp_list:
			self.listWidget_1.addItem(item)
		self.listWidget_1.sortItems()
		
		
	def csvexport_start(self):
		if self.step_2==False:
			
			
			if self.step_1!=True:
				reply = QMessageBox.information(self,'提示','请先导入实验数据再导出')
			else:
				self.csvexport_filename,filetype=QFileDialog.getSaveFileName(self,'',r"csv_export","(*.csv)")
				
				if self.csvexport_filename!='':

					self.data_clean=self.lineEdit_clean.text()
					self.pbar=QProgressBar(self)
					self.pbar.show()
					self.pbar.setGeometry(710,770,481,20)
					
					self.csthread=CsThread(self.import_filename,\
										   self.widgetlist_2, \
										   self.csvexport_filename,\
										   self.data_clean,\
										   self.ex_sort)
					self.csthread.start()
					
					self.step_2=True
					while True:
						self.pbar.setValue(int(100*(self.csthread.num)/self.csthread.news_long+1))
						#print(self.exthread.news_long)
						QApplication.processEvents()#用来刷新防止卡死
						if self.csthread.num==self.csthread.news_long:
							self.pbar.setValue(int(100*(self.csthread.num)/self.csthread.news_long+1))
							break

					self.pbar.close()
					self.pbar.deleteLater()
					reply = QMessageBox.information(self,'提示','已导出成功')

					self.step_2=False
		else:
			reply = QMessageBox.information(self,'提示','请先等导出完成')
	
	def excelexport_start(self):
		if self.step_2==False:
			
			if self.step_1!=True:
				reply = QMessageBox.information(self,'提示','请先导入实验数据再导出')
			else:
				self.excelexport_filename,filetype=QFileDialog.getSaveFileName(self,'',r"excel_export","(*.xlsx)")
				
				
				if self.excelexport_filename!='':

					self.data_clean=self.lineEdit_clean.text()
					self.pbar=QProgressBar(self)
					self.pbar.show()
					self.pbar.setGeometry(710,770,481,20)
					
					
					self.exthread=ExThread(self.import_filename,\
										   self.widgetlist_2,\
										   self.excelexport_filename,\
										   self.data_clean,\
										   self.ex_sort)
					self.exthread.start()
					self.step_2=True
					while True:
						self.pbar.setValue(int(100*(self.exthread.num)/self.exthread.news_long+1))
						#print(self.exthread.news_long)
						QApplication.processEvents()
						if self.exthread.num==self.exthread.news_long:
							self.pbar.setValue(int(100*(self.exthread.num)/self.exthread.news_long+1))
							break

					self.pbar.close()
					self.pbar.deleteLater()
					reply = QMessageBox.information(self,'提示','已导出成功')

					self.step_2=False
		else:
			reply = QMessageBox.information(self,'提示','请先等导出完成')


	def plot_start(self):

		if self.step_1!=True:
			reply =QMessageBox.information(self,'提示','请先导入实验数据再画图')

		else:
			if len(self.widgetlist_2)>100:
				self.reply=Ui_plotms()

				self.reply.settings(self.import_filename,\
									self.widgetlist_2,\
									self.plot_figure)
				self.reply.show()

			else:
				self.plot_figure()

	def plot_figure(self):
		self.plotthread=PlotThread(self.import_filename,\
								   self.header_row,\
								   self.widgetlist_2)
		self.plotthread.start()

		while self.plotthread.nn<len(self.widgetlist_2):

			time.sleep(1)

		x1=self.plotthread.plot_x
		y_dir=self.plotthread.plot_ydir

		self.figure=plt.figure(figsize=(12,8))

		for i in self.widgetlist_2:
			y1=y_dir[i]
			plt.plot(x1,y1,label=i,marker='.',linewidth=1)

		if len(self.widgetlist_2)<12:
			plt.legend(ncol=1)
		elif len(self.widgetlist_2)>11 and len(self.widgetlist_2)<23:
			plt.legend(ncol=2)
		else:
			plt.legend(ncol=3)

		plt.show()
		plt.close()
	




if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MainWindow()
	w.show()
	
	sys.exit(app.exec())
	
