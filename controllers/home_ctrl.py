from repositories.dashboard_repo import DashboardRepository

class HomeCtrl:
    def __init__(self, view, db_context):
        self.view = view
        # Inicializamos el repo con la DB que recibimos del Router
        self.repo = DashboardRepository(db_context)

    def cargar_dashboard(self):
        """Coordina la obtención de datos y la actualización visual"""
        
        # 1. Pedir los datos al repositorio
        datos = self.repo.obtener_resumen_dashboard()
        
        # 2. Entregar los datos a la vista
        # Esto solo modifica las variables en memoria, NO intenta pintar en pantalla todavía.
        self.view.actualizar_datos(datos)
        
        # --- CORRECCIÓN DEL CRASH ---
        # NO llamamos a self.view.update() aquí.
        # ¿Por qué? Porque el Router llama a este método ANTES de agregar la vista a la página.
        # Al terminar el Router su trabajo, hará page.update() y todo se verá bien.