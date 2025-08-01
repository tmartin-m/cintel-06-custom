# --------------------------------------------
# Imports
# --------------------------------------------
from shiny import reactive, App, ui, render
from shinywidgets import output_widget, render_widget
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

# --------------------------------------------
# Load data
# --------------------------------------------
iris = sns.load_dataset("iris")
sns.set_style("whitegrid")

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
                ["sepal_length", "sepal_width", "petal_length", "petal_width"]
            ),
            ui.input_slider(
                "seaborn_bin_count",
                "Seaborn Histogram Bins",
                1,
                100,
                5
            ),
            ui.input_select("x_axis", "X-Axis", ["sepal_length", "sepal_width", "petal_length", "petal_width"]),
            ui.input_select("y_axis", "Y-Axis", ["sepal_length", "sepal_width", "petal_length", "petal_width"]),
            ui.input_checkbox_group(
                "selected_species_list",
                "Filter by Species",
                ["Setosa", "Versicolor", "Virginica"],
                selected=["Setosa", "Versicolor", "Virginica"],
                inline=True
            ),
            ui.input_radio_buttons(
                "plot_type",
                "Choose Plot Type:",
                choices=["Scatterplot", "Line Graph"],
                selected="Scatterplot",
                inline=True
            ),
            ui.hr(),
            style="background-color: #E6E6FA; padding: 15px; border-radius: 8px; color: #333333;"
        ),

        ui.layout_columns(
            ui.card(
                ui.card_header("Iris Data Grid"),
                ui.output_data_frame("iris_data_grid"),
                style="background-color: #F8F8FF; padding: 10px; border-radius: 8px;"
            ),
            ui.card(
                ui.card_header("Seaborn Histogram"),
                ui.output_plot("seaborn_hist"),
                style="background-color: #F8F8FF; padding: 10px; border-radius: 8px;"
            )
        ),

        ui.card(
            ui.card_header("Average Measurements by Species"),
            ui.output_data_frame("iris_summary_table"),
            style="max-height: 200px; font-size: 0.85rem; padding: 10px; margin: auto;"
        ),

        ui.card(
            ui.card_header("Correlation Heatmap"),
            ui.output_plot("correlation_heatmap"),
            style="background-color: #F8F8FF; padding: 10px; border-radius: 8px;"
        ),

        ui.card(
            ui.card_header("Plotly Scatterplot"),
            output_widget("plotly_scatterplot"),
            full_screen=True,
            style="background-color: #F8F8FF; padding: 10px; border-radius: 8px;"
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
            nbins=input.seaborn_bin_count(),
            hover_data=["petal_length", "petal_width", "sepal_length", "sepal_width"],
            title=f"Histogram of {input.selected_attribute().replace('_', ' ').title()} by Species",
            color_discrete_map={
                "setosa": "#B497BD",
                "versicolor": "#5D3FD3",
                "virginica": "#77DD77"
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
            alpha=0.6,
            palette={
                "setosa": "#B497BD",
                "versicolor": "#5D3FD3",
                "virginica": "#77DD77"
            }
        )
        plt.title(f"Seaborn Histogram of {input.selected_attribute().replace('_', ' ').title()} by Species")
        plt.xlabel(input.selected_attribute().replace('_', ' ').title())
        plt.ylabel("Count")
        return plt.gcf()

    @output
    @render.plot
    def correlation_heatmap():
        plt.figure(figsize=(6, 4))
        corr = iris.drop(columns="species").corr()
        sns.heatmap(corr, annot=True, cmap="Purples", fmt=".2f", linewidths=0.5)
        plt.title("Correlation Heatmap of Iris Features")
        return plt.gcf()

    @output
    @render_widget
    def plotly_scatterplot():
        df = filtered_data()
        plot_type = input.plot_type()
        x = input.x_axis()
        y = input.y_axis()

        if plot_type == "Scatterplot":
            fig = px.scatter(
                df,
                x=x,
                y=y,
                color="species",
                title=f"{x.replace('_', ' ').title()} vs {y.replace('_', ' ').title()} (Scatterplot)",
                hover_data=["petal_length", "petal_width", "sepal_length", "sepal_width"],
                color_discrete_map={
                    "setosa": "#B497BD",
                    "versicolor": "#5D3FD3",
                    "virginica": "#77DD77"
                }
            )
        else:
            fig = px.line(
                df.sort_values(by=x),
                x=x,
                y=y,
                color="species",
                title=f"{x.replace('_', ' ').title()} vs {y.replace('_', ' ').title()} (Line Graph)",
                markers=True,
                hover_data=["petal_length", "petal_width", "sepal_length", "sepal_width"],
                color_discrete_map={
                    "setosa": "#B497BD",
                    "versicolor": "#5D3FD3",
                    "virginica": "#77DD77"
                }
            )

        fig.update_layout(margin=dict(t=40, r=10, l=10, b=40))
        return fig

# --------------------------------------------
# App Launch
# --------------------------------------------
app = App(app_ui, server)
