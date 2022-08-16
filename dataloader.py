import math
def load_data(path):#根据路径加载数据集
	ans=[]#将数据保存到该数组
	if path.split(".")[-1]=="xls":#若路径为药方.xls
		from xlrd import open_workbook
		import xlwt
		workbook=open_workbook(path)
		sheet=workbook.sheet_by_index(0)#读取第一个sheet
		for i in range(1,sheet.nrows):#忽视header,从第二行开始读数据,第一列为处方ID,第二列为药品清单
			temp=sheet.row_values(i)[1].split(";")[:-1]#取该行数据的第二列并以“;”分割为数组
			if len(temp)==0: continue
			temp=[j.split(":")[0] for j in temp]#将药品后跟着的药品用量去掉
			temp=list(set(temp))#去重，排序
			temp.sort()
			ans.append(temp)#将处理好的数据添加到数组
	elif path.split(".")[-1]=="csv":
		import csv
		with open(path,"r") as f:
			reader=csv.reader(f)
			for row in reader:
				row=list(set(row))#去重，排序
				row.sort()
				ans.append(row)#将添加好的数据添加到数组

	return ans#返回处理好的数据集，为二维数组