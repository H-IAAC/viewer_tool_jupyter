import re
configs={}
configs['line_chekpoint_color']='green'

def update_shapes(df_protocol, min_x=None, max_x=None, min_y=0, max_y=10):
    # Create and filter shapes based on the x and y ranges, or return all shapes if no range is specified
    updated_shapes = [
        dict(
            type='line',
            x0=row['timestamp'],
            x1=row['timestamp'],
            y0=min_y/2,
            y1=max_y/2,
            line=dict(color=configs['line_chekpoint_color'], width=2, dash='dash'),
            name=generate_label(row)  # Add a name to the shape based on timestamp and other information
        )
        for _, row in df_protocol.iterrows()
        if (min_x is None or row['timestamp'] >= min_x) and (max_x is None or row['timestamp'] <= max_x)
        # The above condition ensures that if min_x or max_x is not provided, all shapes are included
    ]
    return updated_shapes

def update_annotation(df_protocol,min_x=None, max_x=None, min_y=0, max_y=10):
    # Anotações df_protocol['change_point_name'].unique()verticais para cada linha verde
    annotations = [
        dict(
            x=row['timestamp']+1,
            y=min_y+(max_y-min_y)/2,  # Alinha verticalmente ao meio da linha
            xref='x',
            yref='y',
            text=generate_label(row),
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-0,
            font=dict(size=10, color=configs['line_chekpoint_color']),
            textangle=-90  # Gira o texto para que fique vertical
        )
        for _, row in df_protocol.iterrows()
        if (min_x is None or row['timestamp'] >= min_x) and (max_x is None or row['timestamp'] <= max_x)
    ]
    return annotations

def update__line_timestamp(timestamp,y0,y1):
    return [dict(
                type='line',
                x0=timestamp,
                x1=timestamp,
                y0=y0,  # Ajuste para cobrir todo o eixo Y
                y1=y1,  # Ajuste para cobrir todo o eixo Y
                xref='x',
                yref='paper',
                line=dict(color='orange', width=2, dash='dash'),
                name='timestamp_id'
            )]


def update_line_color(matching_line,updated_figure):
    name=get_name(matching_line['left_label'],
                            matching_line['change_point_name'],
                            matching_line['change_point_time'],"x")##############mudar aquiii
    shapes=updated_figure['layout']['shapes']
    annotations=[]#updated_figure['layout']['annotations']
    #shapes[index]=dict(color=configs['line_chekpoint_select_color'],dash='dash')
    for shape in shapes:
        
        if shape.get('name') == name:
            if(matching_line['timestamp']!= shape.get('x0')):
                # Atualize a cor do shape
                shape['line'] = dict(color=configs['line_chekpoint_select_color'],dash='dash')
                line_found = True
                for annotation in annotations:
                    if annotation['text'] == name:
                        # Atualize a posição x da annotation
                        annotation['x'] = shape['x0']+1  # Supondo que x0 é a nova posição x do shape
                        annotation['font'] = dict(color=configs['line_chekpoint_select_color'])
                        break


        # Atualize os shapes no layout da figura
    updated_figure['layout']['shapes'] = shapes
    updated_figure['layout']['annotations'] =annotations
    
    

    return updated_figure

def get_name(left_label,change_point_name,change_point_time,sensor_ref):
        name = f"{left_label}__{change_point_name}__{change_point_time}__{sensor_ref}"
        return name

def generate_label(row):
    return f"{row['left_label']}__{row['change_point_name']}__{row['change_point_time']}__{row['sensor_ref']}"

def get_columns_df_protocol():
    return ["timestamp","left_label","change_point_name","change_point_time","sensor_ref"]

def extract_index_from_key(key):
    match = re.search(r'shapes\[(\d+)\]', key)
    if match:
        return int(match.group(1))
    return None