from tkinter import *
import dbmodule
import tkinter.ttk as ttk
from tkinter import messagebox
def theApp():

    app = Tk()
    app.geometry("1080x1336")
    app.title("gestion des approvisionnements de stock")

    #product name
    e1 = Entry(app)
    e1.place(x=100, y=10)
    Label(app, text="Produit").place(x=10, y=10)
    #sm
    e2 = Entry(app)
    e2.place(x=100,y=50)
    Label(app, text='Stock moyen').place(x=10, y=50)
    #csu
    e3 = Entry(app)
    e3.place(x=100, y=90)
    Label(app, text='cout stock uni').place(x=10, y=90)
    #pu
    e4 = Entry(app)
    e4.place(x=100, y=130)
    Label(app, text='prix uni').place(x=10, y=130)
    # client
    e5 = Entry(app)
    e5.place(x=100, y=170)
    Label(app, text='client').place(x=10, y=170)
    # fournisseur
    e6 = Entry(app)
    e6.place(x=100, y=210)
    Label(app, text='fournisseur').place(x=10, y=210)
    #product for scatter plot and forecast
    e7 = Entry(app)
    e7.place(x=100, y=480)
    Label(app, text='product').place(x=10, y=480)
    # regression lineaire the month prediction
    e8 = Entry(app)
    e8.place(x=100, y=550)
    Label(app, text='period').place(x=10, y=550)
    #SMA base
    e9 = Entry(app)
    e9.place(x=100, y=600)
    Label(app, text='base').place(x=10, y=600)
    # WMA weights
    e10 = Entry(app)
    e10.place(x=100, y=650)
    Label(app, text='weighs :\n separate \n comma').place(x=10, y=650)
    # Simple expo smoothing alpha
    e11 = Entry(app)
    e11.place(x=100, y=700)
    Label(app, text='Alpha').place(x=10, y=700)
    # stock de securite
    e12 = Entry(app)
    e12.place(x=550, y=450)
    Label(app, text='Coefficient de\n Rupture').place(x=450, y=450)

    def populate_inventory():
        p = e1.get()
        q = e2.get()
        sm = e3.get()
        csu = e4.get()
        cl = e5.get()
        f = e6.get()

        dbmodule.populate_inventory(p, q, sm, csu, cl, f)

    def scatter_plot():
        product = e7.get()
        dbmodule.scatterplot(product)
        pass


    def regression_simple():
        x = int(e8.get())
        product = e7.get()
        forecast = dbmodule.regression_simple(product,x)
        Label(app, text=forecast).place(x = 400,y=550)
        messagebox.showinfo(title=f'mois: {x}', message=f'forecast = {forecast}')
        pass
    def simple_moving_average():
        base = int(e9.get())
        product = e7.get()
        sma = dbmodule.simple_moving_average(product, base)
        forecast = sma[0]
        eam = sma[1]

        messagebox.showinfo(title=f'next month', message=f'forecast = {forecast}  \n eam = {eam} ')

    def weighted_moving_average():
        weighs = e10.get()
        weighs = weighs.split(",")
        weighs = [eval(i) for i in weighs]

        product = e7.get()
        wma = dbmodule.weighted_moving_average(product,len(weighs),weighs)
        forecast = wma[0]
        eam = wma[1]

        messagebox.showinfo(title=f'next month', message=f'forecast = {forecast}  \n eam = {eam} ')

    def simple_expo_smoothing():
        alpha = float(e11.get())
        product = e7.get()

        ses = dbmodule.simple_expo_smoothing(product,alpha)
        forecast = ses[0]
        eam = ses[1]
        messagebox.showinfo(title=f'next month', message=f'forecast = {forecast}  \n eam = {eam} ')

    def procurement_method():
        product = e7.get()
        abc = dbmodule.abc_vente()
        global method
        for i in range(len(abc[['product']])):
            if abc.iloc[i][0] == product:
                if abc.iloc[i][-1] == 'A':
                    method = ' Sueil + Stock de securite'
                elif abc.iloc[i][-1] == 'B' :
                    method = 'NdR + Stock de securite'
                else:
                    method = 'NdR'
        #maybe i can add here stock de securite and for each if, a label with method and ss if necessary

        messagebox.showinfo(title=f'procurement methode', message=f'methode dappro : {method}')

        pass
    def gestion_stock():
        product = e7.get()
        k = float(e12.get())
        SS = dbmodule.security_stock(product,k)
        messagebox.showinfo(title=f'Stock security', message=f'SS = {SS}')

    def treeview_abc_stock():
        df = dbmodule.abc_stock()
        popup = Toplevel()
        popup.grab_set()
        Top = Frame(popup, width=700, height=50, bd=8, relief="raise")
        Top.pack(side=TOP)
        Button_Group = Frame(popup, width=700, height=50)
        Button_Group.pack(side=TOP)
        Buttons = Frame(Button_Group, width=200, height=50)
        Buttons.pack(side=LEFT)
        Buttons1 = Frame(Button_Group, width=500, height=50)
        Buttons1.pack(side=RIGHT)
        Body = Frame(popup, width=700, height=300, bd=8, relief="raise")
        Body.pack(side=BOTTOM)
        # ==================================LABEL WIDGET=======================================
        txt_title = Label(Top, width=300, font=('arial', 24), text="Python - Display SQLite3 Data In TreeView")
        txt_title.pack()

        # ==================================LIST WIDGET & TREE========================================
        scrollbary = Scrollbar(Body, orient=VERTICAL)
        scrollbarx = Scrollbar(Body, orient=HORIZONTAL)

        tree = ttk.Treeview(Body)
        df_col = df.columns.values

        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)

        tree["columns"] = (df_col)
        counter = len(df)

        rowLabels = df.index.tolist()
        for x in range(len(df_col)):
            tree.column(x, width=100)
            tree.heading(x, text=df_col[x])
            # generating for loop to print values of dataframe in treeview column.
        for i in range(counter):
            tree.insert('', i, text=rowLabels[i], values=df.iloc[i, :].tolist())
        tree.pack()
    def treeview_abc_vente():
        df = dbmodule.abc_vente()
        popup = Toplevel()
        popup.grab_set()
        Top = Frame(popup, width=700, height=50, bd=8, relief="raise")
        Top.pack(side=TOP)
        Button_Group = Frame(popup, width=700, height=50)
        Button_Group.pack(side=TOP)
        Buttons = Frame(Button_Group, width=200, height=50)
        Buttons.pack(side=LEFT)
        Buttons1 = Frame(Button_Group, width=500, height=50)
        Buttons1.pack(side=RIGHT)
        Body = Frame(popup, width=700, height=300, bd=8, relief="raise")
        Body.pack(side=BOTTOM)
        # ==================================LABEL WIDGET=======================================
        txt_title = Label(Top, width=300, font=('arial', 24), text="Python - Display SQLite3 Data In TreeView")
        txt_title.pack()

        # ==================================LIST WIDGET & TREE========================================
        scrollbary = Scrollbar(Body, orient=VERTICAL)
        scrollbarx = Scrollbar(Body, orient=HORIZONTAL)

        tree = ttk.Treeview(Body)
        df_col = df.columns.values

        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)

        tree["columns"] = (df_col)
        counter = len(df)

        rowLabels = df.index.tolist()
        for x in range(len(df_col)):
            tree.column(x, width=100)
            tree.heading(x, text=df_col[x])
            # generating for loop to print values of dataframe in treeview column.
        for i in range(counter):
            tree.insert('', i, text=rowLabels[i], values=df.iloc[i, :].tolist())
        tree.pack()



    # addnew product
    Button(app, text='add or update product', command=populate_inventory).place(x=150, y=230)
    # call abc_stock method
    Button(app, text='Class ABC Stock', command=treeview_abc_stock).place(x=150, y=270)
    # call abc_vente method
    Button(app, text='Class ABC vente', command=treeview_abc_vente).place(x=150, y=310)
    #plot scatter
    Button(app, text='Scatter plot', command=scatter_plot).place(x=100, y=500)
    #procrumenet method for each product depending on its class
    Button(app, text='procrumenet method', command=procurement_method).place(x=150, y=350)
    #regression lineaire simple button
    Button(app, text='regression lineaire', command=regression_simple).place(x=250, y=550)
    # simple moving average button
    Button(app, text='SMA', command=simple_moving_average).place(x=250, y=600)
    # weighted moving average button
    Button(app, text='WMA', command=weighted_moving_average).place(x=250, y=650)
    # simple expo smoothing
    Button(app, text='SES', command=simple_expo_smoothing).place(x=250, y=700)
    # simple expo smoothing
    Button(app, text='stock security ', command=gestion_stock).place(x=700, y=450)

    app.mainloop()

theApp()