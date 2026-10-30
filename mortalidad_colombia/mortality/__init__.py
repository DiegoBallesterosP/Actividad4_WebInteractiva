"""Dashboard of the deaths registered in Colombia in 2019."""

from dash import Dash

from mortality.config import APP_TITLE, PROJECT_ROOT
from mortality.data import load_dataset
from mortality.ui.callbacks import register_callbacks
from mortality.ui.layout import build_layout


def create_app():
    dataset = load_dataset()
    app = Dash(__name__, title=APP_TITLE, assets_folder=str(PROJECT_ROOT / "assets"))
    app.layout = build_layout(dataset)
    register_callbacks(app, dataset)
    return app
