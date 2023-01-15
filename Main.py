import PySimpleGUI as sg
from enum import Enum, auto
from Fit.FitData import FitData
from Basic.Basic import Basic
import ResClass
import os
import platform
from getData_Human.getData import getData


class Status(Enum):
	NULL = 0
	QUIT = auto()
	ERROR = auto()
	GET_DATA = auto()
	BASIC = auto()
	FIT_2D = auto()
	FIT_3D = auto()
	FIT_mD = auto()

def main(default):
	dic = {
		Status.GET_DATA: 'Make DataFile',
		Status.BASIC: 'Calculate Basic Statistic',
		Status.FIT_2D: 'Do Curve Fitting and Show 2D Graph',
		Status.FIT_3D: 'Do Curve Fitting and Show 3D Graph',
		Status.FIT_mD: 'Do Curve Fitting (Multi-dimension)'
	}
	
	res = select(default, dic)
	
	if res == Status.GET_DATA:
		return (ResClass.readGetData(getData()), dic[res])
	elif res == Status.BASIC:
		return (ResClass.basic(Basic()), dic[res])
	elif res == Status.FIT_2D:
		return (ResClass.readFit2d(FitData(2)), dic[res])
	elif res == Status.FIT_3D:
		return (ResClass.readFit2d(FitData(3)), dic[res])
	elif res == Status.FIT_mD:
		return (ResClass.readFit2d(FitData(0)), dic[res])
	else:
		return (ResClass.readMain(res), 'Select')

def select(default, dic):
	sg.theme('Dark Brown')
	
	selectData = [v for v in dic.values()]
	
	layout = [
		[sg.Combo(selectData, default_value=default, readonly=True, key='Combo')],
		[sg.Button('Exit'), sg.Submit()]
	]
	window = sg.Window('Theme Browser', layout)
	
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = Status.QUIT
			break
		elif event == 'Submit':
			for k, v in dic.items():
				if values['Combo'] == v:
					cmd = k
					breakFlag = True
					break
			else:
				breakFlag = False
			if breakFlag:
				break	
	
	window.close()
	return cmd
