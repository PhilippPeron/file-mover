import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from pathlib import Path
import re

DIR_POSTFIX = "Pano"


class Label(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Panorama Images Here \n\n')
        self.setStyleSheet("""
             QLabel{
                 border: 3px dashed #aaa
             }
         """)


def handle_drop_files(file_list):
    file_dict = files_to_dict(file_list)
    dir_path = create_directory(file_dict=file_dict)
    move_files(file_dict, dir_path)


def move_files(file_dict, dir_path):
    for _, file_path in file_dict.items():
        file_path.rename(dir_path / file_path.name)
    print(f"Moved {str(list(file_dict.keys()))} to {str(dir_path)}")


def create_directory(file_dict):
    lowest_file_stem = sorted(file_dict.keys())[0]
    dir_name = f"{lowest_file_stem} {DIR_POSTFIX}"
    dir_path = Path(file_dict[lowest_file_stem].parent / dir_name)
    dir_path.mkdir(parents=False, exist_ok=False)
    return dir_path


def files_to_dict(file_list):
    file_dict = {}  # Key:file-stem Value:Path(file)
    for file in file_list:
        file_path = Path(file)
        # Check file existence
        if not file_path.exists():
            print(f"{file_path.name} does not exist and was skipped")
        file_name = file_path.name
        if not check_regex(file_name=file_name):
            print(f"Problem: '{file_name}' is not a valid file name. Operation Canceled!")
            return {}
        file_dict[file_path.stem] = file_path
    return file_dict


def check_regex(file_name):
    regex = r'^[a-zA-Z0-9]{3}_[0-9]{4}.[a-zA-Z]{3}$'
    match = re.compile(regex).match(file_name)
    return bool(match)


class ImageMover(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAcceptDrops(True)
        self.resize(300, 100)
        main_layout = QVBoxLayout()
        self.photoViewer = Label()
        main_layout.addWidget(self.photoViewer)

        self.setLayout(main_layout)

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            urls = event.mimeData().urls()
            file_list = [url.toLocalFile() for url in urls]
            handle_drop_files(file_list=file_list)
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ImageMover()
    demo.show()
    sys.exit(app.exec_())
