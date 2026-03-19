import os
import subprocess
import platform
import webbrowser
import pyautogui
import shutil
from pathlib import Path
from datetime import datetime

class PandoraExecutar:
    def __init__(self):
        self.system = platform.system()
        self.home = Path.home()
        if self.system == "Darwin":
            pyautogui.PAUSE = 0.5
    
    # ---------- Pandora abre aplicativos ----------
    def pandora_apps(self, nome_app):
        nome_app = nome_app.lower()

        mapa_apps = {
            "brave": {"Windows": "brave", "Linux": ["brave-browser", "brave"], "Darwin": "Brave"},
            "firefox": {"Windows": "firefox", "Linux": ["firefox"], "Darwin": "Firefox"},
            "chrome": {"Windows": "chrome", "Linux": ["google-chrome", "chromium-browser"], "Darwin": "Google Chrome"},
            "navegador": {
                "Windows": "brave", 
                "Linux": ["x-www-browser", "firefox", "google-chrome", "brave-browser"], 
                "Darwin": "Safari"
            },
            "calculadora": {
                "Windows": "calc",
                "Linux": ["gnome-calculator", "mate-calc", "kcalc", "galculator", "xcalc"],
                "Darwin": "Calculator"
            },
            "bloco de notas": {
                "Windows": "notepad",
                "Linux": ["xed", "gedit", "kate", "mousepad", "pluma", "leafpad"],
                "Darwin": "TextEdit"
            },
            "editor": {
                "Windows": "notepad",
                "Linux": ["xed", "gedit", "kate", "mousepad", "pluma", "leafpad"],
                "Darwin": "TextEdit"
            },
            "vs code": {
                "Windows": "code",
                "Linux": ["code"],
                "Darwin": "Visual Studio Code"
            },
            "explorer": {
                "Windows": "explorer",
                "Linux": ["nemo", "nautilus", "dolphin", "thunar", "xdg-open"],
                "Darwin": "Finder"
            },
            "whatsapp": {"Windows": "whatsapp", "Linux": ["whatsapp-for-linux", "zapzap"], "Darwin": "Whatsapp"},
            "telegram": {"Windows": "telegram", "Linux": ["telegram-desktop", "telegram"], "Darwin": "Telegram"}
        }

        if nome_app in mapa_apps:
            cmd_os = mapa_apps[nome_app].get(self.system, nome_app)
        else:
            cmd_os = nome_app
        
        cmd_final = cmd_os
        
        if self.system == "Linux" and isinstance(cmd_os, list):
            cmd_final = None
            for opcao in cmd_os:
                if shutil.which(opcao):
                    cmd_final = opcao
                    break
            
            if not cmd_final:
                return f"Não encontrei nenhum aplicativo {nome_app} com esse nome instalado."
        
        try:
            print(f"Execuatndo: {cmd_final}")
            if self.system == "Windows":
                os.system(f'start "" "{cmd_final}"')
            elif self.system == "Linux":
                if cmd_final == "xdg-open" and nome_app == "explorer":
                    subprocess.Popen([cmd_final, str(self.home)])
                else:
                    subprocess.Popen([cmd_final])
            elif self.system == "Darwin":
                subprocess.Popen(["open", "-a", cmd_final])
            
            return f"Abrindo {nome_app}..."
        except Exception as e:
            print(f"Erro complexo ao abrir app: {e}")
            return f"Não consegui abrir o app: {nome_app}"

    # ---------- Ela abre as pastas também ----------
    def pandora_pastas(self, nome_pasta):
        nome_pasta = nome_pasta.lower()

        def check_path(en, pt):
            p = self.home / en
            if p.exists():
                return p
            return self.home / pt
        
        mapa = {
            "downloads": self.home / "Downloads",
            "documentos": check_path("Documents", "Documentos"),
            "imagens": check_path("Pictures", "Imagens"),
            "videos": check_path("Videos", "Vídeos")
        }

        if nome_pasta in ["desktop", "área de trabalho", "area de trabalho"]:
            path_real = check_path("Desktop", "Área de Trabalho")
        elif nome_pasta in mapa:
            path_real = mapa[nome_pasta]
        else:
            print(f"🔎 Iniciando a varredura profunda (lá ele) para achar a pasta {nome_pasta}...")
            path_real = None

        '''else:
            path_real = self.home / nome_pasta'''
        
        # Abaixo tem as pastas que ela tem permissão para procurar alguma pasta especifica!!
        pastas_base = [
            check_path("Documents", "Documentos"),
            self.home / "Downloads",
            check_path("Desktop", "Área de trabalho")
        ]

        for base in pastas_base:
            if not base.exists():
                continue

            for raiz, diretorios, arquivos in os.walk(base):
                for diretorio in diretorios:
                    if nome_pasta == diretorio.lower():
                        path_real = Path(raiz) / diretorio
                        break
                    if path_real:
                        break
                if path_real:
                    break
        
        if not path_real:
            path_real = self.home / nome_pasta

        if not os.path.exists(str(path_real)):
            return f"Revirei os seus arquivos de ponta cabeça, mas a pasta {nome_pasta} não foi encontrada :'("
        
        '''if not os.path.exists(str(path_real)):
            return f"A pasta {nome_pasta} não foi encontrada!!"'''
        
        try:
            if self.system == "Windows":
                os.startfile(str(path_real))
            elif self.system == "Linux":
                subprocess.Popen(["xdg-open", str(path_real)])
            elif self.system == "Darwin":
                subprocess.Popen(["open", str(path_real)])
            return f"A pasta {nome_pasta} está aberta na sua tela!!"
        except:
            return "Ocorreu um erro ao tentar abrir a sua pasta!!"
    
    # ---------- Até navega na web e faz atalhos ----------
    def atalhos_pandora(self, comando):
        links = {
            'miyauti': "https://www.youtube.com/@Miyauti/videos",
            'youtube': "https://youtube.com",
            'sigaa': "https://sigaa.ufersa.edu.br/sigaa/verTelaLogin.do",
            'github': "https://github.com/3squ1vo",
            'gemini': "https://gemini.google.com",
            'twitch': "https://twitch.tv",
            'kick': "https://kick.com",
            'google': "https://www.google.com",
            'gmail': "https://mail.google.com"
        }

        for chave, url, in links.items():
            if f"abrir {chave}" in comando or chave in comando:
                webbrowser.open(url)
                return f"Abrindo {chave}"
            
            if "abrir nova aba" in comando or "nova aba" in comando:
                pyautogui.hotkey("ctrl", "t")
                return "Uma aba nova foi aberta!"
            
            if "fechar aba" in comando or "feche a aba" in comando:
                pyautogui.hotkey("ctrl", "t")
                return "Uma aba foi fechada!"

            return None
    
    # ---------- Comandos para o sistema ----------
    def pandora_system(self, acao):
        acao = acao.lower()

        if "hora" in acao or "que horas são" in acao:
            return f"Agora são exatamente {datetime.now().strftime('%H:%M')}."
        
        if "data" in acao or "que data é hoje" in acao:
            return f"Hoje é dia {datetime.now().strftime*('%d/%m/%Y')}."
        
        if "aumentar" in acao or "aumente" in acao or "suba" in acao:
            pyautogui.press("volumeup", presses=5)
            return f"Aumentando o volume."
        
        if "baixar" in acao or "baixe" in acao or "diminua" in acao:
            pyautogui.press("volumedown", presses=5)
            return f"Diminuindo o volume."
        
        if "mute" in acao or "mutar" in acao or "mudo" in acao:
            pyautogui.press("volumemute")
            return f"Volume mutado"
        
        if"tela cheia" in acao or "fullscreen" in acao:
            if "sair" in acao or "sair de tela cheia" in acao:
                pyautogui.press("esc")
                return "Saindo da tela cheia (fullscreen)"
            else:
                pyautogui.press("f11")
                return "Colocando em tela cheia (fullscreen)"
        
        '''if "desligar pc" in acao or "desligue o pc" in acao:
            os.system("shutdown -s -t 10")
            return "Iniciando o desligamento em 10 segundos. Foi bom trabalhar com você enquando durou!!"'''
        
        return None