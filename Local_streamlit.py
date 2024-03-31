import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.subplots as pls
import plotly.graph_objects as go

########################################################################################
##################### Page Configuration ###############################################
########################################################################################

#Page layout and quick title
st.set_page_config(
    page_title="Calgary Traffic",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")

#Page header
st.header(f"Traffic in Calgary", divider = True)

#Split into columns
col1, col2 = st.columns([0.2, 0.8])

########################################################################################
##################### Example Data Viz #################################################
########################################################################################
chart_data = pd.read_csv('traffic_detection-2.csv')
chart_data.rename(columns = {'camera_location': 'Intersection'}, inplace = True)
chart_data['traffic_sum'] = chart_data[['car','truck','bus']].sum(axis = 1)
chart_data['Traffic'] = pd.cut(chart_data['traffic_sum'], 
                            bins = chart_data['traffic_sum'].quantile([0,.3, .7,1]),
                            labels = ['Low', 'Moderate', 'High'])

#Customize sidebar
st.sidebar.title("Current Conditions")
st.sidebar.write(chart_data[['Intersection', 'Traffic']])

#Populate col 1
with col1:
    labels = list(chart_data['Traffic'].dropna().unique())
    values = list(chart_data['Traffic'].value_counts())

        
    fig = pls.make_subplots(rows=2, cols=1, specs=[[{'type':'domain'}],[{'type':'xy'}]], row_width=[0.3, 0.7])
    fig.add_trace(go.Pie(labels=labels, values=values, title=f"Traffic <br> <b>Levels</b>", 
                        title_font=dict(size=20, color = "white", family='Arial, sans-serif'),
                        hole=.4, hoverinfo="label+value+name", textinfo='percent+label',
                        marker=dict(colors=['darkorange', 'lightyellow', 'darkred'], line=dict(color='#000000', width=2))), 
                    row=1, col=1) 
    n=16 #example hours
    x_example = np.arange(n*12)
    fig.add_trace(go.Scatter(
        x = pd.date_range('2024-04-01', periods=24*12, freq='5min'),
        y = np.sin(1/2*np.pi*x_example/n)+np.cos(1/4*np.pi*x_example/n) + 100,
        marker=dict(color='grey'),
        name="Historical Traffic",
        mode = 'lines'
    ), row=2, col=1)

    fig.update_layout(
        title_text="PE",
        showlegend=False,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}, plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', autosize = True)

    fig.update_yaxes(title_text="Avg. Traffic Vol.", row=2, col=1, showgrid=False)
    fig.update_xaxes(title_text="Time", row=2, col=1, showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

#Populate col 2

#Define custom RGBA colur scheme
color_scheme = [
        [255,255,178],
        [254,217,118],
        [254, 178, 76],
        [253, 141, 60],
        [240,59,32],
        [189,0,38]
    ]

#Project traffic sum observations onto linear representation of custom RGBA values
min_count = chart_data['traffic_sum'].min()
max_count = chart_data['traffic_sum'].max()
diff = max_count - min_count

from math import floor
def get_color(row):
    number_of_colors = len(color_scheme)
    index = floor(number_of_colors * (row['traffic_sum'] - min_count) / diff)
    # the index might barely go out of bounds, so correct for that:
    if index == number_of_colors:
        index = number_of_colors - 1
    elif index == -1:
        index = 0
    return color_scheme[index]

chart_data['color_column'] = chart_data.apply(get_color, axis = 1)

with col2:
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=51.066886,
            longitude=-114.065353,
            zoom=10,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
            'ColumnLayer',
            data=chart_data,
            get_position='[longitude, latitude]',
            get_elevation="traffic_sum",
            radius=200,
            elevation_scale=100,
            get_fill_color='color_column',
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
            )
        ],
    ))