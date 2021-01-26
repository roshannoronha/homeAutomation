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

from categories.lighting.lights import getBridge, setBrightness, setColor, getCurrentColor, getCurrentBrightness
from categories.calendar.googleCalendar import getCalendarEvents
from categories.investing.investing import getCurrentFinancialInfo, stockDataViz, networthHistoryViz


b, groupNums = getBridge()
#currentColor = getCurrentColor()
calendarData = getCalendarEvents(Path("C:\\homeAutomation\\categories\\calendar\\calendarInfo.txt"))
overview, holdings = getCurrentFinancialInfo()


app = dash.Dash(__name__, external_stylesheets= ["bootstrap.css"])

# investingCard = html.Div([
    
#     dbc.CardGroup([

#         dbc.Card(color = 'dark', inverse = True, children = [

#             dbc.CardBody([

#                 html.H4('CURRENT NETWORTH'),
#                 html.H5(currentNetworth),
#             ]),
#         ]),

#         dbc.Card(color = 'dark', inverse = True, children = [

#             dbc.CardBody([

#                 html.H4('CURRENT NETWORTH'),
#                 html.H5(currentNetworth),
#             ]),
#         ]),
#     ])
# ])

printerOne = dbc.Card(color= 'dark', inverse= True, children=[

    dbc.CardBody([

        html.Center(children = [

            html.Div(children = [
                html.H5('Ultimaker-2214b7'),
                html.Iframe(id = 'printerOne', className = "printerWindow--one", src= "http://192.168.128.188:8080/?action=stream", height = 604, width = 804),
            ]),
        ]),
    ]),
]),

printerTwo = dbc.Card(color= 'dark', inverse= True, children=[

    dbc.CardBody([

        html.Center(children = [

            html.Div(children = [
                html.H5('Ultimaker-22a1d8'),
                html.Iframe(id = 'printerTwo', className = "printerWindow--one", src= "http://192.168.128.175:8080/?action=stream", height = 604, width = 804),
            ]),
        ]),
    ]),
]),    

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
            },

            #sets the slider to the current brightness of the bulbs
            value= 0
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

            #sets to slider to the current color of the bulbs
            value= getCurrentColor(b, groupNums),
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
                #'display': 'none',
            },

            style_cell = {
                'backgroundColor': 'rgba(0,0,0,0)',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': 20,
                #'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
            },

            style_data_conditional = [
                {
                    'if': {
                        'state': 'active'
                    },

                    'backgroundColor': 'transparent',
                    'border-top': '1px solid rgb(211, 211, 211)',
                    'border-bottom': '1px solid rgb(211, 211, 211)',
                }
            ],  
        ),

        html.Div(id='calendar-container'),
    ]),
])

tabs_styles = {
    'height': '70px',
    'font-size': '20px',
}

tab_style = {
    'backgroundColor': 'rgba(0,0,0,0.1)',
    'color': 'white',
    'borderTop': 'none',
    'borderBottom': 'none',
    'padding': '15px',
    'borderTop': 'none',
    'borderLeft': '4px solid #d6d6d6',
    'borderRight': '4px solid #d6d6d6',
    'border-color': 'rgba(0,0,0,0)',

}

tab_selected_style = {
    'borderTop': 'none',
    'borderLeft': '4px solid #d6d6d6',
    'borderRight': '4px solid #d6d6d6',
    'borderBottom': 'none',
    'backgroundColor': 'rgba(0,0,0,0.5)',
    'color': 'white',
    'padding': '15px',
    'fontWeight': 'bold',
    'border-color': 'rgba(0,0,0,0)',
}

app.layout = html.Div([
    dcc.Tabs(id='navTabs', value='investing', children=[
        dcc.Tab(label='DASHBOARD', value='dashboard', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='INVESTING', value='investing', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='3D PRINTERS', value='printers', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='GAMING', value='gaming', style=tab_style, selected_style=tab_selected_style),

    ], style=tabs_styles),
    
    html.Div(id='tabs'),

])

@app.callback(dash.dependencies.Output('tabs', 'children'), dash.dependencies.Input('navTabs', 'value'))
def displayContent(navTabs):

    if navTabs == 'dashboard':

        return html.Div([
            dbc.Row(dbc.Col(lightingCard, width= {'size': 10, 'offset': 1}, style={'padding': 40})),
            dbc.Row(dbc.Col(calendarCard, width= {'size': 10, 'offset': 1}, style={'padding': 40})),
        ])
    
    elif navTabs == 'investing':

        #overview should be networth + wealthica data
        overviewCards = []
        for item in overview.keys():
            overviewCards.append(dbc.Card(color = 'dark', inverse = True, children = [
                dbc.CardBody([
                    html.Center(html.H3(item.upper())),
                    html.Center(
                        html.Listing([
                            html.H4(overview[item], style= {'font-size': '40px'}),
                        ]),
                    ),
                ]),
            ]))
        
        holdingCards = []
        for item in holdings.keys():
            
            moreKeys = isinstance(holdings[item], str)
            
            accountInfo = []

            if moreKeys == False:
                for account in holdings[item].keys():
                    accountInfo.append(html.U(html.H4(account))),
                    accountInfo.append(html.H5(holdings[item][account]))
            
                holdingCards.append(dbc.Card(color = 'dark', inverse = True, children = [
                    dbc.CardBody([
                        html.Center(html.H3(item.upper())),
                        html.Listing(accountInfo),
                    ])
                ]))
            
            else:
                holdingCards.append(dbc.Card(color = 'dark', inverse = True, children = [
                    dbc.CardBody([
                        html.Center(html.H3(item.upper())),
                        html.Listing([
                            html.U(html.H4("Current Value")),
                            html.H5(holdings[item]),
                        ]),
                    ]),
                ]))
        
        stockInfoCard = dbc.Card(color = 'dark', inverse = True, children = [
            dbc.CardBody([
                dcc.Graph(figure = stockDataViz(), config = {'displayModeBar': False})
            ]),
        ])

        networthHistoryCard = dbc.Card(color = 'dark', inverse = True, children = [
            dbc.CardBody([
                dcc.Graph(figure = networthHistoryViz(), config = {'displayModeBar': False})
            ]),
        ])

        return html.Div([

            dbc.Row(dbc.Col(dbc.CardDeck(overviewCards), style={'padding': 40})),
            dbc.Row(dbc.Col(dbc.CardDeck(networthHistoryCard), style={'padding': 40})),       
            dbc.Row(dbc.Col(dbc.CardDeck(holdingCards), style={'padding': 40})),
            dbc.Row(dbc.Col(stockInfoCard, style={'padding': 40}))
        ])

    
    elif navTabs == 'printers':
        return html.Div([
            dbc.Row([
                dbc.Col(printerOne, width= {'size': 6}, style={'padding': 40}),
                dbc.Col(printerTwo, width= {'size': 6}, style={'padding': 40}),
            ])
        ])

    #elif navTabs == 'gaming':


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