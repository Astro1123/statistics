import PySimpleGUI as sg

from scipy import stats
import numpy as np

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

def plotResiduals(data):
	(residuals, model, d) = data[0]
	(count, variable) = d
	sg.theme('Dark Brown')

	#Chi-square
	ydata = residuals + model
	chi2 = stats.chisquare(ydata, f_exp = model)
	
	#Coefficient of determination
	residuals =  ydata - model
	rss = np.sum(residuals**2)
	tss = np.sum((ydata-np.mean(ydata))**2)
	r_squared = 1 - (rss / tss)
	count = len(ydata)
	variable = 1
	adj_r_squared = 1 - ((rss / (count - variable - 1)) / (tss / (count - 1)))
	
	mae = np.sum(np.abs(residuals)) / count
	mse = tss / count
	rmse = np.sqrt(mse)
	vResiduals = rss / (count - variable - 1)

	#Multiple correlation coefficient
	mcc_data = np.array([ydata, model])
	corrcoef = np.corrcoef(mcc_data)
	mcc = corrcoef[0][1]
	meaning = meaningCov(mcc)

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
	
	t1 = sg.Tab('Scatter plot' ,[[column1, sg.Canvas(key='CANVAS_S', size=(640, 480))]])
	t2 = sg.Tab('Probability plot' ,[[column2, sg.Canvas(key='CANVAS_P', size=(640, 480))]])

	layout = [
		[sg.TabGroup ([[t1 ,t2]])],
		[sg.Button("Back"), sg.Button('Exit')]
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
