import os
import sys
import subprocess
import asyncio
import hashlib
import webbrowser
import warnings
import speech_recognition as sr
import pygame
import edge_tts
import re
import time
from ddgs import DDGS
from langdetect import detect
from groq import Groq
from config import GROQ_API_KEY
from contextlib import contextmanager
from pandora_executar import PandoraExecutar

warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

@contextmanager
def silenciador_de_erros():
    try:
        fd_erro_original = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        os.close(devnull)
        yield
    finally:
        os.dup2(fd_erro_original, 2)
        os.close(fd_erro_original)

class SentidosPandora:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.rec_gravador = sr.Recognizer()
        self.rec_gravador.energy_threshold = 2500
        self.rec_gravador.dynamic_energy_threshold = True
        self.rec_gravador.pause_threshold = 0.5
        self.rec_gravador.non_speaking_duration = 0.4

        with silenciador_de_erros():
            try:
                pygame.mixer.init()
            except Exception as e:
                pass

        try:
            with silenciador_de_erros():
                mic = sr.Microphone()

                with mic as source:
                    print("Calibrando silêncio... (Fique em silêncio por 1 seg)")
                    self.rec_gravador.adjust_for_ambient_noise(source, duration=1)
                    print("Ouvidos calibrados!!", flush=True)
        except Exception as e:
            print(f"Erro ao calibrar mic: {e}")

        '''try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Aviso: Problema na lingua (motor de áudio) da Pandora: {e}")
        
        try:
            with sr.Microphone(device_index=INDICE_MICROFONE) as source:
                print("Calibrando silêncio... (Fique em silêncio por 1 seg)")
                self.rec_gravador.adjust_for_ambient_noise(source, duration=1)
                print("Ouvidos calibrados!!")
        except Exception as e:
            print(f"Erro ao calibrar mic: {e}")'''
    
    def ouvidosPandora(self):
        try:
            with silenciador_de_erros():
                mic = sr.Microphone()

                with mic as source:
                    print("Ouvindo...", flush=True)
                    try:
                        audio = self.rec_gravador.listen(source, timeout=5, phrase_time_limit=10)

                        with open("temp_audio.wav", "wb") as f:
                            f.write(audio.get_wav_data())
                    
                        with open("temp_audio.wav", "rb") as file:
                            transcricao = self.client.audio.transcriptions.create(
                                file=(file.name, file.read()),
                                model="whisper-large-v3",
                                temperature=0.0
                        )

                        texto_final = transcricao.text.strip().lower()

                        lista_negra = [
                           # Português
                            "obrigado", "obrigada", "obrigado por assistir",
                            "inscreva-se", "deixe o like", "legendas",
                            "legendado por", "amara.org", "até a proxima",
                            "tchau", "obrigado", "ah", "eh", "uh",

                            # Inglês
                            "thank you", "thanks for watching", "subscribe",
                            "bye", "thanks", "subtitles", "you", "thank you.",

                            # Espanhol
                            "gracias", "gracias por ver", "suscríbete",
                            "adiós", "subtítulos", "subtitulado por", "gracias."
                    ]

                        if not texto_final or len(texto_final) < 3:
                            return None
                    
                        for fantasma in lista_negra:
                         if fantasma in texto_final and len(texto_final) < 25:
                            return None
                    
                        return texto_final
                    except sr.WaitTimeoutError:
                        return None
                    except Exception as e:
                        print(f"Erro na transcrição: {e}")
                        return None
        except OSError:
            print("Erro: Mic desconectado ou não encontrado.")
            return None
        '''try:
            with sr.Microphone(device_index=INDICE_MICROFONE) as source:
                print("Ouvindo...")

                try:
                    audio = self.rec_gravador.listen(source, timeout=5, phrase_time_limit=10)
                    with open("temp_audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())

                    with open("temp_audio.wav", "rb") as file:
                        transcricao = self.client.audio.transcriptions.create(
                            file=(file.name, file.read()),
                            model="whisper-large-v3",
                            temperature=0.0
                        )
                    
                    texto_final = transcricao.text.strip()

                    if texto_final and len(texto_final) > 2:
                        return texto_final.lower()
                
                except sr.WaitTimeoutError:
                    return None
                except Exception as e:
                    print(f"Erro na transcrição: {e}")
                    return None
        except OSError:
            print("Erro: Mic desconectado ou não encontrado.")
            return None'''
    
    def falaPandora(self, texto):
        if not texto:
            return
        
        print(f"Pandora: {texto}")
        texto_limpo_voz = re.sub(r'[*#_~`>\[\]{}-]', "", texto)
        texto_limpo_voz = texto_limpo_voz.replace("\n", "; ").strip()

        if not texto_limpo_voz:
            return

        try:
            lang = detect(texto_limpo_voz)
        except:
            lang = "pt"

        voz = "pt-BR-ThalitaNeural"
        if lang == 'en':
            voz = "en-US-ArialNeural"
        elif lang == "es":
            voz = "es-ES-ElviraNeural"
        
        if not os.path.exists("cache_audios"):
            os.makedirs("cache_audios")

        chave_unica = f"{texto_limpo_voz}_{voz}"
        nome_hash = hashlib.md5(chave_unica.encode()).hexdigest() + ".mp3"
        caminho_arquivo = os.path.join("cache_audios", nome_hash)

        if os.path.exists(caminho_arquivo):
            self._tocar_audio(caminho_arquivo)
            return
        
        async def gerar_audio_com_retry():
            tentativas = 3
            for tentativa in range(tentativas):
                try:
                    communicate = edge_tts.Communicate(texto_limpo_voz, voz, rate="+10%")
                    await communicate.save(caminho_arquivo)
                    return True
                except Exception as e:
                    print(f"⚠️ [Rede] Falha ao conectar com a Microsoft. Tentando novamente ({tentativa + 1}/{tentativas})...")
                    await asyncio.sleep(1)

            print("❌ Erro: Não foi possível baixar a voz após 3 tentativas.")
            return False
        
        try:
            sucesso = asyncio.run(gerar_audio_com_retry())
            if sucesso:
                self._tocar_audio(caminho_arquivo)
        except Exception as e:
            print(f"Erro fatal no motor de voz: {e}")
        
    def _tocar_audio(self, caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()

        except KeyboardInterrupt:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            raise
        except Exception as e:
            print(f"Erro no player de voz: {e}")

        '''try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(30)
            pygame.mixer.music.unload()
        except KeyboardInterrupt:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            raise
        except Exception as e:
            print(f"Erro no player de voz: {e}")'''

    # -------- Habilidades integradas (Windows e Linux) --------    
    '''def _abrir_arquivos(self, nome_alvo):
        self.falaPandora(f"Procurando por '{nome_alvo}' nos seus arquivos...")
        busca_pastas = [
            os.path.join("/home/{usuario}/Área de trabalho"),
            os.path.join("/home/{usuario}/Documentos"),
            os.path.join("/home/{usuario}/Downloads")
        ]

        for pasta in busca_pastas:
            for raiz, diretorios, arquivos in os.walk(pasta):
                for arquivo in arquivos:
                    if nome_alvo.lower() in arquivo.lower():
                        caminho_completo = os.path.join(raiz, arquivo)
                        self.falaPandora(f"Encontrei!! Abrindo {arquivo}")
                        try:
                            os.starfile(caminho_completo)
                            return True
                        except:
                            self.falaPandora("O Windows não me deu permissão para abrir isso.")
                            return False
        self.falaPandora("Revirei essas janelas de cabo a rabo, mas não achei nada com esse nome.")
        return False'''
    
    def _abrir_arquivos(self, nome_alvo):
        self.falaPandora(f"Procurando por '{nome_alvo}' nos seus arquivos...")

        home_dir = os.path.expanduser("~")

        busca_pastas = [
            os.path.join(home_dir, "Desktop"),
            os.path.join(home_dir, "Documents"),
            os.path.join(home_dir, "Downloads"),
            os.path.join(home_dir, "Área de trabalho"),
            os.path.join(home_dir, "Documentos"),
            os.path.join(home_dir, "Imagens"),
            os.path.join(home_dir, "Músicas"),
            os.path.join(home_dir, "Vídeos"),
            os.path.join(home_dir, "Pasta pessoal"),
            os.path.join(home_dir, "Lixeira")
        ]

        for pasta in busca_pastas:
            if not os.path.exists(pasta):
                continue

            for raiz, diretorios, arquivos in os.walk(pasta):
                for arquivo in arquivos:
                    if nome_alvo.lower() in arquivo.lower():
                        caminho_completo = os.path.join(raiz, arquivo)
                        self.falaPandora(f"Encontrei!! Abrindo {arquivo}")

                        try:
                            if sys.platform == "win32":
                                os.startfile(caminho_completo)
                            
                            elif sys.platform.startswith("linux"):
                                subprocess.call(["xdg-open", caminho_completo])
                            return True
                        except Exception as e:
                            self.falaPandora("O sistema não me deu permissão para abrir isso.")
                            print(f"Erro ao abrir o arquivo: {e}")
                            return False
            self.falaPandora("Revirei isso aqui de cabo a rabo, mas não achei nada com esse nome.")
            return False
    
    def _abrir_pastas(self, nome_pasta):
        self.falaPandora(f"Verifcando a pasta {nome_pasta}...")

        home_dir = os.path.expanduser("~")

        pastas_conhecidas = {
            "downloads": os.path.join(home_dir, "Dowloads"),
            "documentos": os.path.join(home_dir, "Documents"),
            "área de trabalho": os.path.join(home_dir, "Desktop"),
            "desktop": os.path.join(home_dir, "Desktop"),
            "músicas": os.path.join(home_dir, "Music"),
            "vídeos": os.path.join(home_dir, "Videos"),
            "imagens": os.path.join(home_dir, "Pictures"),
            "fotos": os.path.join(home_dir, "Pictures")
        }

        alvo = nome_pasta.lower().strip()
        caminho_encontrado = None

        if alvo in pastas_conhecidas and os.path.exists(pastas_conhecidas[alvo]):
            caminho_encontrado = pastas_conhecidas[alvo]
        
        else:
            pastas_busca = [
                os.path.join(home_dir, "Desktop"),
                os.path.join(home_dir, "Documents"),
                os.path.join(home_dir, "Downloads"),
                os.path.join(home_dir, "Projeto Pandora")
            ]

            for pasta_base in pastas_busca:
                if not os.path.exists(pasta_base):
                    continue

                for raiz, diretorios, arquivos in os.walk(pasta_base):
                    for diretorio in diretorios:
                        if alvo in diretorio.lower():
                            caminho_encontrado = os.path.join(raiz, diretorio)
                            break
                    if caminho_encontrado:
                        break
                if caminho_encontrado:
                    break
        
        if caminho_encontrado:
            nome_final = os.path.basename(caminho_encontrado)
            self.falaPandora(f"Abrindo a pasta {nome_final}")
            try:
                if sys.platform == "win32": 
                    os.startfile(caminho_encontrado)
                elif sys.platform.startswith("linux"):
                    subprocess.call(["xdg-open", caminho_encontrado])
                return True
            except Exception as e:
                self.falaPandora("Você é tão seguro que não deixaram eu abri essa pasta.")
                return False
        else:
            self.falaPandora(f"Está ficando brisado, não tem nenhuma pasta chamada {nome_pasta} no seus diretórios principais.")
            return False
    
    # ------- A visão para buscas eye blue(Buscas visuais) and eye green(Buscas mais inteligentes) --------
    def _busca_web_visual_blue(self, comando):
        termos_excluidos = ["pesquisar", "pesquise", "busque", "procurar", "procure", "no google", "por", "sobre"]
        termo = comando.lower()
        for palavra in termos_excluidos:
            termo = termo.replace(palavra, "")
        
        termo = termo.strip()
        if termo:
            self.falaPandora(f"Irei pesquisar para {termo} na tela.")
            webbrowser.open(f"https://duckduckgo.com/?q={termo}")
        else:
            self.falaPandora("Você quer que eu pesquise pelo o quê, exatamente??")
    
    def buscas_inteligentes_green(self, pergunta):
        self.falaPandora(f"Vasculhando a internet sobre {pergunta}...")
        try:
            resultados = DDGS().text(pergunta, max_results=1)
            if resultados:
                resumo = resultados[0]["body"]

                if len(resumo) > 300:
                    resumo = resumo[:500] + "... e várias outras coisas aborrecidas."
                
                self.falaPandora(f"Aqui está o resumo: {resumo}")
                return True
            else:
                self.falaPandora("A internet não faz ideia do que é isso.")
                return False
        except Exception as e:
            print(f"Erro DuckDuckGo: {e}")
            self.falaPandora("Minha conexão com a base de dados deu pau!!")
            return False
    
    def processar_comandos(self, texto):
        if not texto:
            return False
        
        comando = texto.lower()

        executar = PandoraExecutar()

        resposta_atalho = executar.atalhos_pandora(comando)
        if resposta_atalho:
            self.falaPandora(resposta_atalho)
            return True
        
        termos_sistema = ["hora", "data", "dia é hoje", "volume", "mudo", "mutar", "tela cheia", "fullscreen"]
        if any(termo in comando for termo in termos_sistema):
            resposta_sys = executar.pandora_system(comando)
            if resposta_sys:
                self.falaPandora(resposta_sys)
                return True
        
        if "abrir pasta" in comando:
            nome_pasta = comando.replace("abrir pasta", "").strip()
            resposta_pasta = executar.pandora_pastas(nome_pasta)
            self.falaPandora(resposta_pasta)
            return True
        
        if "abrir aplicativo" in comando or "abrir o aplicativo" in comando:
            nome_app = comando.replace("abrir o aplicativo", "").replace("abrir aplicativo", "").strip()
            resposta_app = executar.pandora_apps(nome_app)
            self.falaPandora(resposta_app)
            return True

        elif "abrir" in comando:
            nome_app = comando.replace("abrir", "").replace("o", "").replace("a", "").strip()

            if nome_app in ["downloads", "documentos", "imagens", "videos", "desktop"]:
                resposta = executar.pandora_pastas(nome_app)
            else:
                resposta = executar.pandora_apps(nome_app)

            self.falaPandora(resposta)
            return True
        
        if "o que é" in comando or "quem foi" in comando or "me explica" in comando:
            termo = comando.replace("o que é", "").replace("quem foi", "").replace("me explica", "").strip()
            self.pesquisas_inteligentes(termo)
            return True
        
        return False
    
        '''if "pasta" in comando or "diretorio" in comando:
                nome_alvo = comando.replace("abrir", "").replace("a pasta", "").replace("pasta", "").replace("arquivo", "").strip()
                self._abrir_pastas(nome_alvo)
                return True
            
            elif "arquivo" in comando:
                nome_alvo = comando.replace("abrir", "").replace("o arquivo", "").replace("arquivo", "").strip()
                self._abrir_arquivos(nome_alvo)
                return True

            else:
                nome_alvo = comando.replace("abrir", "").replace("o", "").replace("a", "").strip()
                self._abrir_arquivos(nome_alvo)
                return True'''  