import urllib.parse                   # 参数处理
import http.client                    # 建立http连接
import json                           # json处理
from urllib import request            # 发送请求
from bs4 import BeautifulSoup         # 解析html
from tkinter import *                 # 调用图形界面库
from tkinter import messagebox        # 弹出框
from tkinter import ttk               # 表格
import os                             # 处理路径
import webbrowser                     # 打开浏览器

class Application(Frame):
    def __init__(self):
      self.root = Tk()
      self.root.title('免费书城 (作者：陈俊翰)')
      self.width = 500                  # 窗口宽度
      self.height = 350                 # 窗口高度
      self.root.geometry(str(self.width) + 'x' + str(self.height))     # 设置窗口大小
      self.root.resizable(width=False, height=False)       # 宽度高度不可变
      self.window_center()

      self.header = Frame(width=250, height=30)
      self.fictionList = Frame(width=450, height=150)
      self.footerLeft = Frame(width=50, height=30)

      self.header.grid(row=0, padx=125, pady=10)
      self.fictionList.grid(row=1, padx=25)
      self.footerLeft.grid(row=2, column=0, sticky=E, padx=50, pady=10)

      self.createWidgets()
 
    # 窗口居中
    def window_center(self):
      width = self.root.winfo_screenwidth()
      height = self.root.winfo_screenheight()
      size = '+%d+%d' % ((width - self.width) / 2, (height - self.height) / 2)
      self.root.geometry(size)

    # 构建界面
    def createWidgets(self):

      # 搜索框
      self.var = StringVar()
      self.lb = Entry(self.header, textvariable = self.var)
      self.lb.grid(row=0)
      self.lb.focus_set()                              # 获取搜索框焦点
      self.lb.bind('<Key>', self.printkey)             # 监听回车事件

      Button(self.header, text='搜索小说', command=self.search).grid(row=0, column=1,padx=5)
      button = Button(self.footerLeft, text='下载TXT', command=self.getDownloadUrl).pack(side='right', fill='y', ipadx=10)
      button = Button(self.footerLeft, text='在线阅读', command=self.onlineRead, bg="green", fg="white").pack(side='right', fill='y', padx=10, ipadx=10)

      # 固定容器大小
      self.header.grid_propagate(0)
      self.fictionList.grid_propagate(0)
      self.footerLeft.grid_propagate(0)

      self.showList()

      self.root.mainloop()

    # 输入框监听键盘事件
    def printkey(self, event):
      
      # 如果按下回车键，则进行搜索
      if event.keycode == 13:
        self.search()

    # 显示列表
    def showList(self):
      self.tree = ttk.Treeview(self.fictionList)    #表格

      vsb = ttk.Scrollbar(self.fictionList, orient="vertical", command=self.tree.yview)
      vsb.pack(side='right', fill='y')

      self.tree.configure(yscrollcommand=vsb.set)

      self.tree["columns"] = ("0","1","2","3")
      self.tree['show'] = "headings"
      self.tree.column("0", width=50, anchor="c") 
      self.tree.column("1", width=200, anchor="c")   #表示列,不显示
      self.tree.column("2", width=150, anchor="c")
      self.tree.column("3", width=50, anchor="c")
      
      self.tree.heading("0", text="编号")
      self.tree.heading("1", text="文章名称")  #显示表头
      self.tree.heading("2", text="作者")
      self.tree.heading("3", text="状态") 
      self.tree.pack()
      
    # 搜索小说
    def search(self):
      
      kw = self.var.get()        # 搜索关键字
      
      if len(kw) == 0:
        messagebox.showinfo('提示信息', '请输入小说名')
        return
      
      key = urllib.parse.quote(kw.encode('utf-8'))       # url编码处理
      url = "https://www.ixdzs.com/bsearch?q=" + key

      f = urllib.request.urlopen(url)
      result = f.read().decode('utf-8')
      soup = BeautifulSoup(result, 'html.parser')
      list = soup.find("div", attrs={"class": "box_k"}).find('ul').find_all('li')

      self.fictionList = []
      
      for index, l in enumerate(list):
        info = l.find('div', attrs={"class": "list_info"})
        self.fictionList.append({
          'id': index,
          'name': info.find('h2').get_text(),
          'author': info.find('span', attrs={"class": "l1"}).find('a').get_text(),
          'state': info.find('span', attrs={"class": "l3"}).find('i').get_text(),
          'link': 'https://www.ixdzs.com' + info.find('h2').find('a').get('href')
        })

      self.addList()

    # 增加列表
    def addList(self):
      self.delList()
      for l in self.fictionList:
        self.tree.insert("", "end", values=(l['id'], l['name'], l['author'], l['state']))    # 插入数据，  
      self.tree.pack()

    # 清空列表
    def delList(self):
      x = self.tree.get_children()
      for item in x:
        self.tree.delete(item)

    # 获取选中的小说编号
    def select(self):
      if len(self.tree.selection()) == 0:
        messagebox.showinfo('提示信息','请选择小说！')
        self.id = 9999         # 未选择小说
        return 

      for item in self.tree.selection():
        item_text = self.tree.item(item,"values")
        self.id = int(item_text[0])

    # 获取小说页面
    def getSelectedPage(self):
      
      self.select()
      if self.id == 9999:
        return 'null'

      url = self.fictionList[self.id]['link']
      f = urllib.request.urlopen(url)
      result = f.read().decode('utf-8')
      return BeautifulSoup(result, 'html.parser')

    # 获取下载地址
    def getDownloadUrl(self):
      
      soup = self.getSelectedPage()

      if soup == 'null':
        return

      downloadUrl = 'https://www.ixdzs.com/' + soup.find('div', attrs={'class': 'd_lk'}).find('a').get('href')  # 下载链接
      self.downloadFiction(downloadUrl, self.fictionList[self.id]['name'])
    
    # 下载小说
    def downloadFiction(self, url, fictionName):
      
      name = fictionName + '.zip'
      f = request.urlopen(url)
      d = f.read()
      saveDir = os.getcwd().replace('\\', "/") + '/小说/'

      if os.path.isdir(saveDir):    # 若无music文件夹则创建
        pass
      else:
        os.mkdir(saveDir)

      with open(saveDir + name, 'wb') as code:    
        code.write(d)
      messagebox.showinfo('下载成功','成功下载到' + saveDir + '目录中！')

    # 在线阅读
    def onlineRead(self):
      soup = self.getSelectedPage()

      if soup == 'null':
        return
        
      onlineUrl = soup.find_all('a', attrs={'class': 'd_ot'})[1].get('href')
      webbrowser.open(onlineUrl)

if __name__ == '__main__':
  app = Application()
 
