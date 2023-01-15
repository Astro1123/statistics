import PySimpleGUI as sg
import pandas as pd
import numpy as np
import os
import CommandClass as cc

err = None

def fileselect():
	sg.theme('Dark Brown')
	
	filetype = (("csv files", "*.csv"), )
	filebrows = sg.FileBrowse(key="-FILE-", file_types=filetype, initial_folder=os.getcwd())
	filebrows2 = sg.FileBrowse(key="-FILE2-", file_types=filetype, initial_folder=os.getcwd())
	
	layout = [
		[sg.Text("ファイル"), sg.InputText(), filebrows],
		[sg.Text("ファイル"), sg.InputText(), filebrows2, sg.Button('Set')],
		[sg.Button('Exit')]
	]
	window = sg.Window('Theme Browser', layout)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = cc.QuitCommand()
			break
		elif event == "Set":
			if values['-FILE-'] != '':
				if values['-FILE2-'] != '':
					cmd = cc.MakeCommand(cc.const.FILESELECT, values['-FILE-'], cc.const.FILESELECT, values['-FILE2-'])
					break
				cmd = cc.MakeCommand(cc.const.FILESELECT, values['-FILE-'])
				break
	
	window.close()
	return cmd

def selectEncode(filename):
	enc = ["utf-8", "shift-jis", "cp932", "utf-8-sig", "iso2022_jp", "euc_jp"]
	i = 0
	for s in enc:
		try:
			df = pd.read_csv(filename, encoding=enc[i])
			res = enc[i]
			break
		except UnicodeDecodeError as e1:
			i += 1
	else:
		res = "unknown"
	return res

def readFile(tup):
	(code, filename, fl) = tup
	try:
		if code != cc.const.FILESELECT:
			raise ValueError
	except ValueError as e:
		err = e
		return cc.InvalidValueCommand()
	try:
		if fl[0] == 0:
			enc = selectEncode(filename)
			if enc == "unknown":
				raise ValueError
			df = pd.read_csv(filename, header=1, skiprows=[2], encoding=enc)
			dfRes = df.drop(columns=df.columns[[0]]).dropna(how='all').dropna(subset=['個人番号'])
		elif fl[0] == 2 and fl[1] == cc.const.FILESELECT:
			enc = selectEncode(filename)
			if enc == "unknown":
				raise ValueError
			df = pd.read_csv(filename, header=1, encoding=enc)
			df2 = pd.read_csv(fl[2], header=1, encoding=enc)
			dfRes = pd.merge(df, df2, on=['ID', '性別', '年齢群'], how='right')
		else:
			raise ValueError
	except ValueError as e:
		err = e
		return cc.InvalidValueCommand()
	except KeyError as e:
		err = e
		return cc.FalureCommand()
	return dfRes

def split_list(l, n):
	return [ l[idx:idx + n] for idx in range(0,len(l), n) ]

def makeColumnList(chkBoxList, s, n):
	l = [[sg.Text(s, size=(45, 1))]]
	l.extend(split_list(chkBoxList, n))
	l.append([sg.Button('Exit', key='Exit'), sg.Button('Select', key='Select')])
	return l

def isDefaultSelectUse(item):
	selList = []
	selList.append('ID')
	selList.append('個人番号')
	selList.append('性別')
	selList.append('年齢群')
	selList.append('年齢')
	selList.append('身長')
	selList.append('体重')
	selList.append('胸囲（静時・女子）')
	selList.append('下部胸囲（女子）')
	selList.append('胴囲')
	selList.append('殿囲')
	selList.append('大腿囲')
	selList.append('乳頭位胸囲（バスト）')
	selList.append('下部胸囲（アンダーバスト）(女性のみ）')
	selList.append('ウエスト（ウエストベルト使用）')
	selList.append('ヒップ囲')
	return item in selList

def useColumns(df):
	l = list(df.columns.values)
	
	sg.theme('Dark Brown')
	
	chkboxList = [sg.Checkbox(item, key=item, default=isDefaultSelectUse(item)) for item in l]
	columns = sg.Column(
		makeColumnList(chkboxList, '読み込む列名を選択', 7), scrollable=True, size=(640,480)
	)
	
	layout = [[columns]]
	
	window = sg.Window('Theme Browser', layout)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = cc.QuitCommand()
			break
		elif event == 'Select':
			sel = []
			for value in values.items():
				if value[1]:
					sel.append(value[0])
			if sel:
				res = cc.MakeCommand(cc.const.DATASELECT, df[sel])
				break
	
	window.close()
	return res

def isDefaultSelectSearch(item):
	selList = []
	selList.append('性別')
	selList.append('年齢群')
	selList.append('年齢')
	return item in selList

def searchbox(sel):
	dic = {}
	l = []
	g_id = 0
	for s in sel:
		if s == '性別':
			l.append([sg.Text(s), sg.Radio('M', key='Male', group_id=str(g_id)), sg.Radio('F', key='Female', group_id=str(g_id), default=True), sg.Checkbox('非表示', key=s+'非表示', default=True)])
			g_id += 1
		elif s == '年齢群':
			l.append([sg.Text(s), sg.Radio('A', key='Adult', group_id=str(g_id)), sg.Radio('Y', key='Young', group_id=str(g_id), default=True), sg.Checkbox('非表示', key=s+'非表示', default=True)])
			g_id += 1
		elif s == '計測年月日':
			l.append([sg.Text(s), sg.InputText(key = s), sg.Radio('一致', key=s+'一致', group_id=str(g_id), default=True), sg.Radio('含む', key=s+'含む', group_id=str(g_id)), sg.Radio('いづれか', key=s+'いづれか', group_id=str(g_id)), sg.Checkbox('非表示', key=s+'非表示')])
			g_id += 1
		elif s == '個人番号':
			l.append([sg.Text(s), sg.InputText(key = s), sg.Radio('一致', key=s+'一致', group_id=str(g_id), default=True), sg.Radio('含む', key=s+'含む', group_id=str(g_id)), sg.Radio('いづれか', key=s+'いづれか', group_id=str(g_id)), sg.Checkbox('非表示', key=s+'非表示')])
			g_id += 1
		else:
			l.append([sg.Text(s), sg.InputText(key = s+'以上'), sg.Text('〜'), sg.InputText(key = s+'以下'), sg.Checkbox('非表示', key=s+'非表示')])
	return l

def runSearch(s, values, df):
	if s == '性別':
		if values['Female']:
			return df[df[s] == 'F']
		else:
			return df[df[s] == 'M']
	elif s == '年齢群':
		if values['Young']:
			return df[df[s] == 'Y']
		else:
			return df[df[s] == 'A']
	elif s == '計測年月日':
		if values[s+'一致']:
			return df[df[s] == values[s]]
		elif values[s+'含む']:
			return df.query(f'{s}.str.contains(\"{f"{values[s]}"}\")', engine='python')
		else:
			return df[df[s].isin(values[s].split())]
	elif s == '個人番号':
		if values[s+'一致']:
			return df[df[s] == values[s]]
		elif values[s+'含む']:
			return df.query(f'{s}.str.contains(\"{f"{values[s]}"}\")', engine='python')
		else:
			return df[df[s].isin(values[s].split())]
	else:
		if values[s+'以上'] != '':
			if values[s+'以下'] != '':
				return df.query(f'{values[f"{s}以上"]} <= {s} <= {values[f"{s}以下"]}')
			else:
				return df.query(f'{values[f"{s}以上"]} <= {s}')
		else:
			return df.query(f'{s} <= {values[s+"以下"]}')

def search(sel, df):
	sg.theme('Dark Brown')
	
	searchlist = searchbox(sel)
	searchlist.append([sg.Button('Exit', key='Exit'), sg.Button('Search', key='Search')])
	columns = sg.Column(
		searchlist, scrollable=True, size=(640,480)
	)
	layout = [[columns]]
	window = sg.Window('Theme Browser', layout)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = cc.QuitCommand()
			break
		elif event == 'Search':
			dfRes = df
			for s in sel:
				dfRes = runSearch(s, values, dfRes)
				if values[s+'非表示']:
					dfRes = dfRes.drop(s, axis=1)
			res = cc.MakeCommand(cc.const.DATASELECT, dfRes)
			break
	
	window.close()
	return res

def searchData(df):
	l = list(df.columns.values)
	
	sg.theme('Dark Brown')
	
	chkboxList = [sg.Checkbox(item, key=item, default=isDefaultSelectSearch(item)) for item in l]
	columns = sg.Column(
		makeColumnList(chkboxList, '絞込みに使う列名を選択', 1), scrollable=True, size=(640,480)
	)
	
	layout = [[columns]]
	
	window = sg.Window('Theme Browser', layout)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = cc.QuitCommand()
			break
		elif event == 'Select':
			sel = []
			for value in values.items():
				if value[1]:
					sel.append(value[0])
			if sel:
				res = search(sel, df)
				(code, cmd) = res.getcmd()
				if code == cc.const.DATASELECT:
					res = cc.MakeCommand(cc.const.DATASELECT, cmd)
				break
			else:
				res = cc.MakeCommand(cc.const.DATASELECT, df)
				break
	
	window.close()
	return res

def main(tup):
	res = readFile(tup)
	
	if type(res) == cc.CommandClass:
		return res
	elif type(res) == pd.DataFrame:
		res = useColumns(res)
		(code, cmd) = res.getcmd()
		if code == cc.const.DATASELECT:
			res = searchData(cmd)
			(code, cmd) = res.getcmd()
			if code == cc.const.DATASELECT:
				df = cmd.reset_index(drop=True).fillna('').astype(str)
				l = df.reset_index().T.reset_index().T.values.tolist()
			else:
				return res
		else:
			return res
	else:
		try:
			raise ValueError
		except ValueError as e:
			err = e
			return cc.InvalidValueCommand()
	
	value = sg.popup_yes_no('インデックスを表示しますか？')
	if value != 'Yes':
		tmp = []
		for sl in l:
			tmp.append(sl[1:])
		l = tmp
	
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Table(l[1:], headings=l[0])],
		[sg.Button('Exit'), sg.Button('Save'), sg.Button('Other')]
	]
	window = sg.Window('Theme Browser', layout, resizable=True)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			cmd = cc.QuitCommand()
			break
		elif event == 'Save':
			save(l)
		elif event == 'Other':
			cmd = cc.OtherCommand()
			break
	
	window.close()
	return cmd

def save(l):
	filename = sg.popup_get_file('save', save_as=True)
	if filename != None:
		f = open(filename, "w")
		for sl in l:
			f.write(','.join([str(a) for a in sl]))
			f.write("\n")
		f.close()
		sg.popup('保存完了')
