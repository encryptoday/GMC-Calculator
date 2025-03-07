from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from includes import predict
import threading
from time import sleep
import random

# Manually load the KV file
Builder.load_file("style.kv")

Window.size = (1236, 700)

class commandThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.stop_event = threading.Event()  # Stop signal

    def run(self):
        self.app.ids.label_command.text = "Doing image correction ... "
        sleep(5)
        self.app.ids.label_command.text += " DONE \nRunning model ... "
        sleep(3)
        self.app.ids.label_command.text += " DONE \nPredicting result ... "

    def stop(self):
        self.stop_event.set()  # Stop signal

class loadingThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.stop_event = threading.Event()  # Stop signal

    def run(self):
        load = 0

        self.app.ids.label_msg.text = "LOADING"
        while load < 100 and not self.stop_event.is_set():
            sleep(1)  # Simulate processing delay
            self.app.ids.label_result.text = f"{load}%"
            load += random.randint(0, 5)


    def stop(self):
        self.stop_event.set()  # Stop signal

class FileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

    def fileSelected(self):
        selected = self.ids.fileChooser.selection
        if selected:
            self.callback(selected[0])
            super().dismiss()

    def fileCancel(self):
        super().dismiss()


class GMCCalculatorLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 12
        self.model2 = 22
        self.file = None

    def change_style(self, button):
        print(self.model)
        if (self.model != 12):
            idd = self.model
            self.ids[idd].background_color = (132 / 255, 169 / 255, 140 / 255)
            self.ids[idd].color = (1, 1, 1, 1)

        button.background_color = (202 / 255, 210 / 255, 197 / 255)
        button.color = (0, 0, 0, 1)
        self.model = button.name

    def change_style2(self, button):
        if(self.model2 != 22):
            idd = self.model2
            self.ids[idd].background_color = (1, 1, 1, 1)
            self.ids[idd].color = (0, 0, 0, 1)

        button.background_color = (202/255,210/255,197/255)
        button.color = (0, 0, 0, 1)
        self.model2 = button.name

    def show_file_chooser(self):
        popup = FileChooserPopup(self.fileChooserCallback)
        popup.open()

    def fileChooserCallback(self, selectedFile):
        self.file = selectedFile
        self.changeImage(self.file)

    def changeImage(self, img):
        self.ids.image.source = img



    def goo(self, btn):
        btn.text = "RUNNING ..."
        self.ids.label_suggest.text = "Please wait while we finish up loading our model. This may take a while depending on your hardware."
        self.ids.label_graphs.opacity = 0
        self.ids.grid_graphs.opacity = 0
        loading = loadingThread(self)
        loading.start()
        commandThread(self).start()
        threading.Thread(target=self.run_prediction, args=(btn,loading), daemon=True).start()

    def run_prediction(self, btn, loading):

        result = predict.predict_moisture(self)  # Long-running task
        loading.stop()
        loading.join()
        # Update UI elements on the main thread
        self.update_ui(result, btn)

    def update_ui(self, result, btn):

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.apply_results(result, btn))

    def apply_results(self, result, btn):

        self.ids.label_graphs.opacity = 1
        self.ids.grid_graphs.opacity = 1
        self.ids.label_result.text = f"[b]{result['gmc']:0.2f}[/b]"
        self.ids.label_msg.text = result['msg']
        self.ids.label_suggest.text = result['suggest']
        self.ids.label_command.text += "DONE"
        btn.text = "RUN AGAIN"



class GMCCalculatorApp(App):
    def build(self):
        return GMCCalculatorLayout()

if __name__ == "__main__":
    GMCCalculatorApp().run()