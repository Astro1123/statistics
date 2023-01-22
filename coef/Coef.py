import PySimpleGUI as sg

from enum import Enum, auto

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import japanize_matplotlib

import seaborn as sns

class Status(Enum):
	NULL = 0
	SUCCESS = auto()
	ERROR = auto()
	BACK = auto()
	NEXT = auto()
	QUIT = auto()

class ReturnInfo:
	status = -1
	data = ''
	
	def makeInfo(self, status, data):
		self.status = status
		self.data = data
		
	def getData(self):
		return self.data
		
	def getStatus(self):
		return self.status
	
	def splitInfo(self):
		return (self.status, self.data)

def QuitCmd():
	res = ReturnInfo()
	res.makeInfo(Status.QUIT, '')
	return res

def NextCmd():
	res = ReturnInfo()
	res.makeInfo(Status.NEXT, '')
	return res

def BackCmd():
	res = ReturnInfo()
	res.makeInfo(Status.BACK, '')
	return res

def SuccessCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.SUCCESS, data)
	return res

def ErrorCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.ERROR, data)
	return res
	
	
def Coef():
	filename = None
	select = []
	while True:
		(code1, filename) = LoadData(filename).splitInfo()
		if code1 != Status.SUCCESS:
			return code1
		(code2, df) = OpenFile(filename).splitInfo()
		while True:
			(code3, select) = SelectData(df, select).splitInfo()
			if code3 == Status.QUIT:
				return code3
			elif code3 == Status.BACK:
				break
			(code4, _) = PlotData(df, select).splitInfo()
			if code4 == Status.QUIT:
				return code4


def PlotData(df, sel):
	data = df[sel].values.T
	
	data = data[:, ~np.isnan(data).any(axis=0)]
	
	corrcoef = np.corrcoef(data)
	
	layout = [
		[sg.Canvas(key='CANVAS', size=(640, 480))],
		[sg.Button("Back"), sg.OK(), sg.Button('Exit')]
	]
	location = (0, 0)
	window = sg.Window('Theme Browser', layout, finalize=True, location=location)
	
	fig = plt.Figure()
	ax = fig.add_subplot(111)
	sns.heatmap(corrcoef, linewidths=0.5, cmap='coolwarm', annot=True, ax=ax, vmin=-1, vmax=1, xticklabels=sel, yticklabels=sel)
	ax.set_title("Heatmap")
	
	fig_agg = draw_figure(window['CANVAS'].TKCanvas, fig)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = QuitCmd()
			break
		elif event == 'Back':
			res = BackCmd()
			break
		elif event == 'OK':
			res = SuccessCmd(None)
			break
			
	window.close()
	return res

def SelectData(df, sel):
	dataName = list(df.columns.values)
	
	chkboxList = [sg.Checkbox(item, default=(item in sel)) for item in dataName]
	
	layout = [
		chkboxList,
		[sg.Button("Back"), sg.Button('Exit'), sg.Button('Select')]
	]
	window = sg.Window('Theme Browser', layout)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = QuitCmd()
			break
		elif event == 'Back':
			res = BackCmd()
			break
		elif event == 'Select':
			sel = []
			for value in values.items():
				if value[1]:
					sel.append(dataName[value[0]])
			if len(sel) > 1:
				res = SuccessCmd(sel)
				break
	
	window.close()
	return res

def selectEncode(filename):
	enc = ["utf-8", "shift-jis", "cp932", "utf-8-sig", "iso2022_jp", "euc_jp"]
	i = 0
	for s in enc:
		try:
			df = pd.read_csv(filename, encoding=enc[i])
			res = enc[i]
			break
		except UnicodeDecodeError as e:
			i += 1
	else:
		res = "unknown"
	return res

def OpenFile(filename):
	encodeName = selectEncode(filename)
	if encodeName == "unknown":
		raise ValueError(f'Cannot open {filename}')
	df = pd.read_csv(filename, encoding=encodeName)
	return SuccessCmd(df)

def LoadData(filename):
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Text("File"), sg.InputText(default_text=filename, key='Text'), sg.FileBrowse(key="file")], 
		[sg.Cancel(), sg.Button('Exit'), sg.OK()]
	]
	window = sg.Window('Title', layout)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Cancel'):
			res = BackCmd()
			break
		elif event == 'Exit':
			res = QuitCmd()
			break
		elif event == 'OK':
			if values["file"] != "":
				res = SuccessCmd(values["file"])
				break
			elif values["Text"] != "":
				res = SuccessCmd(values["Text"])
				break
	
	window.close()
	return res


def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg
