import http.server
import socketserver
import threading
import webbrowser

from pathlib import Path
import subprocess
import time
import sys

from pathlib import Path
import os

import json


import webview


def ouvre_server():
    PORT = 8787

    # Racine du projet (on remonte depuis tools/)
    BASE_DIR = Path(__file__).resolve().parent.parent

    print("Serving directory:", BASE_DIR)

    # Lance le serveur EXACTEMENT comme en terminal
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=BASE_DIR
    )

    # Petite pause pour laisser le serveur démarrer
    time.sleep(1)

    urls = [
        "./physics/faculty/themeze/index.html"
    ]

    for url in urls:
        webbrowser.open(f"http://localhost:{PORT}/{url}")

    print(f"Serveur lancé sur http://localhost:{PORT}")
    print("PID serveur :", process.pid)

    return process  # utile pour pouvoir le tuer proprement

import socket
import subprocess
import sys
import time
from pathlib import Path


def find_free_port():
    """Retourne un port TCP libre."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def ouvre_server():

    PORT = find_free_port()

    BASE_DIR = Path(__file__).resolve().parent.parent
    print("Serving directory:", BASE_DIR)

    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=BASE_DIR
    )

    time.sleep(1)  # laisse le serveur démarrer

    urls = [
        "www.reed.edu/physics/faculty/themeze/index.html"
    ]

    for url in urls:
        full_url = f"http://localhost:{PORT}/{url}"
        subprocess.run([
            "open",
            "-n",
            "-a",
            "Google Chrome",
            full_url
        ])

    print(f"Serveur lancé sur http://localhost:{PORT}")
    print("PID serveur :", process.pid)

    return process

def ouvre_server_sep_sep():
    PORT = 8000

    # Racine du projet (on remonte depuis tools/)
    BASE_DIR = Path(__file__).resolve().parent.parent
    print("Serving directory:", BASE_DIR)

    # Lance le serveur EXACTEMENT comme en terminal
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=BASE_DIR
    )

    # Petite pause pour laisser le serveur démarrer
    time.sleep(1)

    # Liste des pages à ouvrir
    urls = [
        ("⚛️ Global graph", f"http://localhost:{PORT}/physics/faculty/themeze/index.html"),
    ]

    # Crée une fenêtre principale PyWebView
    window = webview.create_window(
        "Dashboard",
        urls[0][1],  # charge la première page par défaut
        width=1200,
        height=800,
        resizable=True,
        #debug=True  # ouvre console JS si erreur
    )

    # Ouvre les autres pages comme onglets dans des fenêtres séparées (PyWebView ne supporte pas encore de vrais onglets natifs)
    for title, url in urls[1:]:
        webview.create_window(title, url, width=1200, height=800, resizable=True)

    # Lance l'interface PyWebView
    webview.start()

    print(f"Serveur lancé sur http://localhost:{PORT}")
    print("PID serveur :", process.pid)

    return process


def create_tabs_html(urls):

    buttons = ""
    frames = ""

    for i, (name, url) in enumerate(urls):
        active = "active" if i == 0 else ""
        display = "block" if i == 0 else "none"

        buttons += f'<button class="tablink {active}" onclick="openTab({i})">{name}</button>'
        frames += f'''
        <iframe id="tab{i}" src="{url}" style="display:{display};width:100%;height:95%;border:none;"></iframe>
        '''

    return f"""
    <html>
    <head>
    <style>
    body {{margin:0;font-family:Arial}}
    .tabbar {{
        display:flex;
        background:#333;
    }}
    .tabbar button {{
        background:#444;
        color:white;
        border:none;
        padding:10px;
        cursor:pointer;
    }}
    .tabbar button:hover {{
        background:#666;
    }}
    </style>

    <script>
    function openTab(i) {{
        let frames = document.getElementsByTagName("iframe")
        for(let f of frames) f.style.display="none"
        document.getElementById("tab"+i).style.display="block"
    }}
    </script>

    </head>

    <body>

    <div class="tabbar">
    {buttons}
    </div>

    {frames}

    </body>
    </html>
    """


ouvre_server()