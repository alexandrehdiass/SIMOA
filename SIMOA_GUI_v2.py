import os
import numpy as np
from math import atan, sin, cos
from tkinter import *#Tk, Frame, Menu, Label
from tkinter import filedialog
import webbrowser as wb
import matplotlib.pyplot as plt
import datetime as dt
import shapefile
import glob
import gdal, gdalnumeric, osr
from pandas import DataFrame
import statsmodels.api as sm

##INITIAL_PATH = '//home//philippe//Documents//CEMIG_TRES_MARIAS_2019'

class Sat_Model():
    def __init__(self, name, band, weight, pvalue):
        self.name = name
        self.band = band
        self.weight = weight
        self.pvalue = pvalue

#****************** A Classe de Interface Grafica do Usuario **********************
class SIMOA_GUI(Frame):
    def __init__(self, initial_path):
        super().__init__()
        self.initUI()
        self.initial_path = initial_path

    def initUI(self):
        self.master.title("SIMOA (Sistema Inteligente de MOnitoramento da Agua) (v. 1.01)")
        self.grid()
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        
        # Display Imagem
        self._figura = PhotoImage(file = "Simoa_marca-03.gif")
        self._rotulo_figura = Label(self, image = self._figura)
        self._rotulo_figura.grid(row = 0, column = 0, columnspan = 3)

        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        
        ModelMenu = Menu(menubar, tearoff=0)
        ModelMenu.add_command(label=u'\u2022'+" Set General Path", command = self._SIMOA_child_0)
        ModelMenu.add_command(label=u'\u2022'+" Produce WQ model from satellite image (S-2 or L-8)", command = self._SIMOA_child_1)
        ModelMenu.add_command(label=u'\u2022'+" Produce WQ model from shapefile with WQ data", command = self._SIMOA_child_13)
        ModelMenu.add_command(label=u'\u2022'+" Apply WQ model to satellite image", command = self._SIMOA_child_2)
        menubar.add_cascade(label="WQ Models ",menu=ModelMenu, font = ('Verdana', 10))
        DataMenu = Menu(menubar, tearoff=0)
        DataMenu.add_command(label=u'\u2022'+"Get Reflectance Data (GEE)", command = self._SIMOA_child_14)
        menubar.add_cascade(label="WQ Data",menu=DataMenu, font = ('Verdana', 10))
        helpMenu = Menu(menubar, tearoff=0)
        helpMenu.add_command(label=u'\u2022'+" Open Manual", command = self._SIMOA_child_12)
        menubar.add_cascade(label="Help ",menu=helpMenu, font = ('Verdana', 10))

######################################################################################################################################################################
# SIMOA child 14 window _____________________________________________________________________
    def _SIMOA_child_14(self):
        self.top14 = Toplevel()
        self.top14.title("Get reflectance values from shapefile and GEE")
        self.top14.grid()
        self.top14.attributes('-topmost', True)

#   GET SHAPEFILE
        self.top14._shp_label = Label(self.top14, text = "ShapeFile Water Quality Data",anchor="w").grid(column=0,row=1,columnspan=1,sticky='W')
        self.top14._shp_var = StringVar()
        self.top14._shp_var_label = Label(self.top14,textvariable=self.top14._shp_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=1)
        self.top14.button_shp = Button(self.top14,text=u"Change  File",command=self.OnButtonClick_shp_file2).grid(column=2,row=1)

        # Botao para fazer a mascara inversa
        self.top14.satellite = StringVar(value="S2")
        self.top14._sat = Radiobutton(self.top14,text="Sentinel-2",variable=self.top14.satellite, value="S2").grid(row = 2, column = 0)
        self.top14._sat = Radiobutton(self.top14,text= "Landsat-8",variable=self.top14.satellite, value="L8").grid(row = 2, column = 1)

    def OnButtonClick_shp_file2(self):
        self.file_opt = options = {}
        self.file_opt['initialdir'] = self.initial_path
        self.file_opt['filetypes'] = [('Shapefile files','.shp')]
        self.top14.shp = self.askopenfname3()
        self.top14._shp_var.set(self.top14.shp)

    def askopenfname3(self):
        return filedialog.askopenfilename(parent=self.top14,**self.file_opt)

######################################################################################################################################################################
# SIMOA child 13 window _____________________________________________________________________
    def _SIMOA_child_13(self):
        today=dt.date.today()
        self.top13 = Toplevel()
        self.top13.title("Produce WQ model from shapefile")
        self.top13.grid()
        self.top13.attributes('-topmost', True)

#   GET SHAPEFILE
        self.top13._shp_label = Label(self.top13, text = "ShapeFile Water Quality Data",anchor="w").grid(column=0,row=0,columnspan=1,sticky='W')
        self.top13._shp_var = StringVar()
        self.top13._shp_var_label = Label(self.top13,textvariable=self.top13._shp_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=0)
        self.top13.button_shp = Button(self.top13,text=u"Change  File",command=self.OnButtonClick_shp_file4).grid(column=2,row=0)

        self.top13._modelcomp_label = Label(self.top13, text = "Model Name Complement",anchor="w").grid(column=0,row=1,sticky='W')
        self.top13._modelcomp_var = StringVar()
        self.top13._modelcomp_var.set(str(today))
        self.top13._modelcomp_entry = Entry(self.top13,textvariable=self.top13._modelcomp_var,relief=SUNKEN,width=30).grid(column=1,row=1)

        self.top13._valinter_label = Label(self.top13, text = "Value Interval",anchor="w").grid(column=0,row=2,sticky='W')
        self.top13._valinter_var = StringVar()
        self.top13._valinter_var.set('0-10000')
        self.top13._valinter_entry = Entry(self.top13,textvariable=self.top13._valinter_var,relief=SUNKEN,width=10).grid(column=1,row=2,sticky='W')

        self.top13._days_label = Label(self.top13, text = "Max day difference",anchor="w").grid(column=0,row=3,sticky='W')
        self.top13._days_var = IntVar()
        self.top13._days_var.set(2)
        self.top13._days_entry = Entry(self.top13,textvariable=self.top13._days_var,relief=SUNKEN,width=3).grid(column=1,row=3,sticky='W')

        self.top13.showbands = Button(self.top13, text='Show Image Bands',anchor="w", command=self.OnButtonClick_Show_bands).grid(row = 4, column = 0)

    def OnButtonClick_shp_file4(self):
        self.file_opt = options = {}
        self.file_opt['initialdir'] = self.initial_path
        self.file_opt['filetypes'] = [('Shapefile files','.shp')]
        self.top13.shp = self.askopenfname4()
        self.top13._shp_var.set(self.top13.shp)

    def askopenfname4(self):
        return filedialog.askopenfilename(parent=self.top13,**self.file_opt)

    def OnButtonClick_Show_bands(self):
        print(self.top13._shp_var.get(), self.top13._modelcomp_var.get())
        pts_shp = shapefile.Reader(self.top13._shp_var.get())
        pts = pts_shp.shapes()
        pts_fields = pts_shp.fields
        
        bandlist = []
        bandlistidx = []
        attribute_list = 'Number of points: '+str(len(pts))+'\nBands:\n'
        for i in range(1,len(pts_fields)):
            if (pts_fields[i][0] == 'B1' or pts_fields[i][0] == 'B2' or pts_fields[i][0] == 'B3' or pts_fields[i][0] == 'B4' or pts_fields[i][0] == 'B5' or
            pts_fields[i][0] == 'B6' or pts_fields[i][0] == 'B7' or pts_fields[i][0] == 'B8' or pts_fields[i][0] == 'B8A' or pts_fields[i][0] == 'B9' or
            pts_fields[i][0] == 'B11' or pts_fields[i][0] == 'B12'):
                print(pts_fields[i][0])
                bandlist.append(pts_fields[i][0])
                bandlistidx.append(i)
        pts_shp.close()

        self.top13a = Toplevel()
        self.top13a.wm_attributes("-topmost", 1)
        self.top13a.title("Band list")
        self.top13a.label1 = Label(self.top13a, text = 'Uncheck unwanted bands',width=30,font=("Times", 12)).grid(column=0,row=0)
        self.top13.bcheck = [1]*len(bandlist)
        for j in range(0,len(bandlist)):
            self.top13.bcheck[j] = IntVar()
            self.top13.bcheck[j].set(1)
            self.top13a.check1 = Checkbutton(self.top13a,text="Band"+bandlist[j],variable=self.top13.bcheck[j],width=30,font=("Times", 12))
            self.top13a.check1.grid(column=0,row=j+1)
        self.top13a.geometry("+%d+%d" % (self.top13a.winfo_rootx()+400,self.top13a.winfo_rooty()+250))

        self.top13.compute_model = Button(self.top13, text='Compute Model',anchor="w", command=self.OnButtonClick_compute_model).grid(row=3, column = 2)

        self.top13.pmax_var = DoubleVar()
        self.top13.pmax_var.set(-99.0)
        self.top13._pmax_entry = Entry(self.top13,textvariable=self.top13.pmax_var,width=5)
        self.top13._pmax_entry.grid(column=2,row=4,sticky='W')
        self.top13._pmax_entry.config(state = DISABLED)

        def activate_pmax():
            if self.top13._pval_var.get():
                self.top13._pmax_entry.config(state = NORMAL)
                self.top13.pmax_var.set(0.05)
            else:
                self.top13._pmax_entry.config(state = DISABLED)
#                self.top13.pmax_var.set(0)

#   CHECKBUTTONS for P-Value threshold
        self.top13._pval_var = IntVar()
        self.top13.check_pval = Checkbutton(self.top13,text="Eliminate bands with P-value >",variable=self.top13._pval_var,width=28, anchor=W, command=activate_pmax).grid(column=1,row=4, sticky='W')

    def OnButtonClick_compute_model(self):
        pts_shp = shapefile.Reader(self.top13._shp_var.get())
        pts = pts_shp.shapes()
        pts_fields = pts_shp.fields
        
        attributes = []
        bandlist = []
        bandlistidx = []
        code = '-'
        codidx = -1
        validx = -1
        unitidx = -1
        surday = dt.datetime(1000,1,1)
        imday = dt.datetime(1000,1,1)
        inter = self.top13._valinter_var.get().split('-')
        minval = int(inter[0])
        maxval = int(inter[1])
        print('Min value:', minval, '\nMax value:',maxval)
        attribute_list = 'Number of points: '+str(len(pts))+'\nBands:\n'
        for i in range(1,len(pts_fields)):
            if (pts_fields[i][0] == 'B1' or pts_fields[i][0] == 'B2' or pts_fields[i][0] == 'B3' or pts_fields[i][0] == 'B4' or pts_fields[i][0] == 'B5' or
            pts_fields[i][0] == 'B6' or pts_fields[i][0] == 'B7' or pts_fields[i][0] == 'B8' or pts_fields[i][0] == 'B8A' or pts_fields[i][0] == 'B9' or
            pts_fields[i][0] == 'B11' or pts_fields[i][0] == 'B12'):
                bandlist.append(pts_fields[i][0])
                bandlistidx.append(i)
            elif pts_fields[i][0].find('CODE') == 0:
                code = pts_fields[i][0]
                codidx = i
            elif pts_fields[i][0].find('VALUE') == 0:
                validx = i
            elif pts_fields[i][0].find('UNIT') == 0:
                unitidx = i
            elif pts_fields[i][0].find('DATE') == 0:
                surdayidx = i
            elif pts_fields[i][0].find('IMAGEDATE') == 0:
                imdayidx = i
            elif pts_fields[i][0].find('DIFDATE') == 0:
                daydifidx = i
            else:
                attributes.append(pts_fields[i][0])
        bandflags = []
        for i in range(0,len(self.top13.bcheck)):
            bandflags.append(self.top13.bcheck[i].get())
        
##        print(codidx, validx, unitidx, surdayidx, bandlistidx, bandflags)

        scale_factor = 0.0001
        z = []
        allbands = []
        allbandvalues=[]
        sdate = []
        idate = []
        zf = []
        independent = {}
        
        for k in range(0,len(bandlist)):
            if bandlistidx[k] and bandflags[k]:
                bandname = bandlist[k]
                allbands.append(bandname)
                
        for i in range(0,len(pts)):
            pt_rec = pts_shp.record(i)
            paraname = pt_rec[codidx-1]
            daydif = pt_rec[daydifidx-1]
            if validx >= 0 and daydif <= self.top13._days_var.get():
                if float(pt_rec[validx-1]) >= minval and float(pt_rec[validx-1]) <= maxval:
                    z.append(float(pt_rec[validx-1]))
##            if surdayidx >= 0:
##                surday = pt_rec[surdayidx-1]
##                surday = surday.split('-')
##                surday = dt.datetime(int(surday[0]),int(surday[1]),int(surday[2]))
##                sdate.append(surday)
##            if imdayidx >= 0:
##                imday = pt_rec[imdayidx-1]
##                imday = imday.split('-')
##                imday = dt.datetime(int(imday[0]),int(imday[1]),int(imday[2]))
##                idate.append(imday)

        for k in range(0,len(bandlist)):
            if bandflags[k]:
                bandname = bandlist[k]
                bandvalues = []
                for i in range(0,len(pts)):
                    pt_rec = pts_shp.record(i)
                    daydif = pt_rec[daydifidx-1]
                    if validx >= 0 and daydif <= self.top13._days_var.get():
                        if float(pt_rec[validx-1]) >= minval and float(pt_rec[validx-1]) <= maxval:
                            bandvalues.append(float(pt_rec[bandlistidx[k]-1])*scale_factor)
                independent[bandname] = bandvalues
            allbandvalues.append(bandvalues)

        dependent = {paraname: z}
        print(len(bandvalues), len(z), len(bandname))
        self.top13a.destroy()
           
        explained = DataFrame(dependent)
        predictors = DataFrame(independent)
        model = sm.GLS(explained, predictors).fit()
        predictions = model.predict(predictors)
        print_model = model.summary()
        print(print_model)

##  AUTOMATIC ELIMINATION OF BANDS BASED ON P-VALUES ##
        if self.top13.pmax_var.get() != -99.0:
            new_allbands = []
            new_independent = {}
            for i in range(0,len(allbands)):
                if model.pvalues[i] <= self.top13.pmax_var.get():
                    new_allbands.append(allbands[i])
                    bandflags[i] = 0
                    print('rrrrrrrr', allbands[i])
                    new_independent[allbands[i]] = independent[allbands[i]]
##                    print(new_independent[allbands[i]])
            print('>>>>>>>>>>>>>>>> Recomputing model without non-significant bands <<<<<<<<<<<<<<<<<<\n\n')
            allbands = []
            for b in new_allbands:
                allbands.append(b)
                
            explained = DataFrame(dependent)
            newpredictors = DataFrame(new_independent)
            model = sm.GLS(explained, newpredictors).fit()
            predictions = model.predict(newpredictors)
            print_model = model.summary()
            print(print_model)


#_________________________________________ Print model and model summary ________________________________
        model_path = self.top13._shp_var.get()
        model_path = model_path.replace('.shp','')
        if not os.path.isdir(str(model_path)):
            os.mkdir(model_path)
        comp = self.top13._modelcomp_var.get()
        fout1 = open(model_path+'//regression_summary_'+paraname+'_'+comp+'.txt','wt')
        header = 'Shapefile: ' + self.top13._shp_var.get() + '\n' + 'Water_quality_parameter ' + paraname + '\n\n'
        fout1.write(header)
        fout1.write(str(print_model))
        fout1.close()
        fout2 = open(model_path+'//model_parameters_'+paraname+'_'+comp+'.txt','wt')
        fout2.write(header+'Model_parameters ' + str(len(allbands)) + ' ' + '(Variable Weight P-Value)\n')

        for i in range(0, len(allbands)):
            print(allbands[i], model.params[i], model.pvalues[i])
            s = str(allbands[i]) + '\t' + str(model.params[i]) + '\t' + str(model.pvalues[i]) + '\n'
            fout2.write(s)
        fout2.close()

######################################################################################################################################################################
# SIMOA child 12 window _____________________________________________________________________
    def _SIMOA_child_12(self):
        wb.open_new(r'Manual_SIMOA.pdf')

######################################################################################################################################################################
# SIMOA child 0 window _____________________________________________________________________
    def _SIMOA_child_0(self):
        self.top0 = Toplevel()
        self.top0.title("Set General Path Location")
        self.top0.grid()
        self.top0.attributes('-topmost', True)
        self.top0._gpath_label = Label(self.top0, text = "General Data Path ",anchor="w").grid(column=0,row=0,columnspan=1,sticky='W')
        self.top0._gpath_var = StringVar()
        self.top0._shp_var_label = Label(self.top0,textvariable=self.top0._gpath_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=0)
        self.top0.button_shp = Button(self.top0,text=u"Change  Path",command=self.OnButtonClick_General_Path).grid(column=2,row=0)

    def OnButtonClick_General_Path(self):
        g_path = self.askdir0()
        self.initial_path = g_path
        print ('General Path:', g_path)
        f_config = open('_config.txt', 'wt')
        f_config.write(g_path)
        
        f_config.close()
        self.top0._gpath_var.set(g_path)

    def askdir0(self):
        return filedialog.askdirectory(parent=self.top0,initialdir='/')

######################################################################################################################################################################
# SIMOA child 1 window _____________________________________________________________________
    def _SIMOA_child_1(self):
        today=dt.date.today()
        self.top1 = Toplevel()
        self.top1.title("Produce WQ model from satellite image")
        self.top1.grid()
        self.top1.attributes('-topmost', True)

#   GET IMAGE PATH

        self.top1._path_label = Label(self.top1, text = "Satellite Image Path ",anchor="w").grid(column=0,row=0,columnspan=1,sticky='W')
        self.top1._path_var = StringVar()
        self.top1._imtype_var = StringVar()
        self.top1._shp_var_label = Label(self.top1,textvariable=self.top1._path_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=0)
        self.top1.button_shp = Button(self.top1,text=u"Change  Path",command=self.OnButtonClick_Image_Path1).grid(column=2,row=0)

#   GET SHAPEFILE
        self.top1._shp_label = Label(self.top1, text = "ShapeFile Water Quality Data",anchor="w").grid(column=0,row=1,columnspan=1,sticky='W')
        self.top1._shp_var = StringVar()
        self.top1._shp_var_label = Label(self.top1,textvariable=self.top1._shp_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=1)
        self.top1.button_shp = Button(self.top1,text=u"Change  File",command=self.OnButtonClick_shp_file).grid(column=2,row=1)

        self.top1._modelcomp_label = Label(self.top1, text = "Model Name Complement",anchor="w").grid(column=0,row=2,sticky='W')
        self.top1._modelcomp_var = StringVar()
        self.top1._modelcomp_var.set(str(today))
        self.top1._modelcomp_entry = Entry(self.top1,textvariable=self.top1._modelcomp_var,relief=SUNKEN,width=30).grid(column=1,row=2)

        self.top1.showdatabutton = Button(self.top1, text=' Show  Data  ',anchor="w", command=self.OnButtonClick_show_data)
        self.top1.showdatabutton.grid(row = 3, column = 0)
        
    def OnButtonClick_Image_Path1(self):
        im_path = self.askdir1()
        if im_path.find('SENTINEL') >= 0:
            self.top1._imtype_var.set('S2')
        if im_path.find('LC08') >= 0:
            self.top1._imtype_var.set('L8')
        self.top1._path_var.set(im_path)

    def OnButtonClick_shp_file(self):
        self.file_opt = options = {}
        self.file_opt['initialdir'] = self.initial_path
        self.file_opt['filetypes'] = [('Shapefile files','.shp')]
        self.top1.shp = self.askopenfname1()
        self.top1._shp_var.set(self.top1.shp)

    def askdir1(self):
        return filedialog.askdirectory(parent=self.top1,initialdir=self.initial_path)

    def askopenfname1(self):
        return filedialog.askopenfilename(parent=self.top1,**self.file_opt)

######################################################################################################################################################################
# SIMOA child 2 window _____________________________________________________________________
    def _SIMOA_child_2(self):
        self.top2 = Toplevel()
        self.top2.title("Apply WQ model to satellite image")
        self.top2.grid()
        self.top2.attributes('-topmost', True)

#   GET IMAGE PATH

        self.top2._path_label = Label(self.top2, text = "Satellite Image Path ",anchor="w").grid(column=0,row=0,columnspan=1,sticky='W')
        self.top2._path_var = StringVar()
        self.top2._imtype_var = StringVar()
        self.top2._shp_var_label = Label(self.top2,textvariable=self.top2._path_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=0,sticky='W')
        self.top2.button_shp = Button(self.top2,text=u"Change Path",command=self.OnButtonClick_Image_Path2).grid(column=2,row=0)

#   GET MODEL
        self.top2._model_label = Label(self.top2, text = "Water Quality Model",anchor="w").grid(column=0,row=1,columnspan=1,sticky='W')
        self.top2._model_var = StringVar()
        self.top2._model_var_label = Label(self.top2,textvariable=self.top2._model_var,anchor="w",fg="black",bg="white",relief=SUNKEN,width=30).grid(column=1,row=1,sticky='W')
        self.top2.button_model = Button(self.top2,text=u"Change  File",command=self.OnButtonClick_model_file).grid(column=2,row=1)

#   GET WATER MASK

        self.top2._use_wmask_var = IntVar()
        self.top2._check_wmask = Checkbutton(self.top2,text="Create Water Mask from NIR threshold:",variable=self.top2._use_wmask_var,width=35, anchor=W, command=self.OnButtonClick_wmask_file).grid(column=0,row=2, sticky='W')
        self.top2._thresh_var = IntVar()
        self.top2._thresh_entry = Entry(self.top2, textvariable=self.top2._thresh_var,width=7).grid(column=1,row=2, sticky='W')
        
        self.top2.processdatabutton = Button(self.top2, text='Process Data',anchor="w", command=self.OnButtonClick_Process_data).grid(row = 3, column = 0)

    def OnButtonClick_Image_Path2(self):
        im_path = self.askdir2()
        if im_path.find('SENTINEL') >= 0:
            self.top2._imtype_var.set('S2')
        if im_path.find('LC08') >= 0:
            self.top2._imtype_var.set('L8')
        self.top2._path_var.set(im_path)
        if self.top2._imtype_var.get() == 'S2':
            self.top2._thresh_var.set(500)
        elif self.top2._imtype_var.get() == 'L8':
            self.top2._thresh_var.set(7000)

    def OnButtonClick_model_file(self):
        self.file_opt = options = {}
        self.file_opt['initialdir'] = self.initial_path
        self.file_opt['filetypes'] = [('Model files','.txt')]
        self.top2.model = self.askopenfname2()
        self.top2._model_var.set(self.top2.model)

    def OnButtonClick_wmask_file(self):
        if self.top2._use_wmask_var.get():
            print('Using Water Mask from NIR of Image', self.top2._imtype_var.get(), 'with threshold', self.top2._thresh_var.get())

    def OnButtonClick_Process_data(self):
        mfile = open(self.top2._model_var.get(), 'rt')
        comp = self.top2._model_var.get().split('_')[-1].split('.')[0]
        bandnumber = []
        bandweight = []
        bandpvalue = []
        t = 'x'
        while t != '':
            t = mfile.readline()
            t1 = t.split(' ')
            if t1[0] == 'Water_quality_parameter':
                paramname = t1[-1].replace('\n','')
            if t1[0] == 'Model_parameters':
                nparam = int(t1[1])
                for i in range(0,nparam):
                    t2 = mfile.readline()
                    t2 = t2.split()
                    bandnumber.append(t2[0])
                    bandweight.append(float(t2[1]))
                    bandpvalue.append(float(t2[2]))
                sentinel2_model = Sat_Model(paramname, bandnumber, bandweight, bandpvalue)
        mfile.close()
        process_satimage_data(self.top2._path_var.get(), sentinel2_model, self.top2._use_wmask_var.get(), self.top2._thresh_var.get(), comp, self.top2._imtype_var.get())

    def askdir2(self):
        return filedialog.askdirectory(parent=self.top2,initialdir=self.initial_path)

    def askopenfname2(self):
        return filedialog.askopenfilename(parent=self.top2,**self.file_opt)

######################################################################################################################################################################
    def OnButtonClick_show_data(self):
        pts_shp = shapefile.Reader(self.top1._shp_var.get())
        pts = pts_shp.shapes()
        pts_fields = pts_shp.fields
        self.top1.pick_parameter_label = Label(self.top1, text='Pick Water Quality Parameter',anchor="w").grid(row = 3, column = 1)
        self.top1.window_parameter_label = Label(self.top1, text='Window size (must be 1,3,5,7 or 9)',anchor="w").grid(row = 4, column = 1)
        

        param_list = 'Number of points: '+str(len(pts))+'\nParameters:\n'
        for i in range(0,len(pts_fields)):
            param_list+=str(i+1)+': '+pts_fields[i][0]+'\n'
        self.top2 = Toplevel()
        self.top2.wm_attributes("-topmost", 1)
        self.top2.title("ShapeFile Attributes")
        self.top2.label_1 = Label(self.top2, text = param_list,width=40)
        self.top2.label_1.config(font=("Times", 12))
        self.top2.label_1.grid(column=0,row=2)
        self.top2.geometry("+%d+%d" % (self.top2.winfo_rootx()+100,self.top2.winfo_rooty()+200))

        path_sub = self.top1._path_var.get().split('/')
        if self.top1._imtype_var.get() == 'S2': ## FOR SENTINEL-2 IMAGES
            print('Reading a Sentinel-2 Image')
            imagetype = 'SENTINEL2*_FRE_B*.tif'
            band_separator = 'FRE_'
        elif self.top1._imtype_var.get() == 'L8': ## FOR LANDSAT-8 IMAGES
            print('Reading a Landsat-8 Image')
            imagetype = 'LC08*_RT_B*.TIF'
            band_separator = 'RT_'

##        elif self.top1._imtype_var.get() == 'L5': ## FOR LANDSAT-5 IMAGES
##            print('Reading a Landsat-5 Image')
##            imagetype = 'LC05*_RT_B*.TIF'
##            band_separator = 'RT_'

        i_files = glob.glob(self.top1._path_var.get()+'/'+imagetype)
        i_files.sort()
        print(self.top1._path_var.get()+'/'+imagetype)

        s = str(len(i_files))+' Bands:\n'
        allbands = []
        for j in range(0,len(i_files)):
            im = i_files[j]
            bandname = im.split(band_separator)[-1].split('.')[0]
            allbands.append(bandname)
        self.top3 = Toplevel()
        self.top3.wm_attributes("-topmost", 1)
        self.top3.title("Band list")
        self.top3.label1 = Label(self.top3, text = 'Uncheck unwanted bands',width=30,font=("Times", 12)).grid(column=0,row=0)
        self.top3.bcheck = [1]*len(i_files)
        for j in range(0,len(allbands)):
            self.top3.bcheck[j] = IntVar()
            self.top3.bcheck[j].set(1)
            self.top3.check1 = Checkbutton(self.top3,text="Band"+allbands[j],variable=self.top3.bcheck[j],width=30,font=("Times", 12))
            self.top3.check1.grid(column=0,row=j+1)
        self.top3.geometry("+%d+%d" % (self.top3.winfo_rootx()+400,self.top3.winfo_rooty()+250))
        
        self.top1.pmax_var = DoubleVar()
        self.top1.pmax_var.set(-99)
        self.top1._pmax_entry = Entry(self.top1,textvariable=self.top1.pmax_var,width=5)
        self.top1._pmax_entry.grid(column=2,row=5,sticky='W')
        self.top1._pmax_entry.config(state = DISABLED)

        self.top1.window_var = IntVar()
        self.top1.window_var.set(1)
        self.top1._window_entry = Entry(self.top1,textvariable=self.top1.window_var,width=5).grid(column=2,row=4,sticky='W')

        def activate_pmax():
            if self.top1._pval_var.get():
                self.top1._pmax_entry.config(state = NORMAL)
                self.top1.pmax_var.set(0.05)
            else:
                self.top1._pmax_entry.config(state = DISABLED)
#                self.top1.pmax_var.set(0)

#   CHECKBUTTONS for P-Value threshold
        self.top1._pval_var = IntVar()
        self.top1.check_pval = Checkbutton(self.top1,text="Eliminate bands with P-value >",variable=self.top1._pval_var,width=28, anchor=W, command=activate_pmax).grid(column=1,row=5, sticky='W')

        self.top1.param_var = IntVar()
##        self.top1.param_var.set(10)
        self.top1.param_entry = Entry(self.top1,textvariable=self.top1.param_var,width=3).grid(column=2,row=3,sticky='W')
        self.top1.getdatabutton = Button(self.top1, text='Compute Model',anchor="w", command=self.OnButtonClick_get_data).grid(row=5, column = 0)


    def OnButtonClick_get_data(self):
        pts_shp = shapefile.Reader(self.top1._shp_var.get())
        pts = pts_shp.shapes()
        pts_fields = pts_shp.fields
        s = 'WQ Parameter: '+pts_fields[self.top1.param_var.get()-1][0]
        self.top1.label_1 = Label(self.top1, text = s,anchor="w")
        self.top1.label_1.config(font=("Times", 12))
        self.top1.label_1.grid(column=1,row=3)
        bandflags = []
        for i in range(0,len(self.top3.bcheck)):
            bandflags.append(self.top3.bcheck[i].get())
        self.top2.destroy()
        self.top3.destroy()
        self.update()
        
        read_satimage_data(self.top1._path_var.get(), self.top1._shp_var.get(), self.top1.param_var.get(), bandflags,
                           self.top1._modelcomp_var.get(), self.top1.pmax_var.get(), self.top1._imtype_var.get(),
                           self.top1.window_var.get())

        
def read_satimage_data(path, shp, param, bflag, comp, pmax, imagetype, wsize):
##    print('*****************************', shp, param, bflag, pmax)
    pts_shp = shapefile.Reader(shp)
    pts = pts_shp.shapes()
    pts_fields = pts_shp.fields
    dateindex = -1
    for f in range(0,len(pts_shp.fields)):
        tdate = str(pts_shp.fields[f][0])
        if tdate.lower() == 'date':
            dateindex = f
##            print('okkkkkkkkkkkkkkkkkkkkkkkk', pts_shp.fields[f], f)
            
    paraname = pts_fields[param-1][0]
    print(paraname)
    zindex = param-2
    inipix = 0
    finpix = 1
    if wsize != 1 and wsize != 3 and wsize != 5 and wsize != 7 and wsize != 9:
        print('Illegar window size: window is set to 1')
        wsize = 1
        
    if wsize > 1:
        inipix = int(0 - ((wsize - 1)/2))
        finpix = int(1 + ((wsize - 1)/2))
    x = []
    y = []
    z = []
    for i in range(0,len(pts)):
        pt_rec = pts_shp.record(i)
        if dateindex >= 0:
            point_date = pt_rec[dateindex-1]
            point_date = point_date.split('/')
            point_date = dt.datetime(int(point_date[2]),int(point_date[1]),int(point_date[0]))
        else:
            point_date = dt.datetime(1000,1,1)
#        print('Point date', point_date)
        xy = pts[i].points[0]
        x.append(xy[0])
        y.append(xy[1])
        z.append(float(pt_rec[zindex]))
##    print(x,y,z)
    dependent = {paraname: z}
##    print (dependent)
    independent = {}
    allbands = []

    print('----------------------------------------------', path)
    path_sub = path.split('/')
    if imagetype == 'S2': ## FOR SENTINEL-2 IMAGES
        print('Reading a Sentinel-2 Image')
        imagetype = 'SENTINEL2*_FRE_B*.tif'
        band_separator = 'FRE_'
        scale_factor = 0.0001
        image_date = path.split('SENTINEL2B_')
        image_date = image_date[1].split('-')[0]
        image_date = dt.datetime(int(image_date[0:4]),int(image_date[4:6]),int(image_date[6:8]))
        print('Image date:', image_date)
    elif imagetype == 'L8': ## FOR LANDSAT-8 IMAGES
        print('Reading a Landsat-8 Image')
        imagetype = 'LC08*_RT_B*.TIF'
        band_separator = 'RT_'
        scale_factor = 0.00002
        image_date = path.split('LC08_')
        image_date = image_date[1].split('_')[2]
        image_date = dt.datetime(int(image_date[0:4]),int(image_date[4:6]),int(image_date[6:8]))
        print('Image date:', image_date)
##    elif imagetype == 'L5': ## FOR LANDSAT-5 IMAGES
##        print('Reading a Landsat-5 Image')
##        imagetype = 'LC05*_RT_B*.TIF'
##        band_separator = 'RT_'
        
    image_files = glob.glob(path+'/'+imagetype)
    image_files.sort()
    print('Reading reflectance values from:')
    allbandvalues=[]
    for m in range(0,len(image_files)):
        if bflag[m]:
            bandvalues = []
            imf = image_files[m]
            bandname = imf.split(band_separator)[-1].split('.')[0]
            print ('Band ',bandname)
            allbands.append(bandname)
            ds = gdal.Open(imf, gdal.GA_ReadOnly)
            rb = ds.GetRasterBand(1)
            nbands = ds.RasterCount
            ncols = ds.RasterXSize
            nrows = ds.RasterYSize
            geotransform = ds.GetGeoTransform()
            ulx = geotransform[0]
            uly = geotransform[3]
            if uly < 0:
                uly += 10000000
            xdim = geotransform[1]
            ydim = geotransform[5]
            band = ds.GetRasterBand(1)
##            print(ncols,nrows,ulx,uly,xdim,ydim)
            imageband = band.ReadAsArray().astype(np.uint16)


            for j in range(0,len(x)):
                val = 0.0
                for ii in range(inipix, finpix):
                    for jj in range(inipix, finpix):
                        px = x[j] + jj
                        py = y[j] + ii
                        col = int(((px-ulx)/xdim))
                        row = int(((uly-py)/abs(ydim)))
                        val+= imageband[row,col] * scale_factor
                val = val / (wsize * wsize)
                bandvalues.append(val)
            independent[bandname] = bandvalues
            allbandvalues.append(bandvalues)
##    if pmax == -99.0:
##        print('Predicted:\n', dependent)
##        print('\nPredictors:')
##        for b in allbands:
##            print(b, ':', independent[b])
            
    explained = DataFrame(dependent)
    predictors = DataFrame(independent)
    model = sm.GLS(explained, predictors).fit()
    predictions = model.predict(predictors)
    
# ___________________Create new Shapefile with reflectance values_____________________________
    newshp = shp.replace('.shp', '_new.shp')
    newpts = shapefile.Writer(newshp,pts_shp.shapeType)
    newpts.fields = list(pts_shp.fields)
    for i in range(0,len(allbands)):
        newpts.field(allbands[i],"N",20,5)
    newpts.field('Image_Date','C',10)
    for j in range(0,len(pts)):
        newpts.point(x[j], y[j])
        pt_rec = pts_shp.record(j)
        for k in range(0,len(allbands)):
            pt_rec.append(allbandvalues[k][j])
        pt_rec.append(image_date.strftime("%d/%m/%Y"))
        newpts.record(*pt_rec)
    newpts.autoBalance
    newpts.close()


##  AUTOMATIC ELIMINATION OF BANDS BASED ON P-VALUES ##
    if pmax != -99.0:
        new_allbands = []
        new_independent = {}
        for i in range(0,len(allbands)):
            if model.pvalues[i] <= pmax:
                new_allbands.append(allbands[i])
                bflag[i] = 0
                print('rrrrrrrr', allbands[i])
                new_independent[allbands[i]] = independent[allbands[i]]
                print(new_independent[allbands[i]])
        print('>>>>>>>>>>>>>>>> Recomputing model without non-significant bands <<<<<<<<<<<<<<<<<<\n\n')
        allbands = []
        for b in new_allbands:
            allbands.append(b)
            
##        print('Predicted:\n', dependent)
##        print('\nPredictors:')
##        for b in allbands:
##            print(b, ':', new_independent[b])
        
        
        explained = DataFrame(dependent)
        newpredictors = DataFrame(new_independent)
        model = sm.GLS(explained, newpredictors).fit()
        predictions = model.predict(newpredictors)

########################################################

    print_model = model.summary()
    print(print_model)
    model_path = (path+'/models')
    if not os.path.isdir(str(model_path)):
        os.mkdir(model_path)
    fout1 = open(model_path+'/regression_summary_'+paraname+'_'+comp+'.txt','wt')
    header = 'Image type: '+ imagetype + image_files[0] + '\nShapefile: ' + shp + '\n' + 'Water_quality_parameter ' + paraname + '\n\n'
    fout1.write(header)
    fout1.write(str(print_model))
    fout1.close()
    fout2 = open(model_path+'/model_parameters_'+paraname+'_'+comp+'.txt','wt')
    fout2.write(header+'Model_parameters ' + str(len(allbands)) + ' ' + '(Variable Weight P-Value)\n')

    for i in range(0, len(allbands)):
        print(allbands[i], model.params[i], model.pvalues[i])
        s = str(allbands[i]) + '\t' + str(model.params[i]) + '\t' + str(model.pvalues[i]) + '\n'
        fout2.write(s)
    fout2.close()

def process_satimage_data(path, model, mask, thrld, comp, imagetype):
##    print(path, model.band, model.weight)
    if imagetype == 'S2': ## FOR SENTINEL-2 IMAGES
        imtype = 'SENTINEL2*_FRE_B8A.tif'
        scale_factor = 0.0001
    elif imagetype == 'L8': ## FOR LANDSAT-8 IMAGES
        imtype = 'LC08*_RT_B6.TIF'
        scale_factor = 0.00002
##    elif if imagetype == 'L5': ## FOR LANDSAT-5 IMAGES
##        print('Reading a Landsat-5 Image')
##        imtype = 'LC05*_RT_B5.TIF'
##        band_separator = 'RT_'
    image_files = glob.glob(path+'/'+imtype)
    image_files.sort()
    bname = image_files[0].split('_')[-1].split('.')[0]
    images = []
    weights = []
    for i in range(0,len(model.band)):
        imagename = image_files[0].replace(bname, model.band[i])
        if os.path.isfile(imagename):
##            print(imagename+' exists')
            images.append(imagename)
            weights.append(model.weight[i])
        else:
            print('Could not find ' + imagename + '!!!\n')

    for m in range(0,len(images)):
        ds = gdal.Open(images[m], gdal.GA_ReadOnly)
        nbands = ds.RasterCount
        ncols = ds.RasterXSize
        nrows = ds.RasterYSize
        geotransform = ds.GetGeoTransform()
        ulx = geotransform[0]
        uly = geotransform[3]
        xdim = geotransform[1]
        ydim = geotransform[5]
        print(images[m].split('/')[-1], weights[m], ncols,nrows,ulx,uly,xdim,ydim)
        if m == 0:
            raster = np.zeros((nrows, ncols), dtype=np.float32)
        band = ds.GetRasterBand(1)
        imageband = band.ReadAsArray().astype(np.uint16)
        raster += imageband * scale_factor * weights[m]

    if mask:
        path_sub = path.split('/')
            
        nir_band = glob.glob(path+'/'+imtype)
        if len(nir_band) > 1:
            print('Not sure where NIR Band is located')
        else:
            dswm = gdal.Open(nir_band[0], gdal.GA_ReadOnly)
            bandwm = dswm.GetRasterBand(1)
            imagemask = bandwm.ReadAsArray().astype(np.uint16)
            imagemask[imagemask > thrld] = 0
            imagemask[imagemask != 0] = 1
            raster *= imagemask
    
    outimage_name = path+'//'+model.name+'_'+comp+'.tif'
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create(outimage_name, ncols, nrows, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(ds.GetProjection())
##    print (ds.GetProjection())
    dst_ds.GetRasterBand(1).WriteArray( raster )
    dst_ds.FlushCache()
    dst_ds = None
    rb = None
    ds = None

    raster[raster == 0.0] = np.nan
    plt.figure(model.name + ' Model')
    plt.imshow(raster, cmap=plt.get_cmap('jet'))#,vmin=0, vmax=10)
    plt.colorbar(label='ug/l')
    plt.show()
        


def main():
    try:
        f_conf = open('_config.txt', 'rt')
        t = f_conf.read()
        init_dir = t
        print('Found config,', 'Initial path =', init_dir)
    except IOError:
        init_dir = '/'
        print('Cant find config,', 'Initial path =', init_dir)
    SIMOA_GUI(init_dir).mainloop()
main()
