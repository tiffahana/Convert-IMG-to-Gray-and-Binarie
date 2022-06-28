import sys
from PyQt5 import QtGui, QtWidgets, uic, QtCore
import cv2
import numpy as np
import copy

class Ventana(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = uic.loadUi('Interfaz.ui')#Nombre de la interfaz .ui
        self.ui.setWindowIcon(QtGui.QIcon('uoh.jpg')) #Foto del logo superior
        self.ui.show()#al momento de crear el objeto "Ventana", esta se mostrará
        #aqui van las señales a los widgets
        self.ui.abrirfoto.triggered.connect(self.Abrir) 
        self.ui.mostrar.clicked.connect(self.Mostrar) 
        self.ui.Barrita.valueChanged.connect(self.Umbral)
        self.ui.actionCerrar.triggered.connect(self.Cerrar)
        self.ui.aplicar.clicked.connect(self.Aplicar)
        self.ui.deshacer.clicked.connect(self.Deshacer)
        self.ui.mostrar.clicked.connect(self.Histograma)
        self.ui.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui.dateTimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.widget_plot = self.ui.visor_2.addPlot()
        self.pen = [255, 0, 0]
        self.widget_plot.setLabel(axis = 'bottom', text='Intensidad')
        self.widget_plot.setLabel(axis = 'left', text='Cantidad de píxel')
        self.curve = self.widget_plot.plot([], pen=self.pen)
        self.ui.setFixedSize(1000,400)
    #aqui van los metodos/funciones a las que las señales son enlazadas.
    
    def Tiempo(self):
        dt = self.ui.dateTimeEdit.dateTime() #Con el módulo dateTime podemos manipular fechas y horas
        dt_string = dt.toString(self.ui.dateTimeEdit.displayFormat()) #Lo pasamos a string para que se le pueda asignar el formato de la señal
        self.ui.textEdit.setText(dt_string) #Cambiamos el texto con la fecha y hora actual
        
    def Abrir(self):
        path,_= QtWidgets.QFileDialog.getOpenFileName(self, 'Abrir archivo', '.') #Con path podemos abrir un archivo de nuestro pc
        self.img = cv2.imread(path, 3) #Leemos la imagen
        self.img = cv2.resize(self.img, (400,300)) #Reajustamos el tamaño de la imagen
        self.rgb =  cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB ) #La convertimos en RGB
        R, G, B = self.rgb[:,:,0], self.rgb[:,:,1], self.rgb[:,:,2] #Creamos una matriz 3 matrices para cada canal de 3x3
        self.gray = (0.299*R)+(0.587*G)+(0.114*B) #Multiplicamos en la fórmula para pasarla a gris
        self.gray = self.gray.astype(np.uint8)
        self.height, self.width, self.channel = self.rgb.shape
        a = self.gray.shape[0] #Creamos un array donde a son las filas
        b = self.gray.shape[1] #Creamos un array donde b son las columnas
        TH = 100 
        self.bw = self.gray.copy() #Realizamos una copia de la imagen gris
        for i in range(a): #Ciclos para recorrer la matriz de la imagen gris
            for j in range(b):
                pixel = self.bw[i][j]  
                if pixel > TH: #Formula para escribir la matriz binaria
                    self.bw[i][j] = 255
                else:
                    self.bw[i][j] = 0
        self.gray_auxmedia = copy.deepcopy(self.gray) #Copias para después aplicar filtros
        self.gray_auxmediana = copy.deepcopy(self.gray)

    def Mostrar(self): #Función para mostrar cada imagen según el comboBox
        if self.ui.comboBox.currentText() == 'RGB': 
            qim = QtGui.QImage(self.rgb.data, self.width, self.height, 3*self.width, QtGui.QImage.Format_RGB888)
        elif self.ui.comboBox.currentText() == 'Gris': 
            #print(self.gray)
            qim = QtGui.QImage(self.gray.data, self.width, self.height, 1*self.width, QtGui.QImage.Format_Indexed8)
        else:
            #print(self.bw)
            qim = QtGui.QImage(self.bw.data, self.width, self.height, 1*self.width, QtGui.QImage.Format_Indexed8) 
        pix = QtGui.QPixmap.fromImage(qim)
        self.ui.visor.setPixmap(pix)      
        
    def Umbral(self): #Función para el QSlider
        valorumbral= self.ui.Barrita.value() #Conectamos el valor de la barrita a la variable
        self.th = self.ui.Barrita.value() #Conectamos el valor de la barrita al th
        ret, self.bw = cv2.threshold(self.gray, self.th, 255, cv2.THRESH_BINARY)
        self.ui.umbral.setText(str(valorumbral))
 
        
    def Cerrar(self): #Función para cerrar la aplicación
        self.ui.close()
        
    def Aplicar(self): #Función para aplicar los filtros
        if self.ui.radioButton1.isChecked():
            self.gray_auxmedia = cv2.resize(self.gray, (400,300)) #Se reajusta la copia de la imagen al mismo tamaño de la imagen original
            self.gray_auxmedia = cv2.blur(self.gray,(3,3)) #Le aplicamos el filtro a la copia
            qim = QtGui.QImage(self.gray_auxmedia.data, self.width, self.height, 1*self.width, QtGui.QImage.Format_Indexed8) #Procesa la nueva imagen
        elif self.ui.radioButton2.isChecked():
            self.gray_auxmediana = cv2.resize(self.gray_auxmediana, (400,300)) #Se reajusta la copia de la imagen al mismo tamaño de la imagen original
            self.gray_auxmediana = cv2.medianBlur(self.gray_auxmediana,3) #Le aplicamos el filtro a la copia
            qim = QtGui.QImage(self.gray_auxmediana.data, self.width, self.height, 1*self.width, QtGui.QImage.Format_Indexed8) #Procesa la nueva imagen
        pix = QtGui.QPixmap.fromImage(qim)
        self.ui.visor.setPixmap(pix)    
    
    def Deshacer(self): #Función para quitar los filtros aplicados 
        qim = QtGui.QImage(self.gray.data, self.width, self.height, 1*self.width, QtGui.QImage.Format_Indexed8) #Ocupamos lo de función Mostrar
        pix = QtGui.QPixmap.fromImage(qim)
        self.ui.visor.setPixmap(pix)
    
    def Histograma(self): #Función para crear el histograma
        if self.ui.comboBox.currentText() == 'Binario': #Para crearlo en binario
            y,x = np.histogram(self.bw.ravel(),bins=255) #Librería numpy para hacer el histograma
            x=x[0:-1]
            self.curve.setData(x, y, pen = self.pen)
        elif self.ui.comboBox.currentText() == 'Gris': #Para crearlo en gris
            y,x = np.histogram(self.gray.ravel(),bins=255) #Librería numpy para hacer el histograma
            x=x[0:-1]
            self.curve.setData(x, y, pen = self.pen)
        

app = QtWidgets.QApplication(sys.argv)
ventana = Ventana()
sys.exit(app.exec())