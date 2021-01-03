import dash
from dash_bootstrap_components._components.CardBody import CardBody
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Center import Center
from dash_html_components.Div import Div
import plotly.express as px
import plotly.io as pio
import pandas as pd
import dash_table
from pathlib import Path

from categories.lighting.lights import getBridge, setBrightness, setColor
from categories.calendar.googleCalendar import getCalendarEvents


b, groupNums = getBridge()
#currentColor = getCurrentColor()
calendarData = getCalendarEvents(Path("C:\\homeAutomation\\categories\\calendar\\calendarInfo.txt"))

external_stylesheets = ["bootstrap.css"]

app = dash.Dash(__name__, external_stylesheets= external_stylesheets)

investingCard = dbc.Card(color = 'dark', inverse = True, children = [

    dbc.CardBody([

        html.H4('INVESTING'),

        html.Center(children = [

            html.Div(children = [
                html.Iframe(id = 'investingWindow', className = "investingWindow--one", src= "https://app.wealthica.com/addons/wealthica/wealthica-balance-sheet-addon", height = 1000, width = 1000),
            ])
        ]),
    ])  
])

threeDPrinterCard = dbc.Card(color= 'dark', inverse= True, children=[

    dbc.CardBody([

        html.H4('3D PRINTERS'),

        html.Center(children = [

            html.Div(children = [
                html.H5('Ultimaker-2214b7'),
                html.Iframe(id = 'printerOne', className = "printerWindow--one", src= "http://192.168.128.188:8080/?action=stream", height = 604, width = 804),
            ]),
        ]),
    ]),  
    
])

lightingCard = dbc.Card(color= 'dark', inverse= True, children=[

    dbc.CardBody([
        
        html.H4('LIGHTING'),
        dcc.Slider(
            id="lightSlider",
            min = 0,
            max = 100,
            step = 1,
            marks={
                0: "OFF",
                25: "25%",
                50: "50%",
                75: "75%",
                100: "100%",
            }
        ),

        html.Div(id='light-output-container'),

        dcc.Slider(
            id="colorSlider",
            min = 153,
            max = 500,
            step = 1,
            marks={
                153: "IVORY",
                210: "DAYLIGHT",
                267: "COOL WHITE",
                324: "WARM WHITE",
                381: "INCANDESCENT",
                500: "CANDLELIGHT",
            },
            #value= currentColor,
        ),

        html.Div(id='color-output-container'),
    ]),
])

calendarCard = dbc.Card(color= 'dark', inverse= True, children=[

    dbc.CardBody([

        html.H4("CALENDAR"),

        dash_table.DataTable(
            id= 'calendar',
            columns = [{"name": i, "id": i} for i in calendarData.columns],
            data = calendarData.to_dict("rows"),
            editable = False,
            
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'rgba(0,0,0,0)',
                'fontWeight': 'bold',
                'border': '1 px',
                'display': 'none',
            },

            style_cell = {
                'backgroundColor': 'rgba(0,0,0,0)',
                'color': 'white',
                'textAlign': 'center'
            },
        ),

        html.Div(id='calendar-container'),
    ]),
])

app.layout = html.Div([
    dbc.Row(dbc.Col(lightingCard, width= {'size': 10, 'offset': 1}, style={'padding': 20})),
    dbc.Row(dbc.Col(calendarCard, width= {'size': 10, 'offset': 1}, style={'padding': 20})),
    dbc.Row(dbc.Col(threeDPrinterCard, width= {'size': 10, 'offset': 1}, style={'padding': 20})),
    dbc.Row(dbc.Col(investingCard, width= {'size': 10, 'offset': 1}, style={'padding': 20}))
])

@app.callback(dash.dependencies.Output('light-output-container', 'children'), [dash.dependencies.Input('lightSlider', 'value')])
def update_light(value):

    if (value is not None):
        setBrightness(b, groupNums, value)

@app.callback(dash.dependencies.Output('color-output-container', 'children'), [dash.dependencies.Input('colorSlider', 'value')])
def update_color(value):

    if (value is not None):
        setColor(b, groupNums, value)
   
if __name__ == '__main__':
    app.run_server(debug=True)