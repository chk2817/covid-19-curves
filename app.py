import pathlib
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import plotly_express as px
from datetime import timedelta
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                                      {'href': 'https://fonts.googleapis.com/icon?family=Material+Icons',
                                       'rel': 'stylesheet'}],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},
                           {'name': 'description', 'content': 'COVID-19 ANALTICAL APP'},
                           {'property': 'og:title', 'content': 'COVID-19 CURVES'},
                           {'property': 'og:type', 'content': 'website'},
                           {'property': 'og:url:', 'content': 'https://covid19-curves.herokuapp.com/'},
                           {'property': 'og:image',
                            'content': 'https://covid19-curves.herokuapp.com/assets/covid-curve-app.png'},
                           {'property': 'og:image:secure_url',
                            'content': 'https://covid19-curves.herokuapp.com/assets/covid-curve-app.png'},
                           {'property': 'og:image:type', 'content': 'image/png'},
                           {'http-equiv': 'X-UA-Compatible', 'content': 'IE=edge'},
                           {'name': "author", 'content': "Alban Tranchard"},
                           {'charset': "UTF-8"},
                           ],

                )

app.title = 'COVID-19'
server = app.server
app.config.suppress_callback_exceptions = True

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

# load data

df = pd.read_csv(DATA_PATH.joinpath("covid.csv"))
df["date"] = pd.to_datetime(df["date"], dayfirst=True)
begin_date = df['date'].min() + timedelta(days=1)
end_date = df['date'].max()
no_days = (end_date - begin_date).days
df['Timeline'] = df['date'].dt.strftime('%b %d')

seq = [0, 9, 23, 38, 52, 69, 83, 99,113,130,144,160,174,191, 205, 222,236,252,266]

slider_marks = {i: (begin_date + timedelta(days=i)).strftime('%b')
if ((begin_date + timedelta(days=i)).day == 1 or i == 0) else (begin_date + timedelta(days=i)).strftime('%d')
                for i in seq}

region = np.sort(df['region'].unique())
region_options = [{'label': x, 'value': x} for x in region]
subregion = np.sort(df['subregion'].unique())
subregion_options = [{'label': x, 'value': x} for x in subregion]
country = np.sort(df['country'].unique())
country_options = [{'label': x, 'value': x} for x in country]
area = np.sort(df['country_area'].unique())
area = np.sort(df.loc[df['country_area'] != df['country'], 'country_area'].unique())
area_options = [{'label': x, 'value': x} for x in area]

split_options = [{'label': k, 'value': v} for k, v in zip(['Region', 'Sub-Region', 'Country', 'Area'],
                                                          ['region', 'subregion', 'country', 'country_area'])]
# load projections data
proj_df = pd.read_csv(DATA_PATH.joinpath("data_predictions.csv"), low_memory=False)
country_area=proj_df['country_area'].unique()
country_area_options= [{'label': x, 'value': x} for x in country_area]

model_df= pd.read_csv(DATA_PATH.joinpath("model_parameters.csv"), low_memory=False)
model_factors=[{'label':x, 'value':x} for x in model_df['factors_label'].unique()]

config = {'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'zoomOut2d', 'zoomIn2d', 'hoverClosestCartesian',
                                     'zoom2d', 'autoScale2d', 'hoverCompareCartesian', 'zoomInGeo', 'zoomOutGeo',
                                     'hoverClosestGeo', 'hoverClosestGl2d', 'toggleHover',
                                     'zoomInMapbox', 'zoomOutMapbox', 'toggleSpikelines'],
          'displaylogo': False}

md1 = '''
Use any of the data filters `REGION`, `SUB-REGION`, `COUNTRY`, `AREA` to select a subset of the data.  
The filters selection is all-inclusive performing the union.  
> 
> For example, you can select `EUROPE` in the `REGION` filter and add the `US` in the `COUNTRY` filter.  
> 
> Leave filters `empty` to select the worldwide dataset.  
>  

The `COUNTRY` split is a geolocation split, not a political state.  

The `AREA` data is currently available for `US` states, `CHINA` provinces, `CANADA` and `AUSTRALIA`. 
The area data defaults to country-level for the other.  
'''
md2 = '''
Use the `SPLIT` dropdown list to show a split of the selected dataset.  
>
> For example, use `REGION` to show the timeline split by region. 
>

Use the `Limit Split to Top` field to condense the split information. An empty entry corresponds to no limit.  

The Data split view is shown when switching "on" the `Show Split Data`.  

Please note, when using the data split, the second `TAB` becomes available to show 
the COVID-19 statistics based on the most current data extract date.  

'''
md3 = '''
Recap of the COVID-19 Statistics
* `Cases`: number of confirmed cases
* `Cases per capita`: Number of confirmed cases per one million population.
* `Death rate` : Number of deaths divided by confirmed cases.
* `Recovered` or `Rec'd` : Number of recovered 
* `Rec'd Rate` : Number of recovered divided by confirmed cases. 
* `Active Cases` : Number of outstanding confirmed cases.
'''

# top navbar
navbar_layout = dbc.Navbar([
    html.A(
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url("logo.png"), height="60px", style={'stroke': '#508caf'})),
            dbc.Col(dbc.NavbarBrand("COVID-19", className="ml-2",
                                    style={'fontSize': '2em', 'fontWeight': '900', 'color': '#508caf'})),
        ], align="center", no_gutters=True),
        href='#'),

    dbc.NavbarToggler(id="navbar-toggler", className="ml-auto"),

    dbc.Collapse(
        dbc.Row([
            dbc.NavLink("MAP", href='#'),
            dbc.NavLink("TIMELINE", href='#timeline', external_link=True),
            dbc.NavLink("PROGRESSION", href='#progression', external_link=True),
            dbc.NavLink("PROJECTIONS", href='#projection', external_link=True),
            dbc.NavLink("ABOUT", href='#about', external_link=True),
        ], no_gutters=True, className="ml-auto flex-nowrap mt-3 mt-md-0", align="center"),
        id="navbar-collapse", navbar=True),

], sticky="top", className='mb-4 bg-white', style={'WebkitBoxShadow': '0px 5px 5px 0px rgba(100, 100, 100, 0.1)', })


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# app.layout

map_data_options = [{'label': 'Confirmed Cases', 'value': 'confirmed_cases'},
                    {'label': 'Deaths', 'value': 'deaths'},
                    {'label': 'Recovered', 'value': 'recovered'},
                    {'label': 'Active Cases', 'value': 'active'}, ]

map_section = dbc.Container([
    dbc.Row([
        html.Div(id='output-clientside', style={'height': '5vh'}),
        dbc.Col(dcc.Graph(id='map_plot', config=config, style={'height': '78vh'}), width=12),
    ]),

    dbc.Row(
        dbc.Col(
            dbc.Select(id='map_data', options=map_data_options, className='position-relative',
                       style={'left': '3vw', 'top': '-75vh', 'width': '240px'}, value='confirmed_cases')
            , className='col-12')
        , id='timeline', style={'height': '0px'}),

    dbc.Row([
        dbc.Col([
            dbc.Checklist(options=[{"label": "Per mio Capita", "value": True, 'disabled': False}], value=[],
                          id="per_capita", switch=True, className='position-relative',
                          style={'left': '3vw', 'top': '-70vh', 'color': '#508caf', 'width': '240px'}),
        ], className='col-12'),
        dbc.Col([
            dbc.Checklist(options=[{"label": "Exclude Population < 300K", "value": True, 'disabled': False}], value=[],
                          id="small_pop", switch=True, className='position-relative',
                          style={'left': '3vw', 'top': '-68vh', 'color': '#508caf', 'width': '240px'}),
        ], className='col-12'),
    ], style={'height': '0px'}),

    html.Div(
        dcc.Slider(min=0, max=no_days, step=1, value=no_days, id='date_slider', updatemode='mouseup',
                   marks=slider_marks,
                   className='pl-0')
        , className='position-relative', style={'left': '3vw', 'bottom': '-2vh', 'width': '94vw', 'height': '0px'}),

    dbc.Card([
        dbc.CardHeader(
            html.H2("", id='stat_card_header', className='m-0',
                    style={'color': '#508caf'})
            , style={'backgroundColor': 'rgba(255,255,255,0.5)'}),
        dbc.CardBody([
            html.H4("", id='lbl_cases', style={'color': '#666666'}),
            html.Pre('', id='lbl_cases_per_capita', style={'color': '#666666'}),
            html.H4('', id='lbl_deaths', style={'color': '#666666'}),
            html.Pre('', id='lbl_deaths_rate', className='m-0', style={'color': '#666666'}),
        ], style={'backgroundColor': 'rgba(255,255,255,0.5)', 'padding': '10px 5px 10px 20px'})
    ], style={'backgroundColor': 'rgba(255,255,255,0.5)', 'left': '3vw', 'top': '-25vh', 'width': '242px'}),

], fluid=True, id='map_section', style={'height': '90vh'})

timeline_section = dbc.Container([
    dbc.Card([
        dbc.CardHeader([
            html.H4('TIMELINE', className='d-inline'),
            dbc.Button(html.I('info', className='material-icons md-24 logoColor'), color='link', id='info1',
                       className='float-right p-0'),
            dbc.Modal([
                dbc.ModalHeader("INFORMATION"),
                dbc.ModalBody([
                    html.H5('Data Selection', className='font-weight-bold'),
                    dcc.Markdown(md1),
                    html.Br(),
                    html.H5('Data Split', className='font-weight-bold'),
                    dcc.Markdown(md2),
                    html.Br(),
                    html.H5('Definition', className='font-weight-bold'),
                    dcc.Markdown(md3),
                ]),
                dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
            ], id="modal", size='lg', scrollable=True, style={'Height': '40vh'})
        ]),

        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Region', html_for='timeline_dd_region'),
                    dcc.Dropdown(options=region_options, id='timeline_dd_region', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Region'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Sub-Region', html_for='timeline_dd_subregion'),
                    dcc.Dropdown(options=subregion_options, id='timeline_dd_subregion', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Sub-Region'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Country', html_for='timeline_dd_country'),
                    dcc.Dropdown(options=country_options, id='timeline_dd_country', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Country'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Area', html_for='timeline_dd_area'),
                    dcc.Dropdown(options=area_options, id='timeline_dd_area', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Country Area'),
                ], className='col-12 col-md-6 col-xl-3'),
                html.Div(id='first_time', children=True, style={'display': 'none'}),
            ], className='mb-4'),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(options=split_options, id='timeline_split',
                                 multi=False, style={'fontSize': '100%'},
                                 placeholder='Optional Split by')
                ], className='col-12 col-md-6 col-xl-3 mb-4'),
                dbc.Col([
                    dbc.Row([
                        dbc.Label('Limit Split to Top:', width=6, className='text-right pr-0'),
                        dbc.Col(dbc.Input(type="number", min=1, step=1, value='5', id='top_limit'), width=6)
                    ], id='row_limit', className='d_none'),
                ], className='col-12 col-md-6 col-xl-3 mb-4'),
                dbc.Col([
                    dbc.Button('Refresh', color='primary', id='timeline_refresh', className='float-right',
                               style={'width': '100px'})
                ], className='col-12 col-md-12 col-xl-6 mb-4'),
            ], className='mb-4'),
            dbc.Row([
                dbc.Col(
                    dbc.Toast(
                        'The tab "Current" will be enabled upon refresh',
                        id="toast",
                        header="Tooltip",
                        is_open=False,
                        dismissable=False,
                        duration=3000,
                        icon="primary",
                        style={"position": "fixed", "top": 100, "right": 30, "width": 300, 'zIndex': 999},
                    )
                    , className='col-12')
            ]),
            dbc.Tabs([
                dbc.Tab(label="Timeline", tab_id="tab_timeline"),
                dbc.Tab(label="Current: " + str(end_date.strftime('%d %b')), tab_id="tab_current",
                        id='extra_tab', disabled=True),
            ], id="tabs", active_tab="tab_timeline",
            ),
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Spinner(dcc.Graph(id='timeline_1', config=config, style={'height': '47vh'}),
                                         color='secondary', size='lg')], className='col-12 col-xl-6'),
                    dbc.Col([dbc.Spinner(dcc.Graph(id='timeline_2', config=config, style={'height': '47vh'}),
                                         color='secondary', size='lg')], className='col-12 col-md-6 col-xl-3'),
                    dbc.Col([dbc.Spinner(dcc.Graph(id='timeline_3', config=config, style={'height': '47vh'}),
                                         color='secondary', size='lg')], className='col-12 col-md-6 col-xl-3'),
                ], style={'minHeight': '47vh'}, id='split_view', className='mt-4 d-none'),
                dbc.Row([
                    dbc.Col(dbc.Spinner(
                        dcc.Graph(id='stack_1', config=config, style={'height': '47vh'}), color='secondary', size='lg')
                        , className='col-12 col-xl-6'),
                    dbc.Col(dbc.Spinner(
                        dcc.Graph(id='stack_2', config=config, style={'height': '47vh'}), color='secondary', size='lg')
                        , className='col-12 col-xl-6'),
                ], id='stack_view', className='mt-4', style={'minHeight': '47vh'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Checklist(options=[{"label": "Show Split Data", "value": True}],
                                      id="split_data", switch=True, className='mb-4 position-relative',
                                      style={'left': '3vw'}, value=False),
                    ], className='col-12 col-md-4 col-lg-3 col-xl-2'),
                    dbc.Col([
                        dbc.Checklist(options=[{"label": "Show Daily Increments", "value": True}],
                                      id="incremental_data", switch=True, className='mb-4 position-relative',
                                      value=False),  # style={'left':'3vw'}),
                    ], className='col-12 col-md-6'),
                ]),
            ], id='timeline_row', className='mt-4'),

            dbc.Row([
                dbc.Col([dbc.Spinner(dcc.Graph(id='detail_1', config=config, style={'height': '50vh'}),
                                     color='secondary', size='lg')], className='col-12 col-xl-6'),
                dbc.Col([dbc.Spinner(dcc.Graph(id='detail_2', config=config, style={'height': '50vh'}),
                                     color='secondary', size='lg')], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([dbc.Spinner(dcc.Graph(id='detail_3', config=config, style={'height': '50vh'}),
                                     color='secondary', size='lg')], className='col-12 col-md-6 col-xl-3'),
            ], id='current_row', className='mt-4 d-none'),
        ]),
    ], style={'minHeight': '80vh'}),

    # bottom of screen
    dbc.Row([], id='progression', style={'minHeight': '10vh'}),
], fluid=True, id='timeline_section')


@app.callback(Output('incremental_data', 'className'),
              [Input('split_data', 'value')])
def show_increment_switch(value):
    if value:
        return 'mb-4 position-relative'
    else:
        return 'mb-4 position-relative d-none'


@app.callback([Output('split_view', 'className'),
               Output('stack_view', 'className')],
              [Input('split_data', 'value')])
def show_stack_split_view(value):
    if value:
        return 'mt-4', 'mt-4 d-none'
    else:
        return 'mt-4 d-none', 'mt-4'


@app.callback(
    Output("modal", "is_open"),
    [Input("info1", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(Output('row_limit', 'className'),
              [Input('timeline_split', 'value')])
def update_display_row_limit(value):
    return "" if value else 'd-none'


@app.callback(Output("toast", "is_open"),
              [Input('timeline_split', 'value')],
              [State('extra_tab', 'disabled')])
def open_toast(split, state):
    if split and state:
        return True
    raise PreventUpdate


@app.callback([Output('timeline_row', 'className'),
               Output('current_row', 'className')],
              [Input('tabs', 'active_tab')])
def update_timeline_view(sel_tab):
    if sel_tab == 'tab_timeline':
        return 'mt-4', 'mt-4 d-none'
    elif sel_tab == 'tab_current':
        return 'mt-4 d-none', 'mt-4'


@app.callback([Output('timeline_1', 'figure'),
               Output('timeline_2', 'figure'),
               Output('timeline_3', 'figure'),
               Output('detail_1', 'figure'),
               Output('detail_2', 'figure'),
               Output('detail_3', 'figure'),
               Output('stack_1', 'figure'),
               Output('stack_2', 'figure'),
               Output('extra_tab', 'disabled'),
               Output('tabs', 'active_tab'),
               Output('first_time', 'children')
               ],
              [Input('timeline_refresh', 'n_clicks'), Input('incremental_data', 'value')],
              [State('timeline_dd_region', 'value'), State('timeline_dd_subregion', 'value'),
               State('timeline_dd_country', 'value'), State('timeline_dd_area', 'value'),
               State('timeline_split', 'value'), State('top_limit', 'value'),
               State('first_time', 'children')])
def update_timeline_plots(n, show_increments, region, subregion, country, area, split, top_limit, first_time):
    ctx = dash.callback_context
    if not ctx.triggered:
        comp_id = 'no.one'
    else:
        comp_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # apply filter on df
    region_idx = []
    if region:
        region_idx = df[df['region'].isin(region)].index.to_list()
    subregion_idx = []
    if subregion:
        subregion_idx = df[df['subregion'].isin(subregion)].index.to_list()
    country_idx = []
    if country:
        country_idx = df[df['country'].isin(country)].index.to_list()
    area_idx = []
    if area:
        area_idx = df[df['country_area'].isin(area)].index.to_list()

    idx = list(set().union(region_idx, subregion_idx, country_idx, area_idx))

    if idx:
        dff = df.loc[idx, :]
    else:
        dff = df
    # need to aggregate the dff

    cat_orders = {}
    if split:
        dff_agg = dff.loc[:, [split, 'date', 'confirmed_cases', 'deaths', 'recovered', 'active', 'population']].groupby(
            [split, 'date']).sum().reset_index().sort_values([split, 'date'])
        if show_increments:
            dff_agg[['confirmed_cases_inc', 'deaths_inc', 'recovered_inc']] = dff_agg.groupby([split])[
                ['confirmed_cases', 'deaths', 'recovered']].diff().fillna(0)
        # compute the category orders
        dff_cat_order = dff_agg.loc[dff_agg['date'] == end_date, [split, 'confirmed_cases', 'population']].groupby(
            [split]).sum() \
            .reset_index().sort_values(by=['confirmed_cases', 'population'], ascending=False)
        cat_orders = {split: dff_cat_order[split].tolist()}

        if top_limit:
            limit = max(1, int(top_limit))
            top_split = dff_cat_order.nlargest(limit, ['confirmed_cases'])[split].tolist()
            dff_agg_split = dff_agg[dff_agg[split].isin(top_split)]
            dff_agg_rest = dff_agg[~dff_agg[split].isin(top_split)].groupby(['date']).sum().reset_index()
            dff_agg_rest[split] = 'Rest'
            dff_agg = dff_agg_split.append(dff_agg_rest)
            dff_cat_order = dff_agg.loc[dff_agg['date'] == end_date, [split, 'confirmed_cases', 'population']].groupby(
                [split]).sum().reset_index().sort_values(by=['confirmed_cases', 'population'], ascending=False)
            cat_orders = {split: dff_cat_order[split].tolist()}

    else:
        dff_agg = dff.loc[:, ['date', 'confirmed_cases', 'deaths', 'recovered', 'active', 'population']].groupby(
            ['date']).sum().reset_index().sort_values(['date'])
        if show_increments:
            dff_agg[['confirmed_cases_inc', 'deaths_inc', 'recovered_inc']] = dff_agg[
                ['confirmed_cases', 'deaths', 'recovered']].diff().fillna(0)

    if show_increments:
        if split:
            dff_agg[['case_capita', 'deaths_rate', 'rec_rate']] = dff_agg.groupby([split])[
                ['confirmed_cases_inc', 'deaths_inc', 'recovered_inc']].pct_change()
        else:
            dff_agg[['case_capita', 'deaths_rate', 'rec_rate']] = dff_agg[
                ['confirmed_cases_inc', 'deaths_inc', 'recovered_inc']].pct_change()
    else:
        dff_agg['case_capita'] = dff_agg['confirmed_cases'] / dff_agg['population']
        dff_agg['deaths_rate'] = dff_agg['deaths'] / dff_agg['confirmed_cases']
        dff_agg['rec_rate'] = dff_agg['recovered'] / dff_agg['confirmed_cases']

    fig = px.bar(dff_agg, x='date', y='confirmed_cases_inc' if show_increments else 'confirmed_cases', color=split,
                 color_discrete_sequence=px.colors.qualitative.Dark24,
                 custom_data=['case_capita', split] if split else ['case_capita'],
                 category_orders=cat_orders)
    fig.update_layout(margin={"r": 0, "t": 30, "l": 20, "b": 10}, plot_bgcolor='white',
                      title_text="Confirmed Cases", title_font_size=20,
                      yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',
                      xaxis_title_text="", showlegend=True if split else False, autosize=True,
                      legend_x=0.05, legend_y=0.95, legend_title="", legend_bgcolor='rgba(255,255,255,0)')

    ht = ''
    if split: ht = '<b>%{customdata[1]}</b><br>'
    ht = ht + 'Date : %{x|%d %b}<br>'
    ht = ht + 'Cases : %{y:.3s}<br>'
    if show_increments:
        ht = ht + '% Daily change : %{customdata[0]:,.1%}<extra></extra>'
    else:
        ht = ht + 'Per capita : %{customdata[0]:,.0f}<extra></extra>'
    fig.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    fig2 = px.bar(dff_agg, x='date', y='deaths_inc' if show_increments else 'deaths', color=split,
                  color_discrete_sequence=px.colors.qualitative.Dark24,
                  custom_data=['deaths_rate', split] if split else ['deaths_rate'],
                  category_orders=cat_orders)
    fig2.update_layout(margin={"r": 0, "t": 30, "l": 20, "b": 10}, plot_bgcolor='white',
                       title_text="Deaths", title_font_size=20,
                       yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # , title_y=0.95
                       xaxis_title_text="", showlegend=False, autosize=True)  # ,title_pad_b=20
    ht = ''
    if split: ht = '<b>%{customdata[1]}</b><br>'
    ht = ht + 'Date : %{x|%d %b}<br>'
    ht = ht + 'Deaths : %{y:.3s}<br>'
    if show_increments:
        ht = ht + '% Daily change : %{customdata[0]:,.1%}<extra></extra>'
    else:
        ht = ht + 'Rate : %{customdata[0]:.1%}<extra></extra>'
    fig2.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    fig3 = px.bar(dff_agg, x='date', y='recovered_inc' if show_increments else 'recovered', color=split,
                  color_discrete_sequence=px.colors.qualitative.Dark24,
                  custom_data=['rec_rate', split] if split else ['rec_rate'],
                  category_orders=cat_orders)
    fig3.update_layout(margin={"r": 0, "t": 30, "l": 20, "b": 10}, plot_bgcolor='white',
                       title_text="Recovered", title_font_size=20,
                       yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # title_y=0.95,
                       xaxis_title_text="", showlegend=False, autosize=True)  # ,title_pad_b=20
    ht = ''
    if split: ht = '<b>%{customdata[1]}</b><br>'
    ht = ht + 'Date : %{x|%d %b}<br>'
    ht = ht + "Rec'd : %{y:.3s}<br>"
    if show_increments:
        ht = ht + '% Daily change : %{customdata[0]:,.1%}<extra></extra>'
    else:
        ht = ht + 'Rate : %{customdata[0]:.0%}<extra></extra>'
    fig3.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    if comp_id == 'incremental_data' and not first_time:
        return fig, fig2, fig3, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # add the stack view plots
    dff_stack = dff_agg.loc[:, ['date', 'confirmed_cases', 'deaths', 'recovered', 'active', 'population']].groupby(
        ['date']).sum().reset_index()
    dff_stack = pd.melt(dff_stack, value_vars=['deaths', 'recovered', 'active'], id_vars=['date'], var_name='var',
                        value_name='val')
    dff_stack['var'] = dff_stack['var'].str.title()
    dff_stack['inc_val'] = dff_stack.sort_values(['var', 'date']).groupby('var')['val'].diff().fillna(0)
    dff_stack['val_pct_chge'] = dff_stack.sort_values(['var', 'date']).groupby('var')['val'].pct_change()
    dff_stack['inc_val_pct_chge'] = dff_stack.sort_values(['var', 'date']).groupby('var')['inc_val'].pct_change()

    stack_order = {'var': ['deaths', 'recovered', 'active']}

    # cumulative plot
    fig_stack_1 = px.bar(dff_stack, x='date', y='val', color='var', category_orders=stack_order,
                         color_discrete_sequence=['#d62728', '#2ca02c', '#ff7f0e'],
                         custom_data=['var', 'val_pct_chge'])
    fig_stack_1.update_layout(margin={"r": 0, "t": 30, "l": 30, "b": 10}, plot_bgcolor='white',
                              title_text="Cumulative View", title_font_size=20,
                              yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # title_y=0.95,
                              xaxis_title_text="", showlegend=True, autosize=True, legend_title="")  # ,title_pad_b=20

    ht = '<b>%{customdata[0]}</b><br>'
    ht = ht + 'Date : %{x|%d %b}<br>'
    ht = ht + "<b>Data : %{y:.3s}</b><br>"
    ht = ht + "% Change : %{customdata[1]:.1%}<br><extra></extra>"

    fig_stack_1.update_traces(hovertemplate=ht)
    fig_stack_1.for_each_trace(lambda trace: trace.update(name=trace.name.replace("var=", "").capitalize()))

    # Incremental plot
    fig_stack_2 = px.bar(dff_stack, x='date', y='inc_val', color='var', category_orders=stack_order,
                         color_discrete_sequence=['#d62728', '#2ca02c', '#ff7f0e'],
                         custom_data=['var', 'inc_val_pct_chge'])
    fig_stack_2.update_layout(margin={"r": 0, "t": 30, "l": 30, "b": 10}, plot_bgcolor='white',
                              title_text="Daily Increments", title_font_size=20,
                              yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # title_y=0.95,
                              xaxis_title_text="", showlegend=True, autosize=True, legend_title="")  # ,title_pad_b=20
    fig_stack_2.update_traces(hovertemplate=ht)
    fig_stack_2.for_each_trace(lambda trace: trace.update(name=trace.name.replace("var=", "").capitalize()))

    if split is None:
        return fig, fig2, fig3, dash.no_update, dash.no_update, dash.no_update, fig_stack_1, fig_stack_2, True, 'tab_timeline', False

    # figures for details only available if split is given
    dff_agg['case_capita'] = dff_agg['confirmed_cases'] / dff_agg['population']
    dff_agg['deaths_rate'] = dff_agg['deaths'] / dff_agg['confirmed_cases']
    dff_agg['rec_rate'] = dff_agg['recovered'] / dff_agg['confirmed_cases']
    dff_agg_current = dff_agg[dff_agg['date'] == end_date].copy(deep=True)

    dff_agg_current['split_cat'] = pd.Categorical(dff_agg_current[split],
                                                  categories=cat_orders[split],
                                                  ordered=True)
    dff_agg_current.sort_values('split_cat', inplace=True)

    fig4 = px.bar(dff_agg_current, x='confirmed_cases', y=split, color=split,
                  color_discrete_sequence=px.colors.qualitative.Dark24, orientation='h',
                  category_orders=cat_orders)

    ht = '<b>%{y}</b><br>'
    ht = ht + 'Cases: %{x:.3s}<extra></extra>'

    fig4.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    ht = '<b>%{y}</b><br>'
    ht = ht + 'per mio capita: %{x:,.0f}<extra></extra>'

    fig4.add_trace(go.Scatter(x=dff_agg_current['case_capita'], y=dff_agg_current[split], mode='markers',
                              xaxis='x2', yaxis='y', marker_color='#666666',
                              marker_size=8, marker_line_width=0, hovertemplate=ht))

    fig4.update_layout(margin={"r": 0, "t": 60, "l": 20, "b": 10}, plot_bgcolor='white',
                       title_text="Cases", title_font_size=20,
                       yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # , title_y=0.975
                       xaxis_title_text="", showlegend=False,
                       xaxis2={'side': 'top', 'showline': False, 'showgrid': False, 'overlaying': 'x',
                               'zeroline': False, 'visible': False, 'mirror': True}, autosize=True)

    fig5 = px.bar(dff_agg_current, x='deaths', y=split, color=split,
                  color_discrete_sequence=px.colors.qualitative.Dark24, orientation='h',
                  category_orders=cat_orders)

    ht = '<b>%{y}</b><br>'
    ht = ht + 'Deaths: %{x:.3s}<extra></extra>'

    fig5.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    ht = '<b>%{y}</b><br>'
    ht = ht + 'as rate: %{x:.1%}<extra></extra>'

    fig5.add_trace(go.Scatter(x=dff_agg_current['deaths_rate'], y=dff_agg_current[split], mode='markers',
                              xaxis='x2', yaxis='y', marker_color='#666666',
                              marker_size=8, marker_line_width=0, hovertemplate=ht))

    fig5.update_layout(margin={"r": 0, "t": 60, "l": 30, "b": 10}, plot_bgcolor='white',
                       title_text="Deaths", title_font_size=20,
                       yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # , title_y=0.975
                       xaxis_title_text="", showlegend=False,
                       yaxis={'showticklabels': False},
                       xaxis2={'side': 'top', 'showline': False, 'showgrid': False, 'overlaying': 'x',
                               'zeroline': False, 'visible': False, 'mirror': True}, autosize=True)

    fig6 = px.bar(dff_agg_current, x='recovered', y=split, color=split,
                  color_discrete_sequence=px.colors.qualitative.Dark24, orientation='h',
                  category_orders=cat_orders)

    ht = '<b>%{y}</b><br>'
    ht = ht + 'Recovered: %{x:.3s}<extra></extra>'

    fig6.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    ht = '<b>%{y}</b><br>'
    ht = ht + 'as rate: %{x:.0%}<extra></extra>'

    fig6.add_trace(go.Scatter(x=dff_agg_current['rec_rate'], y=dff_agg_current[split], mode='markers',
                              xaxis='x2', yaxis='y', marker_color='#666666',
                              marker_size=8, marker_line_width=0, hovertemplate=ht))

    fig6.update_layout(margin={"r": 0, "t": 60, "l": 30, "b": 10}, plot_bgcolor='white',
                       title_text="Recovered", title_font_size=20,
                       yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # , title_y=0.975
                       xaxis_title_text="", showlegend=False,
                       yaxis={'showticklabels': False},
                       xaxis2={'side': 'top', 'showline': False, 'showgrid': False, 'overlaying': 'x',
                               'zeroline': False, 'visible': False, 'mirror': True}, autosize=True)

    return fig, fig2, fig3, fig4, fig5, fig6, fig_stack_1, fig_stack_2, False, dash.no_update, False


@app.callback(Output('per_capita', 'options'),
              [Input('map_data', 'value')])
def upd_switch_label(value):
    if value == 'confirmed_cases':
        return [{"label": "Per mio Capita", "value": True, 'disabled': False}]
    else:
        return [{"label": "As Rate on Cases", "value": True, 'disabled': False}]


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


@app.callback([Output('map_plot', 'figure'), Output('stat_card_header', 'children'),
               Output('lbl_cases', 'children'), Output('lbl_cases_per_capita', 'children'),
               Output('lbl_deaths', 'children'), Output('lbl_deaths_rate', 'children')],
              [Input('map_data', 'value'), Input('per_capita', 'value'), Input('date_slider', 'value'),
               Input('small_pop', 'value')])
def update_map(map_data, per_capita, sel_day, small_pop):
    target_col = map_data + '_rate' if per_capita else map_data

    sel_date = begin_date + timedelta(days=sel_day)
    if small_pop:
        dff = df[(df['date'] == sel_date) & df['pop_flag'] == 1]
    else:
        dff = df[(df['date'] == sel_date)]

    max_col = df[df['pop_flag'] == 1][target_col].max()
    sizeref = 2 * max_col / (60 ** 2)
    points_opacity = 0.9 - 0.7 * (np.sqrt(np.maximum(0, np.minimum(dff[target_col], max_col))) / np.sqrt(max_col))

    data_per_capita = map_data + '_rate'
    if map_data == 'confirmed_cases':
        ht = '<b>%{customdata[0]}</b><br>' \
             + 'Cases : %{customdata[2]:,f}<br>' \
             + 'Population : %{customdata[1]:,.1f} mio<br>' \
             + 'Per capita : %{customdata[3]:,.0f}<extra></extra>'
    else:
        ht = '<b>%{customdata[0]}</b><br>' \
             + map_data.capitalize() + ' : %{customdata[2]:,f}<br>' \
             + 'Cases : %{customdata[4]:,f}<br>' \
             + '% of cases : %{customdata[3]:,.1%}<extra></extra>'

    customdata = dff.loc[:, ['country_area', 'population', map_data, data_per_capita, 'confirmed_cases']].to_numpy()

    if map_data == 'confirmed_cases':
        m_color = '#508caf'
    elif map_data == 'deaths':
        m_color = 'red'
    elif map_data == 'recovered':
        m_color = 'green'
    else:
        m_color = 'orange'

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(mode='markers', lat=dff['lat'], lon=dff['long'], hovertemplate=ht,
                                   marker_size=np.maximum(0, np.minimum(dff[target_col], max_col)),
                                   marker_sizeref=sizeref, marker_sizemode='area',
                                   customdata=customdata,
                                   marker_color=m_color, marker_opacity=points_opacity.to_numpy()))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken='pk.eyJ1IjoiY2hrMjgxNyIsImEiOiJjazg0bzFpOTkxa3JqM2twZzF1bndjZTJiIn0.5ATp6O0t0VwjN0CiTVyqBw',
            center={'lat': 36, 'lon': -5.4},
            zoom=1.5,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        autosize=True,
    )

    # compute aggregate stats on Dff
    agg_dff = df.loc[(df['date'] >= sel_date - timedelta(days=1)) & (df['date'] <= sel_date),
                     ['date', 'confirmed_cases', 'deaths', 'recovered', 'active', 'population']].groupby(['date']).sum()
    total_cases_sel_date = agg_dff.loc[sel_date, 'confirmed_cases']
    total_population_sel_date = agg_dff.loc[sel_date, 'population']
    total_cases_prev_date = agg_dff.loc[sel_date - timedelta(days=1), 'confirmed_cases']

    total_deaths_sel_date = agg_dff.loc[sel_date, 'deaths']
    total_death_prev_date = agg_dff.loc[sel_date - timedelta(days=1), 'deaths']

    selected_date = str(sel_date.month_name()) + " " + str(sel_date.day)
    if total_cases_prev_date > 0:
        cases_variance = total_cases_sel_date / total_cases_prev_date - 1
    else:
        cases_variance = ''
    if total_population_sel_date > 0:
        cases_per_exposure = total_cases_sel_date / total_population_sel_date
    else:
        cases_per_exposure = ''
    if total_death_prev_date > 0:
        death_variance = total_deaths_sel_date / total_death_prev_date - 1
    else:
        death_variance = ''
    if total_cases_sel_date > 0:
        death_rate = total_deaths_sel_date / total_cases_sel_date
    else:
        death_rate = ''

    cases_label = ["Cases : " + human_format(total_cases_sel_date),
                   dbc.Badge(str('{:+.0%}'.format(cases_variance)), className="mr-3 position-relative float-right", id='badge_case',
                             style={'backgroundColor': '#508caf', 'width':'50px'}),
                   dbc.Tooltip("Variance over previous day", target="badge_case")
                   ]

    lbl_cases_per_capita = "per mio capita : " + human_format(cases_per_exposure)

    lbl_deaths = ["Deaths : " + human_format(total_deaths_sel_date),
                  dbc.Badge(str('{:+.0%}'.format(death_variance)), className="mr-3 position-relative float-right", id='badge_death',
                            style={'backgroundColor': '#508caf', 'width':'50px'}),
                  dbc.Tooltip("Variance over previous day", target="badge_death")
                  ]

    lbl_deaths_rate = 'as % cases : ' + str('{:.1%}'.format(death_rate))

    return fig, selected_date, cases_label, lbl_cases_per_capita, lbl_deaths, lbl_deaths_rate


########
#########
#########
md1 = '''
Use any of the data filters `REGION`, `SUB-REGION`, `COUNTRY`, `AREA` to select a subset of the data.  
The filters selection is all-inclusive performing the union.  
> 
> For example, you can select `EUROPE` in the `REGION` filter and add the `US` in the `COUNTRY` filter.  
> 
> Leave filters `empty` to select the worldwide dataset.  
>  

The `COUNTRY` split is a geolocation split, not a political state.  

The `AREA` data is currently available for `US` states, `CHINA` provinces, `CANADA` and `AUSTRALIA`. 
The area data defaults to country-level for the other.  
'''
md4 = '''
The left panel allows you to select the data to plot. Select first the data type from `confirmed cases`, `deaths`,
`Recovered` or `Active Cases`.  

The data filters `Region`, `Sub-Region`, `Country` and `Area` are all inclusive by selecting the data union.  
Curves are shown are shown at `Country-Area` level.  

> 
> For example, selecting the `United States` in the country filter would produce all the state-level curves.  
> 

By default, the number of `curves is limited to 12`. It can be changed to any number. An empty field corresponds to no-limit.  

Use the `Refresh` button to update the plot.
'''
md5 = '''

`Exponential-alike` curves are sometimes better seen as `linear-alike` using a log-scale on the `Y-axis`.  

'''
md6 = '''

To allow for the delays in the contagion development across countries / areas, we use a **time-offset** called `Development Time`.  

For each country-area, the `Development Time` t=0 corresponds to the first date when the contagion reached at least 5 per 1 million capita.
The minimum 5+ per million threshold was ''somewhat'' arbitrarily chosen.  

> 
> For example, for China-Hubei province, t=0 is set on `Jan-22`. For Spain, the same t=0 is set on `March-05`.  
> 

The `Development Time` enables us to overlay and better compare the progression of the curves.
'''
progression_section = dbc.Container([
    dbc.Card([
        dbc.CardHeader([
            html.H4('PROGRESSION', className='d-inline'),
            dbc.Button(html.I('info', className='material-icons md-24 logoColor'), color='link', id='info2',
                       className='float-right p-0'),
            dbc.Modal([
                dbc.ModalHeader("INFORMATION"),
                dbc.ModalBody([
                    html.H5('Data Selection', className='font-weight-bold'),
                    dcc.Markdown(md4),
                    html.Br(),
                    html.H5('Log-Scale', className='font-weight-bold'),
                    dcc.Markdown(md5),
                    html.Br(),
                    html.H5('Development Time', className='font-weight-bold'),
                    dcc.Markdown(md6),
                ]),
                dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto")),
            ], id="modal2", size='lg', scrollable=True, style={'Height': '40vh'})
        ]),

        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(options=map_data_options, id='prog_dd_data', value='confirmed_cases', clearable=False,
                                 multi=False, style={'fontSize': '100%'}, placeholder='Select Data', className='mb-4'),
                    dbc.Checklist(options=[{"label": "Per Capita", "value": True}], value=[True],
                                  id="prog_dd_scale", switch=True, className='mb-4'),
                    dbc.Checklist(options=[{"label": "Show Daily % Variance", "value": True}], value=[],
                                  id="prog_percent",
                                  switch=True, className='mb-4'),
                    dcc.Dropdown(options=region_options, id='prog_dd_region', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Select Region(s)',
                                 className='mb-4'),
                    dcc.Dropdown(options=subregion_options, id='prog_dd_subregion', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Select Sub-Region(s)',
                                 className='mb-4'),
                    dcc.Dropdown(options=country_options, id='prog_dd_country',
                                 value=['Italy', 'Spain', 'France', 'Switzerland'],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Select Country(ies)',
                                 className='mb-4'),
                    dcc.Dropdown(options=area_options, id='prog_dd_area', value=['China - Hubei', 'US - New York'],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Select Area(s)',
                                 className='mb-4'),
                    dbc.Row([
                        dbc.Label('Limit Number of Curves:', width=6, className='text-right pr-0'),
                        dbc.Col(dbc.Input(type="number", min=1, step=1, value='12', id='prog_toplimit'), width=6)
                    ], className='mb-4'),
                    dbc.Checklist(options=[{"label": "Log-Scale", "value": True}], value=[True], id="prog_logscale",
                                  switch=True, className='mb-4'),
                    dbc.Checklist(options=[{"label": "Show Development Time", "value": True, 'disabled': False}],
                                  value=[True],
                                  id="prog_dd_devtime", switch=True, className='mb-4'),
                    dbc.Button('Refresh', color='primary', id='prog_refresh', className='float-right',
                               style={'width': '100px'})
                ], className='col-12 col-md-6 col-xl-3'),

                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(label="Curve", tab_id='tab_curve'),
                        dbc.Tab(label="Extra", tab_id='tab_extra'),
                    ], id="prog_tabs", active_tab="tab_curve", className='mb-4'),
                    html.Div(
                        dbc.Spinner(
                            dcc.Graph(id='prog_1', config=config, style={'height': '70vh'}), color='secondary',
                            size='lg'),
                        id='div_1'),
                    html.Div(
                        dcc.Graph(id='extra_1', config=config, style={'height': '70vh'}),
                        id='div_2'),
                ], className='col-12 col-md-6 col-xl-9')
            ]),
        ]),
    ], style={'minHeight': '80vh'}),

    # bottom of screen
    dbc.Row([], id='projection',style={'minHeight': '10vh'}),
], fluid=True, id='prog_section')


@app.callback([Output('div_1', 'className'),
               Output('div_2', 'className')],
              [Input('prog_tabs', 'active_tab')])
def update_timeline_view(sel_tab):
    if sel_tab == 'tab_curve':
        return '', 'd-none'
    else:
        return 'd-none', ''


@app.callback(Output('prog_dd_scale', 'options'),
              [Input('prog_dd_data', 'value')])
def update_label(value):
    if value != 'confirmed_cases':
        return [{"label": "As Rate", "value": True}]
    else:
        return [{"label": "Per Capita", "value": True}]


@app.callback(
    Output("modal2", "is_open"),
    [Input("info2", "n_clicks"), Input("close2", "n_clicks")],
    [State("modal2", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback([Output('prog_1', 'figure'), Output('extra_1', 'figure')],
              [Input('prog_refresh', 'n_clicks')],
              [State('prog_dd_data', 'value'), State('prog_dd_scale', 'value'),
               State('prog_dd_region', 'value'), State('prog_dd_subregion', 'value'),
               State('prog_dd_country', 'value'), State('prog_dd_area', 'value'),
               State('prog_logscale', 'value'), State('prog_dd_devtime', 'value'),
               State('prog_toplimit', 'value'), State('prog_percent', 'value')])
def update_progression_plots(n, data, scale, region, subregion, country, area, logscale, devtime, top_limit, percent):
    # apply filter on df
    region_idx = []
    if region:
        region_idx = df[df['region'].isin(region)].index.to_list()
    subregion_idx = []
    if subregion:
        subregion_idx = df[df['subregion'].isin(subregion)].index.to_list()
    country_idx = []
    if country:
        country_idx = df[df['country'].isin(country)].index.to_list()
    area_idx = []
    if area:
        area_idx = df[df['country_area'].isin(area)].index.to_list()

    idx = list(set().union(region_idx, subregion_idx, country_idx, area_idx))

    if idx:
        dff = df.loc[idx, :]
    else:
        dff = df

    # limit data to top n entries
    if top_limit:
        dff_groupby = dff.loc[dff['date'] == end_date, ['country_area', data, 'population']].groupby(
            ['country_area']).sum().reset_index().sort_values(by=[data, 'population'], ascending=False)
        limit = max(1, int(top_limit))
        top_split = dff_groupby.nlargest(limit, [data])['country_area'].tolist()
        dff = dff[dff['country_area'].isin(top_split)]

    target_col = data
    if scale:
        target_col = data + '_rate'

    if devtime:
        x_col = 'devt_time'
        dff1 = dff.loc[dff[x_col] >= 0, :].sort_values(['country_area', 'devt_time'])
    else:
        x_col = 'date'
        dff1 = dff.sort_values(['country_area', 'date'])

    if percent:
        dff1['percent'] = dff1.groupby('country_area')[target_col].apply(pd.Series.pct_change)
        target_col = 'percent'

    cat_orders = {}
    dff_cat_order = dff.loc[dff['date'] == end_date, ['country_area', 'confirmed_cases', 'population']].groupby(
        ['country_area']).sum() \
        .reset_index().sort_values(by=['confirmed_cases', 'population'], ascending=False)
    cat_orders = {'country_area': dff_cat_order['country_area'].tolist()}

    if data == 'confirmed_cases':
        title = 'Confirmed Cases'
        hover_lbl = 'Cases'
        cdata = ['confirmed_cases', 'confirmed_cases_rate', 'country_area', 'population']
    elif data == 'deaths':
        title = 'Deaths'
        hover_lbl = 'Deaths'
        cdata = ['deaths', 'deaths_rate', 'country_area', 'confirmed_cases']
    elif data == 'recovered':
        title = 'Recovered'
        hover_lbl = "Rec'd"
        cdata = ['recovered', 'recovered_rate', 'country_area', 'confirmed_cases']
    else:
        title = 'Active Cases'
        hover_lbl = 'Active'
        cdata = ['active', 'active_rate', 'country_area', 'confirmed_cases']

    if percent:
        cdata.append('percent')

    fig = px.line(dff1, x=x_col, y=target_col, color='country_area', log_y=True if logscale else None,
                  category_orders=cat_orders, custom_data=cdata)

    fig.update_layout(margin={"r": 20, "t": 50, "l": 20, "b": 50}, plot_bgcolor='white',
                      title_text=title, title_font_size=20,
                      yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',  # , title_y=0.95
                      xaxis_title_text='Development Time (in days)' if devtime else '', showlegend=True, autosize=True,
                      legend_title="", legend_font_size=14, xaxis_showspikes=True,
                      xaxis_spikethickness=2, yaxis_showspikes=True, yaxis_spikethickness=2,
                      yaxis_tickformat=".0%" if percent else "",
                      )  # , title_pad_b=20

    ht = '<b>%{customdata[2]}</b><br>'
    if devtime:
        ht = ht + 'Devt Time: %{x} days<br>'
    else:
        ht = ht + 'Date : %{x|%d %b}<br>'
    ht = ht + hover_lbl + ' : %{customdata[0]:.3s}<br>'
    if percent:
        ht = ht + '<b>Daily change: %{customdata[4]:.1%}</b><br>'
    if data == 'confirmed_cases':
        ht = ht + 'Population : %{customdata[3]:,.1f} mio<br>'
        ht = ht + 'Per mio capita : %{customdata[1]:,.0f}<extra></extra>'
    else:
        ht = ht + 'Cases : %{customdata[3]:.3s}<br>'
        ht = ht + 'As rate : %{customdata[1]:.1%}<br>'

    fig.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    # second chart
    dff2 = dff.loc[dff['confirmed_cases'] > 0, :].groupby(['country_area']).min().reset_index()
    dff2['lbl'] = 'First Notification'
    dff3 = dff.loc[dff['devt_time'] == 0, :].groupby(['country_area']).min().reset_index()
    dff3['lbl'] = 'Devt Time=0, rate 5+ per mio'
    dff2 = dff2.append(dff3)

    fig2 = px.line(dff2, y='country_area', x='date', color='country_area', category_orders=cat_orders,
                   custom_data=['lbl', 'confirmed_cases', 'confirmed_cases_rate'])

    fig2.update_layout(plot_bgcolor='white', title_text='Development Time Reference',
                       showlegend=False, yaxis_title_text='', xaxis_title_text='', xaxis_gridcolor='#eee',
                       xaxis_showspikes=True, xaxis_spikethickness=2, autosize=True, title_font_size=20,
                       title_x=0.05
                       )

    ht = 'Date : %{x|%d %b}<br>'
    ht = ht + '<b>%{customdata[0]}</b><br>'
    ht = ht + 'Cases : %{customdata[1]:.3s}<br>'
    ht = ht + 'Per mio capita : %{customdata[2]:.1f}<br><extra></extra>'

    fig2.for_each_trace(lambda trace: trace.update(marker_size=15, marker_line_width=2, mode='lines+markers',
                                                   hovertemplate=ht))

    return fig, fig2


footer_section = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Data Source', className='mb-4', id='about'),
            html.Span("The data is primarily sourced from "),
            html.Span('Johns Hopkins CSSE', style={'fontWeight': '700', 'fontFamily': 'campaign,sans-serif'}),
            html.Span(' repository: '),
            html.A('2019 nCoV data', href='https://github.com/CSSEGISandData/COVID-19',
                   target='_blank'),
            html.P(" "),
            html.Span(
                "Where possible, the data has been cross-checked and manually corrected looking at various Wikipedia pages: "),
            html.A('Italy Example Page', href='https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Italy',
                   target='_blank'),
            html.P(' '),
            html.Span(
                'Worth noting is the current number of recovered cases for the US & Canada not being allocated to each state / province.'),
            html.P(' '),
            html.Span('The population data is based on the United Nations Population 2020 estimates: '),
            html.A('UN download page', href='https://population.un.org/wpp/Download/Standard/Population/',
                   target='_blank'),
            html.P(' '),
            html.Span('Latest data extract as of: '),
            html.Span(str(end_date.strftime('%d %b %Y')),
                      style={'fontWeight': '700', 'fontFamily': 'campaign,sans-serif'}),
            html.Div([
                html.A([
                    html.Img(src=app.get_asset_url("linkedin logo.png"), className='position-relative',
                             style={'left': '-15px'}),
                    html.Span('Alban Tranchard', className='text-uppercase',
                              style={'fontSize': '1.5rem', 'fontWeight': '700', 'fontFamily': 'campaign,sans-serif'}),
                ], href='https://linkedin.com/in/alban-tranchard-actuary',
                    target="_blank"),

            ], className='mt-4'),
        ], className='col-12 col-md-8 col-xl-9'),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.A(html.Img(src=app.get_asset_url("plotly-dash3.png"), className='position-relative',
                                    style={'left': '-13px'}),
                           href='https://plotly.com', target="_blank"),
                    html.Div([
                        html.Span('Powered by '),
                        html.Span('Plotly', className='text-uppercase',
                                  style={'fontSize': '1.25rem', 'fontWeight': '700',
                                         'fontFamily': 'campaign,sans-serif'}),
                    ]),
                ])
            ], align="center", no_gutters=True, style={'height': '80px'})
        ], className='col-12 col-md-4 col-xl-3'),
    ], className='m-4', align="center", style={'height': '30vh'}),

], fluid=True, id='footer_section', className='border-top bg-white', style={'borderColor': '#666666'})

md1_proj = '''  

 The model approach is to estimate the daily development factors (i.e. successive increments) of the number of cases.  
 
 It is one combined model fitted using a `weighted log-linear regression` based on the `development time` and `country-area` factors.  
 
 The final model selection regroups the individual `country-area` into 9 country groups to avoid over-fitting data with less statistical relevance.  
          
 The model is only fitted to `country / areas` that have reached a development time greater than 0, i.e. where the rate 
 of cases is at least 5 per mio capita.
 
'''


projection_section = dbc.Container([
    dbc.Card([
        dbc.CardHeader([
            html.H4('PROJECTION MODEL', className='d-inline'),
            dbc.Button(html.I('info', className='material-icons md-24 logoColor'), color='link', id='proj_info',
                       className='float-right p-0'),
            dbc.Modal([
                dbc.ModalHeader("INFORMATION"),
                dbc.ModalBody([
                    html.H5('Projection Model', className='font-weight-bold mb-4'),
                    dcc.Markdown(md1_proj),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.H5('Fitted Development Factors', className='font-weight-bold'),className='col-12 col-md-6'),
                        dbc.Col(
                            dcc.Dropdown(options=country_area_options, id='model_dd', value='Italy',
                                        multi=False, style={'fontSize': '100%'}, clearable=False),
                        className='col-12 col-md-6')
                    ], align='center'),
                    dcc.Graph(id='model_fit_curve', config=config, style={'height': '50vh'}),
                    dbc.Row([
                        dbc.Col(html.H5('Model Parameters', className='font-weight-bold'),className='col-12 col-md-6'),
                        dbc.Col(
                            dcc.Dropdown(options=model_factors,
                                         id='factors_dd', value=model_factors[0]['value'],multi=False, style={'fontSize': '100%'}, clearable=False),
                        className='col-12 col-md-6')
                    ], align='center'),
                    dcc.Graph(id='model_parameters', config=config, style={'height': '50vh'}),
                    dbc.Row([
                        dbc.Col(html.H5('Model Residuals', className='font-weight-bold'),className='col-12 col-md-6'),
                        dbc.Col(
                            dcc.Dropdown(options=[{'label':'Devt Time', 'value':'devt_time'},{'label':'Country Groups', 'value':'country group'}],
                                         id='residuals_dd', value='devt_time',multi=False, style={'fontSize': '100%'}, clearable=False),
                        className='col-12 col-md-6')
                    ], align='center'),
                    dcc.Graph(id='model_residuals', config=config, style={'height': '50vh'}),
                ]),
                dbc.ModalFooter(dbc.Button("Close", id="proj_close", className="ml-auto")),
            ], id="proj_modal", size='xl', scrollable=True, style={'minHeight': '70vh'})
        ]),

        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Region', html_for='proj_dd_region'),
                    dcc.Dropdown(options=region_options, id='proj_dd_region', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Region'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Sub-Region', html_for='proj_dd_subregion'),
                    dcc.Dropdown(options=subregion_options, id='proj_dd_subregion', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Sub-Region'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Country', html_for='proj_dd_country'),
                    dcc.Dropdown(options=country_options, id='proj_dd_country', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Country'),
                ], className='col-12 col-md-6 col-xl-3'),
                dbc.Col([
                    dbc.Label('Area', html_for='proj_dd_area'),
                    dcc.Dropdown(options=area_options, id='proj_dd_area', value=[],
                                 multi=True, style={'fontSize': '100%'}, placeholder='Optional Country Area'),
                ], className='col-12 col-md-6 col-xl-3'),
                html.Div(id='proj_first_time', children=True, style={'display': 'none'}),
            ], className='mb-4'),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(options=split_options, id='proj_split',
                                 multi=False, style={'fontSize': '100%'},
                                 placeholder='Optional Split by')
                ], className='col-12 col-md-6 col-xl-3 mb-4'),
                dbc.Col([
                    dbc.Row([
                        dbc.Label('Limit Split to Top:', width=6, className='text-right pr-0'),
                        dbc.Col(dbc.Input(type="number", min=1, step=1, value='12', id='proj_top_limit'), width=6)
                    ], id='proj_row_limit', className='d_none'),
                ], className='col-12 col-md-6 col-xl-3 mb-4'),
                dbc.Col([
                    dbc.Button('Refresh', color='primary', id='proj_refresh', className='float-right',
                               style={'width': '100px'})
                ], className='col-12 col-md-12 col-xl-6 mb-4'),
            ], className='mb-4'),
            dbc.Row([
                dbc.Col(
                    dbc.Toast(
                        'The tab "Split View" will be enabled upon refresh',
                        id="proj_toast",
                        header="Tooltip",
                        is_open=False,
                        dismissable=False,
                        duration=3000,
                        icon="primary",
                        style={"position": "fixed", "top": 100, "right": 30, "width": 300, 'zIndex': 999},
                    )
                    , className='col-12')
            ]),
            dbc.Tabs([
                dbc.Tab(label="Aggregated View", tab_id="tab_aggregated_view"),
                dbc.Tab(label="Split View", tab_id="tab_split_view",
                        id='proj_extra_tab', disabled=True),
            ], id="proj_tabs", active_tab="tab_aggregated_view",
            ),
            dbc.Row([
                dbc.Col(dbc.Spinner(
                    dcc.Graph(id='proj_split_1', config=config, style={'height': '50vh'}), color='secondary', size='lg')
                    , className='col-12 col-xl-6'),
                dbc.Col(dbc.Spinner(
                    dcc.Graph(id='proj_split_2', config=config, style={'height': '50vh'}), color='secondary', size='lg')
                    , className='col-12 col-xl-6'),
            ], id='proj_split_row', className='mt-4', style={'minHeight': '47vh'}),
            dbc.Row([
                dbc.Col([dbc.Spinner(dcc.Graph(id='proj_agg_1', config=config, style={'height': '50vh'}),
                                     color='secondary', size='lg')], className='col-12 col-xl-6'),
                dbc.Col([dbc.Spinner(dcc.Graph(id='proj_agg_2', config=config, style={'height': '50vh'}),
                                     color='secondary', size='lg')], className='col-12 col-xl-6'),
            ], id='proj_agg_row', className='mt-4 d-none', style={'minHeight': '47vh'}),
            dbc.Row([
                dbc.Col([
                    html.Span("Documentation about the underlying projection model can be read here: "),
                    html.A('COVID-19 Projection Model', href='https://medium.com/@alban.tranchard/covid-19-cases-projections-4d09fe655303?source=friends_link&sk=a9506c925ca80fbd51a95727c8b7a741',
                        target='_blank'),
                    html.P(' '),
                    html.Span('The companion python Jupyter notebook is available here: '),
                    html.A('Github Repository', href='https://github.com/chk2817/COVID-19-Jupyter',
                        target='_blank'),
                ],className='ml-4'),
            ],className='mt-4'),
        ]),
    ], style={'minHeight': '80vh'}),

    # bottom of screen
    dbc.Row([], style={'minHeight': '15vh'}),
], fluid=True, id='projection_section')

@app.callback(Output('model_parameters','figure'),
              [Input('factors_dd', 'value')])
def update_fit_curve(factor):
    plot_data = model_df.loc[(model_df['factors_label'] == factor)].sort_values(
        'levels')
    fig = px.line(plot_data, x='levels', y='coef', template='plotly_white',
                  color_discrete_sequence=px.colors.qualitative.D3, title='Weighted Log-Linear Regression')
    fig.add_scatter(x=plot_data['levels'], y=plot_data['ci_95_upper'], line_dash='dash', mode='lines',
                    name='95% CI Upper Bound', marker_color=px.colors.qualitative.D3[1])
    fig.add_scatter(x=plot_data['levels'], y=plot_data['ci_95_lower'], line_dash='dash', mode='lines',
                    name='95% CI Lower Bound', marker_color=px.colors.qualitative.D3[1])
    fig.update_layout(xaxis_title='Levels', yaxis_title='Parameters')
    return fig

@app.callback(Output('model_residuals','figure'),
              [Input('residuals_dd', 'value')])
def update_fit_curve(res_type):
    plot_data = proj_df.loc[~proj_df['weighted_residuals'].isnull()].sort_values('country group')
    color_split='country group' if res_type=='devt_time' else 'devt_time'
    xaxistitle='Development Time' if res_type=='devt_time' else 'Country Groups'
    fig = px.scatter(plot_data, x=res_type, y='weighted_residuals', hover_name='country_area',
                     hover_data=['link_ratio', 'fitted link ratio'], template='plotly_white',
                     color=color_split, color_discrete_sequence=px.colors.qualitative.D3,
                     color_continuous_scale=px.colors.sequential.Viridis_r,
                     title='Weighted Model Residuals')
    fig.update_layout(yaxis_title='', xaxis_title=xaxistitle, showlegend=True)
    return fig

@app.callback(Output('model_fit_curve','figure'),
              [Input('model_dd', 'value')])
def update_fit_curve(country):
    plot_data = proj_df.loc[(proj_df['country_area'] == country) & (proj_df['devt_time'] > 0)]
    fig = px.line(plot_data, x='devt_time', y='link_ratio', template='plotly_white', title='Daily Cases Development Factor',
                  color_discrete_sequence=px.colors.qualitative.D3)
    fig.add_scatter(x=plot_data['devt_time'], y=plot_data['fitted link ratio'], line_dash='dash',
                    marker_color=px.colors.qualitative.D3[1])
    fig.update_layout(yaxis_title='Factor', xaxis_title='Development Time', showlegend=False)
    return fig

@app.callback(
    Output("proj_modal", "is_open"),
    [Input("proj_info", "n_clicks"), Input("proj_close", "n_clicks")],
    [State("proj_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(Output('proj_row_limit', 'className'),
              [Input('proj_split', 'value')])
def update_display_row_limit(value):
    return "" if value else 'd-none'

@app.callback(Output("proj_toast", "is_open"),
              [Input('proj_split', 'value')],
              [State('proj_extra_tab', 'disabled')])
def open_toast(split, state):
    if split and state:
        return True
    raise PreventUpdate

@app.callback([Output('proj_agg_row', 'className'),
               Output('proj_split_row', 'className')],
              [Input('proj_tabs', 'active_tab')])
def update_timeline_view(sel_tab):
    if sel_tab == 'tab_aggregated_view':
        return 'mt-4', 'mt-4 d-none'
    elif sel_tab == 'tab_split_view':
        return 'mt-4 d-none', 'mt-4'

@app.callback([Output('proj_agg_1', 'figure'),
               Output('proj_agg_2', 'figure'),
               Output('proj_split_1', 'figure'),
               Output('proj_split_2', 'figure'),
               Output('proj_extra_tab', 'disabled'),
               Output('proj_tabs', 'active_tab'),
               #Output('proj_first_time', 'children')
               ],
              [Input('proj_refresh', 'n_clicks')],
              [State('proj_dd_region', 'value'), State('proj_dd_subregion', 'value'),
               State('proj_dd_country', 'value'), State('proj_dd_area', 'value'),
               State('proj_split', 'value'), State('proj_top_limit', 'value'),
               State('proj_first_time', 'children')])
def update_timeline_plots(n, region, subregion, country, area, split, top_limit, first_time):
    # ctx = dash.callback_context
    # if not ctx.triggered:
    #     comp_id = 'no.one'
    # else:
    #     comp_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # apply filter on df
    region_idx = []
    if region:
        region_idx = proj_df[proj_df['region'].isin(region)].index.to_list()
    subregion_idx = []
    if subregion:
        subregion_idx = proj_df[proj_df['subregion'].isin(subregion)].index.to_list()
    country_idx = []
    if country:
        country_idx = proj_df[proj_df['country'].isin(country)].index.to_list()
    area_idx = []
    if area:
        area_idx = proj_df[proj_df['country_area'].isin(area)].index.to_list()

    idx = list(set().union(region_idx, subregion_idx, country_idx, area_idx))

    if idx:
        dff = proj_df.loc[idx, :].copy(deep=True)
    else:
        dff = proj_df.copy(deep=True)
    # need to aggregate the dff

    # first aggregated plot

    dff_agg = dff.loc[:,['date','data','population','cases','cases_inc']].groupby(['date','data']).sum()\
        .reset_index().sort_values(['date'])
    dff_agg['cases_capita'] = dff_agg['cases'] / dff_agg['population']
    dff_agg['cases_capita_inc'] = dff_agg['cases_inc'] / dff_agg['population']
    dff_agg['cases_pct_chge'] = dff_agg['cases'].pct_change().fillna(0)

    fig = px.bar(dff_agg, x='date', y='cases_inc', color_discrete_sequence=px.colors.qualitative.Dark24,
                 custom_data=['cases','cases_capita'], color='data')
    fig.update_layout(margin={"r": 0, "t": 50, "l": 20, "b": 10}, plot_bgcolor='white',
                      title_text="Daily Confirmed Cases", title_font_size=20,
                      yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',
                      xaxis_title_text="", autosize=True,
                      legend_x=0.05, legend_y=0.95, legend_title="", legend_bgcolor='rgba(255,255,255,0)')

    ht = ''
    ht = ht + '<b>%{x|%d %B}</b><br>'
    ht = ht + 'Daily Cases : %{y:+.3s}<br><br>'
    ht = ht + 'YTD Cases : %{customdata[0]:,.3s}<br>'
    ht = ht + 'YTD per mio capita : %{customdata[1]:,.0f}<extra></extra>'
    fig.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    fig2 = px.line(dff_agg, x='date', y='cases', color_discrete_sequence=px.colors.qualitative.Dark24,
                  custom_data=['cases_inc', 'cases_pct_chge'], color='data')
    fig2.update_layout(margin={"r": 0, "t": 50, "l": 20, "b": 10}, plot_bgcolor='white',
                      title_text="Cumulative Confirmed Cases", title_font_size=20,
                      yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',
                      xaxis_title_text="", autosize=True,
                      legend_x=0.05, legend_y=0.95, legend_title="", legend_bgcolor='rgba(255,255,255,0)')
    ht = ''
    ht = ht + '<b>%{x|%d %B}</b><br>'
    ht = ht + 'Cumulative Cases : %{y:.3s}<br><br>'
    ht = ht + 'Day Increment : %{customdata[0]:+,.3s}<br>'
    ht = ht + 'Day % Change : %{customdata[1]:+.1%}<extra></extra>'

    fig2.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

    # split charts

    if split:
        dff_agg = dff.loc[:, [split,'date', 'devt_time','data', 'population', 'cases', 'cases_inc']].groupby([split,'date']).sum() \
            .reset_index().sort_values(by=[split,'date'], ascending=True)
        dff_agg['cases_capita'] = dff_agg['cases'] / dff_agg['population']
        dff_agg['cases_capita_inc'] = dff_agg['cases_inc'] / dff_agg['population']
        dff_agg['cases_pct_chge'] = dff_agg.groupby(split)['cases'].pct_change().fillna(0)

        df_combined=dff.loc[:, [split,'data', 'cases','date','population']].groupby([split,'data','date']).sum() \
            .reset_index().sort_values(by=[split,'date'], ascending=True)
        df_combined=df_combined.groupby([split,'data']).max().reset_index().sort_values([split,'cases'], ascending=True)
        df_combined['cases_diff'] = df_combined.groupby(split)['cases'].diff().fillna(0)
        df_combined.loc[df_combined['data'] == 'Estimate', 'cases'] = df_combined.loc[df_combined['data'] == 'Estimate', 'cases_diff']
        df_combined.drop(columns='cases_diff', inplace=True)
        totals = pd.Series(df_combined.groupby([split])['cases'].sum(), name='totals')
        df_combined = df_combined.merge(totals, left_on=split, right_index=True)

        if top_limit:
            limit = max(1, int(top_limit))
            top_split=(dff_agg.groupby(split).max().reset_index()).nlargest(limit,['cases'])[split].tolist()

            dff_agg_split = dff_agg[dff_agg[split].isin(top_split)]
            dff_agg_rest = dff_agg[~dff_agg[split].isin(top_split)].groupby(['date']).sum().reset_index()
            dff_agg_rest[split] = 'Rest'
            dff_agg = dff_agg_split.append(dff_agg_rest)
            dff_agg['cases_pct_chge'] = dff_agg.groupby(split)['cases'].pct_change().fillna(0)

            df_combined_split=df_combined[df_combined[split].isin(top_split)]
            df_combined_rest=df_combined[~df_combined[split].isin(top_split)].groupby(['data']).sum().reset_index()
            df_combined_rest[split] = 'Rest'
            df_combined=df_combined_split.append(df_combined_rest)


        fig3 = px.line(dff_agg, x='date', y='cases', color=split,
                       color_discrete_sequence=px.colors.qualitative.Dark24,
                       custom_data=['cases_inc', 'cases_pct_chge', split], log_y=False)
        fig3.update_layout(margin={"r": 0, "t": 50, "l": 20, "b": 10}, plot_bgcolor='white',
                           title_text="Cumulative Confirmed Cases", title_font_size=20,
                           yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',
                           xaxis_title_text="", autosize=True,
                           legend_title="", legend_bgcolor='rgba(255,255,255,0)') #legend_x=0.05, legend_y=0.95,
        ht = ''
        ht = ht + '<b>%{customdata[2]} - </b>'
        ht = ht + '<b>%{x|%d %B}</b><br>'
        ht = ht + 'Cumulative Cases : %{y:.3s}<br><br>'
        ht = ht + 'Day Increment : %{customdata[0]:+,.3s}<br>'
        ht = ht + 'Day % Change : %{customdata[1]:+.1%}<extra></extra>'
        fig3.for_each_trace(lambda trace: trace.update(hovertemplate=ht))


        df_combined.sort_values(['totals','data'], ascending=[True,False], inplace=True)
        df_combined['total_perc']=df_combined['totals']/totals.sum()

        fig4 = px.bar(df_combined, x='cases', y=split, color='data', custom_data=['data','totals','total_perc'],
                      color_discrete_sequence=px.colors.qualitative.Dark24, orientation='h')
        fig4.update_layout(margin={"r": 0, "t": 50, "l": 20, "b": 10}, plot_bgcolor='white',
                           title_text="Confirmed Cases Split", title_font_size=20,
                           yaxis_title_text="", title_x=0.05, yaxis_gridcolor='#eee',
                           xaxis_title_text="", autosize=True, showlegend=True,
                           legend_title="", legend_bgcolor='rgba(255,255,255,0)')
        ht = ''
        ht = ht + '<b>%{y} - </b>'
        ht = ht + '<b>%{customdata[0]}</b><br><br>'
        ht = ht + 'Cases : %{x:.3s}<br>'
        ht = ht + 'Total Cases : %{customdata[1]:.3s}<br>'
        ht = ht + '% of Total : %{customdata[2]:.0%}<extra></extra>'
        fig4.for_each_trace(lambda trace: trace.update(hovertemplate=ht))

        return fig, fig2, fig3, fig4,  False, dash.no_update

    else:
        return fig, fig2, dash.no_update, dash.no_update, True, 'tab_aggregated_view'


app.layout = html.Div([
    navbar_layout,
    map_section,
    timeline_section,
    progression_section,
    projection_section,
    footer_section
]
)

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True, host='127.0.0.1', port=8050)