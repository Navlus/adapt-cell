import random
import threading
import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import *


class Creature:
    def __init__(self, f, stx, sty, exx, exy,d, cr_id):

        #Свойства существа
        
        self.fitness=f#суммарная живучесть. Устанавливается при запуске шага симуляции и может увеличиваться во время её
        self.id=cr_id#номер существа. Позлоляет суммировать живучесть от разных копий существа, созданных во время симуляции
        self.coord=(stx, sty)#координаты текущего суества во время шага симуляции.При инициализации - стартовые значения
        self.exit=(exx, exy)#координаты выхода
        self.gene=d.copy()#гены. Ключ - координата

    def copy(self):
        return Creature(self.fitness, self.coord[0], self.coord[1], self.exit[0], self.exit[1], self.gene.copy(),0)

class Trace:#Трассировка движения объекта
    #x,y - координаты метки на шаге self.met
    #child - массив, в котором лежат номера дочерних к данному элементов в массиве трассировок существа в Управляющем классе
    #если существо не делится, child пуст; иначе там указываются номера
    def __init__(self):
        self.d=[]
        self.len=0
        self.met=-1

    def Len(self):
        return self.len

    def addElem(self, x, y, child=()):
        self.d.append((x,y,child))
        self.len+=1

    def TakeElem(self):
        self.met+=1
        return self.d[self.met]

class MainWindow:
    def __init__(self, h, w, n1=20, n2=20):#n1 - кол-во клеток в теле существа в ширину n2  - в высоту. h, w - высота и длина всего окна (в процентах)
        self.height=h#высота в процентах
        self.width=w#ширина окна в процентах
        self.gui=QApplication(sys.argv)
        self.window=QWidget()#окно
        #self.window.resize(w, h)
        self.window.setWindowTitle('adapt cell')
        self.result={}#ссылка на ячейки, в которую запишется результат существа

        #if (self.width=1 and self.height=1):
    

        screen=QDesktopWidget().availableGeometry()

        self.window.resize(screen.width()*self.width-15, screen.height()*self.height-15)#становка размера окна
        #print('w=  '+str(screen.width()*self.width-15)+'h=  '+str(screen.height()*self.height-15))
        if self.window.height()<300 or self.window.width()<880:#обработка некорректного размера экрана
            self.window.resize(100,20)
            l=QLabel('Этот размер экрана не поддерживается')
            l1=QVBoxLayout(self.window)
            l1.addWidget(l)
            return
        
        #qr = self.window.frameGeometry()#ставим окно в центр
        #cp = screen.center()
        #qr.moveCenter(cp)
        #self.window.move(qr.topLeft())

        self.vert=QVBoxLayout()
        self.gor=QHBoxLayout()

        lf=QFrame()
        lf.setStyleSheet("QWidget { background-color: '#FFFFE0' }")
        lff=QHBoxLayout()
        self.lFrame=QVBoxLayout()
        self.lFrame.setContentsMargins(0,0,0,0)
        lff.addLayout(self.lFrame)
        lff.addStretch(1)
        lf.setLayout(lff)
        
        rf=QFrame()
        rf.setStyleSheet("QWidget { background-color: '#FFFFE0' }")
        rff=QHBoxLayout()
        self.rFrame=QVBoxLayout()
        self.rFrame.setContentsMargins(0,0,0,0)
        rff.addStretch(1)
        rff.addLayout(self.rFrame)
        rf.setLayout(rff)

        c=QHBoxLayout()
        w=QWidget()
        self.body=QTableWidget(n1,n2)#тут лежит тело существа

        for n in range(n1):#делаем ячейки таблицы неизменяемыми пользователем
            for m in range(n2):
                item=QTableWidgetItem()
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.body.setItem(n, m, item)
        
        self.body.verticalHeader().hide()#прячем заглавие таблицы
        self.body.horizontalHeader().hide()
        
        c.addWidget(self.body)
        w.setLayout(c)

        tableWidgetHeight=int(0.8*self.window.height()/n2)
        tableWidgetWidth=int(0.3*self.window.width()/n1)
        w.setFixedSize((tableWidgetWidth+1)*n1+5, (tableWidgetHeight+1)*n2+5)#задаём размер таблицы
        
        for n in range(n1):#устанавливаем размеры клеток
            self.body.setColumnWidth(n, tableWidgetWidth)

        for n in range(n2):
            self.body.setRowHeight(n, tableWidgetHeight)
            
        #dw=s-w.geometry().left()
        #if dw!=0:
        #   w.setFixedSize(w.width()-dw, w.height())
            

        p=QHBoxLayout()
        self.panel=QWidget()#тут лежит панель управления
        self.panel.setMinimumHeight(self.window.height()*0.1)
        self.panel.setMinimumWidth(self.window.width()-20)
        self.panel.setStyleSheet("QWidget { background-color: '#FFFFE0' }")

        uu=QHBoxLayout(self.panel)
        uu.addStretch(1)

        but1=QPushButton('Start')
        uu.addWidget(but1)

        falseButtonStart=QWidget()
        falseButtonStop=QWidget()########переопределить
        but2=QPushButton('Stop')
        uu.addWidget(but2)
        #but2.setStyleSheet("QBushButton { background-color: '#B0C4DE' }")
        #but2.hide()
        
        but3=QPushButton('Graph')
        uu.addWidget(but3)
        
        uu.addStretch(1)




        
        p.addWidget(self.panel)
        
        self.gor.addWidget(lf)
        self.gor.addWidget(w)
        self.gor.addWidget(rf)
        
        self.vert.addLayout(self.gor)
        self.vert.addStretch(10)
        self.vert.addLayout(p)
        self.window.setLayout(self.vert)
        
        
        
        
        
    
    def Print_Creature(self, creature, frame):#creature - существо,чей ген рисуем, frame - layout, куда добавится получившаяся таблица
        dic=creature.gene.copy()
        
        gen=QTableWidget(3, len(dic)+2)#таблица гена
        gen.setContentsMargins(0,0,0,0)
        gen.verticalHeader().hide()
        gen.horizontalHeader().hide()
        gen.setVerticalScrollBarPolicy(1)
        gen.setHorizontalScrollBarPolicy(1)
        
        #таблица gen лежит в layout'е boxL, а тот - в widget'е box, которому уже можно задать размеры.
        
        font=QFont("Helvetica", 3)#шрифт, которым пишется ген
        
        box=QWidget()

        h=(self.window.height()*0.8-15)/10
        box.setFixedHeight(h)
        w=int((self.window.width()*0.35-15-35)/len(dic))
        box.setFixedWidth(w*len(dic)+35+15)
        box.setFont(QFont("Helvetica", 3))
        box.setToolTip('This is a QWidget widget')
        box.setContentsMargins(1,1,1,1)
        
        
        boxL=QHBoxLayout()
        boxL.setContentsMargins(0,0,0,0)
        #########################################################################
        gen.setRowHeight(0, (h-6)/3+1)
        gen.setRowHeight(1, (h-6)/3+1)
        gen.setRowHeight(2, (h-6)/3+1)

        iterator=0#счётчик, в котором лежит номер текущего столбца
        
        for n in range(len(dic)):
            item=dic.popitem()
            gen.setColumnWidth(iterator, w)
            TableWidgetItem=QTableWidgetItem(str(item[0][0]))
            #TableWidgetItem.setContentsMargins(0,0,0,0)
            
            TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
            
            TableWidgetItem.setFont(font)
            gen.setItem(0, iterator, TableWidgetItem)

            TableWidgetItem=QTableWidgetItem(str(item[0][1]))

            TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
            
            TableWidgetItem.setFont(font)
            gen.setItem(1, iterator, TableWidgetItem)

            TableWidgetItem=QTableWidgetItem(item[1])

            TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
            
            TableWidgetItem.setFont(font)
            gen.setItem(2, iterator, TableWidgetItem)

            iterator+=1

        
        gen.setColumnWidth(iterator, 35)
        gen.setColumnWidth(iterator+1, 15)
        
        TableWidgetItem=QTableWidgetItem('id=')
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        TableWidgetItem.setFont(font)
        gen.setItem(0, iterator, TableWidgetItem)

        TableWidgetItem=QTableWidgetItem('fitness=')
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        TableWidgetItem.setFont(font)
        gen.setItem(2, iterator, TableWidgetItem)

        TableWidgetItem=QTableWidgetItem(str(creature.id))
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        TableWidgetItem.setFont(font)
        gen.setItem(0, iterator+1, TableWidgetItem)

        TableWidgetItem=QTableWidgetItem('')
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        gen.setItem(1, iterator, TableWidgetItem)
        TableWidgetItem=QTableWidgetItem('')
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        gen.setItem(1, iterator+1, TableWidgetItem)
        TableWidgetItem=QTableWidgetItem('')
        TableWidgetItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)#делаем ячейку неизменяемой
        gen.setItem(2, iterator+1, TableWidgetItem)
        
        boxL.addWidget(gen)
        box.setLayout(boxL)
        frame.addWidget(box)

        self.result[creature.id]=gen
        
        
    def Print_Creatures(self, creatures):
        for cre in creatures:
            if cre[0].id<10:
                f=self.lFrame
            else:
                f=self.rFrame

            self.Print_Creature(cre[0], f)

    def Print_Body(self, creature):
        gene=creature.gene.copy()
        font=QFont("Helvetica", 6)
        
        for n in range(len(gene)):
            item=gene.popitem()
            x=item[0][1]
            y=item[0][0]
            ch=item[1]

            TableWidgetItem=self.body.item(x, y)
            TableWidgetItem.setFont(font)
            TableWidgetItem.setText(ch)
            
            
    def Print_Result(self, cre_id, res):
        #st=QString('54')
        TableWidgetItem=self.result[cre_id].item(2, self.result[cre_id].columnCount()-1)
        TableWidgetItem.setText(str(res))
        TableWidgetItem.setFont(QFont("Helvetica", 5))
        self.result[cre_id].setItem(2, self.result[cre_id].columnCount()-1, TableWidgetItem)
        
class Action:
    def __init__(self):

        #Свойства симуляции
        
        self.number_creatures=20#Кол-во отбираемых существ
        self.start_gene_ln=20#Стартовая длина генофонда
        self.start_stav_fitness=21#Стартовое значение здоровья
        self.gor=19#Ширина поля
        self.vert=19#Длина поля
        self.result=dict()#Результаты для существ. Ключ - номер существа, общий для всех копий в пределах шага симуляции.
        self.Creature_pool=[]#массив, в котором лежат массивы, в которых лежат существа
        self.mas_Trace=[]#массив,в котором лежат массивы трассировок существ

        for i in range(21):
            self.mas_Trace.append([])

    def Check(self):#Дымовой тест создания пула случайных существ
        i=0
        for c in self.Creature_pool:
            for v in c:
                print(str(i)+'  '+str(v.gene))
            i+=1

            
    def Random_Simbol(self):#возвращает один из четырёх символов случайно
        ch=int(random.random()*3.99)
        if ch==0:
            ch='L'
        elif ch==1:
            ch='R'
        elif ch==2:
            ch='A'
        elif ch==3:
            ch='M'
        return ch

    def Random_Number(self, n):#возвращает случайное число в границах от 0 до n
        num=int(random.random()*(n-0.01))
        return num
    
    def Make_Random_Creatures_Pool(self,startX,startY,exitX,exitY):#Создание пула случайных существ при запуске симуляции
        self.Creature_pool=[]
        num=0
        for k in range(self.number_creatures):
            d=dict()
            
            for t  in range(self.start_gene_ln):
                ch=self.Random_Simbol()
                d[self.Random_Number(self.gor), self.Random_Number(self.vert)]=ch#в словарь добавляем пару, где ключ - список из двух случайных чисел от 0 до 20, а значение - случайная буква

            self.Creature_pool.append([Creature(self.start_stav_fitness, startX,startY,exitX,exitY, d,num)])
            num+=1
        return


    def Make_Offspring(self, creature_p):#создаёт потомка существа
        creature=creature_p.copy()
        t=self.Random_Number(5)
        if t==0:#удаление гена
            d=self.Random_Number(len(creature.gene))
            del creature.gene[list(creature.gene.keys())[d]]
        elif t==1:#изменение символа в гене
            d=self.Random_Number(len(creature.gene))
            creature.gene[list(creature.gene.keys())[d]]=self.Random_Simbol()
        elif t==2:#изменение второй координаты в гене 
            d=self.Random_Number(len(creature.gene))
            creature.gene[(list(creature.gene.keys())[d][0], self.Random_Number(self.vert))]=creature.gene[list(creature.gene.keys())[d]]
            del creature.gene[list(creature.gene.keys())[d]]
        elif t==3:#изменение первой координаты в гене
            d=self.Random_Number(len(creature.gene))
            creature.gene[self.Random_Number(self.gor), list(creature.gene.keys())[d][1]]=creature.gene[list(creature.gene.keys())[d]]
            del creature.gene[list(creature.gene.keys())[d]]
        elif t==4:#добавление символа
            creature.gene[self.Random_Number(self.gor), self.Random_Number(self.vert)]=self.Random_Simbol()
        return creature

            
    def Del_Creature(self, creature):
        self.Creature_pool.remove(creature)
                

    def Move(self, creature, nT):#функция шаг
        if not(creature.id in self.result):#если существо ещё не учавствовало в симуляции, инициализируем поле 0. (существа с M могут вызываться несколькими функциями и их результаты суммируются)
            self.result[creature.id]=0
            self.mas_Trace[creature.id].append(Trace())#создаём объект трассировок
        
        if creature.coord[0]==creature.exit[0] and creature.coord[1]==creature.exit[1]:#условие прибавления очков
            self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
            self.result[creature.id]+=creature.fitness
            return
            
        if creature.coord[0]!=creature.exit[0] and creature.coord[1]==creature.exit[1]:#выбыло
            self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
            return

        if creature.coord in creature.gene:#если координате существа соответствует какая-либо буква в геноме, то...
            
            if creature.gene[creature.coord]=='L' and creature.coord[0]!=self.gor:
                self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
                creature.coord=(creature.coord[0]+1, creature.coord[1])
                creature.coord=(creature.coord[0], creature.coord[1]+1)
                self.Move(creature,nT)
                return

            if creature.gene[creature.coord]=='R' and creature.coord[0]!=0:
                self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
                creature.coord=(creature.coord[0]-1, creature.coord[1])
                creature.coord=(creature.coord[0], creature.coord[1]+1)
                self.Move(creature,nT)
                return

            if creature.gene[creature.coord]=='A':
                self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
                creature.fitness+=1
                creature.coord=(creature.coord[0], creature.coord[1]+1)
                self.Move(creature,nT)
                return

            if creature.gene[creature.coord]=='M':
                if creature.coord[0]==self.gor:
                    self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1], len(self.mas_Trace[creature.id]))#трассируем прохождение клетки
                    self.mas_Trace[creature.id].append(Trace())#Добавляем существу ещё один массив трассировок - для дополнительного элемента
                    cr=Creature(creature.fitness, creature.coord[0]-1, creature.coord[1]+1, creature.exit[0], creature.exit[1], creature.gene, creature.id)
                    #self.Creature_pool[creature.id].append(cr)
                    creature.coord=(creature.coord[0], creature.coord[1]+1)
                    self.Move(creature,nT)
                    self.Move(cr,len(self.mas_Trace[creature.id])-1)
                    return
                
                elif creature.coord[0]==0:
                    self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1], len(self.mas_Trace[creature.id]))#трассируем прохождение клетки
                    self.mas_Trace[creature.id].append(Trace())#Добавляем существу ещё один массив трассировок - для дополнительного элемента
                    cr=Creature(creature.fitness, creature.coord[0]+1, creature.coord[1]+1, creature.exit[0], creature.exit[1], creature.gene, creature.id)
                    #self.Creature_pool.append(cr)
                    creature.coord=(creature.coord[0], creature.coord[1]-1)
                    self.Move(creature,nT)
                    self.Move(cr,len(self.mas_Trace[creature.id])+1)
                    return
                
                else:
                    self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1], len(self.mas_Trace[creature.id]))#трассируем прохождение клетки
                    self.mas_Trace[creature.id].append(Trace())#Добавляем существу ещё один массив трассировок - для дополнительного элемента
                    cr=Creature(creature.fitness, creature.coord[0]-1, creature.coord[1], creature.exit[0], creature.exit[1], creature.gene, creature.id)
                    #self.Creature_pool.append(cr)
                    creature.coord=(creature.coord[0]+1, creature.coord[1])
                    self.Move(creature,nT)
                    self.Move(cr,len(self.mas_Trace[creature.id])-1)
                    return
                
        self.mas_Trace[creature.id][nT].addElem(creature.coord[0], creature.coord[1])#трассируем прохождение клетки
        creature.coord=(creature.coord[0], creature.coord[1]+1)#иначе просто опускаем на 1 клетку
        self.Move(creature, nT)
        return

    def Console_Print_Trace(self):
        for n in self.mas_Trace:
            for k in n:
                for j in range(k.Len()):
                    print(str(k.TakeElem()))

    def Console_Print_Para_Trace(self):
        i=0
        for n in self.mas_Trace:
            for k in range(20):
                for p in n:
                    q=p.TakeElem()
                    if q[1]==k:
                        print(str(q))
                    else:
                        p.met-=1
                

ex=Action()
ex.Make_Random_Creatures_Pool(11,0,10,19)

m=MainWindow(0.9, 0.9)
m.window.show()
m.Print_Creatures(ex.Creature_pool)
m.Print_Body(ex.Creature_pool[0][0])
sys.exit(m.gui.exec_())
#ex.Move(ex.Creature_pool[0][0],0)
#ex.Console_Print_Para_Trace()
#print('Result = '+str(ex.result[ex.Creature_pool[0][0].id]))
