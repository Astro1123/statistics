import numpy as np
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import japanize_matplotlib

from . import ReturnInfo as ri

def ScatterGraph(df, xName, yName):
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Canvas(key='CANVAS')],
		[sg.Button("Back"), sg.Button('Next'), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)
	
	x = df[xName].values
	y = df[yName].values
	
	fig = plt.Figure()
	ax = fig.add_subplot(111)
	ax.scatter(x, y)
	ax.set_title(f"Correlation between {xName} and {yName}")
	ax.set_xlabel(xName)
	ax.set_ylabel(yName)
	ax.grid(True)
	
	fig_agg = draw_figure(window['CANVAS'].TKCanvas, fig)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = ri.QuitCmd()
			break
		elif event == 'Back':
			res = ri.BackCmd()
			break
		elif event == 'Next':
			res = ri.NextCmd()
			break
	
	window.close()
	return res

def SelectData(*data):
	df = data[0]
	if len(data[1]) == 3:
		xdefault = data[1][1]
		ydefault = data[1][2]
	else:
		xdefault = ''
		ydefault = ''
	dataName = list(df.columns.values)
	layout = [
		[sg.Text("x axis"), sg.Combo(dataName, default_value=xdefault, readonly=True, key='ComboX')],
		[sg.Text("y axis"), sg.Combo(dataName, default_value=ydefault, readonly=True, key='ComboY')],
		[sg.Button("Back"), sg.Button('Exit'), sg.Button('Select')]
	]
	window = sg.Window('Theme Browser', layout)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = ri.QuitCmd()
			break
		elif event == 'Back':
			res = ri.BackCmd()
			break
		elif event == 'Select':
			if values['ComboX'] != values['ComboY']:
				if values['ComboX'] != '' and values['ComboY'] != '':
					res = ri.SuccessCmd(df[[values['ComboX'], values['ComboY']]], values['ComboX'], values['ComboY'])
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
	return ri.SuccessCmd(df)

def LoadData(filename):
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Text("ファイル"), sg.InputText(default_text=filename, key='Text'), sg.FileBrowse(key="file")], 
		[sg.Button("Back"), sg.Button('Exit'), sg.Submit()]
	]
	window = sg.Window('Title', layout)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Back'):
			res = ri.BackCmd()
			break
		elif event == 'Exit':
			res = ri.QuitCmd()
			break
		elif event == 'Submit':
			if values["file"] != "":
				res = ri.SuccessCmd(values["file"])
				break
			elif values["Text"] != "":
				res = ri.SuccessCmd(values["Text"])
				break
	
	window.close()
	return res

def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg