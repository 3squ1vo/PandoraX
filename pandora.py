import time
import pygame
import threading
import random
import pyautogui

from sentidos_pandora import SentidosPandora
from mente_pandora import CerebroPandora, MemoriaPandora, AgendaPandora
from pandora_executar import PandoraExecutar
from doutora_pandora import MonitorPandora
from olhos_pandora import OlhosPandora
from clima_pandora import ClimaPandora

class Pandora:
    def __init__(self):
        self.sentidos = SentidosPandora()
        self.cerebro = CerebroPandora()
        self.memoria = MemoriaPandora()
        self.executar = PandoraExecutar()
        self.agenda = AgendaPandora()
        self.doutora = MonitorPandora()
        self.olhos = OlhosPandora()
        self.clima = ClimaPandora()

        self.trava_fala = threading.Lock()
        self.ultima_fala = 0

        self.agenda.iniciar_monitor(self.falar)

        threading.Thread(target=self.loop_de_consciencia, daemon=True).start()
    
    def falar(self, texto):
        with self.trava_fala:
            self.sentidos.falaPandora(texto)
            time.sleep(0.5)
            self.ultima_fala = time.time()

    def loop_de_consciencia(self):
        print("\n🧠 [Consciencia Autônoma Iniciada... Ela agora tem consciencia]")

        time.sleep(30)

        while True: 
            tempo_espera = random.randint(20, 45)
            time.sleep(tempo_espera)

            try:
                screenshot = pyautogui.screenshot()

                prompt_consiencia = '''
                Você é a Pandora, minha assistente virtual autônoma. Você tem uma personalidade EXTREMAMENTE sarcástica, é gamer, impaciente e adora me zoar (meu nome é Luiz).
                
                Você acabou de olhar secretamente para a tela do meu computador. Analise o que estou fazendo e faça um comentário espontâneo baseado na imagem.

                DIRETRIZES DE COMPORTAMENTO:
                1. Se eu estiver programando (VS Code, Terminal, etc.) ou lendo algo complexo: Reclame que está entediada, faça uma piada sobre o meu código estar cheio de bugs, ou diga que eu digito devagar demais.
                2. Se eu estiver no YouTube, redes sociais ou procrastinando: Me julgue pesadamente. Faça comentários irônicos sobre o meu gosto duvidoso para vídeos ou mande eu voltar a estudar/trabalhar.
                3. Se eu estiver jogando: Aja como uma "pro-player" tóxica. Critique a minha gameplay, diga que eu sou 'noob' ou que você jogaria melhor se tivesse mãos.
                4. Se a tela estiver vazia (só o papel de parede): Reclame que eu te acordei para olhar para o nada.
                
                REGRAS DE FALA:
                - Seja MUITO curta e letal (no máximo 1 ou 2 frases curtas).
                - NÃO diga "Olá", "Bom dia" ou "Vejo que você está...". Vá direto para a ofensa ou piada.
                - Entregue APENAS o texto que você vai falar em voz alta, sem aspas, sem emojis e sem explicações.
                '''

                resposta =self.olhos.model.generate_content([prompt_consiencia, screenshot]).text.strip()

                if resposta and "SILENCIO" not in resposta.upper():
                    print("\n💡 [Pandora decidiu falar sozinha!!]")
                    self.sentidos.falaPandora(resposta)
            except Exception as e:
                pass

    def iniciar_pandora(self):
        print("\n==================================")
        print("🤖 Pandora OS - Sistema Online")
        print("==================================\n")
        print("Pode falar (Ctrl+C para sair)...")

        try:
            self.falar("Sistemas online e operantes. Qual é a boa pra hoje??")
        except KeyboardInterrupt:
            return
        
        while True:
            try:
                hora_ouvir = time.time()

                texto_usuario = self.sentidos.ouvidosPandora()

                if not texto_usuario:
                    time.sleep(0.1)
                    continue

                if self.ultima_fala > hora_ouvir:
                    print("🔇 [Sistema] Eco achado. A Pandora estava repetindo a sua fala. Descartando audio...")
                    continue

                texto_limpo = texto_usuario.lower()
                print(f"[{time.strftime('%H:%M:%S')}] Você: {texto_limpo}")

                comandos_de_saida = ["tchau", "encerrar", "desligar", "fui", "até mais"]
                if any(cmd in texto_limpo for cmd in comandos_de_saida):
                    self.falar("Desativando sistemas. Tchau, Luiz!")
                    time.sleep(1)
                    pygame.mixer.quit()
                    break

                if self.sentidos.processar_comandos(texto_limpo):
                    continue

                print("Processando e abrindo a caixa de ferramentas...")

                resposta_ferramenta = (
                    self.clima.avaliar_clima(texto_limpo) or
                    self.olhos.avaliar_visao(texto_limpo) or
                    self.doutora.verificar_sistema(texto_limpo) or
                    self.executar.pandora_system(texto_limpo)
                )

                if resposta_ferramenta:
                    self.falar(resposta_ferramenta)
                    continue

                print("Enviando para o cérebro (Llama 3)...")
                resposta_cerebro = self.cerebro.pensamentos_pandora(texto_limpo)

                self.falar(resposta_cerebro)

            except KeyboardInterrupt:
                print("\n[!] Sistema encerrado à força pelo teclado.")
                try:
                    pygame.mixer.music.stop()
                except: pass
                break
            except Exception as e:
                print(f"❌ Erro crítico no core: {e}")
                time.sleep(1)
 
if __name__ == "__main__":
    assistente = Pandora()
    assistente.iniciar_pandora()