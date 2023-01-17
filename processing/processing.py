import PySimpleGUI as sg
import pandas as pd
import numpy as np
import sympy as sym
from enum import Enum, auto
import warnings
import os

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

def SuccessCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.SUCCESS, data)
	return res

def FailCmd():
    res = ReturnInfo()
    res.makeInfo(Status.FAILURE, '')
    return res


def mergeFiles():
	files = None
	default = None
	while True:
		(cmd, files) = LoadFile(2, files).splitInfo()
		if cmd != Status.SUCCESS:
			return cmd.getStatus()
		(file1, file2) = files
		(_, df1) = OpenFile(file1).splitInfo()
		(_, df2) = OpenFile(file2).splitInfo()
		(cmd, df) = Concat(file1, file2).splitInfo()
		if cmd == Status.QUIT:
			return cmd.getStatus()
		elif cmd == Status.SUCCESS:
			res = save(df)
			return res.getStatus()

def addNewData():
	files = None
	default = None
	while True:
		(cmd, filename) = LoadFile(1,files).splitInfo()
		if cmd != Status.SUCCESS:
			return cmd.getStatus()
		(_, df) = OpenFile(filename).splitInfo()
		(cmd, exprData) = InputFormula(df).splitInfo()
		if cmd == Status.QUIT:
			return cmd
		elif cmd == Status.SUCCESS:
			(res, df) = Calc(df, exprData).splitInfo()
			res = save(df)
			return res.getStatus()


def Calc(df, exprData):
	warnings.simplefilter('error')
	if len(exprData) == 3:
		(xData, expr, Name) = exprData
		(xStr, x) = xData
		xarr = list(df[xStr].values)
		a = []
		for xv in xarr:
			try:
				a.append(expr.subs(x, xv))
			except Exception as e:
				a.append('')
	elif len(exprData) == 4:
		(xData, yData, expr, Name) = exprData
		(xStr, x) = xData
		(yStr, y) = yData
		xarr = list(df[xStr].values)
		yarr = list(df[yStr].values)
		a = []
		for xv, yv in zip(xarr, yarr):
			try:
				a.append(expr.subs([(x, xv), (y, yv)]))
			except:
				a.append('')
	elif len(exprData) == 5:
		(xData, yData, zData, expr, Name) = exprData
		(xStr, x) = xData
		(yStr, y) = yData
		(zStr, z) = zData
		a = []
		for xv, yv, zv in zip(xarr, yarr, zarr):
			try:
				a.append(expr.subs([(x, xv), (y, yv), (z, zv)]))
			except:
				a.append('')
	warnings.resetwarnings()
	df.insert(len(df.columns), Name, a)
	return SuccessCmd(df)

def InputFormula(df):
	dataName = list(df.columns.values)
	sg.theme('Dark Brown')
	
	defaultX = 'Select'
	defaultY = 'Select'
	defaultZ = 'Select'
	formula = ''
	Name = ''
	
	layout = [
		[sg.Text('x'), sg.Combo(dataName, default_value=defaultX, readonly=True, key='ComboX')],
		[sg.Text('y (Optional)'), sg.Combo(dataName, default_value=defaultY, readonly=True, key='ComboY')],
		[sg.Text('z (Optional)'), sg.Combo(dataName, default_value=defaultZ, readonly=True, key='ComboZ')],
		[sg.Text('Formula'), sg.InputText(key='Text', default_text=formula)],
		[sg.Text('Data Name'), sg.InputText(key='Text2', default_text=Name)],
		[sg.Button('Exit'), sg.Button('Back'), sg.Button('Select')]
	]
	window = sg.Window('Theme Browser', layout)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = QuitCmd()
			break
		if event in (sg.WIN_CLOSED, 'Back'):
			cmd = BackCmd()
			break
		elif event == "Select":
			if values['ComboX'] in dataName:
				if values['ComboY'] in dataName:
					if values['ComboZ'] in dataName:
						x, y, z = sym.symbols('x, y, z')
						res = [ (values['ComboX'], x), (values['ComboY'], y), (values['ComboZ'], z) ]
					else:
						x, y = sym.symbols('x, y')
						res = [ (values['ComboX'], x), (values['ComboY'], y) ]
				else:
					x = sym.symbols('x')
					res = [ (values['ComboX'], x) ]
				warnings.simplefilter('error')
				try:
					expr = sym.sympify(values['Text'])
					res.append(expr)
					res.append(values['Text2'])
					cmd = SuccessCmd(tuple(res))
					break
				except SympifyError as e:
					pass
				except TypeError as e:
					pass
				except Warning as e:
					pass
				warnings.resetwarnings()
	
	warnings.resetwarnings()
	window.close()
	return cmd

def Concat(file1, file2):
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Text('axis'), sg.Radio('Vertical', group_id='0'), sg.Radio('Horizontal', group_id='0')],
		[sg.Button('Exit'), sg.Button('Back'), sg.Button('Select')]
	]
	window = sg.Window('Theme Browser', layout)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = QuitCmd()
			break
		if event in (sg.WIN_CLOSED, 'Back'):
			cmd = BackCmd()
			break
		elif event == "Select":
			if values['Vertical']:
				df = pd.concat([file1, file2])
			else:
				df = pd.concat([file1, file2], axis=1)
			cmd = SuccessCmd(df)
	
	window.close()
	return cmd

def LoadFile(num, files):
	sg.theme('Dark Brown')
	
	filetype = (("csv files", "*.csv"), )
	filebrows = sg.FileBrowse(key="-FILE-", file_types=filetype, initial_folder=os.getcwd())
	if num == 2:
		filebrows2 = sg.FileBrowse(key="-FILE2-", file_types=filetype, initial_folder=os.getcwd())
	
	if num == 2:
		if files == None:
			file1 = ''
			file2 = ''
		else:
			(file1, file2) = files
		layout = [
			[sg.Text("File"), sg.InputText(key='Text', default_text=file1), filebrows],
			[sg.Text("File2"), sg.InputText(key='Text2', default_text=file2), filebrows2],
			[sg.Button('Exit'), sg.Button('Back'), sg.Button('Set')]
		]
	else:
		if files == None:
			filename = ''
		else:
			filename = files
		layout = [
			[sg.Text("File"), sg.InputText(key='Text', default_text=filename), filebrows],
			[sg.Button('Exit'), sg.Button('Back'), sg.Button('Set')]
		]
	window = sg.Window('Theme Browser', layout)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = QuitCmd()
			break
		if event in (sg.WIN_CLOSED, 'Back'):
			cmd = BackCmd()
			break
		elif event == "Set":
			if num == 2:
				if values['-FILE-'] != '':
					if values['-FILE2-'] != '':
						res = SuccessCmd((values['-FILE-'], values['-FILE2-']))
						break
					elif values['Text2'] != '':
						res = SuccessCmd((values['-FILE-'], values['-Text2-']))
						break
				elif values['Text'] != '':
					if values['-FILE2-'] != '':
						res = SuccessCmd((values['Text'], values['-FILE2-']))
						break
					elif values['Text2'] != '':
						res = SuccessCmd((values['Text'], values['-Text2-']))
						break
			else:
				if values['-FILE-'] != '':
					res = SuccessCmd(values['-FILE-'])
					break
				elif values['Text'] != '':
					res = SuccessCmd(values['Text'])
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

def save(df):
	filename = sg.popup_get_file('save', save_as=True)
	if filename != None:
		df.to_csv(filename)
		sg.popup('Complete')
		return SuccessCmd('')
	return FailCmd()