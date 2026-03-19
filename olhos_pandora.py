import pyautogui
import google.generativeai as genai
from config import GEMINI_API_KEY

class OlhosPandora:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    def avaliar_visao(self, comando):
        comandos_visao = ["o que tem na tela", "olhe para a tela", "veja a tela", "o que você está vendo", "analise a tela"]

        if any(cmd in comando for cmd in comandos_visao):
            print("\n📸 [Pandora printando a tela...]")
            try:
                screenshot = pyautogui.screenshot()
                prompt = "Analise o que está na tela no momento. Responda em português de forma breve, útil e sarcástico se for algo muuuito óbvio."
                resposta = self.model.generate_content([prompt, screenshot])
                return resposta.text
            except Exception as e:
                return f"Caiu um grande cisco no meu olho. Erro: {e}"
            
        return None