# --------------------------------------------
# Imports
# --------------------------------------------
from shiny import reactive, App, ui, render
from shinywidgets import output_widget, render_widget, render_plotly
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from faicons import icon_svg

# --------------------------------------------
# Load data
# --------------------------------------------
iris = sns.load_dataset("iris")
sns.set_style("whitegrid")  # Enhance seaborn visuals

# --------------------------------------------
# UI Layout
# --------------------------------------------
app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.img(
                src="https://images.pexels.com/photos/2471455/pexels-photo-2471455.jpeg",
                height="150px",
                style="margin-bottom: 10px;"
            ),
            ui.h2("Iris Dashboard"),
            ui.input_selectize(
                "selected_attribute",
                "Choose an Attribute:",
                ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
            ),
            ui.input_numeric(
                "plotly_bin_count",
                "Plotly Histogram Bins",
                10
            ),
            ui.input_slider(
                "seaborn_bin_count",
                "Seaborn Histogram Bins",
                1,
                100,
                5
            ),
            ui.input_checkbox_group(
                "selected_species_list",
                "Filter by Species",
                ["Setosa", "Versicolor", "Virginica"],
                selected=["Setosa", "Versicolor", "Virginica"],
                inline=True
            ),
            ui.hr(),
        ),

        ui.layout_columns(
            ui.card(
                ui.card_header("Iris Data Grid"),
                ui.output_data_frame("iris_data_grid")
            ),
              ui.card(
                ui.card_header("Seaborn Histogram"),
                ui.output_plot("seaborn_hist")
            )
        ),

        ui.card(
                ui.card_header("Average Measurements by Species"),
                ui.output_data_frame("iris_summary_table")
        ),

        ui.card(
            ui.card_header("Plotly Scatterplot: Sepal Length vs Sepal Width"),
            output_widget("plotly_scatterplot"),
            full_screen=True
        ),
    )
)

# --------------------------------------------
# Server
# --------------------------------------------
def server(input, output, session):

    @reactive.calc
    def filtered_data():
        df = iris.dropna(subset=[input.selected_attribute()])
        df = df[df["species"].str.capitalize().isin(input.selected_species_list())]
        return df

    @output
    @render.data_frame
    def iris_data_table():
        return render.DataTable(filtered_data(), filters=True)

    @output
    @render.data_frame
    def iris_data_grid():
        return render.DataGrid(filtered_data(), filters=True)

    @output
    @render.data_frame
    def iris_summary_table():
        df = filtered_data()
        summary = (
            df.groupby("species")[["sepal_length", "sepal_width", "petal_length", "petal_width"]]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={
                "sepal_length": "Avg Sepal Length",
                "sepal_width": "Avg Sepal Width",
                "petal_length": "Avg Petal Length",
                "petal_width": "Avg Petal Width"
            })
        )
        return render.DataTable(summary)

    @output
    @render_widget
    def plotly_histogram():
        fig = px.histogram(
            filtered_data(),
            x=input.selected_attribute(),
            color="species",
            barmode="overlay",
            nbins=input.plotly_bin_count(),
            hover_data=["petal_length", "petal_width", "sepal_length", "sepal_width"],
            title=f"Histogram of {input.selected_attribute().replace('_', ' ').title()} by Species",
            color_discrete_map={
                "setosa": "#1f77b4",
                "versicolor": "#ff7f0e",
                "virginica": "#2ca02c"
            }
        )
        fig.update_layout(margin=dict(t=40, r=10, l=10, b=40))
        return fig

    @output
    @render.plot
    def seaborn_hist():
        plt.figure(figsize=(8, 4))
        sns.histplot(
            data=filtered_data(),
            x=input.selected_attribute(),
            hue="species",
            multiple="layer",
            bins=input.seaborn_bin_count(),
            alpha=0.6
        )
        plt.title(f"Seaborn Histogram of {input.selected_attribute().replace('_', ' ').title()} by Species")
        plt.xlabel(input.selected_attribute().replace('_', ' ').title())
        plt.ylabel("Count")
        return plt.gcf()

    @output
    @render_widget
    def plotly_scatterplot():

        fig = px.scatter(
            filtered_data(),
            x="sepal_length",
            y="sepal_width",
            color="species",
            title="Sepal Length vs Sepal Width",
            hover_data=["petal_length", "petal_width"],
            color_discrete_map={
                "setosa": "#1f77b4",
                "versicolor": "#ff7f0e",
                "virginica": "#2ca02c"
            }
        )
        fig.update_layout(margin=dict(t=40, r=10, l=10, b=40))
        return fig

# --------------------------------------------
# App Launch
# --------------------------------------------
app = App(app_ui, server)
