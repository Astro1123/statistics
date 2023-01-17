import PySimpleGUI as sg
import numpy as np
import pandas as pd
from enum import Enum, auto
from scipy import stats
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.special import loggamma

class ExecuteCommand(Enum):
	NULL = 0
	SAVE = auto()
	CONFIG = auto()

class Status(Enum):
	NULL = 0
	SUCCESS = auto()
	ERROR = auto()
	BACK = auto()
	NEXT = auto()
	QUIT = auto()
	FAILURE = auto()
	COMMAND = auto()

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

def CmdCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.COMMAND, data)
	return res

def SuccessCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.SUCCESS, data)
	return res

def FailCmd():
	res = ReturnInfo()
	res.makeInfo(Status.FAILURE, '')
	return res


def SelectData(df, select):
	dataName = list(df.columns.values)
	if select == None:
		default = 'Select'
	else:
		default = select
	
	layout = [
		[sg.Text("Select data which you want to use"), sg.Combo(dataName, default_value=default, readonly=True, key='Combo')],
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
			if values['Combo'] in dataName:
				if 'Text' != '':
					res = SuccessCmd(values['Combo'])
					break
	
	window.close()
	return res

def calcSqDeviation(x, average):
	return (x - average) ** 2

def CalcData(df, sel, binval, saveMet):
	dev = np.frompyfunc(calcSqDeviation, 2, 1)
	data = df[sel].dropna(how='all').values
	
	dic = {}
	c = data.size
	dic['Count'] = c
	s = np.sum(data)
	dic['Sum'] = s
	average = np.mean(data)
	dic['Average'] = average
	maxval = np.max(data)
	dic['Max'] = maxval
	minval = np.min(data)
	dic['Min'] = minval
	var = np.var(data)
	dic['Sample variance'] = var
	uvar = np.var(data, ddof=1)
	dic['Unbiased variance'] = uvar
	sumsq = sum(dev(data, average))
	dic['Sum of squares'] = sumsq
	ustd = np.std(data)
	dic['Uncorrected sample standard deviation'] = ustd
	cstd = np.std(data, ddof=1)
	dic['Corrected sample standard deviation'] = cstd
	std = np.sqrt(2 / (c - 1)) * np.exp(loggamma(c / 2) - loggamma((c - 1) / 2)) * ustd
	dic['Unbiased sample standard deviation'] = std
	midrange = (maxval + minval) / 2
	dic['Mid-range'] = midrange
	rangeval = maxval - minval
	dic['Range'] = rangeval
	median = np.median(data)
	dic['Median'] = median
	q3, q1 = np.percentile(data, [75, 25])
	iqr = q3 - q1
	dic['Third quartile'] = q3
	dic['First quartile'] = q1
	skew = stats.skew(data)
	dic['Skewness'] = skew
	kurtosis = stats.kurtosis(data)
	dic['Kurtosis'] = kurtosis
	modeval = statistics.multimode(data)
	dic['Mode'] = modeval
	
	FrameA = sg.Frame( 'Central tendency', 
		[
			[sg.Text('Average'), sg.InputText(f'{average}', readonly=True)],
			[sg.Text('Median'), sg.InputText(f'{median}', readonly=True)],
			[sg.Text('Mid-range'), sg.InputText(f'{midrange}', readonly=True)],
			[sg.Text('Mode'), sg.InputText(f'{modeval}', readonly=True)],
		]
	)
	FrameB = sg.Frame( 'Dispersion', 
		[
			[sg.Text('Max'), sg.InputText(f'{maxval}', readonly=True)],
			[sg.Text('Third quartile'), sg.InputText(f'{q3}', readonly=True)],
			[sg.Text('Second quartile'), sg.InputText(f'{median}', readonly=True)],
			[sg.Text('First quartile'), sg.InputText(f'{q1}', readonly=True)],
			[sg.Text('Min'), sg.InputText(f'{minval}', readonly=True)],
			[sg.Text('Range'), sg.InputText(f'{rangeval}', readonly=True)],
			[sg.Text('Interquartile range'), sg.InputText(f'{iqr}', readonly=True)],
			[sg.Text('Sum of squares'), sg.InputText(f'{sumsq}', readonly=True)],
			[sg.Text('Sample variance'), sg.InputText(f'{var}', readonly=True)],
			[sg.Text('Unbiased variance'), sg.InputText(f'{uvar}', readonly=True)],
			[sg.Text('Corrected sample standard deviation'), sg.InputText(f'{cstd}', readonly=True)],
			[sg.Text('Uncorrected sample standard deviation'), sg.InputText(f'{ustd}', readonly=True)],
			[sg.Text('Unbiased sample standard deviation'), sg.InputText(f'{std}', readonly=True)],
		]
	)
	FrameC = sg.Frame( 'Others', 
		[
			[sg.Text('Skewness'), sg.InputText(f'{skew}', readonly=True)],
			[sg.Text('Kurtosis'), sg.InputText(f'{kurtosis}', readonly=True)],
			[sg.Text('Sum'), sg.InputText(f'{s}', readonly=True)],
			[sg.Text('Count'), sg.InputText(f'{c}', readonly=True)],
		]
	)
	
	columns = sg.Column(
		[
			[FrameA],
			[FrameB],
			[FrameC],
			[sg.Button("Config"), sg.Button('Save'), sg.Button("Back"), sg.Button('Next'), sg.Button('Exit')]
		]
	)
	
	fig = plt.Figure()
	ax1 = fig.add_subplot(111)
	ax1.hist(data, bins=binval)
	ax1.set_title(f"Histogram of {sel}")
	
	layout = [
		[columns, sg.Canvas(key='CANVAS')]
	]
	
	win_location = (0, 0)
	window = sg.Window('Theme Browser', layout, finalize=True, location=win_location)
	
	draw_figure(window['CANVAS'].TKCanvas, fig)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = QuitCmd()
			break
		elif event == 'Back':
			res = BackCmd()
			break
		elif event == 'Next':
			res = NextCmd()
			break
		elif event == 'Config':
			res = CmdCmd((ExecuteCommand.CONFIG, pd.DataFrame(columns=[sel])))
			break
		elif event == 'Save':
			if saveMet:
				res = CmdCmd((ExecuteCommand.SAVE, (pd.DataFrame(columns=[sel]), dic)))
			else:
				res = CmdCmd((ExecuteCommand.SAVE, (pd.DataFrame(df[sel]), dic)))
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
		[sg.Button("Back"), sg.Button('Exit'), sg.Submit()]
	]
	window = sg.Window('Title', layout)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Back'):
			res = BackCmd()
			break
		elif event == 'Exit':
			res = QuitCmd()
			break
		elif event == 'Submit':
			if values["file"] != "":
				res = SuccessCmd(values["file"])
				break
			elif values["Text"] != "":
				res = SuccessCmd(values["Text"])
				break
	
	window.close()
	return res

def Basic():
	filename = ''
	selectname = 'Select'
	select = None
	binval = 10
	binMet = False
	saveMet = True
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
			while True:
				(code4, cmd) = CalcData(df, select, binval, saveMet).splitInfo()
				if code4 == Status.BACK:
					break
				elif code4 != Status.COMMAND:
					return code4
				(cmd, data) = cmd
				if cmd == ExecuteCommand.SAVE:
					(code, _) = makeSaveData(data).splitInfo()
				elif cmd == ExecuteCommand.CONFIG:
					configValues = (binval, binMet, saveMet, data, selectname)
					(code5, cmd) = configulation(configValues).splitInfo()
					if code5 == Status.QUIT:
						return code5
					elif code5 == Status.SUCCESS:
						(binval, binMet, saveMet, selectname) = cmd
	return Status.NULL

def configulation(configValues):
	(binval, binMet, saveMet, df, selectname) = configValues
	
	method = ['Square-root choice']
	
	widget1 = [
		[sg.Text('Range of Bins'), sg.InputText(key='BinRange', default_text=str(binval))]
	]
	widget2 = [[sg.Combo(method, key='Method', default_value=selectname)]]
	
	column1 = sg.Column( widget1, key='col1', visible=not binMet )
	column2 = sg.Column( widget2, key='col2', visible=binMet )
	
	tab1 = sg.Tab('Range of Bins' ,
		[
			[sg.Radio('manual', group_id='0', key='manual', enable_events=True, default=not binMet), sg.Radio('auto', group_id='0',key='auto',  enable_events=True, default=binMet)],
			[column1, column2]
		]
	)
	tab2 = sg.Tab('Save data' ,
		[
			[sg.Radio('Save original data', group_id='1', default=not saveMet, key='SAVE'), sg.Radio('Don\'t save original data', group_id='1', default=saveMet, key='DSAVE')],
		]
	)
	layout = [
		[ sg.TabGroup( [[ tab1, tab2 ]] ) ],
		[sg.Button("Back"), sg.Button('Exit'), sg.Button('Run')]
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
		elif event == 'Run':
			binMet = values['auto']
			if values['manual']:
				binval = int(values['BinRange'])
			else:
				selectname = values['Method']
				binval = calcBinRange(df, selectname)
			saveMet = values['DSAVE']
			res = SuccessCmd((binval, binMet, saveMet, selectname))
			break
		elif event == 'auto':
			window["col1"].update(visible=values['manual'])
			window["col2"].update(visible=values['auto'])
		elif event == 'manual':
			window["col1"].update(visible=values['manual'])
			window["col2"].update(visible=values['auto'])
	
	window.close()
	return res

def calcBinRange(df, method):
	return 10

def makeSaveData(data):
	(df, dic) = data
	for k, v in dic.items():
		if k == 'mode':
			df = pd.concat([df, pd.DataFrame([','.join([str(i) for i in v])], columns=df.columns, index=[k])])
		else:
			df = pd.concat([df, pd.DataFrame([v], columns=df.columns, index=[k])])
	return save(df)

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
		return SuccessCmd(None)
	return FailCmd()
