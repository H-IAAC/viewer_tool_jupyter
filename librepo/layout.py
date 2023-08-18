from dash import html

class BaseLayout:
    def __init__(self, width='100%', height='100%'):
        self.components = []
        self.width = width
        self.height = height

    def append(self, *args, **kwargs):
        self.components.extend((component, kwargs) for component in args)

    def get_layout(self):
        component_styles = {'flex': '1', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}
        self.components = [(component.get_layout(), kwargs) if hasattr(component, 'get_layout') else (component, kwargs) for component, kwargs in self.components]

        layout_components = []
        for component, kwargs in self.components:
            component_style = {'width': kwargs.get('width', self.width), 'height': kwargs.get('height', self.height)}
            component_style.update(component_styles)
            layout_components.append(html.Div(component, style=component_style))

        layout = html.Div(layout_components, style={'width': self.width, 'height': self.height, 'display': 'flex'})
        return layout

class VerticalLayout(BaseLayout):
    def get_layout(self):
        layout = super().get_layout()
        layout.style.update({'flexDirection': 'column'})
        return layout

class HorizontalLayout(BaseLayout):
    def get_layout(self):
        layout = super().get_layout()
        layout.style.update({'flexDirection': 'row'})
        return layout