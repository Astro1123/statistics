import PySimpleGUI as sg

import math
import copy
from enum import Enum, auto

from scipy import stats

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import japanize_matplotlib

import seaborn as sns

from . import ReturnInfo as ri

class CodeC1(Enum):
	NONE = auto()
	Sigma1 = auto()
	Sigma2 = auto()
	Sigma3 = auto()
	I90 = auto()
	I95 = auto()
	I99 = auto()



def plotResiduals(inputData):
	(residuals, model, d) = inputData[0]
	(count, variable, data, a, name, alpha) = d
	sg.theme('Dark Brown')
	
	dicc1 = {
		'None' : CodeC1.NONE,
		'1σ' : CodeC1.Sigma1, '2σ' : CodeC1.Sigma2, '3σ' : CodeC1.Sigma3,
		'90%' : CodeC1.I90, '95%' : CodeC1.I95, '99%' : CodeC1.I99
	}

	#Chi-square
	ydata = data[-1]
	xdata = data[:-1]
	chi2 = stats.chisquare(ydata, f_exp = model)
	
	freedom = count - variable - 1
	
	#Coefficient of determination
	rss = np.sum(residuals**2)
	tss = np.sum((ydata-np.mean(ydata))**2)
	r_squared = 1 - (rss / tss)
	adj_r_squared = 1 - ((rss / freedom) / (tss / (count - 1)))
	
	mae = np.sum(np.abs(residuals)) / count
	mse = tss / count
	rmse = np.sqrt(mse)
	vResiduals = rss / freedom
	seResiduals = np.sqrt(vResiduals)

	#Multiple correlation coefficient
	mcc_data = np.array([ydata, model])
	corrcoef = np.corrcoef(mcc_data)
	mcc = corrcoef[0][1]
	meaning = meaningCov(mcc)
	
	#Multicollinearity
	m_mcc = np.corrcoef(xdata)
	if (variable > 1):
		inv_m_mcc = np.linalg.inv(m_mcc)
		vif = pd.Series(np.diag(inv_m_mcc), index=name[:-1])
	
	aic = count * ( np.log(math.pi * 2) + np.log(mse) + 1 ) + 2 * ( variable + 2 )
	
	#Standard error of coefficients
	deviation_list = []
	mean_list = []
	for i in range(len(xdata)):
		tmp = np.mean(xdata[i])
		mean_list.append(tmp)
		deviation_list.append( [ x - tmp for x in xdata[i] ] )
	deviation = np.array(deviation_list)
	S_list = []
	for i in range(len(xdata)):
		S_list_sub = []
		for j in range(len(xdata)):
			tmp = np.sum(deviation[i] * deviation[j])
			S_list_sub.append(tmp)
		S_list.append(S_list_sub)
	S_mat = np.matrix(S_list)
	S_inv_mat = np.linalg.inv(S_mat)
	x_average = np.matrix(mean_list)
	SE = []
	for i in range(len(xdata)):
		SE.append(np.sqrt(vResiduals * S_inv_mat[i, i]))
	sum_tmp = 0
	for i in range(len(xdata)):
		for j in range(len(xdata)):
			sum_tmp += x_average * S_inv_mat * x_average.T
	SE.append( np.sqrt( vResiduals * ( 1 / count + sum_tmp ) ) )
	
	stderr_coef = SE[:-1]
	stderr_cnst = SE[-1][0,0]
	
	inputData = (chi2, rss, mse, rmse, mae, aic, vResiduals, seResiduals, r_squared, adj_r_squared, mcc, model, residuals, dicc1)
	(widget, fig1) = showScatterPlot(inputData)
	t1 = sg.Tab('Scatter plot' ,widget)
	inputData = (name, stderr_coef, stderr_cnst, a, freedom, model, residuals, variable)
	t2 = sg.Tab('Statistical significance' ,showStatisticalSignificance(inputData))
	inputData = (residuals, ydata)
	(widget, fig3) = showProbabilityPlot(inputData)
	t3 = sg.Tab('Probability plot' ,widget)
	inputData = (name, residuals, model, data, vResiduals, seResiduals)
	(widget, fig5, df5) = showResiduals(inputData)
	t5 = sg.Tab('Residuals', widget)
	inputData = (count, variable, freedom)
	t0 = sg.Tab('Statistics', showStatistics(inputData))
	if (variable > 1):
		inputData = (name, a, alpha)
		t4 = sg.Tab('Partial regression coefficient' ,showPRC(inputData))
		inputData = (vif, m_mcc, name)
		(widget, fig6) = showMulticollinearity(inputData)
		t6 = sg.Tab('Multicollinearity' ,widget)
		tab = [[t1, t2, t3, t4, t5, t6, t0]]
	else:
		tab = [[t1, t2, t3, t5, t0]]

	layout = [
		[sg.TabGroup(tab)], [sg.Button("Back"), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)
	
	fig_agg1 = draw_figure(window['CANVAS_S'].TKCanvas, fig1)
	fig_agg3 = draw_figure(window['CANVAS_P'].TKCanvas, fig3)
	fig_agg3 = draw_figure(window['CANVAS_R'].TKCanvas, fig5)
	if (variable > 1):
		fig_agg6 = draw_figure(window['CANVAS_M'].TKCanvas, fig6)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Back'):
			res = ri.BackCmd()
			break
		elif event == 'Exit':
			res = ri.QuitCmd()
			break
		elif event == 'Sctc1':
			if dicc1[values['Comboc1']] == CodeC1.NONE:
				additional = (0, None)
			elif dicc1[values['Comboc1']] == CodeC1.Sigma1:
				additional = (1, seResiduals)
			elif dicc1[values['Comboc1']] == CodeC1.Sigma2:
				additional = (2, seResiduals)
			elif dicc1[values['Comboc1']] == CodeC1.Sigma3:
				additional = (3, seResiduals)
			elif dicc1[values['Comboc1']] == CodeC1.I90:
				additional = (4, (stats.t.interval(alpha=0.9, df=freedom), seResiduals))
			elif dicc1[values['Comboc1']] == CodeC1.I95:
				additional = (5, (stats.t.interval(alpha=0.95, df=freedom), seResiduals))
			elif dicc1[values['Comboc1']] == CodeC1.I99:
				additional = (6, (stats.t.interval(alpha=0.99, df=freedom), seResiduals))
			pltScatterPlotc1(fig1, model, residuals, additional)
			fig_agg1.draw()
		elif event == 'Ascc5':
			if values['Comboc5'] == 'Default':
				window['Tablec5'].update(values=df5.values.tolist())
			else:
				window['Tablec5'].update(values=df5.sort_values(values['Comboc5']).values.tolist())
		elif event == 'Descc5':
			if values['Comboc5'] == 'Default':
				window['Tablec5'].update(values=df5.values.tolist())
			else:
				window['Tablec5'].update(values=df5.sort_values(values['Comboc5'], ascending=False).values.tolist())
		elif event == 'Updatec2':
			if values['Comboc2'] == '90%':
				pc = 90
			elif values['Comboc2'] == '99%':
				pc = 99
			else:
				pc = 95
			inputData = (name, stderr_coef, stderr_cnst, a, freedom, pc)
			window['Tablec2a'].update(values=updateTableC2(inputData))

	window.close()
	return res

def pltScatterPlotc1(fig1, model, residuals, additional):
	(code, data) = additional
	x_latent = np.linspace(min(model), max(model), 100)
	ideal = np.linspace(0, 0, 100)
	
	ax1 = fig1.add_subplot(111)
	ax1.scatter(model, residuals)
	ax1.set_title(f"Residual plot")
	ax1.set_xlabel("Fitted values")
	ax1.set_ylabel("Residual")
	ax1.plot(x_latent, ideal, c="red")
	ax1.grid(True)
	if code == 4 or code == 5 or code == 6:
		(data, sigma) = data
		(lower, upper) = data
		y1 = np.linspace(sigma * upper, sigma * upper, 100)
		y2 = np.linspace(sigma * lower, sigma * lower, 100)
		ax1.plot(x_latent, y1, c="green")
		ax1.plot(x_latent, y2, c="green")
	elif code == 1 or code == 2 or code == 3:
		y1 = np.linspace(data * code, data * code, 100)
		y2 = np.linspace(-data * code, -data * code, 100)
		ax1.plot(x_latent, y1, c="green")
		ax1.plot(x_latent, y2, c="green")
	return fig1

def updateTableC2(inputData):
	(name, stderr_coef, stderr_cnst, a, freedom, pc) = inputData
	table2_index = ['Variables', 'Coefficient', 'Standard error', 't-value', 'p-value', f'Lower limit ({pc}%)', f'Upper limit ({pc}%)']
	variables = name[:-1]
	variables.append('Constant')
	stderr_all = copy.copy(stderr_coef)
	stderr_all.append(stderr_cnst)
	stderr_all = np.array(stderr_all)
	stderr_tValues = a / stderr_all
	stderr_pValues = stats.t.sf(x=np.abs(stderr_tValues), df=freedom) * 2
	(low, high) = stats.t.interval(alpha=pc/100, df=freedom)
	lowerLimits = a + stderr_all * low
	upperLimits = a + stderr_all * high
	var2 = []
	for variablev, av, stderr, stderr_tValue, stderr_pValue, l, u in zip(variables, a, stderr_all, stderr_tValues, stderr_pValues, lowerLimits, upperLimits):
		var2_list = [variablev, av, stderr, stderr_tValue, stderr_pValue, l, u]
		var2.append(var2_list)
	return var2



def showStatistics(inputData):
	(count, variable, freedom) = inputData
	column0a = sg.Column(
		[
			[]
		]
	)
	column0b = sg.Column(
		[
			[sg.Text('Number of Data'), sg.InputText(f'{count}', readonly=True)],
			[sg.Text('Number of Parameter'), sg.InputText(f'{variable}', readonly=True)],
			[sg.Text('Degree of Freedom'), sg.InputText(f'{freedom}', readonly=True)],
		]
	)
	return [[column0a, column0b]]

def showScatterPlot(inputData):
	(chi2, rss, mse, rmse, mae, aic, vResiduals, seResiduals, r_squared, adj_r_squared, mcc, model, residuals, dic) = inputData
	#https://rikei-logistics.com/excel-regression
	column1 = sg.Column(
		[
			[sg.Text('Chi-square'), sg.InputText(f'{chi2[0]}', readonly=True)],
			[sg.Text('p-value'), sg.InputText(f'{chi2[1]}', readonly=True)],
			[sg.Text('RSS'), sg.InputText(f'{rss}', readonly=True)],
			[sg.Text('MSE'), sg.InputText(f'{mse}', readonly=True)],
			[sg.Text('RMSE'), sg.InputText(f'{rmse}', readonly=True)],
			[sg.Text('MAE'), sg.InputText(f'{mae}', readonly=True)],
			[sg.Text('AIC (normal distribution)'), sg.InputText(f'{aic}', readonly=True)],
			[sg.Text('Variance of residuals'), sg.InputText(f'{vResiduals}', readonly=True)],
			[sg.Text('Standard error of residuals'), sg.InputText(f'{seResiduals}', readonly=True)],
			[sg.Text('Coefficient of determination'), sg.InputText(f'{r_squared}', readonly=True)],
			[sg.Text('Adjusted coefficient of determination'), sg.InputText(f'{adj_r_squared}', readonly=True)],
			[sg.Text('Multiple correlation coefficient'), sg.InputText(f'{mcc}', readonly=True)],
		]
	)
	
	modeList = list(dic.keys())
	columnG = sg.Column(
		[
			[sg.Canvas(key='CANVAS_S', size=(640, 480))],
			[sg.Button('Draw', key='Sctc1'), sg.Combo(modeList, key='Comboc1', readonly=True, default_value='None')]
		]
	)
	
	fig = plt.Figure()
	pltScatterPlotc1(fig, model, residuals, (CodeC1.NONE, None))
	
	return ([[column1, columnG]], fig)

def showStatisticalSignificance(inputData):
	(name, stderr_coef, stderr_cnst, a, freedom, model, residuals, variable) = inputData
	table2_index = ['Variables', 'Coefficient', 'Standard error', 't-value', 'p-value', 'Lower limit (95%)', 'Upper limit (95%)']
	variables = name[:-1]
	variables.append('Constant')
	stderr_all_tmp = copy.copy(stderr_coef)
	stderr_all_tmp.append(stderr_cnst)
	stderr_all = np.array(stderr_all_tmp)
	stderr_tValues = a / stderr_all
	stderr_pValues = stats.t.sf(x=np.abs(stderr_tValues), df=freedom) * 2
	(low, high) = stats.t.interval(alpha=0.95, df=freedom)
	lowerLimits = a + stderr_all * low
	upperLimits = a + stderr_all * high
	var2 = []
	for variablev, av, stderr, stderr_tValue, stderr_pValue, l, u in zip(variables, a, stderr_all, stderr_tValues, stderr_pValues, lowerLimits, upperLimits):
		var2_list = [variablev, av, stderr, stderr_tValue, stderr_pValue, l, u]
		var2.append(var2_list)
	
	table_index = ['', 'Degree of freedom', 'SS', 'MS', 'F', 'Significance']
	regave = np.average(model)
	resave = np.average(residuals)
	col = ['Regression', 'Residual']
	df = [variable, freedom]
	SS = [np.sum((model - regave)**2), np.sum((residuals - resave)**2)]
	MS = [SS[0] / df[0], SS[1] / df[1]]
	F = MS[0] / MS[1]
	p = stats.f.sf(F, df[0], df[1])
	var = []
	var.append([col[0], df[0], SS[0], MS[0], F, p])
	var.append([col[1], df[1], SS[1], MS[1]])
	column2 = sg.Column(
		[
			[]
		]
	)
	parcent = ['90%', '95%', '99%']
	columnG = sg.Column(
		[
			[sg.Table(var2, headings=table2_index, key='Tablec2a')],
			[sg.Table(var, headings=table_index)],
			[sg.Button('Update', key='Updatec2'), sg.Combo(parcent, key='Comboc2', readonly=True, default_value='95%')]
		]
	)
	return [[column2, columnG]]

def showProbabilityPlot(inputData):
	(residuals, ydata) = inputData
	result1 = stats.shapiro(residuals)
	result2 = stats.ks_1samp(residuals, stats.norm.cdf)
	
	FrameSW = sg.Frame( 'Shapiro–Wilk test', 
		[
			[sg.Text('statistic'), sg.InputText(f'{result1[0]}', readonly=True)],
			[sg.Text('p-value'), sg.InputText(f'{result1[1]}', readonly=True)],
		]
	)
	FrameKS = sg.Frame( 'Kolmogorov–Smirnov test', 
		[
			[sg.Text('statistic'), sg.InputText(f'{result2[0]}', readonly=True)],
			[sg.Text('p-value'), sg.InputText(f'{result2[1]}', readonly=True)],
		]
	)
	
	column3 = sg.Column(
		[
			[FrameSW],
			[FrameKS],
		]
	)
	
	fig3 = plt.Figure()
	ax3 = fig3.add_subplot(111)
	stats.probplot(ydata, dist="norm", plot=ax3)
	ax3.set_title("Probability plot of Residuals (Normal distribution)")
	ax3.grid(True)
	
	return ([[column3, sg.Canvas(key='CANVAS_P', size=(640, 480))]], fig3)

def showPRC(inputData):
	(name, a, alpha) = inputData
	table4_index = ['Variables', 'Partial regression coefficient', 'Standardized partial regression coefficient']
	index_list = name[:-1]
	index_list.append('constant')
	var4 = []
	for index, av, alphav in zip(index_list, a, alpha):
		var4.append([index, av, alphav])
	return [[sg.Table(var4, headings=table4_index)]]

def showResiduals(inputData):
	(name, residuals, model, data, vResiduals, seResiduals) = inputData
	sortList = ['Residuals', 'Standard Residuals', 'Absolute Residuals', 'Relative Residuals']
	table5_index = copy.copy(sortList)
	sortList.append('Default')
	table5_index.extend(name)
	table5_index.append('Model')
	absresiduals = np.abs(residuals)
	reresiduals = residuals / model
	stdresiduals = residuals / seResiduals
	var5 = []
	for residual, stdresidual, absresidual, reresidual, d, m in zip(residuals, stdresiduals, absresiduals, reresiduals, data.T, model):
		var5_list = [residual, stdresidual, absresidual, reresidual]
		var5_list.extend(d)
		var5_list.append(m)
		var5.append(var5_list)
	
	df = pd.DataFrame(var5, columns=table5_index)
	
	FrameMax = sg.Frame( 'Max', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{np.max(residuals)}', readonly=True)],
			[sg.Text('Standard Residuals'), sg.InputText(f'{np.max(stdresiduals)}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{np.max(absresiduals)}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{np.max(reresiduals)}', readonly=True)],
		]
	)
	FrameMin = sg.Frame( 'Min', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{np.min(residuals)}', readonly=True)],
			[sg.Text('Standard Residuals'), sg.InputText(f'{np.min(stdresiduals)}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{np.min(absresiduals)}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{np.min(reresiduals)}', readonly=True)],
		]
	)
	residualsQ = np.quantile(a=residuals, q=np.array([0.25, 0.5, 0.75]))
	absresidualsQ = np.quantile(a=absresiduals, q=np.array([0.25, 0.5, 0.75]))
	reresidualsQ = np.quantile(a=reresiduals, q=np.array([0.25, 0.5, 0.75]))
	stdresidualsQ = np.quantile(a=stdresiduals, q=np.array([0.25, 0.5, 0.75]))
	FrameQ1 = sg.Frame( 'Q1', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[0]}', readonly=True)],
			[sg.Text('Standard Residuals'), sg.InputText(f'{stdresidualsQ[0]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[0]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[0]}', readonly=True)],
		]
	)
	FrameQ2 = sg.Frame( 'Q2', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[1]}', readonly=True)],
			[sg.Text('Standard Residuals'), sg.InputText(f'{stdresidualsQ[1]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[1]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[1]}', readonly=True)],
		]
	)
	FrameQ3 = sg.Frame( 'Q3', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[2]}', readonly=True)],
			[sg.Text('Standard Residuals'), sg.InputText(f'{stdresidualsQ[2]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[2]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[2]}', readonly=True)],
		]
	)
	column5 = sg.Column(
		[
			[FrameMax], [FrameQ3], [FrameQ2], [FrameQ1], [FrameMin],
			[sg.Text('Variance of residuals'), sg.InputText(f'{vResiduals}', readonly=True)],
			[sg.Text('Standard error of residuals'), sg.InputText(f'{seResiduals}', readonly=True)],
		]
	)
	fig = plt.Figure()
	ax = fig.add_subplot(111)
	ax.set_title('Standard Residuals')
	labels = ['Standard Residuals']
	ax.hist(stdresiduals, label=labels, bins=math.ceil(np.sqrt(len(stdresiduals))))
	
	columnT = sg.Column(
		[
			[sg.Canvas(key='CANVAS_R')],
			[sg.Table(var5, headings=table5_index, key='Tablec5')],
			[sg.Button('Asc', key='Ascc5'), sg.Button('Desc', key='Descc5'), sg.Combo(sortList, key='Comboc5', readonly=True, default_value='Default')]
		]
	)
	return ([[column5, columnT]], fig, df)

def showMulticollinearity(inputData):
	(vif, m_mcc, name) = inputData
	column6 = sg.Column(
		[[sg.Text(key), sg.InputText(f'{val}', readonly=True)] for key, val in vif.to_dict().items()]
	)
	fig6 = plt.Figure()
	ax6 = fig6.add_subplot(111)
	sns.heatmap(m_mcc, linewidths=0.5, cmap='coolwarm', annot=True, ax=ax6, vmin=-1, vmax=1, xticklabels=name[:-1], yticklabels=name[:-1])
	ax6.set_title("Heatmap")
	return ([[column6, sg.Canvas(key='CANVAS_M', size=(640, 480))]], fig6)
	




def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg

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
