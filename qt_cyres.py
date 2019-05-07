import sys
import csv
import pandas as pd
from collections import *
from pandas import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi


class ExThread(QThread):
	def __init__(self, import_filename, widgetlist_2, excelexport_filename):
		super(ExThread, self).__init__()
		self.working = True
		self.import_filename=import_filename
		self.widgetlist_2=widgetlist_2
		self.excelexport_filename=excelexport_filename
		self.num=0
		self.news_long=10**16
		#self.pbar=pbar
		
		
	def __del__(self):
		self.working = False
		self.wait()
		
	def run(self):
		#self.pbar=QProgressBar(self)
		#self.pbar.show()
		#self.pbar.setGeometry(710,700,481,23)
		
		df=pd.DataFrame(pd.read_csv(self.import_filename, header=0, low_memory=False))
		
		#self.widgetlist_1=list(filter(None,self.header_row))
		news=list(set(df.columns)-set(self.widgetlist_2))
		self.news_long=len(news)-1
		
		for i in range(len(news)):
			del df[news[i]]
			self.num=i
			#print(self.num)
			#self.pbar.setValue(int(100*(i+1)/len(news)))
			
			
		df.to_excel(self.excelexport_filename, index=None)
		#reply = QMessageBox.information(self,'提示','已导出成功')
		# 线程相关代码
		pass

class CsThread(QThread):
	def __init__(self, import_filename, widgetlist_2, csvexport_filename):
		super(CsThread, self).__init__()
		self.working = True
		self.import_filename=import_filename
		self.widgetlist_2=widgetlist_2
		self.csvexport_filename=csvexport_filename
		self.num=0
		self.news_long=10**16
		#self.pbar=pbar
		
		
	def __del__(self):
		self.working = False
		self.wait()
		
	def run(self):
		#self.pbar=QProgressBar(self)
		#self.pbar.show()
		#self.pbar.setGeometry(710,700,481,23)
		
		df=pd.DataFrame(pd.read_csv(self.import_filename, header=0, low_memory=False))
		
		#self.widgetlist_1=list(filter(None,self.header_row))
		news=list(set(df.columns)-set(self.widgetlist_2))
		self.news_long=len(news)-1
		
		for i in range(len(news)):
			del df[news[i]]
			self.num=i
			#print(self.num)
			#self.pbar.setValue(int(100*(i+1)/len(news)))
			
			
		df.to_csv(self.csvexport_filename, index=None)
		#reply = QMessageBox.information(self,'提示','已导出成功')
		# 线程相关代码
		pass


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		loadUi('qt_cyres.ui', self)
		self.import_filename=''
		self.input_filename=''
		self.output_filename=''
		self.csvexport_filename=''
		self.excelexport_filename=''
		self.header_row=[]
		self.widgetlist_1=[]
		self.widgetlist_2=[]
		self.step_1=False
		self.step_2=False
		self.import_Button.clicked.connect(self.import_start)
		self.input_Button.clicked.connect(self.input_start)
		self.output_Button.clicked.connect(self.output_start)
		self.csvexport_Button.clicked.connect(self.csvexport_start)
		self.excelexport_Button.clicked.connect(self.excelexport_start)
		self.listWidget_1.setSelectionMode(QAbstractItemView.ExtendedSelection)#按住CTRL可多选
		self.listWidget_2.setSelectionMode(QAbstractItemView.ExtendedSelection)
		#self.listWidget_1.itemClicked.connect(self.listItemClick)
		self.listWidget_1.itemDoubleClicked.connect(self.listDoubleClick_1)
		self.listWidget_2.itemDoubleClicked.connect(self.listDoubleClick_2)
		self.lineEdit_search.textChanged.connect(self.search_text_changed)
		
	
	
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
		self.output_filename,filetype=QFileDialog.getSaveFileName(self,'',r"form","(*.csv)")
		
		outer=Series(self.widgetlist_2)
		if self.output_filename!='':
			outer.to_csv(self.output_filename,index=None)
			reply = QMessageBox.information(self,'提示','已导出模板')
	
	
	def listDoubleClick_1(self):
		
		text_list = self.listWidget_1.selectedItems()
		#text = [i.text() for i in list(text_list)]    
		#text = '_',join(text) # text即多选项并以_隔开
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
		
		#item_deleted = self.listWidget_1.takeItem()
		#将读取的值设置为None
		#item_deleted = None
		
	def listDoubleClick_2(self):
		text_list = self.listWidget_2.selectedItems()
		#text = [i.text() for i in list(text_list)]    
		#text = '_',join(text) # text即多选项并以_隔开
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
		aa=[]
		self.listWidget_1.clear()
		for i in self.widgetlist_1:
			if txt in i:
				aa.append(i)
				
		for item in aa:
			self.listWidget_1.addItem(item)
		self.listWidget_1.sortItems()
		
		
	def csvexport_start(self):
		if self.step_2==False:
			
			
			if self.step_1!=True:
				reply = QMessageBox.information(self,'提示','请先导入实验数据再导出')
			else:
				self.csvexport_filename,filetype=QFileDialog.getSaveFileName(self,'',r"csv_export","(*.csv)")
				
				if self.csvexport_filename!='':
					
					self.pbar=QProgressBar(self)
					self.pbar.show()
					self.pbar.setGeometry(710,700,481,23)
					
					self.csthread=CsThread(self.import_filename, self.widgetlist_2, self.csvexport_filename)
					self.csthread.start()
					
					self.step_2=True
					while True:
						self.pbar.setValue(int(100*(self.csthread.num)/self.csthread.news_long))
						#print(self.exthread.news_long)
						QApplication.processEvents()
						if self.csthread.num==self.csthread.news_long:
							self.pbar.setValue(int(100*(self.csthread.num)/self.csthread.news_long))
							break
					
					reply = QMessageBox.information(self,'提示','已导出成功')
					self.pbar.hide()
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
					
					self.pbar=QProgressBar(self)
					self.pbar.show()
					self.pbar.setGeometry(710,700,481,23)
					
					
					self.exthread=ExThread(self.import_filename, self.widgetlist_2, self.excelexport_filename)
					self.exthread.start()
					self.step_2=True
					while True:
						self.pbar.setValue(int(100*(self.exthread.num)/self.exthread.news_long))
						#print(self.exthread.news_long)
						QApplication.processEvents()
						if self.exthread.num==self.exthread.news_long:
							self.pbar.setValue(int(100*(self.exthread.num)/self.exthread.news_long))
							break
					
					reply = QMessageBox.information(self,'提示','已导出成功')
					self.pbar.hide()
					self.step_2=False
		else:
			reply = QMessageBox.information(self,'提示','请先等导出完成')
	
	
	




if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MainWindow()
	w.show()
	
	sys.exit(app.exec())
	
