import tkinter as tk
from ui_components import SplashScreen
from login import LoginWindow


def show_splash():
    """Display splash screen and initialize login"""
    SplashScreen.show()
    LoginWindow()


if __name__ == "__main__":
    show_splash()
