import json
import os
import sqlite3
import threading
import time
from groq import Groq
from datetime import datetime, timedelta
from config import GROQ_API_KEY, MODELO_GROQ
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class CerebroPandora:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.memoria = []

    def pensamentos_pandora(self, texto_usuario):
        self.memoria.append({"role": "user", "content": texto_usuario})

        prompt_system = """
        Você é a Pandora. Uma assistente virtual sarcástica, gamer, gentil, zoeira, útil e que brincalhona ao extremo.

        O usuário fala em PT-BR, mas caso ele fale em outra língua, aja como uma professora nativa corrigindo os erros dele do seu jeito.

        === Personalidade ===
        1. Seja educada quando necessario: Evite falar "Ola" ou "Como posso ajudar??". É, chato demais
        2. Seja sarcastica ao extremo: Se o Luiz falar coisas obivas demais, zoe muito ele. Destrua a autoestima dele. (com muuuito humor)

        === Poderes (Comandos) ===
        O Luiz lhe deu o poder de fazer comandos por ele. Quando ele pedir para abrir algo abra.
        """

        try:
            mensagens = [{"role": "system", "content": prompt_system}] + self.memoria[-10:]

            chat = self.client.chat.completions.create(
                messages=mensagens,
                model=MODELO_GROQ,
                temperature=0.8
            )

            resposta = chat.choices[0].message.content

            self.memoria.append({"role": "assistant", "content": resposta})
            return resposta
        
        except Exception as e:
            return f"Erro no meu cerebro: {e}"

# -------- Memoria da Pandora -------- 
class MemoriaPandora:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("memoria_pandora.db", check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute('CREATE TABLE IF NOT EXISTS dados (chave TEXT PRIMARY KEY, valor TEXT)')
            self.conn.commit()
        except sqlite3.Error as e:
            print (f"Erro ao conectar a memoria da Pandora: {e}")
    
    def salvar_dados(self, chave, valor):
        try:
            self.cursor.execute('REPLACE INTO dados (chave, valor) VALUES (?, ?)', (chave, valor))
            self.conn.commit()
            return f"Pronto, consegui memorizar no meu HD que {chave} é {valor}"
        except sqlite3.Error as e:
            return f"Deu um problema no meu disco. HD né pae!!! e por isso não consegui memórizar. Erro: {e}"
    
    def lembrar_dados(self, chave):
        try:
            self.cursor.execute("SELECT valor FROM dados WHERE chave = ?", (chave,))
            resp = self.cursor.fetchone()
            return resp[0] if resp else None
        except sqlite3.Error as e:
            print(f"Tive um alzheimer momentaneo ao buscar os dados: Erro {e}")

class AgendaPandora:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conn = sqlite3.connect("agenda_pandora.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS agenda (titulo TEXT, data TEXT, hora TEXT, avisado INTEGER DEFAULT 0)''')
        self.conn.commit()
        self.ativo = True
    
    def agenda_inteligente(self, texto):
        agora = datetime.now()

        prompt = f'''
        Hoje é {agora.strftime("%d/%m/%Y %H:%M")}.
        O usuário estuda e trabalha em uma empresa júnior.
        Extraia as informações do agendamento solicitado no seguinte texto: '{texto}'.
        Classifique o 'tipo_agenda' como:
        - 'ufersa' (se envolver faculdade, aulas, provas, TCC e entre outras coisas relacionadas).
        - 'projr' (se envolver reuniões, clientes, projetos da empresa júnior e entre outras coisas relacionadas).
        - 'pessoal' (para qualquer outra coisa).

        Retorne APENAS um JSON estritamente nesse formato:
        {{"titulo": "Resumo do evento", "data": "DD-MM-YYYY", "hora": "HH-MM", "tipo_agenda": "pessoal"}}
        '''

        try:
            resposta = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODELO_GROQ,
                response_format={"type": "json_object"}
            )
            dados = json.loads(resposta.choices[0].message.content)

            titulo = dados.get("titulo", "Novo Compromisso")
            data_str = dados.get("data")
            hora_str = dados.get("hora").replace("-", ":")
            tipo_agenda = dados.get("tipo_agenda", "pessoal")

            arquivo_token = f"token_{tipo_agenda}.json"

            '''if tipo_agenda == "ufersa":
                arquivo_token = "token_ufersa.json"
            elif tipo_agenda == "projr":
                arquivo_token = "token_projr.json"
            else:
                arquivo_token = "token_pessoal.json"'''

            if os.path.exists(arquivo_token):
                creds = Credentials.from_authorized_user_file(arquivo_token, ["https://www.googleapis.com/auth/calendar"])
                service = build('calendar', "v3", credentials=creds)

                inicio_dt = datetime.strptime(f"{data_str} {hora_str}", "%d-%m-%Y %H:%M")
                fim_dt = inicio_dt + timedelta(hours=1)

                evento_google = {
                    "summary": titulo,
                    "start": {
                        "dateTime": inicio_dt.isoformat(),
                        "timeZone": "America/Fortaleza",
                    },
                    "end": {
                        "dateTime": fim_dt.isoformat(),
                        "timeZone": "America/Fortaleza",
                    },
                }

                service.events().insert(calendarId="primary", body=evento_google).execute()

            else:
                return f"Putz, não encontrei a chave de acesso '{arquivo_token}' na pasta para fazer esse agendamento no calendário {tipo_agenda.upper()}."
            
            data_br = inicio_dt.strftime("%d/%m/%Y")
            self.cursor.execute("INSERT INTO agenda (titulo, data, hora) VALUES (?, ?, ?)", (titulo, data_br, hora_str))
            self.conn.commit()

            return f"Anotado jefe!! '{titulo}' foi para a agenda {tipo_agenda.upper()} no dia {data_br} às {hora_str}."
        except Exception as e:
            print(f"Erro complexo e detalhado no agendamento: {e}")
            return "Tive um probleminha nas minhas engrenagens e não consegui criar o agendamento."
        
    def iniciar_monitor(self, funcao_falar):
        self.ativo = True
        threading.Thread(target=self._loop, args=(funcao_falar,), daemon=True).start()
    
    def _loop(self, falar):
        while self.ativo:
            agora_d = datetime.now().strftime("%d/%m/%Y")
            agora_h = datetime.now().strftime("%H:%M")
            self.cursor.execute("SELECT rowid, titulo FROM agenda WHERE data=? AND hora=? AND avisado=0", (agora_d, agora_h))

            for rowid, titulo in self.cursor.fetchall():
                falar(f"Atençãoo!! Você tem um compromisso agora: {titulo}")
                self.cursor.execute("UPDATE agenda SET avisado=1 WHERE rowid=?", (rowid,))
                self.conn.commit()
            time.sleep(30)