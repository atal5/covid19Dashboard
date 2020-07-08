import sys
sys.path.append('D:/Developer/covid19/GITHUB/covid19app/app/data_handling')
#print(sys.path)
# insert at 1, 0 is the script path (or '' in REPL)
#sys.path.insert(1, 'C:/Users/ragha/Developer/covid19/GITHUB/covid19app/app/covid_conf_analysis')
#sys.path.append("path_to_directory")
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#from covid_conf_analysis import covid_conf_analysis as cv
import covid_conf_analysis as cv
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

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
        layout_title_text="Confirmed covid Cases in {}: {:,}".format(cntry,current_cases)
    )
    #fig = px.line(df, y='#cases', x='date',color='country', title=title)
    return fig

def fig_world_trend(top=10,exclude_china=False,log_trans=False):
    #get_covid_data()
    total = covid.get_world_total()
    top_ts = covid.plot_top_countries(top,exclude_china,log_trans)
    df = top_ts[40:].unstack().reset_index()
    df.columns = ['country','date','#cases']
    title = 'World Trend - Total Confirmed Cases: {:,}'.format(total)
    fig = px.line(df, y='#cases', x='date',color='country', title=title,height=600,)
    fig.update_layout(title_x=0.5)
    return fig

def fig_compare_countries_daily_rate(cntry1='US',cntry2='Italy',cntry3='India'):
    df = covid.get_three_countries_daily_rate_for_comparison(cntry1,cntry2,cntry3)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').iloc[-30:,:]
    df = df.reset_index(drop=True)
    title = f"Comparison of {cntry1}, {cntry2} and {cntry3} daily cases as a % of country total"
    fig = px.bar(df, y='dailycases', x='date',color='country', title=title, barmode='group')
    fig.update_layout(yaxis_fixedrange = True,
                    xaxis_fixedrange = True,
                    xaxis_tickmode='linear',title_x=0.5,height=600)
    return fig


#TODO
def fig_top_countries(top=5):
    pass

def fig_dead_rec_active_piechart():
    total_active = covid.get_overall_active()
    total_dead = covid.get_overall_dead()
    total_recovered = covid.get_overall_recovered()
    total_confirmed = total_active + total_dead +  total_recovered
    print("updating figure pie chart")
    df = pd.DataFrame(data = [total_active,total_recovered,total_dead],
                        index = ['Active','Recovered','Dead'],
                        columns=['Total'])
    fig = px.pie(df, values='Total',
             names=df.index,
             labels=['Active','Recovered','Dead'],
             hole=.4,
             title='Overall Situation - Total Cases: {:,}'.format(total_confirmed),
             color=df.index,color_discrete_map={'Active':'indianred',
                                 'Recovered':'mediumseagreen',
                                 'Dead':'black'})
    fig.update_traces(textposition='inside', textinfo='percent+label',
                        textfont_size=10,showlegend=True,
                        insidetextorientation='horizontal')
    fig.update_layout(title_x=0.5)
    return fig

def fig_dead_by_country():
    df = covid.get_latest_dead()
    total_dead = df.num_dead.sum()
    df = df[df.num_dead > 100]
    df = df.sort_values('num_dead',ascending=False)[:25]
    df = df.sort_values('num_dead',ascending=True)
    fig = px.bar(df, x="num_dead", y=df.index, orientation='h',text='num_dead')
    fig.update_layout(title=f'Number of dead by country (Top 25), Total Dead: {total_dead:,}',title_x=0.5,
                    yaxis_title='',xaxis_title='',
                    yaxis_tickfont = dict(size=9),
                    yaxis_fixedrange = True,
                    xaxis_fixedrange = True,
                    #xaxis_autorange='reversed',
                    xaxis_showticklabels=False,
                    xaxis_showgrid=False,
                    #xaxis_title=False,
                    yaxis_side='left',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside',marker_color='black')
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


def fig_logarithmic_trend():
    df = covid.get_dataset_for_log_trend()
    new_df = df.dropna(axis='columns',how='all')
    new_df = new_df.dropna(axis='rows',how='all')
    new_df = new_df.drop('Date',axis='columns')
    log_df = new_df.apply(np.log10,axis='columns')
    df = log_df.iloc[:50,5:]
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col],
                            mode='lines',
                            name=col))


    fig.add_trace(go.Scatter(x=log_df[:15].index, y=log_df.iloc[:15,0],
                            mode='lines',
                            name='',line=dict(color='grey',dash='dot'),showlegend=False))

    fig.add_trace(go.Scatter(x=log_df[:30].index, y=log_df.iloc[:30,3],
                            mode='lines',
                            name='',line=dict(color='grey',dash='dot'),showlegend=False))

    fig.add_trace(go.Scatter(x=log_df[:40].index, y=log_df.iloc[:40,2],
                            mode='lines',
                            name='',line=dict(color='grey',dash='dot'),showlegend=False))

    fig.add_trace(go.Scatter(x=log_df[:45].index, y=log_df.iloc[:45,4],
                            mode='lines',
                            name='',line=dict(color='grey',dash='dot'),showlegend=False))

    fig.add_trace(go.Scatter(x=log_df[:50].index, y=log_df.iloc[:50,1],
                            mode='lines',
                            name='',line=dict(color='grey',dash='dot'),showlegend=False))

    annotations = []

    # Adding labels

    annotations.append(dict(x=14, y=6.25,
                                xanchor='left', yanchor='middle',
                                text='Doubles Every Day',
                                font=dict(family='Arial',
                                            size=16),
                                showarrow=False))

    annotations.append(dict(x=29, y=6.4,
                                xanchor='left', yanchor='middle',
                                text='... Every 2 Days',
                                font=dict(family='Arial',
                                            size=16),
                                showarrow=False))

    annotations.append(dict(x=39, y=5.95,
                                xanchor='left', yanchor='middle',
                                text='... Every 3 Days',
                                font=dict(family='Arial',
                                            size=16),
                                showarrow=False))

    annotations.append(dict(x=44, y=4.7,
                                xanchor='left', yanchor='middle',
                                text='... Every 5 Days',
                                font=dict(family='Arial',
                                            size=16),
                                showarrow=False))

    annotations.append(dict(x=47, y=4.05,
                                xanchor='left', yanchor='middle',
                                text='... Every Week',
                                font=dict(family='Arial',
                                            size=16),
                                showarrow=False))


    # annotations.append(dict(xref='paper', yref='paper', x=0,y=1,
    #                             xanchor='center', yanchor='top',
    #                             text='Data Source: John Hopkins CCSE',
    #                             font=dict(family='Arial',
    #                                         size=12,
    #                                         color='rgb(150,150,150)'),
    #                             showarrow=False))
    #print(annotations)
    fig.update_layout(title='Doubling Rate',title_x=0.5,height=600,annotations=annotations,xaxis_title='Days after first 100 cases', yaxis_showticklabels=False,yaxis_title='Growth Rate')
    return fig

def fig_world_map():
    df = covid.get_raw_data()
    df = df.iloc[:,[2,3,-1]]
    df.columns = ['Lat','Long','Cases']
    mapbox_access_token = "pk.eyJ1IjoiYXRhbDUiLCJhIjoiY2s4b3VneTh1MDBrcDNkcGJudHdka2ExdyJ9.994kXBWoW2pmJQQaZQT9cg"

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(lat = df["Lat"],lon=df["Long"],mode="markers",marker=go.scattermapbox.Marker(
                size = abs(df["Cases"])*0.00001,sizemin=5,color= "red" #df["Cases"],colorscale="reds"
            ),
            text=df["Cases"],name="Cases Reported"

            ))

    fig.add_trace(go.Scattermapbox(lat = [38,40],lon=[59,127],mode="markers",marker=go.scattermapbox.Marker(
                size = 15,color= "green" #df["Cases"],colorscale="reds"
            ),
            text="No Cases Reported",name="No Cases Reported"

            ))

    #38.9697° N, 59.5563°

    fig.update_layout(
        hovermode='closest',
        showlegend=False,
        height=800,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=37,
                lon=-95
            ),
            pitch=0,
            zoom=2,
            style = 'mapbox://styles/mapbox/light-v9'

        )
    )
    return fig


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
                            figure=fig_world_trend(top=12,exclude_china=False,log_trans=False)
                        )

def graph4():
    return  dcc.Graph(
                            id='example-graph4',
                            figure=fig_compare_countries_daily_rate(cntry1='US',cntry2='Italy',cntry3='India')
                        )

def graph5():
    return  dcc.Graph(
                            id='example-graph5',
                            figure=fig_dead_rec_active_piechart(),
                            config={
                                        'displayModeBar': False
                                    }
                        )

def graph6():
    return  dcc.Graph(
                            id='example-graph6',
                            figure=fig_dead_by_country(),
                            config={
                                        'displayModeBar': False
                                    }
                        )

def graph7():
    return  dcc.Graph(
                            id='example-graph7',
                            figure=fig_logarithmic_trend(),
                            config={
                                        'displayModeBar': False
                                    }
                        )

def graph8():
    return  dcc.Graph(
                            id='example-graph8',
                            figure=fig_world_map(),
                            config={
                                        'displayModeBar': False
                                    }
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
                            value=12
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


def generate_page_heading_rows():
    main_header =  dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header,subtitle_header)
    return header


def generate_layout():
    page_header = generate_page_heading_rows()
    layout = dbc.Container(
        [
            page_header[0],
            page_header[1],
            # html.Hr(),
            # dbc.Button("Refresh Dataset", color="primary", className="mr-1",id="refresh-button"),
            # dbc.Row([
            #     dbc.Col(html.Label('Button Pressed',id='button-pressed-label'),md=4)
            # ]),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(graph5(),md=12,lg=6),
                    dbc.Col(graph6(),md=12,lg=6),

                ],
                align="center",

            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(graph8(),md=12),

                ],
                align="center",
                justify="start"


            ),
            dbc.Row(
                [
                    dbc.Col(generate_country_active_rec_dead_table(),md=12,lg=12,style={'maxHeight': '400px', 'overflowY': 'scroll','position':'sticky','top':'0'})
                ],
                align="center",
            ),
            html.Hr(),
            dbc.Row(
                [

                    dbc.Col(vw_how_many_country_dropdown(id=3), md=4),
                    dbc.Col(vw_show_china_flag_dropdown(id=4), md=4)
                    #dbc.Col(vw_show_log_graph_flag_dropdown(id=5), md=4)
                ],
                align="center",
                justify="center",
            ),
            dbc.Row(
                [

                    dbc.Col(graph3(),md=12,lg=dict(size=8),xl=dict(size=8))
                ],
                align="center",
                justify="center",

            ),
            dbc.Row(
                [

                    dbc.Col(graph7(),md=12,lg=dict(size=8),xl=dict(size=8))
                ],
                align="center",
                justify="center",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(get_country_dropdown(id=1),md=dict(size=6)),
                    dbc.Col(get_country_dropdown(id=2),md=dict(size=6))
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

                    dbc.Col(graph4(),md=dict(size=12),lg=dict(size=6,offset=3))
                ],
                align="center",
            ),
        ],
        fluid=True,
    )
    return layout


app.layout = generate_layout

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
    Input(component_id='my-id4',component_property='value')]
    #Input("refresh-button", "n_clicks")]
)
def update_output_div(top_value,china_flag):
    if china_flag=='True':
        china_flag=True
    elif china_flag =='False':
        china_flag = False

    # if log_flag=='True':
    #     log_flag=True
    # elif log_flag =='False':
    #     log_flag = False

    #print(top_value,china_flag,log_flag)
    return fig_world_trend(top=top_value,exclude_china=china_flag)

# @app.callback(
#     Output(component_id='example-graph5',component_property='figure'),
#     [Input("refresh-button", "n_clicks")]
# )
# def on_button_click(n):
#     print("Updatding Pie Chart")
#     if n is None:
#         #return "Click to refresh data from source"
#         return fig_dead_rec_active_piechart()
#     else:
#         get_covid_data()
#         return fig_dead_rec_active_piechart()

# @app.callback(
#     Output(component_id='example-graph5',component_property='figure'),
#     [Input("refresh-button", "n_clicks")]
# )
# def on_button_click(n):
#     if n is None:
#         return fig_dead_rec_active_piechart()
#     else:
#         get_covid_data()
#         return fig_dead_rec_active_piechart()


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
