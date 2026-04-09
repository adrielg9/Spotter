import flet as ft

class ProfileCtrl:
    def __init__(self, view, backup_service):
        self.view = view
        self.backup_service = backup_service

    def volver(self):
        self.view.page.go("/home")

    def ejecutar_backup(self):
        exito, msg = self.backup_service.generar_copia()
        color = "green" if exito else "red"
        self.view.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color))


    def abrir_dialogo_cambio(self, tipo):
        # Aquí podrías redirigir a una vista específica o abrir un modal
        # Por ahora mostramos un mensaje informativo
        self.view.page.open(ft.SnackBar(ft.Text(f"Funcionalidad '{tipo}' en construcción"), bgcolor="blue"))

    def cerrar_sesion(self):
        # Redirige al login y limpia el historial
        self.view.page.go("/")