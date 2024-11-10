import pathlib

import streamlit.web.bootstrap as bootstrap

HERE = pathlib.Path(__file__).parent


def app():
    bootstrap.run(
        str(HERE.joinpath("Home.py")),
        args=list(),
        flag_options=dict(),
    )


if __name__ == "__main__":
    app()