import requests
from config import OPENWEATHERMAP_API_KEY

class ClimaPandora:
    def consultarclima(self, cidade):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=pt_br"
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                dados = response.json()
                temperatura = f"{dados["main"]["temp"]:.1f}".replace(".", ",")
                sensacao = f"{dados["main"]["feels_like"]:.1f}".replace(".", ",")
                temp_min = f"{dados["main"]["temp_min"]:.1f}".replace(".", ",")
                temp_max = f"{dados["main"]["temp_max"]:.1f}".replace(".", ",")
                umidade = dados["main"]["humidity"]
                descricao = dados["weather"][0]["description"]

                return (
                    f"O clima em {cidade} é de {descricao}."
                    f"\nCom a temperatura de {temperatura} graus, com a sensação de {sensacao}."
                    f"\nA mínima é de {temp_min} e a máxima é de {temp_max}"
                    f"\nA umidade do ar está em {umidade}%"
                )
            
            elif response.status_code == 404:
                return f"Rodei pra caramba, mas não encontrei nenhuma cidade chamada {cidade} no mapa."
            else:
                return "Estou off, porém quanto para informar o tempo a você!"
        except requests.exceptions.RequestException:
            return "Perdi a conexão com a internet e a antena meteorológica que construi!!"
        
    def avaliar_clima(self, comando):
        if "clima em" in comando or "temperatura em" in comando:
            palavras = comando.split(" em")

            if len(palavras) > 1:
                cidade = palavras[1].replace("?", "").replace(".", "").strip()
                cidade = cidade.replace(" agora", "").replace(" hoje", "").replace(" por favor", "")

                if cidade:
                    return self.consultarclima(cidade)
        return None