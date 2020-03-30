import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from . import covid_conf_analysis as cv
#import covid_conf_analysis as cv
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]
#external_stylesheets = [dbc.themes.COSMO]

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid 19 Dashboard'

server = app.server

covid = cv.covid_conf_analysis()
covid_raw_ts = covid.get_raw_data()
covid_countries = list(sorted(covid.get_country_list()))

def get_covid_data():
    global covid_raw_ts
    global covid_countries
    covid_raw_ts = covid.get_raw_data()
    covid_countries = list(sorted(covid.get_country_list()))



def fig(cntry='US'):
    #get_covid_data()
    covid_country = covid.get_data_for_cntry(cntry)
    current_cases = covid_country.iloc[-1,0]
    fig = go.Figure(
        data=[go.Bar(y=covid_country.iloc[:,0],x=covid_country.index)],
        layout_title_text="Confirmed covid Cases in {}: {}".format(cntry,current_cases)
    )
    return fig

def fig_world_trend(top=10,exclude_china=False,log_trans=False):
    #get_covid_data()
    total = covid.get_world_total()
    top_ts = covid.plot_top_countries(top,exclude_china,log_trans)
    df = top_ts.unstack().reset_index()
    df.columns = ['country','date','#cases']
    title = 'World Trend - Total Confirmed Cases: {}'.format(total)
    fig = px.line(df, y='#cases', x='date',color='country', title=title)
    return fig

def fig_compare_countries_daily_rate(cntry1='US',cntry2='Italy',cntry3='India'):
    df = covid.get_three_countries_daily_rate_for_comparison(cntry1,cntry2,cntry3)
    title = f"Comparison of {cntry1}, {cntry2} and {cntry3} daily cases as a % of country total"
    fig = px.bar(df, y='dailycases', x='date',color='country', title=title, barmode='group')
    return fig


#TODO
def fig_top_countries(top=5):
    pass

def fig_dead_rec_active_piechart():
    total_active = covid.get_overall_active()
    total_dead = covid.get_overall_dead()
    total_recovered = covid.get_overall_recovered()
    total_confirmed = total_active + total_dead +  total_recovered
    df = pd.DataFrame(data = [total_active,total_recovered,total_dead],
                        index = ['Active','Recovered','Dead'],
                        columns=['Total'])
    fig = px.pie(df, values='Total',
             names=df.index,
             labels=['Active','Recovered','Dead'],
             hole=.4,
             title='Overall Situation - Total Cases: {}'.format(total_confirmed),
             color=df.index,color_discrete_map={'Active':'indianred',
                                 'Recovered':'mediumseagreen',
                                 'Dead':'black'})
    fig.update_traces(textposition='inside', textinfo='percent+label',
                        textfont_size=10,showlegend=True,
                        insidetextorientation='horizontal')
    return fig

def generate_country_active_rec_dead_table(max_rows=250):
    dataframe = covid.get_country_active_conf_dead_data()
    return dbc.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe),max_rows))
        ])
    ],bordered=True,striped=True,responsive=True)


def get_page_heading_style():
    return {'backgroundColor': colors['background']}

def get_page_heading_div():
    return html.Div(style =get_page_heading_style(),children=[
                                get_page_heading_title(),
                                 get_page_heading_subtitle])

def get_page_heading_title():
    return html.H1(children='COVID-19 Dashboard',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def get_page_heading_subtitle():
    return html.Div(children='Visualize Covid-19 data generated from sources all over the world.',
                                         style={
                                             'textAlign':'center',
                                             'color':colors['text']
                                         })

def create_dropdown_list(normal_list=['T1','T2']):
    dropdown_list = []
    for cntry in sorted(covid.get_country_list()):
        tmp_dict = {'label':cntry,'value':cntry}
        dropdown_list.append(tmp_dict)
    return dropdown_list




def graph1():
    return dcc.Graph(
                            id='example-graph1',
                            figure=fig('US')
                        )

def graph2():
    return  dcc.Graph(
                            id='example-graph2',
                            figure=fig('India')
                        )

def graph3():
    return  dcc.Graph(
                            id='example-graph3',
                            figure=fig_world_trend(top=8,exclude_china=False,log_trans=False)
                        )

def graph4():
    return  dcc.Graph(
                            id='example-graph4',
                            figure=fig_compare_countries_daily_rate(cntry1='US',cntry2='Italy',cntry3='India')
                        )

def graph5():
    return  dcc.Graph(
                            id='example-graph5',
                            figure=fig_dead_rec_active_piechart()
                        )


def create_dropdown_list_num_top_country(normal_list=['T1','T2']):
    dropdown_list = []
    for count in range(1,21):
        tmp_dict = {'label':count,'value':count}
        dropdown_list.append(tmp_dict)
    return dropdown_list

def create_dropdown_list_num_top_china_flag():
    dropdown_list = [{'label':'Yes','value':'True'},
                {'label':'No','value':'False'}]
    return dropdown_list

def create_dropdown_list_num_top_log_graph_flag():
    dropdown_list = [{'label':'Yes','value':'True'},
                    {'label':'No','value':'False'}]

    return dropdown_list


def get_country_dropdown(id):
    if id == 1:
        value = 'US'
    elif id==2:
        value = 'India'
    elif id==6:
        value = 'US'
    elif id==7:
        value ='Italy'
    elif id==8:
        value ='India'

    return html.Div([
                        html.Label('Select Country'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list(covid_countries),
                            value=value
                        ),
                        html.Div(id='my-div'+str(id))
                    ])

def vw_how_many_country_dropdown(id):
    return html.Div([
                        html.Label('Top n Countries'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list_num_top_country(),
                            value=5
                        ),
                        html.Div(id='my-div'+str(id))
                    ])


def vw_show_china_flag_dropdown(id):
    return html.Div([
                        html.Label('Exclude China'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list_num_top_china_flag(),
                            value='False'
                        ),
                        html.Div(id='my-div'+str(id))
                    ])

def vw_show_log_graph_flag_dropdown(id):
    return html.Div([
                        html.Label('Log Graph'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list_num_top_log_graph_flag(),
                            value='False'
                        ),
                        html.Div(id='my-div'+str(id))
                    ])


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(get_page_heading_title(),md=12)
            ],
            align="center",
            style=get_page_heading_style()
        ),
        dbc.Row(
            [
                dbc.Col(get_page_heading_subtitle(),md=12)
            ],
            align="center",
            style=get_page_heading_style()
        ),
        html.Hr(),
        dbc.Button("Refresh Dataset", color="primary", className="mr-1",id="refresh-button"),
        dbc.Row([
            dbc.Col(html.Label('Button Pressed',id='button-pressed-label'),md=4)
        ]),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(graph5(),md=12,lg=6),
                dbc.Col(generate_country_active_rec_dead_table(),md=12,lg=6,style={'maxHeight': '400px', 'overflowY': 'scroll','position':'sticky','top':'0'})
            ],
            align="center",

        ),
        html.Hr(),
        dbc.Row(
            [

                dbc.Col(vw_how_many_country_dropdown(id=3), md=4),
                dbc.Col(vw_show_china_flag_dropdown(id=4), md=4),
                dbc.Col(vw_show_log_graph_flag_dropdown(id=5), md=4)
            ],
            align="center",
        ),
        dbc.Row(
            [

                dbc.Col(graph3(), md=12),
                #dbc.Col(graph5(), md=4)
            ],
            align="center",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(get_country_dropdown(id=1),md=6),
                dbc.Col(get_country_dropdown(id=2),md=6)
            ],
            #style={'width': '30px'},
        ),
        dbc.Row(
            [

                dbc.Col(graph1(), md=6),
                dbc.Col(graph2(), md=6),
            ],
            align="center",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(get_country_dropdown(id=6),md=4),
                dbc.Col(get_country_dropdown(id=7),md=4),
                dbc.Col(get_country_dropdown(id=8),md=4),
            ],
            #style={'width': '30px'},
        ),
        dbc.Row(
            [

                dbc.Col(graph4(), md=12)
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# app.layout = html.Div(style={'overflowX': 'scroll'},children=[
#     html.H4(children='Covid 19 Dataset'),
#     generate_table(covid_raw_ts)

# ])


# app.layout = html.Div([
#     html.Label('Dropdown'),
#     dcc.Dropdown(id='my-id',
#         options=create_dropdown_list(covid_countries),
#         value='US'
#     ),
#     html.Div(id='my-div')
# ])


@app.callback(
    Output(component_id='example-graph1',component_property='figure'),
    [Input(component_id='my-id1',component_property='value')]
)
def update_output_div(input_value):
    return fig(input_value)


@app.callback(
    Output(component_id='example-graph2',component_property='figure'),
    [Input(component_id='my-id2',component_property='value')]
)
def update_output_div(input_value):
    return fig(input_value)


@app.callback(
    Output(component_id='example-graph3',component_property='figure'),
    [Input(component_id='my-id3',component_property='value'),
    Input(component_id='my-id4',component_property='value'),
    Input(component_id='my-id5',component_property='value'),
    Input("refresh-button", "n_clicks")]
)
def update_output_div(top_value,china_flag,log_flag,n_clicks):
    if china_flag=='True':
        china_flag=True
    elif china_flag =='False':
        china_flag = False

    if log_flag=='True':
        log_flag=True
    elif log_flag =='False':
        log_flag = False

    print(top_value,china_flag,log_flag)
    return fig_world_trend(top=top_value,exclude_china=china_flag,log_trans=log_flag)

@app.callback(
    Output('button-pressed-label', "children"), [Input("refresh-button", "n_clicks")]
)
def on_button_click(n):
    if n is None:
        return "Click to refresh data from source"
    else:
        get_covid_data()
        return "Data refreshed from source."


@app.callback(
    Output(component_id='example-graph4',component_property='figure'),
    [Input(component_id='my-id6',component_property='value'),
    Input(component_id='my-id7',component_property='value'),
    Input(component_id='my-id8',component_property='value'),]
)
def update_output_div(cntry1,cntry2,cntry3):
    return fig_compare_countries_daily_rate(cntry1,cntry2,cntry3)


if __name__ == '__main__':
    app.run_server(host= '0.0.0.0',debug=True)
