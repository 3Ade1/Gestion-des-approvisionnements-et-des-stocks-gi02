import math
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


connec = sqlite3.connect("stock.db")
c = connec.cursor()


#c.execute('create table if not exists inventory (product text PRIMARY KEY UNIQUE, Sm integer, Csu integer, Pu integer, client text, fournisseur text)')

temp_inventory = pd.read_csv('inventory.csv')
temp_inventory.to_sql('inventory', connec, if_exists='replace', index=False)

################ little manoeuvre to create table inventory with primary key product ###############3######
c.executescript('''
    PRAGMA foreign_keys=ON;

    BEGIN TRANSACTION;
    ALTER TABLE inventory RENAME TO old_inventory;
    CREATE TABLE inventory (product TEXT unique primary key, Sm integer,Csu integer,Pu integer,client text,fournisseur text);

    INSERT INTO inventory SELECT * FROM old_inventory;

    DROP TABLE old_inventory;
    COMMIT TRANSACTION;

    PRAGMA foreign_keys=on;''')
################# ened of manoeuvre###########################################################################3

temp_sortie = pd.read_csv('sortie_mensuel.csv')
temp_sortie.to_sql('sortie_mensuel', connec, if_exists='replace', index = False)

################ little manoeuvre to create table sortie mensuel with foreign key product ###############3######
c.executescript('''
    PRAGMA foreign_keys=ON;

    BEGIN TRANSACTION;
    ALTER TABLE sortie_mensuel RENAME TO old_sortie_mensuel;
    CREATE TABLE sortie_mensuel (product TEXT unique , janvier integer, fevrier integer, mars integer, avril integer,mai integer,juin integer,juillet integer,aout integer,septembre integer,octobre integer ,novembre integer,decembre integer, foreign key(product) references inventory(product));

    INSERT INTO sortie_mensuel SELECT * FROM old_sortie_mensuel;

    DROP TABLE old_sortie_mensuel;
    COMMIT TRANSACTION;

    PRAGMA foreign_keys=on;''')
################# ened of manoeuvre###########################################################################3


def classify_product(percentage):
    """Apply an ABC classification to each product based on
    its ranked percentage revenue contribution. Any split
    can be used to suit your data.

    :param percentage: Running percentage of revenue contributed
    :return: ABC classification
    """

    if percentage > 0 and percentage <= 0.8:
        return 'A'
    elif percentage > 0.8 and percentage <= 0.9:
        return 'B'
    else:
        return 'C'
def abc_stock():
    query = """SELECT      
        product,
        Csu,
        Sm
        From inventory
    ORDER BY Csu*Sm DESC
    """

    df = pd.read_sql(query, con=connec)
    df['Cs'] = df['Sm'] * df['Csu']
    df['Cs_cumsum'] = df['Cs'].cumsum()
    df['running_freq'] = df['Cs_cumsum']/(df['Cs'].sum())
    df.head()
    df['abc_class'] = df['running_freq'].apply(classify_product)
    return(df)
def abc_vente():
    query = """
    SELECT inventory.product, janvier, fevrier, mars, avril, mai, juin, juillet, aout, septembre, octobre , novembre, decembre, inventory.Pu
    FROM inventory
    INNER JOIN sortie_mensuel on sortie_mensuel.product = inventory.product
    """
    df = pd.read_sql(query, con=connec)

    df['cons_annuel'] = df.sum(axis=1,skipna=True)-df['Pu']

    df['revenue'] = df['cons_annuel'] * df['Pu']

    df = df.sort_values('revenue', ascending=False)

    df['revenue_cumsum'] = df['revenue'].cumsum()
    df['frequency'] = df['revenue'] / df['revenue'].sum()

    df['running_revenue'] = df['revenue'].cumsum()
    df['running_freq'] = df['frequency'].cumsum()
    df.head()
    df['abc_class'] = df['running_freq'].apply(classify_product)

    return (df[['product', 'cons_annuel', 'Pu', 'revenue', 'running_revenue', 'frequency', 'running_freq', 'abc_class']])



def scatterplot(product):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    months = list(df.columns.values)
    values = list(df.loc[product])
    plt.scatter(months,values, c='DarkBlue') # basically imma scatter two lists cuz i cant scatter a panda df
    plt.show()

#
def regression_simple(product,x):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    months = list(df.columns.values)
    values = list(df.loc[product])
    for i in range(1,len(months)+1):
        months[i-1] = i
    slope, intercept, r_value, p_value, std_err = stats.linregress(months,values)
    def predict(x):
        return slope * x + intercept
    return(round(predict(x)))

#
def simple_moving_average(product,base):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    values = list(df.loc[product])

    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []

    # Loop through the array to consider
    # every window of size 3
    while i < len(values) - base :
        # Store elements from i to i+base
        # in list to get the current window
        window = values[i: i + base]

        # Calculate the average of current window
        window_average = round(sum(window) / base, 2)
        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)

        # Shift window to right by one position
        i += 1
    result=0
    for i in range(len(moving_averages)):
        ecarts = (abs((values[i+base]) - (moving_averages[i])))
        result = result + ecarts

    eam = (result/ base)
    forecast = 0
    for i in range(base):
        forecast = forecast + values[-i-1]


    return (round(forecast/base,2),round(eam,2)) #i shouldnt return moving averages -1 nooo
    pass

#
def weighted_moving_average(product,base,weigh):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    months = list(df.columns.values)
    values = list(df.loc[product])

    i = 0

    # Initialize an empty list to store moving averages
    moving_averages = []

    # Loop through the array to consider
    # every window of size 3
    while i < len(values) - base:
        # Store elements from i to i+base
        # in list to get the current window
        window = values[i: i + base]

        # Calculate the average of current window
        for j in range(len(weigh)):
            #print(weigh[j],window[j])
            window[j] = weigh[j] * window[j]

        window_average = round(sum(window) / sum(weigh), 2)
        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)
        # Shift window to right by one position
        i += 1

    result = 0
    for i in range(len(moving_averages)):
        ecarts = (abs((values[i + base]) - (moving_averages[i])))
        result = result + ecarts
    eam = (result / base)

    forecast = 0
    for i in range(base):
        forecast = forecast + weigh[-i-1] * values[-i - 1]

    return (round(forecast / sum(weigh), 2), round(eam, 2))
    pass


def security_stock(product, k):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    dp = pd.read_csv('delai.csv')
    dp = dp.set_index('product')
    df['std_cons'] = (df.std(axis=1))
    df['mean_cons'] = (df.sum(axis=1))/12

    dp['std_delai'] = (dp.std(axis=1))
    dp['mean_delai'] = (dp.sum(axis=1))/12
    print(dp.loc[product,'mean_delai'])


    SS = k * math.sqrt(pow(df.loc[product,'mean_cons'],2)*pow(dp.loc[product,'std_delai'],2)+dp.loc[product,'mean_delai']*pow(df.loc[product,'std_cons'],2))

    return(round(SS,2))

# simple exponential smoothing gives forecast for january of new year using 12 months data
def simple_expo_smoothing(product,alpha):
    df = pd.read_csv('sortie_mensuel.csv')
    df = df.set_index('product')
    df1 = pd.read_csv('previsions.csv')
    df1 = df1.set_index('product')
    dt = list(df.loc[product])
    pt = list(df1.loc[product])
    ecart = 0
    for i in range(len(df)+2):
        try:
            pt[i+1]=(alpha*dt[i] + (1-alpha)*pt[i])
            ecart = ecart + abs(dt[i]-pt[i])
        except:
            ecart = ecart + abs(dt[i] - pt[i])
            pt.append(alpha*dt[i] + (1-alpha)*pt[i])
    eam = ecart/len(dt)
    return[round(pt[-1],2),round(eam,2)]

def populate_inventory(p, sm, csu, pu,cl,f):
    with connec:
        c.execute("INSERT OR REPLACE INTO inventory VALUES (?,?,?,?,?,?)", (p, sm, csu, pu,cl,f))

security_stock('p1',0.9)