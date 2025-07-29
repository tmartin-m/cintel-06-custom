# --------------------------------------------
# Imports
# --------------------------------------------
# Core shiny components
from shiny import App, ui, reactive, render

# Extended plotting support
from shinywidgets import render_plotly

# Utility libraries
import pandas as pd
import plotly.express as px
from datetime import datetime

# --------------------------------------------
# Reactive Aspects
# --------------------------------------------

# Load data (you can replace with live data or API later)
data = pd.read_csv("data/dataset.csv", parse_dates=["date"])

# Define a reactive calculation to filter data based on UI input
@reactive.calc
def filtered_data():
    # Access input values for filtering
    df = data.copy()
    df = df[df["temperature"] > input.temp_filter()]
    start_date, end_date = input.date_range()
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df

# --------------------------------------------
# UI Page Inputs
# --------------------------------------------

# Inputs that the user can interact with to filter the data
sidebar_inputs = ui.sidebar(
    ui.input_slider("temp_filter", "Temperature greater than", min=0, max=100, value=50),
    ui.input_date_range("date_range", "Date range",
        start=datetime(2023, 1, 1), end=datetime(2024, 12, 31)),
    ui.input_checkbox("show_chart", "Show Chart", value=True),
)

# --------------------------------------------
# UI Main Content
# --------------------------------------------

# Use layout columns to organize value boxes
value_boxes = ui.layout_columns(
    ui.value_box("Current Date", datetime.now().strftime("%Y-%m-%d")),
    ui.value_box("Mean Temperature", "Loading...")
)

# Use cards to contain your output text, table, and chart
main_content = ui.nav_panel(
    "Dashboard",
    value_boxes,
    ui.card(
        ui.h4("Filtered Table"),
        ui.output_table("filtered_table")
    ),
    ui.conditional_panel(
        "input.show_chart",
        ui.card(
            ui.h4("Temperature Over Time"),
            ui.output_plotly("filtered_chart")
        )
    )
)

# --------------------------------------------
# Define Full Layout (Sidebar + Main Content)
# --------------------------------------------

app_ui = ui.page_sidebar(
    title="Custom Dashboard App",
    sidebar=sidebar_inputs,
    navs=[main_content]
)

# --------------------------------------------
# Output Rendering Functions
# --------------------------------------------

def server(input, output, session):
    # Render the filtered data table
    @output
    @render.table
    def filtered_table():
        return filtered_data()

    # Render the Plotly chart if checkbox is selected
    @output
    @render_plotly
    def filtered_chart():
        df = filtered_data()
        fig = px.scatter(df, x="date", y="temperature", color="category", title="Temperature Over Time")
        return fig

    # Update the second value box (mean temperature)
    @reactive.effect
    def update_temperature_box():
        mean_temp = filtered_data()["temperature"].mean()
        ui.update_value_box("Mean Temperature", f"{mean_temp:.2f}°F")

# --------------------------------------------
# Launch the App
# --------------------------------------------

app = App(ui=app_ui, server=server)
