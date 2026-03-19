import psutil

class MonitorPandora:
    def verificar_sistema(self, comando):
        comandos_bateria = ["status do sistema", "como está o pc", "uso de cpu", "bateria"]

        if any(cmd in comando for cmd in comandos_bateria):
            bateria = psutil.sensors_battery()
            cpu = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory().percent

            status_bat = f"{bateria.percent}%" if bateria else "Modo desktop, conectado na tomada."
            conectado = "e carregando." if bateria and bateria.power_plugged else "na bateria."

            return f"Relatório do Sistema: Processador em {cpu}%, Memória RAM em {memoria}%. Bateria em {status_bat} {conectado if bateria else ""}"