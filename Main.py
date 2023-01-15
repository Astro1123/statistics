import PySimpleGUI as sg
from enum import Enum, auto
from Fit2d.FitData import FitData
import ResClass
import os
import platform


from getData_Human.getData import getData


class Status(Enum):
	NULL = 0
	QUIT = auto()
	ERROR = auto()
	GET_DATA = auto()
	FIT_2D = auto()

def main(default):
	dic = {
		Status.GET_DATA: 'make DataFile',
		Status.FIT_2D: 'do Curve Fitting and show 2D Graph'
	}
	
	res = select(default, dic)
	
	if res == Status.GET_DATA:
		return (ResClass.readGetData(getData()), dic[res])
	elif res == Status.FIT_2D:
		return (ResClass.readFit2d(FitData()), dic[res])
	else:
		return (ResClass.readMain(res), 'Select')

def select(default, dic):
	sg.theme('Dark Brown')
	
	selectData = [v for v in dic.values()]
	
	layout = [
		[sg.Combo(selectData, default_value=default, readonly=True, key='Combo')],
		[sg.Submit(), sg.Button('Exit')]
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
