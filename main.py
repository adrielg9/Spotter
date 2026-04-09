import flet as ft
import threading

from data.db_context import DatabaseContext
from routes.router import Router
from utils.path_handler import obtener_ruta_recurso

from utils.audit_logger import AuditLogger

# --- SEÑAL DE CONTROL ---
stop_latido = threading.Event()

def iniciar_sistema_latido(page):
    """
    Sistema de latidos (Heartbeat).
    Actualiza el archivo cada 60 segundos para decir 'sigo vivo'.
    """
    def loop_latido():
        while not stop_latido.is_set():
            try:
                # Si la conexión se perdió, paramos silenciosamente
                if page.connection is None: 
                    break
                
                # Intentamos leer la sesión actual
                session_id = None
                try:
                    if page.session:
                        session_id = page.session.get("session_id")
                except:
                    break 
                
                # Actualizamos el 'visto por última vez'
                if session_id:
                    AuditLogger().actualizar_latido(session_id)
                
                # Esperamos 60 seg, pero atentos a la señal de parada
                if stop_latido.wait(60):
                    break
            except:
                break

    hilo = threading.Thread(target=loop_latido, daemon=True)
    hilo.start()

def main(page: ft.Page):
    # 1. LIMPIEZA AUTOMÁTICA AL INICIO
    # Esto repara cualquier cierre abrupto (crash o clic en X) de la vez anterior.
    try:
        AuditLogger().cerrar_sesiones_huerfanas()
    except Exception as e:
        print(f"Nota: Limpieza inicial saltada ({e})")

    # CIniciializar DB
    db_context = DatabaseContext("gym.db")

    # Configuración Ventana
    page.title = "Wald Center App"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.icon = obtener_ruta_recurso("assets/logo2.ico")
    page.padding = 0
    page.window.min_width = 800
    page.window.min_height = 600
    
    # --- CAMBIO IMPORTANTE: CONFIGURACIÓN ROBUSTA DE IDIOMA ---
    # Esto fuerza a Flet a usar Español de España (que tiene los calendarios completos)
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("es", "ES"), 
            ft.Locale("es", "AR"),
            ft.Locale("en", "US")
        ],
        current_locale=ft.Locale("es", "ES") 
    )
    # ----------------------------------------------------------
    
    page.update()
    # Router
    router = Router(page, db_context)
    page.on_route_change = router.route_change



    # 2. INICIAR LATIDOS
    stop_latido.clear()
    iniciar_sistema_latido(page)

    
    page.window.prevent_close = True 

    def on_window_event(e):
        if e.data == "close":
            print("Cerrando aplicación...")
            
          
            stop_latido.set()
            
           
            page.window.prevent_close = False
            page.window.close()

    page.window.on_event = on_window_event


    page.go("/")  
 

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")