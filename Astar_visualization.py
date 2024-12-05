# Please do 'pip install PyQt5'
# Reference: https://blog.csdn.net/dujuancao11/article/details/109749219
import time,sys
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QMainWindow,QGridLayout
from PyQt5.QtWidgets import QTextEdit,QLineEdit,QWidget, QMessageBox
from PyQt5.QtWidgets import QApplication,QLabel,QPushButton,QHBoxLayout,QVBoxLayout
from PyQt5.QtCore import Qt,QTimer,QObject,pyqtSignal,QBasicTimer
from PyQt5.QtGui import QPainter, QColor, QFont,QPen
import json
class config:
	WIDTH=20# columns of map
	HEIGHT=20# rows of map
	blockLength=30# Length of each block when drawing the grid
class point:
	_list=[]# List to store all point instances
	_tag=True# Mark if the newly created instance is unique
	def __new__(cls,x,y):
		# Ensure there is only one instance for each unique coordinate
		for i in point._list:
			if i.x==x and i.y==y:
				point._tag=False
				return i
		nt=super(point,cls).__new__(cls)
		point._list.append(nt)
		return nt
	def __init__(self,x,y):
		if point._tag:
			self.x=x
			self.y=y
			self.parent=None
			self.F=0# Total cost (F = G + H)
			self.G=0# Cost from start to current node
			self.cost=0# Cost from parent to current node
		else:
			point._tag=True
	@classmethod
	def clear(cls):
		# The clear(), after each search, clears all point data so that
        # the point data will not conflict when the next search is performed.
		point._list=[]
	def __eq__(self,T):
		if type(self)==type(T):
			return (self.x,self.y)==(T.x,T.y)
		else:
			return False
	def __str__(self):
		return'(%d,%d)[F=%d,G=%d,cost=%d][parent:(%s)]'%(self.x,self.y,self.F,self.G,self.cost,
												   str((self.parent.x,self.parent.y))
												   if self.parent!=None else 'null')
class A_Search:
	def __init__(self,arg_start,arg_end,arg_map):
		self.start=arg_start# Store the start point of this search
		self.end=arg_end# Store the destination point of this search
		self.Map=arg_map# A two-dimensional array of map references for this search
		self.open=[]# Open list: stores nodes to be explored
		self.close=[]# Close list: stores explored nodes
		self.result=[]# Store the final path
		self.count=0# Number of nodes explored
		self.useTime=0# Time spent on search
		self.open.append(arg_start)
	def cal_F(self,loc):
		print('Calculation values: ',loc)
		G=loc.parent.G+loc.cost
		H=self.getEstimate(loc)
		F=G+H
		print("F=%d G=%d H=%d"%(F,G,H))
		return {'G':G,'H':H,'F':F}
	def F_Min(self):
		# Search for the point with the smallest F value
        # in the open list and return it, and determine whether
        # the open list is empty, which means that the search fails
		if len(self.open)<=0:
			return None
		t=self.open[0]
		for i in self.open:
			if i.F<t.F:
				t=i
		return t
	def getAroundPoint(self,loc):
		# Gets all passable points around the specified point
        # and assigns their corresponding movement consumption
		l=[(loc.x,loc.y+1,10),(loc.x+1,loc.y+1,14),(loc.x+1,loc.y,10),(loc.x+1,loc.y-1,14),
	        (loc.x,loc.y-1,10),(loc.x-1,loc.y-1,14),(loc.x-1,loc.y,10),(loc.x-1,loc.y+1,14)]
		for i in l[::-1]:
			if i[0]<0 or i[0]>=config.HEIGHT or i[1]<0 or i[1]>=config.WIDTH:
				l.remove(i)
		nl=[]
		for i in l:
			if self.Map[i[0]][i[1]]==0:
				nt=point(i[0],i[1])
				nt.cost=i[2]
				nl.append(nt)
		return nl
 
	def addToOpen(self,l,parent):
		# The passable points around the point of this judgment are added
        # to the OPEN list, if this point is already in the OPEN list then
        # it is judged, if the F value obtained from this path is smaller than
        # the previous F value, then its parent node is updated to the point
        # of this judgment, and the F and G values are updated at the same time
		for i in l:
			if i not in self.open:
				if i not in self.close:
					i.parent=parent
					self.open.append(i)
					r=self.cal_F(i)
					i.G=r['G']
					i.F=r['F']
			else:
				tf=i.parent
				i.parent=parent
				r=self.cal_F(i)
				if i.F>r['F']:
					i.G=r['G']
					i.F=r['F']
					# i.parent=parent
				else:
					i.parent=tf
	def getEstimate(self,loc):
		# H: estimated cost to move from point loc to end point
		return (abs(loc.x-self.end.x)+abs(loc.y-self.end.y))*10
	def DisplayPath(self):
		print('Time spent on search:%.2fs. Iterations:%d, Path length:%d'%(self.useTime,self.count,len(self.result)))
		if self.result!=None:
			for i in self.result:
				self.Map[i.x][i.y]=8
			for i in self.Map:
				for j in i:
					if j==0:
						print('%s'%'□',end='')
					elif j==1:
						print('%s'%'▽',end='')
					elif j==8:
						print('%s'%'★',end='')
				print('')
		else:
			print('Search failed, no passable path')
	def process(self):
		while True:
			self.count+=1
			#First get the point with the lowest F value in the open list tar
			tar=self.F_Min()
			if tar==None:
				self.result=None
				self.count=-1
				break
			else:
				# Get the list of available points around tar, aroundP
				aroundP=self.getAroundPoint(tar)
				# add aoundP to the open list and update the F value and set the parent node
				self.addToOpen(aroundP,tar)
				# remove tar from the open list
				self.open.remove(tar)
				# Iterate the node tar into the close list
				self.close.append(tar)
				# Determine if the end point is already in the open list
				if self.end in self.open:
					e=self.end
					self.result.append(e)
					while True:
						e=e.parent
						if e==None:
							break
						self.result.append(e)
					yield (tar,self.open,self.close)
					break
 
			yield (tar,self.open,self.close)
			time.sleep(0.05)#stop
		#self.useTime=time2-time1
class GameBoard(QMainWindow):#pyqt5 used for visualization
	def __init__(self):
		print('Initializing map...')
		self.Map=[]
		for i in range(config.HEIGHT):
			col=[]
			for j in range(config.WIDTH):
				col.append(0)
			self.Map.append(col)
		self.startPoint=None
		self.endPoint=None
		self.search=None
		self.centerTimer=None
		self.yi=None
		self.special=None
		self.displayFlush=False
		super().__init__()
		print('Initializing UI...')
		self.initUI()
	def initUI(self):
		# Begin initializing UI controls
		# Create UI controls
		self.label_tips = QLabel("<p style='color:green'>Instructions:</p> Right-click a cell to set it as the start point, left-click a cell to set/remove it as a wall.\n<p style='color:green'>Color Explanation:</p>\nYellow is the start, green is the end, black is wall, red is the open list for nodes to be searched, gray is the closed list for searched nodes, and blue is the current path found.", self)
		self.label_display=QLabel("",self)
		self.button_start=QPushButton("Start Search",self)
		self.button_clearSE=QPushButton("Reset Start/End Points",self)
		self.button_clearWall=QPushButton("Clear Map Walls",self)
		self.button_saveMap=QPushButton("Save Map",self)
		self.button_loadMap=QPushButton("Load Map",self)
 
 
		# Set control properties
		self.label_tips.setWordWrap(True)
		self.label_display.setWordWrap(True)
		# Set control styles
		self.label_display.setStyleSheet("border:1px solid black")
		self.label_display.setAlignment(Qt.AlignLeft)
		self.label_display.setAlignment(Qt.AlignTop)
		# Set control size and position
		self.label_tips.resize(250,200)
		self.button_start.resize(180, 30)
		self.button_clearSE.resize(180, 30)
		self.button_clearWall.resize(180, 30)
		self.button_saveMap.resize(90,30)
		self.button_loadMap.resize(90,30)
		self.label_display.resize(200,300)
 
		self.label_tips.move(100+(config.WIDTH-1)*config.blockLength,0)
		self.label_display.move(100+(config.WIDTH-1)*config.blockLength,400)
		self.button_start.move(100+(config.WIDTH-1)*config.blockLength,200)
		self.button_clearSE.move(100+(config.WIDTH-1)*config.blockLength,250)
		self.button_clearWall.move(100+(config.WIDTH-1)*config.blockLength,300)
		self.button_saveMap.move(100+(config.WIDTH-1)*config.blockLength,350)
		self.button_loadMap.move(200+(config.WIDTH-1)*config.blockLength,350)
		# Bind events to controls
		self.button_start.clicked.connect(self.button_StartEvent)
		self.button_clearSE.clicked.connect(self.button_Clear)
		self.button_clearWall.clicked.connect(self.button_Clear)
		self.button_saveMap.clicked.connect(self.button_SaveMap)
		self.button_loadMap.clicked.connect(self.button_LoadMap)
		# UI initialization complete
		self.setGeometry(0, 0, 150+(config.WIDTH*config.blockLength-config.blockLength)+200, 150+(config.HEIGHT*config.blockLength-config.blockLength))
		self.setMinimumSize(150+(config.WIDTH*config.blockLength-config.blockLength)+200, 150+(config.HEIGHT*config.blockLength-config.blockLength))
		self.setMaximumSize(150+(config.WIDTH*config.blockLength-config.blockLength)+200, 150+(config.HEIGHT*config.blockLength-config.blockLength))
		self.setWindowTitle('A* Search')
		self.show()
	def addDisplayText(self,text):
		if self.displayFlush:
			self.label_display.setText(text+'\n')
			self.displayFlush=False
		else:
			self.label_display.setText(self.label_display.text()+text+'\n')
	def mousePressEvent(self,event):
		x,y=event.x()-50,event.y()-50
		x=x//config.blockLength
		y=y//config.blockLength
		if x>=0 and x<config.WIDTH and y>=0 and y<config.HEIGHT:
			if event.button()==Qt.LeftButton:
				if (x,y)!=self.startPoint and (x,y)!=self.endPoint:
					self.Map[y][x]=(1 if self.Map[y][x]==0 else 0)
			if event.button()==Qt.RightButton:
				if self.Map[y][x]==0:
					if self.startPoint==None:
						self.startPoint=(x,y)
						self.addDisplayText('Added a start point:(%d,%d)'%(x,y))
					elif self.endPoint==None and self.startPoint!=(x,y):
						self.endPoint=(x,y)
						self.addDisplayText('Added an end point:(%d,%d)'%(x,y))
			self.repaint()
	def button_StartEvent(self):
		sender=self.sender()
		print(sender)
		if self.startPoint!=None and self.endPoint!=None:
			if self.centerTimer==None:
				self.centerTimer=QBasicTimer()
			self.button_start.setEnabled(False)
			self.button_clearSE.setEnabled(False)
			self.button_clearWall.setEnabled(False)
			self.centerTimer.start(200,self)
			self.search=A_Search(point(self.startPoint[1],self.startPoint[0]),point(self.endPoint[1],self.endPoint[0]),self.Map)
			self.yi=self.search.process()
			self.addDisplayText('Starting search')
	def button_SaveMap(self):
		with open('map.txt','w') as f:
			f.write(json.dumps(self.Map))
			self.addDisplayText('Map saved successfully-->map.txt')
		# else:
			# self.addDisplayText('Map saved failed')
	def button_LoadMap(self):
		try:
			with open('map.txt','r') as f:
				self.Map=json.loads(f.read())
				config.HEIGHT=len(self.Map)
				config.WIDTH=len(self.Map[0])
				self.addDisplayText('Map loaded successfully')
				self.repaint()
		except Exception as e:
			print('Failed',e,type(e))
			if type(e)==FileNotFoundError:
				self.addDisplayText('Map loading failed: Map file does not exist')
			elif type(e)==json.decoder.JSONDecodeError:
				self.addDisplayText('Map loading failed: Invalid map file')
	def button_Clear(self):
		sender=self.sender()
		print(self.button_clearSE,type(self.button_clearSE))
		if sender==self.button_clearSE:
			self.startPoint=None
			self.endPoint=None
			self.repaint()
			self.addDisplayText('Cleared start/end points')
		elif sender==self.button_clearWall:
			for i in range(len(self.Map)):
				for j in range(len(self.Map[i])):
					self.Map[i][j]=0
			self.repaint()
			self.addDisplayText('Cleared all walls')
	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		self.drawBoard(event,qp)
		qp.end()
	def drawBoard(self, event, qp):
		self.drawMap(qp)
	def drawMap(self,qp):
		# Redraw each time the map changes
		time1=time.time()
		if self.search!=None:
			if self.special!=None:
				e=self.special[0]
				path=[e]
				while True:
					e=e.parent
					if e!=None:
						path.append(e)
					else:
						break
			else:
				path=None
			pen=QPen(QColor(0,0,0),1,Qt.SolidLine)
			qp.setPen(pen)
			for i in range(len(self.Map)):
				for j in range(len(self.Map[i])):
					wordTag=False
					if i==self.search.start.x and j==self.search.start.y:
						qp.setBrush(QColor(255,255,0))
					elif i==self.search.end.x and j==self.search.end.y:
						qp.setBrush(QColor(100,200,50))
					else:
						if self.Map[i][j]==0:
							tagx=True
							if path:
								for k in path:
									if k.x==i and k.y==j:
										tagx=False
										qp.setBrush(QColor(0,100,255))
							if tagx:
								if self.special!=None:
									if i==self.special[0].x and j==self.special[0].y:
										qp.setBrush(QColor(0,255,0))
									else:
										tag=True
										for k in self.special[1]:
											if k.x==i and k.y==j:
												tag=False
												wordTag=True
												word=str(k.F)
 
												qp.setBrush(QColor(150,0,0))
												break
											else:
												qp.setBrush(QColor(220,220,220))
										if tag:
											for k in self.special[2]:
												if k.x==i and k.y==j:
													qp.setBrush(QColor(150,150,150))
													break
												else:
													qp.setBrush(QColor(220,220,220))
								else:
									qp.setBrush(QColor(220,220,220))
						elif self.Map[i][j]==1:
							qp.setBrush(QColor(0,0,0))
						else:
							qp.setBrush(QColor(255,0,0))
					qp.drawRect(50+j*config.blockLength,50+i*config.blockLength,config.blockLength,config.blockLength)
					if wordTag:
						qp.setFont(QFont('Helvetica',5,QFont.Thin))
						qp.drawText(50+10+j*config.blockLength,50+10+i*config.blockLength,word)
						wordTag=False
		#time.sleep(20)
		else:
			for i in range(len(self.Map)):
				for j in range(len(self.Map[i])):
					if (j,i)==self.startPoint:
						qp.setBrush(QColor(255,255,0))
					elif (j,i)==self.endPoint:
						qp.setBrush(QColor(100,200,50))
					else:
						if self.Map[i][j]==0:
							qp.setBrush(QColor(220,220,220))
						elif self.Map[i][j]==1:
							qp.setBrush(QColor(0,0,0))
						else:
							qp.setBrush(QColor(255,0,0))
 
					qp.drawRect(50+j*config.blockLength,50+i*config.blockLength,config.blockLength,config.blockLength)
		time2=time.time()
	#time.sleep(20)
		# print('Drawing time: ',time2-time1)
	def timerEvent(self,e):
		try:
			data=next(self.yi)
		except Exception as e:
			self.addDisplayText('Search ended:')
			print('Search ended!')
			if self.search.result==None:
				self.addDisplayText('No feasible path found')
				print('Search ended!')
			else:
				self.addDisplayText('Total number of nodes searched:%d'%self.search.count)
				self.addDisplayText('Final path length:%d'%len(self.search.result))
			self.centerTimer.stop()
			self.search=None
			self.yi=None
			self.special=None
			point.clear()
			self.button_start.setEnabled(True)
			self.button_clearSE.setEnabled(True)
			self.button_clearWall.setEnabled(True)
			self.displayFlush=True
		else:
			self.special=data
			self.repaint()
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = GameBoard()
	sys.exit(app.exec_())
 