# $Id: pbPlot.py 693 2008-01-06 20:54:17Z felder $
import os, pylab, math, imp
from matplotlib.lines import Line2D

__author__ = 'Martin Felder and Frank Sehnke'

class MultilinePlotter:
    """  Basic plotting class build on pylab   
  Implementing by instancing the class with the number of different plots to show.
  Every plot has an id so adding data is done by addData(id, xValue, yValue) of the given data point   
  @todo: Add possibility to stick markers to the plots
  @todo: Some error checking and documentation
  @todo: Derive from this to make classes for trn/tst data plotting with different linestyles
  """
    
    # some nice color definitions for graphs (from colorbrewer.org)
    graphColor = [(0.894117647, 0.101960784, 0.109803922),\
        (0.215686275, 0.494117647, 0.721568627),\
        (0.301960784, 0.68627451, 0.290196078),\
        (0.596078431, 0.305882353, 0.639215686),\
        (1, 0.498039216, 0),\
        (1, 1, 0.2),\
        (0.650980392, 0.337254902, 0.156862745),\
        (0.968627451, 0.505882353, 0.749019608),\
        (0.6, 0.6, 0.6)]
    
    def __init__(self, maxLines = 1, **kwargs):
        """
    @param maxID: Number of Plots to draw and so max ID.
    @var indexList: The x-component of the data points
    @var DataList: The y-component of the data points"""
        self.indexList = []  
        self.dataList = []
        self.Lines = []
        pylab.clf()
        self.Axes = pylab.axes(**kwargs)
        self.nbLines = 0
        self.defaultLineStyle = {}
        self._checkMaxId(maxLines-1)
        self.replot = True           # is the plot still current?
        self.currentID = None
        self.offset = 0              # external references to IDs are modified by this
        
    def setOffset(self, offs):
        """ Set an offset that modifies all subsequent references to line IDs 
    @param offs: The desired offset """
        self.offset = offs
        
    #def createFigure(self, size=[12,8], interactive=True):
        #""" initialize the graphics output window """
        ## FIXME: doesn work, because axes() in the constructor already creates a figure
        #pylab.figure(figsize=size)
        #if interactive: pylab.ion()

    def _checkMaxId(self, id):
        """ Appends additional lines as necessary
    @param id: Lines up to this id are added automatically """
        if id >= self.nbLines:
            for i in range(self.nbLines, id+1):
                # create a new line with corresponding x/y data, and attach it to the plot
                l = Line2D([],[], color=self.graphColor[i % 9], **self.defaultLineStyle)
                self.Lines.append(l)
                self.Axes.add_line(l)
                self.indexList.append([])
                self.dataList.append([])
            self.nbLines=id+1


    def addData(self, id0, x, y):
        """ The given data point or points is appended to the given line. 
    @param id0: The plot ID (counted from 0) the data point(s) belong to.
    @param x: The x-component of the data point(s)
    @param y: The y-component of the data point(s)"""
        id = id0 + self.offset
        if not (isinstance(x,list) | isinstance(x,tuple)):
            self._checkMaxId(id)
            self.indexList[id].append(x)  
            self.dataList[id].append(y)
            self.currentID = id
        else:
            for i, xi in enumerate(x):
                self.addData(id0, xi, y[i])
        self.replot = True

    def setData(self,id0, x, y):
        """ Data series id0 is replaced by the given lists
    @param id0: The plot ID (counted from 0) the data point(s) belong to.
    @param x: The x-component of the data points
    @param y: The y-component of the data points"""
        id = id0 + self.offset
        self._checkMaxId(id)
        self.indexList[id] = x
        self.dataList[id] = y
        self.replot = True
        
    def saveData(self, filename):
        """ Writes the data series for all points to a file 
    @param filename: The name of the output file """
        file = open(filename,"w")
        for i in range(self.nbLines):
            datLen=len(self.indexList[i])
            for j in range(datLen):
                file.write(repr(self.indexList[i][j])+"\n")
                file.write(repr(self.dataList[i][j])+"\n")
        file.close()

 
    def setLabels(self, x= '', y= '', title = ''):
        """ set axis labels and title """
        self.Axes.set_xlabel(x)
        self.Axes.set_ylabel(y)
        self.Axes.set_title(title)
        
    def setLegend(self, *args,**kwargs):
        """ hand parameters to the legend """
        self.Axes.legend(*args,**kwargs)
    
    def setLineStyle(self, id=None, **kwargs):
        """ hand parameters to the specified line(s), and set them as default for new lines 
    @param id: The line or lines (list!) to be modified - defaults to last one added """
        if id is None: 
            id = self.currentID
            
        if isinstance(id,list) | isinstance(id,tuple):
            # apply to specified list of lines
            self._checkMaxId(max(id)+self.offset)
            for i in id:
                self.Lines[i+self.offset].set(**kwargs)
        elif id >= 0:
            # apply to selected line
            self._checkMaxId(id+self.offset)
            self.Lines[id+self.offset].set(**kwargs)
        else:
            # apply to all lines
            for l in self.Lines:
                l.set(**kwargs)
                
        # set as new default linestyle
        if kwargs.has_key('color'):
            kwargs.popitem('color')
        self.defaultLineStyle = kwargs
        
            
    def update(self):
        """ Updates the current plot, if necessary """
        if not self.replot: 
            return
        for i in range(self.nbLines):
            self.Lines[i].set_data(self.indexList[i], self.dataList[i])
        pylab.draw_if_interactive()
        self.replot = False


    def show(self, xLabel = '', yLabel = '', title = '', popup = False, imgfile = None):
        """ Plots the data internally and saves an image of it to the plotting directory. 
    @param title: The title of the plot.
    @param xLable: The label for the x-axis
    @param yLable: The label for the y-axis
    @param popup: also produce a popup window with the image?"""
        pylab.clf()
        for i in range(self.nbLines):
            pylab.plot(self.indexList[i], self.dataList[i])
        pylab.xlabel(xLabel)
        pylab.ylabel(yLabel)
        pylab.title(title)
        if imgfile == None:
            imgfile = imp.find_module('pybrain')[1]+"/tools/plotting/plot.png"
        pylab.savefig(imgfile)
        if popup:
            pylab.ioff()
            pylab.show()    


"""Small example to demonstrate how the plot class can be used"""
if __name__ == "__main__":
    pbplot=MultilinePlotter(7)
    for i in range(400000):
        if i/100000 == i/100000.0:
            for j in range(7):
                pbplot.addData(j, i, math.sqrt(float(i*(j+1))))
    pbplot.show("WorldInteractions", "Fitness", "Example Plot", True)