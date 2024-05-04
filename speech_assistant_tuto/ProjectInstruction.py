import os
import webbrowser

class ProjectInstruction:
    def __init__(self):
        pass
    
    def execute(self):
        # open postgresql
        # open chrome and figma
        # open vscode in projects folder
        self.openPostgreSQL()
        self.openFigma()
        self.openVSCode()
        self.openNotion()

    def openPostgreSQL(self):
        # Open postgreSQL
        path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PostgreSQL 16\pgAdmin 4.lnk"
        if os.path.exists(path):
            os.startfile(path)  # Example for Windows (replace with appropriate method for other OS)
        else:
            print(f"Error: Application path '{path}' does not exist.")

    def openVSCode(self):
        # Open vscode
        path = r"C:\Users\berna\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk"
        if os.path.exists(path):
            os.startfile(path)  # Example for Windows (replace with appropriate method for other OS)
        else:
            print(f"Error: Application path '{path}' does not exist.")

    def openFigma(self):
        # Open figma
        webbrowser.open("https://www.figma.com/")

    def openNotion(self):
        # Open notion
        webbrowser.open("https://www.notion.com/")


    
