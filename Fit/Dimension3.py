import numpy as np
import sympy as sym
from scipy import stats
from sympy.plotting import plot
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import optimize
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.font_manager as fm
import japanize_matplotlib
import io

from . import ReturnInfo as ri

def fiting_func(param ,x ,y ,z):
    residual = z - (param[0] * x + param[1] * y + param[2])
    return residual

def function(a, x, y):
	return a[0] * x + a[1] * y + a[2]

def ScatterGraph3(df, xName, yName, zName):
	sg.theme('Dark Brown')
	
	xdata = df[xName].values
	ydata = df[yName].values
	zdata = df[zName].values
	
	#Correlation coefficients
	data = np.array([xdata, ydata, zdata])
	data = data[:, ~np.isnan(data).any(axis=0)]
	xdata = data[0]
	ydata = data[1]
	zdata = data[2]
	
	#Fitting function (linear)
	x_latent = np.linspace(min(xdata), max(xdata), 100)
	y_latent = np.linspace(min(ydata), max(ydata), 100)
	sym.init_printing(use_unicode=True)
	x, y, z = sym.symbols("x y z")
	param = [0, 0, 0]
	optimised_param =  optimize.leastsq(fiting_func, param, args=(xdata, ydata, zdata))
	a = optimised_param[0]
	f = np.vectorize(function)
	expr = function(a, x, y)
	fitted_curve = function(a, x_latent, y_latent)
	eq = sym.Eq(z, expr)
	
	#Coefficient of determination
	model = function(a, xdata, ydata)
	residuals =  zdata - model
	rss = np.sum(residuals**2)
	tss = np.sum((zdata-np.mean(zdata))**2)
	r_squared = 1 - (rss / tss)
	
	layout = [
		[sg.Canvas(key='CANVAS', size=(640, 480))],
		[sg.Text('Fitting function'), sg.InputText(f'{eq}', readonly=True)],
		[sg.Text('Coefficient of determination'), sg.InputText(f'{r_squared}', readonly=True)],
		[sg.Button("Back"), sg.Button('Next'), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)
	
	#Graphs
	fig = plt.Figure()
	ax1 = fig.add_subplot(111, projection='3d')
	ax1.scatter(xdata, ydata, zdata)
	ax1.set_title(f"Correlation between {xName}, {yName}, and {zName}")
	ax1.set_xlabel(xName)
	ax1.set_ylabel(yName)
	ax1.set_zlabel(zName)
	zl = function(a, x_latent, y_latent)
	
	x_latent2 = np.append(min(xdata),xdata.flatten())
	y_latent2 = np.append(min(ydata),ydata.flatten())
	x_latent2, y_latent2 = np.meshgrid(x_latent2, y_latent2)
	
	zl = function(a, x_latent2, y_latent2)
	
	ax1.plot_trisurf(x_latent2.flatten(), y_latent2.flatten(), zl.flatten(), color='red')
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
	
	window.close()
	return res

def fiting_func_m(param ,*arg):
	x = [i for i in arg]
	residual = x[-1] - param[-1]
	for i in range(len(x) - 1):
		residual -= x[i] * param[i]
	return residual

def function_m(a, x):
	s = 0
	for i in range(len(x)):
		s += a[i] * x[i]
	return s + a[len(a) - 1]

def ScatterGraphm(df, xName):
	sg.theme('Dark Brown')
	
	xdata = []
	for i, name in enumerate(xName):
		xdata.append(df[name].values)
	
	#Correlation coefficients
	data = []
	for d in xdata:
		data.append(d)
	data = np.array(data)
	data = data[:, ~np.isnan(data).any(axis=0)]
	for i in range(len(xdata)):
		xdata[i] = data[i]
	
	#Fitting function (linear)
	x_latent = []
	for i in range(len(xdata) - 1):
		x_latent.append(np.linspace(min(xdata[i]), max(xdata[i]), 100))
	param = [0 for i in range(len(xdata))]
	optimised_param =  optimize.leastsq(fiting_func_m, param, args=tuple(xdata))
	a = optimised_param[0]
	f = np.vectorize(function_m)
	sym.init_printing(use_unicode=True)
	z = sym.symbols("z")
	x = []
	for i in range(len(xdata) - 1):
		x.append(sym.symbols("x{i}"))
	expr = function_m(a, x)
	fitted_curve = function_m(a, x_latent[:-1])
	#eq = sym.Eq(z, expr)
	eq = a
	
	"""
	obj = io.BytesIO()
	sym.preview(eq, output='png', viewer='BytesIO', outputbuffer=obj, euler=False,
    dvioptions=["-T", "tight", "-z", "0", "--truecolor", "-D 600", "-bg", "Transparent"])
	"""
	
	#Coefficient of determination
	model = function_m(a, xdata[:-1])
	residuals =  data[-1] - model
	rss = np.sum(residuals**2)
	tss = np.sum((data[-1]-np.mean(data[-1]))**2)
	r_squared = 1 - (rss / tss)
	
	layout = [
		#[sg.Image(filename='', key='-image-')],
		[sg.Text('Fitting function'), sg.InputText(f'{eq}', readonly=True)],
		[sg.Text('parameter'), sg.InputText(f'{xName}', readonly=True)],
		[sg.Text('Coefficient of determination'), sg.InputText(f'{r_squared}', readonly=True)],
		[sg.Button("Back"), sg.Button('Next'), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)
	#window['-image-'].update(data=obj)
	
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

def SelectData3(*data):
	df = data[0]
	if len(data[1]) == 4:
		xdefault = data[1][1]
		ydefault = data[1][2]
		zdefault = data[1][3]
	else:
		xdefault = ''
		ydefault = ''
		zdefault = ''
	dataName = list(df.columns.values)
	layout = [
		[sg.Text("x axis"), sg.Combo(dataName, default_value=xdefault, readonly=True, key='ComboX')],
		[sg.Text("y axis"), sg.Combo(dataName, default_value=ydefault, readonly=True, key='ComboY')],
		[sg.Text("z axis"), sg.Combo(dataName, default_value=ydefault, readonly=True, key='ComboZ')],
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
			if not values['ComboX'] in [values['ComboY'], values['ComboZ']]:
				if values['ComboY'] != values['ComboZ']:
					if values['ComboX'] != '' and values['ComboY'] != '' and values['ComboZ']:
						res = ri.SuccessCmd(df[[values['ComboX'], values['ComboY'], values['ComboZ']]], values['ComboX'], values['ComboY'], values['ComboZ'])
						break
	
	window.close()
	return res

def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg

def split_list(l, n):
	return [ l[idx:idx + n] for idx in range(0,len(l), n) ]

def makeColumnList(chkBoxList, s, n, dataName):
	l = [
		[sg.Text(s, size=(45, 1))], 
		[sg.Text("z axis"), sg.Combo(dataName, default_value='Select', readonly=True, key='ComboZ')]
	]
	l.extend(split_list(chkBoxList, n))
	return l

def SelectDatam(*data):
	df = data[0]
	if len(data[1]) > 0:
		xdefault = data[1]
	else:
		xdefault = []
	dataName = list(df.columns.values)
	
	chkboxList = [sg.Checkbox(item) for item in dataName]
	columns = sg.Column(
		makeColumnList(chkboxList, 'Select data which you want to use', 7, dataName), scrollable=True, size=(640,480)
	)
	
	layout = [
		[columns],
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
			sel = []
			for value in values.items():
				if value[1] and value[0] != 'ComboZ':
					sel.append(dataName[value[0]])
			if values['ComboZ'] in sel:
				sel.remove(values['ComboZ'])
				sel.append(values['ComboZ'])
				if len(sel) > 3:
					res = ri.SuccessCmd(df[sel], sel)
					break
	
	window.close()
	return res