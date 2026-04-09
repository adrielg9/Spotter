import flet as ft

def build_logo():
    """
    Genera el logo oficial de Wald Center con sus colores corporativos.
    """
    # Colores oficiales definidos una sola vez
    AZUL_GYM = "#3B82F6"
    TEXTO_GYM = "white"

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.FITNESS_CENTER, size=35, color=AZUL_GYM),
                    padding=10, 
                    bgcolor=ft.Colors.with_opacity(0.1, AZUL_GYM), 
                    border_radius=12
                ),
                ft.Column([
                    ft.Text("WALD CENTER", size=20, weight="bold", color=TEXTO_GYM),
                    ft.Text("GYM", size=12, weight="bold", color=AZUL_GYM, style=ft.TextStyle(letter_spacing=3))
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        margin=ft.margin.only(bottom=20)
    )