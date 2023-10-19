import dash
from dash.development.base_component import Component
import dash_html_components as html
from dash.dependencies import Input, Output

class LinearLayout(html.Div):
    def __init__(self, children=[], width="wrap_content", height="wrap_content", orientation="horizontal", align="start", gap=0):
        super().__init__(children)
        self._width = self._check_dimension(width)
        self._height = self._check_dimension(height)
        self._orientation = self._check_orientation(orientation)
        self._align = self._check_align(orientation, align)
        self._gap = self._check_gap(gap)
        self.style = {
            "width": self._width,
            "height": self._height,
            "overflowX": "auto" if orientation == "horizontal" else "hidden",
            "overflowY": "auto" if orientation == "vertical" else "hidden",
            "display": "flex",
            "flexDirection": self._orientation,
            "alignItems": self._align,
            "justifyContent": "space-between",
            "gap": self._gap
        }
        for child in self.children:
            child.style["flexShrink"] = "0"
    
    def _check_dimension(self, dim):
        if dim == "match_parent":
            return "100%"
        elif dim == 0 or dim == "wrap_content":
            return "fit-content"
        elif type(dim) == int or type(dim) == float and dim > 0:
            return dim
        else:
            raise ValueError("Invalid dimension value. Use 'match_parent', 'wrap_content' or a positive number.")
        
    def _check_orientation(self, orientation):
        if orientation == "horizontal":
            return "row"
        elif orientation == "vertical":
            return "column"
        else:
            raise ValueError("Invalid orientation value. Use 'horizontal' or 'vertical'.")
    
    def _check_align(self, orientation, align):
        if align == "start":
            return "start"
        elif align == "center":
            return "center"
        elif align == "end":
            return "end"
        elif orientation == "horizontal":
            if align == "top":
                return "start"
            elif align == "bottom":
                return "end"
            else:
                raise ValueError("Invalid align value. If orientation is 'horizontal', use 'start', 'center', 'end', 'top' or 'bottom'.")
        elif orientation == "vertical":
            if align == "left":
                return "start"
            elif align == "right":
                return "end"
            else:
                raise ValueError("Invalid align value. If orientation is 'vertical', use 'start', 'center', 'end', 'left' or 'right'.")
            
    def _check_gap(self, gap):
        if type(gap) == int or type(gap) == float and gap >= 0:
            return gap
        else:
            raise ValueError("Invalid gap value. Use a positive number.")
        
    def append(self, component):
        self.children.append(component)
        
class ConstraintLayout(html.Div):
    def __init__(self, components_with_constraints, width="match_parent", height="match_parent"):
        self._width = self._check_dimension(width)
        self._height = self._check_dimension(height)
        self.style = {
            "width": self._width,
            "height": self._height,
            "overflow": "hidden",
            "position": "absolute"
        }
        super().__init__(list(map(lambda comp: comp.component, components_with_constraints)))
        
    def _check_dimension(self, dim):
        if dim == "match_parent":
            return "100%"
        elif dim == 0 or dim == "wrap_content":
            return "fit-content"
        elif type(dim) == int or type(dim) == float and dim > 0:
            return dim
        else:
            raise ValueError("Invalid dimension value. Use 'match_parent', 'wrap_content' or a positive number.")

class ComponentWithConstraints:
    def __init__(self,
                 component,
                 top_to_top_of = None,
                 top_to_bottom_of = None, 
                 left_to_left_of = None, 
                 left_to_right_of = None, 
                 bottom_to_bottom_of = None, 
                 bottom_to_top_of = None, 
                 right_to_right_of = None, 
                 right_to_left_of = None, 
                 top_margin = 0,
                 left_margin = 0,
                 bottom_margin = 0,
                 right_margin = 0):
        self.component = component
        if ((top_to_top_of != None) + (top_to_bottom_of != None) + (bottom_to_bottom_of != None) + (bottom_to_top_of != None)) > 1:
            raise ValueError("'top_to_top_of', 'top_to_bottom_of', 'bottom_to_bottom_of', 'bottom_to_top_of'. Only one of these can be set different than None.")
        if ((left_to_left_of != None) + (left_to_right_of != None) + (right_to_right_of != None) + (right_to_left_of != None)) > 1:
            raise ValueError("'left_to_left_of', 'left_to_right_of', 'right_to_right_of', 'right_to_left_of'. Only one of these can be set different than None.")
        
        if top_to_top_of != None:
            self._top = top_to_top_of.style["top"] + top_margin
        elif top_to_bottom_of != None:
            self._top = top_to_bottom_of.style["top"] + float(top_to_bottom_of.style["height"].replace("px", "")) + top_margin
        else:
            self._top = top_margin
            
        if left_to_left_of != None:
            self._left = left_to_left_of.style["left"] + left_margin
        elif left_to_right_of != None:
            self._left = left_to_right_of.style["left"] + float(left_to_right_of.style["width"].replace("px", "")) + left_margin
        else:
            self._left = left_margin
            
        if bottom_to_bottom_of != None:
            self._bottom = bottom_to_bottom_of.style["bottom"] + bottom_margin
        elif bottom_to_top_of != None:
            self._bottom = bottom_to_top_of.style["bottom"] + float(bottom_to_top_of.style["height"].replace("px", "")) + bottom_margin
        else:
            self._bottom = bottom_margin
            
        if right_to_right_of != None:
            self._right = right_to_right_of.style["right"] + right_margin
        elif right_to_left_of != None:
            self._right = right_to_left_of.style["right"] + float(right_to_left_of.style["width"].replace("px", "")) + right_margin
        else:
            self._right = right_margin
            
        self.component.style.update({
            "position": "absolute",
            "top": self._top,
            "left": self._left,
            "bottom": self._bottom,
            "right": self._right,
        })
        
class HorizontalLayout(LinearLayout):
    def __init__(self, children=[], width="match_parent", height="wrap_content", align="start", gap=0):
        super().__init__(children, width=width, height=height, orientation="horizontal", align=align, gap=0)
        
class VerticalLayout(LinearLayout):
    def __init__(self, children=[], width="wrap_content", height="match_parent", align="start", gap=0):
        super().__init__(children, width=width, height=height, orientation="vertical", align=align, gap=0)