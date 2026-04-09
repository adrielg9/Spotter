import flet as ft

class AppTheme:
    # --- PALETA DE COLORES (Tu "ADN" visual) ---
    bgcolor = "#121212"           # Fondo principal oscuro
    card_color = "#1E1E1E"        # Fondo de tarjetas/inputs
    
    primary = ft.Colors.BLUE_600  # Color principal (Botones, bordes)
    success = ft.Colors.GREEN_500 # Éxito
    error = ft.Colors.RED_500     # Error
    
    text_primary = ft.Colors.WHITE
    text_secondary = ft.Colors.GREY_400

    # --- ESTILOS REUTILIZABLES (Para escribir menos en las vistas) ---
    
    @staticmethod
    def get_button_style(color):
        """Devuelve el estilo estándar de tus botones grandes"""
        return ft.ButtonStyle(
            bgcolor={"": color, "hovered": ft.Colors.with_opacity(0.8, color)},
            color={"": ft.Colors.WHITE},
            shape={"": ft.RoundedRectangleBorder(radius=15)},
            padding={"": 20},
            elevation={"press": 2, "": 8}
        )

    @staticmethod
    def get_input_border(color):
        """Devuelve la configuración de borde para inputs"""
        return dict(
            border_color=color,
            focused_border_color=color,
            border_radius=15,
            border_width=2
        )
    
    @staticmethod
    def get_input_style():
        """Devuelve el estilo UNIFICADO para todos los inputs de la app"""
        return {
            "label_style": ft.TextStyle(color=AppTheme.text_secondary),
            "text_style": ft.TextStyle(color=AppTheme.text_primary, size=16),
            "bgcolor": AppTheme.card_color,
            "cursor_color": AppTheme.primary,
            "border_color": AppTheme.primary,
            "focused_border_color": AppTheme.primary,
            "border_radius": 15,
            "border_width": 1,
            "content_padding": 20,
            "height": 60
        }