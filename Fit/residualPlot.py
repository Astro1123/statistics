import PySimpleGUI as sg

from scipy import stats
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import japanize_matplotlib

import pandas as pd

import seaborn as sns

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

def plotResiduals(inputData):
	(residuals, model, d) = inputData[0]
	(count, variable, data, a, name, alpha) = d
	sg.theme('Dark Brown')

	#Chi-square
	ydata = data[-1]
	xdata = data[:-1]
	chi2 = stats.chisquare(ydata, f_exp = model)
	
	#Coefficient of determination
	rss = np.sum(residuals**2)
	tss = np.sum((ydata-np.mean(ydata))**2)
	r_squared = 1 - (rss / tss)
	adj_r_squared = 1 - ((rss / (count - variable - 1)) / (tss / (count - 1)))
	
	mae = np.sum(np.abs(residuals)) / count
	mse = tss / count
	rmse = np.sqrt(mse)
	vResiduals = rss / (count - variable - 1)
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
	
	#https://rikei-logistics.com/excel-regression
	column1 = sg.Column(
		[
			[sg.Text('Chi-square'), sg.InputText(f'{chi2[0]}', readonly=True)],
			[sg.Text('p-value'), sg.InputText(f'{chi2[1]}', readonly=True)],
			[sg.Text('RSS'), sg.InputText(f'{rss}', readonly=True)],
			[sg.Text('MSE'), sg.InputText(f'{mse}', readonly=True)],
			[sg.Text('RMSE'), sg.InputText(f'{rmse}', readonly=True)],
			[sg.Text('MAE'), sg.InputText(f'{mae}', readonly=True)],
			[sg.Text('Variance of residuals'), sg.InputText(f'{vResiduals}', readonly=True)],
			[sg.Text('Standard error of residuals'), sg.InputText(f'{seResiduals}', readonly=True)],
			[sg.Text('Coefficient of determination'), sg.InputText(f'{r_squared}', readonly=True)],
			[sg.Text('Adjusted coefficient of determination'), sg.InputText(f'{adj_r_squared}', readonly=True)],
			[sg.Text('Multiple correlation coefficient'), sg.InputText(f'{mcc}', readonly=True)],
		]
	)
	
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
	
	column2 = sg.Column(
		[
			[FrameSW],
			[FrameKS],
		]
	)
	
	if (variable > 1):
		column5 = sg.Column(
			[[sg.Text(key), sg.InputText(f'{val}', readonly=True)] for key, val in vif.to_dict().items()]
		)
	
	if (variable > 1):
		table3_index = ['Variables', 'Partial regression coefficient', 'Standardized partial regression coefficient']
		index_list = name[:-1]
		index_list.append('constant')
		var3 = []
		for index, av, alphav in zip(index_list, a, alpha):
			var3.append([index, av, alphav])
	
	table4_index = ['Residuals', 'Absolute Residuals', 'Relative Residuals']
	table4_index.extend(name)
	table4_index.append('Model')
	absresiduals = np.abs(residuals)
	reresiduals = residuals / model
	var4 = []
	for residual, absresidual, reresidual, d, m in zip(residuals, absresiduals, reresiduals, data.T, model):
		var4_list = [residual, absresidual, reresidual]
		var4_list.extend(d)
		var4_list.append(m)
		var4.append(var4_list)
	
	FrameMax = sg.Frame( 'Max', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{np.max(residuals)}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{np.max(absresiduals)}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{np.max(reresiduals)}', readonly=True)],
		]
	)
	FrameMin = sg.Frame( 'Min', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{np.min(residuals)}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{np.min(absresiduals)}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{np.min(reresiduals)}', readonly=True)],
		]
	)
	residualsQ = np.quantile(a=residuals, q=np.array([0.25, 0.5, 0.75]))
	absresidualsQ = np.quantile(a=absresiduals, q=np.array([0.25, 0.5, 0.75]))
	reresidualsQ = np.quantile(a=reresiduals, q=np.array([0.25, 0.5, 0.75]))
	FrameQ1 = sg.Frame( 'Q1', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[0]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[0]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[0]}', readonly=True)],
		]
	)
	FrameQ2 = sg.Frame( 'Q2', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[1]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[1]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[1]}', readonly=True)],
		]
	)
	FrameQ3 = sg.Frame( 'Q3', 
		[
			[sg.Text('Residuals'), sg.InputText(f'{residualsQ[2]}', readonly=True)],
			[sg.Text('Absolute Residuals'), sg.InputText(f'{absresidualsQ[2]}', readonly=True)],
			[sg.Text('Relative Residuals'), sg.InputText(f'{reresidualsQ[2]}', readonly=True)],
		]
	)
	column4 = sg.Column(
		[
			[FrameMax], [FrameQ3], [FrameQ2], [FrameQ1], [FrameMin],
			[sg.Text('Variance of residuals'), sg.InputText(f'{vResiduals}', readonly=True)],
			[sg.Text('Standard error of residuals'), sg.InputText(f'{seResiduals}', readonly=True)],
		]
	)
	
	t1 = sg.Tab('Scatter plot' ,[[column1, sg.Canvas(key='CANVAS_S', size=(640, 480))]])
	t2 = sg.Tab('Probability plot' ,[[column2, sg.Canvas(key='CANVAS_P', size=(640, 480))]])
	t4 = sg.Tab('Residuals', [[ column4, sg.Table(var4, headings=table4_index) ]])
	if (variable > 1):
		t3 = sg.Tab('Partial regression coefficient' ,[[sg.Table(var3, headings=table3_index)]])
		t5 = sg.Tab('Multicollinearity' ,[[column5, sg.Canvas(key='CANVAS_M', size=(640, 480))]])
		tab = [t1 ,t2, t3, t4, t5]
	else:
		tab = [t1 ,t2, t4]

	layout = [
		[sg.TabGroup ([tab])], [sg.Button("Back"), sg.Button('Exit')]
	]
	
	win_location = (0, 0)
	
	window = sg.Window('Title', layout, finalize=True, location=win_location)

	x_latent = np.linspace(min(model), max(model), 100)
	ideal = np.linspace(0, 0, 100)
	
	#Graphs
	fig1 = plt.Figure()
	ax1 = fig1.add_subplot(111)
	ax1.scatter(model, residuals)
	ax1.set_title(f"Residual plot")
	ax1.set_xlabel("Fitted values")
	ax1.set_ylabel("Residual")
	ax1.plot(x_latent, ideal, c="red")
	ax1.grid(True)
	
	fig2 = plt.Figure()
	ax2 = fig2.add_subplot(111)
	stats.probplot(ydata, dist="norm", plot=ax2)
	ax2.set_title("Probability plot of Residuals (Normal distribution)")
	ax2.grid(True)
	
	if (variable > 1):
		fig5 = plt.Figure()
		ax5 = fig5.add_subplot(111)
		sns.heatmap(m_mcc, linewidths=0.5, cmap='coolwarm', annot=True, ax=ax5, vmin=-1, vmax=1, xticklabels=name[:-1], yticklabels=name[:-1])
		ax5.set_title("Heatmap")
		fig_agg5 = draw_figure(window['CANVAS_M'].TKCanvas, fig5)
		
	fig_agg1 = draw_figure(window['CANVAS_S'].TKCanvas, fig1)
	fig_agg2 = draw_figure(window['CANVAS_P'].TKCanvas, fig2)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Back'):
			res = ri.BackCmd()
			break
		elif event == 'Exit':
			res = ri.QuitCmd()
			break

	window.close()
	return res



def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg
