import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QFileDialog, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtWebEngineWidgets import QWebEngineView

class SpecDirectEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows GUI App Spec Editor")
        self.resize(1100, 900)
        self.current_file_path = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # ツールバー
        toolbar = QHBoxLayout()
        
        load_btn = QPushButton("テンプレートをロード")
        load_btn.clicked.connect(self.load_file)
        
        save_btn = QPushButton("名前を付けて保存")
        save_btn.setStyleSheet("background-color: #1a6bff; color: white; font-weight: bold; padding: 6px 15px;")
        save_btn.clicked.connect(self.save_current_state)

        toolbar.addWidget(load_btn)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("プレビュー内を直接編集してください"))
        toolbar.addWidget(save_btn)
        layout.addLayout(toolbar)

        # Webエンジン（表示・編集エリア）
        self.view = QWebEngineView()
        # 起動時は案内を表示
        self.view.setHtml("""
            <div style="display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif; color:#999;">
                <h2>「テンプレートをロード」からHTMLファイルを選択してください</h2>
            </div>
        """)
        layout.addWidget(self.view)

    def load_file(self):
        """エクスプローラーからHTMLをロード"""
        path, _ = QFileDialog.getOpenFileName(self, "テンプレートを選択", "", "HTML Files (*.html)")
        if path:
            self.current_file_path = path
            with open(path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                self.view.setHtml(html_content)
                self.setWindowTitle(f"Editing: {os.path.basename(path)}")

    def save_current_state(self):
        """編集後のHTML構造を抽出して保存"""
        # JavaScript経由で現在のDOM(HTML全体)を取得
        self.view.page().toHtml(self.execute_save)

    def execute_save(self, html):
        """ファイル保存ダイアログを表示"""
        path, _ = QFileDialog.getSaveFileName(self, "仕様書を保存", "product_spec.html", "HTML Files (*.html)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"Successfully saved to: {path}")
            except Exception as e:
                print(f"Error saving file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # UIの微調整
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    window = SpecDirectEditor()
    window.show()
    sys.exit(app.exec())