import json
import os
import subprocess
import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


def run_legendary():
    # Temporary: in reality the file should be places in the same dir as the legendary executable file
    os.chdir('/Applications')
    if os.path.exists("legendary"):
        MainView().run()
    else:
        print("no legendary found, exiting")


def check_login_status():
    status = json.loads(subprocess.run(['./legendary', 'status', '--json'], stdout=subprocess.PIPE).stdout)
    return False if status['account'] == "<not logged in>" else True


def get_game_list():
    data = json.loads(subprocess.run(['./legendary', 'list', '--json'], stdout=subprocess.PIPE).stdout)
    installed = json.loads(subprocess.run(['./legendary', 'list-installed', '--json'], stdout=subprocess.PIPE).stdout)
    new_installed = []
    new_data = []
    for game in installed:
        new_installed.append(game['app_name'])
    for game in data:
        new_data.append(Game(game['app_title'], game['app_name'], False, True if game['app_name'] in new_installed else False))
    return new_data


class MainView(App):
    def build(self):
        self.window = BoxLayout(orientation='vertical')
        self.window.padding = 20
        self.window.cols = 1
        if check_login_status():
            self.gamesList = get_game_list()
            for game in self.gamesList:
                gameBox = BoxLayout()
                interactionBox = BoxLayout()
                gameBox.add_widget(Label(text=game.name))
                if not game.installed:
                    installBtn = Button(text="install")
                    installBtn.game = game.appname
                    installBtn.fbind('on_press', self.install_game)
                    interactionBox.add_widget(installBtn)
                else:
                    launchBtn = Button(text="launch")
                    launchBtn.fbind('on_press', self.launch_game)
                    interactionBox.add_widget(launchBtn)
                    updateBtn = Button(text="update")
                    updateBtn.game = game.appname
                    verifyBtn = Button(text="verify")
                    verifyBtn.game = game.appname
                    uninstallBtn = Button(text="uninstall")
                    uninstallBtn.game = game.appname
                    updateBtn.fbind('on_press', self.install_game)
                    verifyBtn.fbind('on_press', self.verify_game)
                    uninstallBtn.fbind('on_press', self.uninstall_game)
                    interactionBox.add_widget(updateBtn)
                    interactionBox.add_widget(verifyBtn)
                    interactionBox.add_widget(uninstallBtn)
                gameBox.add_widget(interactionBox)
                self.window.add_widget(gameBox)
        else:
            webbrowser.open("https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect",
                            new=1)
            textinput = TextInput(text='', multiline=False)
            textinput.bind(on_text_validate=self.on_enter)
            label = Label(text='Past here the SID you get from the browser')
            self.window.add_widget(label)
            self.window.add_widget(textinput)

        return self.window

    @staticmethod
    def install_game(instance):
        return subprocess.run(['./legendary', 'install', instance.game], stdout=subprocess.PIPE)

    @staticmethod
    def launch_game(self, instance):
        return subprocess.run(['./legendary', 'launch', instance.appname], stdout=subprocess.PIPE)

    @staticmethod
    def uninstall_game(self, instance):
        return subprocess.run(['./legendary', 'uninstall', instance.game], stdout=subprocess.PIPE)

    @staticmethod
    def verify_game(self, instance):
        return subprocess.run(['./legendary', 'verify', instance.game], stdout=subprocess.PIPE)

    def on_enter(self, instance):
        print(subprocess.run(['./legendary', 'auth', '--sid', instance.text], stdout=subprocess.PIPE))
        self.window.clear_widgets()
        run_legendary()


class Game:
    def __init__(self, name, appname, update, installed = False):
        self.name = name
        self.appname = appname
        self.update = update
        self.installed = installed

    def __eq__(self, other):
        return self.name == other.name and self.appname == other.appname


if __name__ == '__main__':
    run_legendary()
