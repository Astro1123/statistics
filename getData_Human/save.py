import PySimpleGUI as sg

def save(l):
	filename = sg.popup_get_file('save', save_as=True)
	if filename != None:
		f = open(filename, "w")
		for sl in l:
			f.write(','.join([str(a) for a in sl]))
			f.write("\n")
		f.close()
		sg.popup('保存完了')