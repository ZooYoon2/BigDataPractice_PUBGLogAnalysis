from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
from tkinter import filedialog
import copy
import numpy as np
import json

root = Tk()
root.title("맵 폴리곤좌표 제작")
root.geometry("798x810")
root.resizable(False, False)

polygon_pos = []
polygon_list = dict()
img_zoom = 1.0
wd = 768
wh = 768

canvas = Canvas(width = wd, height = wh, bg = 'blue')
canvas.place(x=15,y=30)

input_text = Entry(root)
input_text.place(x=15,y=0,width=100,height=30)

def changeMonth():
    combo_material["values"] = list(polygon_list.keys())

def callback_mouse(event):
    print(event.x,event.y)
    canvas.create_oval(event.x-3,event.y-3,event.x+3,event.y+3,fill='black',tag='point')
    polygon_pos.append([event.x,event.y])

def createPolyGon():
    canvas.create_polygon(polygon_pos, fill='black',stipple="gray50",outline='black',width=2,tag='polygon')
    print(polygon_pos)
    polygon_list[input_text.get()]=copy.deepcopy(polygon_pos)
    input_text.delete("0", "end")
    canvas.delete('point')
    polygon_pos.clear()

def selectPolyGon():
    canvas.delete('polygon')
    for name,pos in polygon_list.items():
        print(name, pos)
        if name == combo_material.get():
            canvas.create_polygon(pos,fill='blue',stipple="gray50",outline='blue',width=2,tag='polygon')
        else:
            canvas.create_polygon(pos,fill='black',stipple="gray50",outline='black',width=2,tag='polygon')
            
def deletePolyGon():
    canvas.delete('polygon')
    for name,pos in polygon_list.items():
        if name == combo_material.get():
            polygon_list.pop(name)
        else:
            canvas.create_polygon(pos,fill='black',stipple="gray50",outline='black',width=2)
    changeMonth()

def fopen():
    filename = filedialog.askopenfilename(initialdir='', title='파일선택', filetypes=(
    ('png files', '*.png'), ('jpg files', '*.jpg'), ('all files', '*.*')))
    global img
    img = Image.open(filename)
    img_w, img_h = img.size
    global img_zoom 
    img_zoom = float(img_w/wd)
    print(img_w)
    print(img_zoom)
    img = img.resize((wd,wh), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image = img,anchor='nw')
    polygon_pos.clear()
    polygon_list.clear()

def fsave():
    filename = filedialog.asksaveasfilename(initialdir='', title='파일선택', filetypes=(
    ('json files', '*.json'), ('csv files', '*.csv'), ('all files', '*.*')))
    if not filename=="":
        file = open(filename+'.json',"w")
        realSizePos = dict()
        for name,pos in polygon_list.items():
            print(type(pos))
            print(type(pos[0]))
            realSizePos[name]=(np.array(pos)*img_zoom*100).tolist()
        json.dump(realSizePos,file)
        file.close()
        print("저장 완료")

my_btn = Button(root, text='맵 이미지 파일 열기', command=fopen)
my_btn.place(x=630,y=0,width=150,height=30)
my_btn = Button(root, text='저장', command=fsave)
my_btn.place(x=380,y=0,width=50,height=30)

button1 = ttk.Button(root, text="생성",command=createPolyGon)
button1.place(x=110,y=0,width=50,height=30)

combo_material = ttk.Combobox(root, values=list(polygon_list.keys()), justify="center", postcommand=changeMonth)
#combo_material.bind('<<ComboboxSelected>>', lambda event: label_selected.config(text=polygon_list[var_material.get()]))
combo_material.place(x=170,y=0,width=100,height=30)

button2 = ttk.Button(root, text="확인",command=selectPolyGon)
button2.place(x=275,y=0,width=50,height=30)

button3 = ttk.Button(root, text="삭제",command=deletePolyGon)
button3.place(x=325,y=0,width=50,height=30)

canvas.bind("<Button-1>",callback_mouse)
root.mainloop()

