#!/usr/bin/env python3
#
#
#   Script for generating plots from processed L1 csv polra data
#  Call this function with:
#               python interval_L1plotter.py filename_processed.csv
#  After already running the processing to ouput this file.
#
import base64
import pandas as pd
import ntpath
import sys
from flask import Flask, send_from_directory
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import webbrowser

#### Processed Datafile CSV ####
datfile = sys.argv[1]
measperiod = sys.argv[2]

### only for non-server testing / prototyping
# from tkinter import Tk     # from tkinter import Tk for Python 3.x
# from tkinter.filedialog import askopenfilename
# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# datfile = askopenfilename() # show an "Open" dialog box and return the path to the selected file
###  remove these imports when used without user
L1path,L1filename = ntpath.split(datfile)  # split L0path and L0filename

# Define some constants..
mapboxtoken = 'pk.eyJ1IjoiaG91dHpkIiwiYSI6ImNrY3FvaXVlNDBzdWYycXQ2NTN3Mnl4dmwifQ.1IjaVyqUk6yi8SJSkeuW_Q'

defaultplotoption = ['TBV (K)','TBH (K)']  # the starting (defualt) value for the dropdown of plot variable

# Load the TRT logo and convert for display on dash app
logopng = './logo.png'
logobase64 = base64.b64encode(open(logopng, 'rb').read()).decode('ascii')

# Load the datafile into a pandas dataframe
poldf = pd.read_csv(datfile,header=0,na_values=['NaN','nan'])

poldf['timestamp']=pd.to_datetime(poldf['# posix time'],unit='s')
poldf = poldf.set_index('timestamp')
poldf = poldf.drop(['# posix time'], axis=1)
#poldf = poldf.dropna(subset = ['TBV (K)'])

poldf.sort_index(inplace=True)
poldf = poldf.resample(measperiod+'T', label='left').mean()
print(poldf)
print(poldf.dtypes)
# Get the possible variables for plotting
columns = poldf.columns
plotoptions = columns



def updatefigts(poldf,varstr):
    if isinstance(varstr,str):  # single string (1 values selected)
        var1=poldf[varstr]
        unitstr=varstr
        fig = go.Figure(go.Scatter(x=poldf.index, y=var1,fill="none",
                                         mode='lines+markers'
                                         #marker=dict(color=var1,colorscale=cscale,opacity=opacity,size=10,colorbar=dict(thickness=30),cmin=cminval,cmax=cmaxval),
                                         #text = var1,
                                         #hoverlabel=dict(bgcolor='#313335',font_size=16),
                                        )
                        )
    else:
        fig = go.Figure()
        for i in range(len(varstr)):
            fig.add_trace(go.Scatter(x=poldf.index,y=poldf[varstr[i]],fill="none",
                                    mode='lines+markers',name = varstr[i])
            )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
fig = updatefigts(poldf,defaultplotoption)
###### set up Dash app #######
server = Flask(__name__)
external_stylesheets = 'https://use.typekit.net/dvv2gfc.css'
app = dash.Dash(server=server)#,external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div([html.Img(src='data:image/png;base64,{}'.format(logobase64),style={'height':'10vh'}),],style={'textAlign':'center','backgroundColor':'#3B86C0'}),
        #html.Div([html.H1("pypolra: PROCESSOR FOR PORTABLE L-BAND RADIOMETER")],style={'font-family':'athelas','font-weight':'400','margin-top':'50px','textAlign':'center','height':'10vh','verticalAlign':'middle'}),
        html.Div([html.H1(L1filename)],style={'font-weight':'400','margin-top':'50px','textAlign':'center','height':'10vh','verticalAlign':'middle'}),
        html.Div([
                dcc.Dropdown(id='data-dropdown',options=plotoptions,value=defaultplotoption,multi=True,style={"width": "92%","verticalAlign": "middle","textAlign": "center","margin": "20px",},),
                dcc.Loading(children=[
                    dcc.Graph(id= 'Map Overlay',
                        style={
                         'height': '80vh',
                        },
                        figure= fig),
                ], color="#51B4EB"),

        ]),
        html.Div([html.P("Copyright 2022 TERRARAD TECH AG, Zürich Switzerland",style={"vertical-align": "middle"})],style={'font-family':'athelas','font-weight':'400','color':'white','text-align':'center','backgroundColor':'#3B86C0','margin-top':'10px','height':'8vh',"vertical-align": "middle"}),
    ],

)



@app.callback(
    [Output(component_id='Map Overlay',component_property='figure'),
     Output(component_id='data-dropdown',component_property='multi')],
    [
    Input("data-dropdown", "value"),
    ]
    )
def update_output(varstr):
    fig = updatefigts(poldf,varstr)
    multi = True
    return [fig,multi]

if __name__ == "__main__":
    webbrowser.open('0.0.0.0:8080', new=2)
    app.run_server(debug=False, port=8080, host='0.0.0.0')
