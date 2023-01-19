import numpy as np
import sympy as sym
from scipy import stats
from sympy.plotting import plot
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import japanize_matplotlib

from . import ReturnInfo as ri

def meaningCov(rho):
	if (rho >= 0.7):
		return "Very strong positive relationship"
	elif (rho >= 0.4):
		return "Strong positive relationship"
	elif (rho >= 0.3):
		return "Moderate positive relationship"
	elif (rho >= 0.2):
		return "Weak positive relationship"
	elif (rho > 0):
		return "No or negligible relationship"
	elif (rho <= 0.7):
		return "Very strong negative relationship"
	elif (rho <= 0.4):
		return "Strong negative relationship"
	elif (rho <= 0.3):
		return "Moderate negative relationship"
	elif (rho <= 0.2):
		return "Weak negative relationship"
	elif (rho < 0):
		return "No or negligible relationship"
	return "No relationship [zero correlation]"

def ScatterGraph(df, xName, yName):
	sg.theme('Dark Brown')
	
	xdata = df[xName].values
	ydata = df[yName].values
	
	#Correlation coefficients
	data = np.array([xdata, ydata])
	data = data[:, ~np.isnan(data).any(axis=0)]
	xdata = data[0]
	ydata = data[1]
	corrcoef = np.corrcoef(data)
	rho = corrcoef[0][1]
	meaning = meaningCov(rho)
	
	#Fitting function (linear)
	x_latent = np.linspace(min(xdata), max(xdata), 100)
	sym.init_printing(use_unicode=True)
	x, y = sym.symbols("x y")
	coefficients = np.polyfit(xdata, ydata, 1)
	expr = 0
	for index, coefficient in enumerate(coefficients):
		expr += coefficient * x ** (len(coefficients) - index - 1)
	fitted_curve = np.poly1d(np.polyfit(xdata, ydata, 1))(x_latent)
	eq = sym.Eq(y, expr)
	
	#Chi-square
	model = np.poly1d(np.polyfit(xdata, ydata, 1))(xdata)
	chi2 = stats.chisquare(ydata, f_exp = model)
	
	#Coefficient of determination
	residuals =  ydata - model
	rss = np.sum(residuals**2)
	tss = np.sum((ydata-np.mean(ydata))**2)
	r_squared = 1 - (rss / tss)
	count = len(xdata)
	variable = 1
	adj_r_squared = 1 - ((rss / (count - variable - 1)) / (tss / (count - 1)))

	#Multiple correlation coefficient
	mcc_data = np.array([ydata, model])
	corrcoef = np.corrcoef(mcc_data)
	mcc = corrcoef[0][1]
	meaning = meaningCov(mcc)
	
	layout = [
		[sg.Canvas(key='CANVAS', size=(640, 480))],
		[sg.Text('Correlation coefficients'), sg.InputText(f'{rho} ({meaning})', readonly=True)],
		[sg.Text('Fitting function'), sg.InputText(f'{eq}', readonly=True)],
		[sg.Text('Chi-square'), sg.InputText(f'{chi2[0]}', readonly=True)],
		[sg.Text('p-value'), sg.InputText(f'{chi2[1]}', readonly=True)],
		[sg.Text('Coefficient of determination'), sg.InputText(f'{r_squared}', readonly=True)],
		[sg.Text('Adjusted coefficient of determination'), sg.InputText(f'{adj_r_squared}', readonly=True)],
		[sg.Text('Multiple correlation coefficient'), sg.InputText(f'{mcc}', readonly=True)],
		[sg.Button("Back"), sg.Button('Next'), sg.Button('Details'), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)
	
	#Graphs
	fig = plt.Figure()
	ax1 = fig.add_subplot(111)
	ax1.scatter(xdata, ydata)
	ax1.set_title(f"Correlation between {xName} and {yName}")
	ax1.set_xlabel(xName)
	ax1.set_ylabel(yName)
	ax1.plot(x_latent, fitted_curve, c="red")
	ax1.grid(True)
	
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
		elif event == 'Details':
			res = ri.CmdCmd(ri.ExecuteCommand.RPLOT, residuals, model, (count, variable, data, coefficients, [xName, yName], []))
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
		[sg.Text("File"), sg.InputText(default_text=filename, key='Text'), sg.FileBrowse(key="file")], 
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

def save(df):
	filename = sg.popup_get_file('save', save_as=True)
	if filename != None:
		df.to_csv(filename)
		sg.popup('Complete')
		return ri.SuccessCmd('')
	return ri.FailCmd()
