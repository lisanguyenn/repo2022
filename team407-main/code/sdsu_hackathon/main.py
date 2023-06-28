import pandas as pd
import plotly.graph_objects as go
import os

#instantiate file local directory
path = os.path.realpath('..')
path = path + '/sdsu_hackathon'

'''
First visualization, medicare patients in San Diego with chronic conditions
'''

df = []
for i in ['2008','2009','2010']:
    for ii in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']:
        #may need to change path from relative location
        df_=pd.read_csv(path+ '/data/DE1_0_' + i + '_Beneficiary_Summary_File_Sample_'+ ii +'.csv')
        df_['year'] = i
        df_['sample'] = ii
        df.append(df_)
df = pd.concat(df)

#subset the dataframe into our area
df=df.loc[(df['SP_STATE_CODE']==5)&(df['BENE_COUNTY_CD']==470)]


#how many unique ids?- 17072
df['DESYNPUF_ID'].nunique()
#how many had alzheimers (and no stroke)?- 6123
df.loc[(df['SP_ALZHDMTA']==1) & (df['SP_STRKETIA']!=1)]['DESYNPUF_ID'].nunique()
#how many had stroke (and no alzheimers)?- 881
df.loc[(df['SP_ALZHDMTA']!=1) & (df['SP_STRKETIA']==1)]['DESYNPUF_ID'].nunique()
#how many had both?- 859
df.loc[(df['SP_ALZHDMTA']==1) & (df['SP_STRKETIA']==1)]['DESYNPUF_ID'].nunique()

#vis 1
fig= go.Figure()
labels = ["Other Chronic Conditions","Alzheimer's ", "Stroke", "Alzheimer's  & Stroke"]
parents = ['','','','']
fig.add_trace(go.Treemap(
    labels = labels,
    parents=parents,
    values =  [9209, 6123,881, 859],
    root_color="white",
    textinfo = "label+value"
))
fig.update_layout({'title': 'San Diego Chronic Conditions Medicare Recipients (2008-2010)',
                       "showlegend": True},
    treemapcolorway = ["firebrick", "lightsteelblue","lightsteelblue","lightsteelblue"],
    margin = dict(t=50, l=100, r=100, b=500),
    font=dict(family="Helvetica",
                size=20,
                color="rgb(50,50,50)"),
                      title={'y': 0.95,
                             'x': 0.45,
                             'xanchor': 'center',
                             'yanchor': 'top'},
)
fig.show()

'''
Second visualization, relevant EMS calls per year
'''
#load data
df = pd.read_csv(path + '/data/fd_problem_nature_agg_datasd_v1.csv')

#suubset to relevant problem calls
df_ss=df.loc[df['problem'].str.contains('Stroke')|df['problem'].str.contains('Fainting')|df['problem'].str.contains('Seizures')|df['problem'].str.contains('Convulsions')]
df_ss['count'] = 1
df__=df_ss.groupby(['year_response']).sum()['count'].reset_index()

#vis 2
fig= go.Figure()
fig.add_trace(go.Scatter(
    x = df__['year_response'][1:],
    y= df__['count'][1:],
    line=dict(color='firebrick')))
fig.add_hline(y=59, line_width=0.5, line_color="black", name='title',opacity=0.7)
fig.add_annotation(x=2008, y=59,
            text="Avg - 59 calls per year",
            showarrow=False,
            yshift=10)
fig.update_layout({'title': 'San Diego EMS calls: fainting, seizures, or convulsions',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                       "showlegend": False},
    font=dict(family="Helvetica",
                size=12,
                color="rgb(50,50,50)"),
                      title={'y': 0.95,
                             'x': 0.45,
                             'xanchor': 'center',
                             'yanchor': 'top'},
)

fig.show()
