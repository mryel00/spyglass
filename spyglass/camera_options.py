def parse_dictionary_to_html_page(camera, parsed_controls='None', processed_controls='None'):
    html = """
            <html>
                <head>
                    <title>Spyglass camera options</title>
                    <style>
                        table {
                            border-collapse: collapse;
                            width: 100%;
                        }
                        
                        th, td {
                            border: 1px solid black;
                            padding: 8px;
                            text-align: left;
                        }
                        
                        tr:nth-child(even) {
                            background-color: #f2f2f2;
                        }
                    </style>
                </head>
            """
    html+= f"""
                <body>
                    <h1>Available camera options</h1>
                    <h3>Parsed Controls: {parsed_controls}</h3>
                    <h3>Processed Controls: {processed_controls}</h3>
                    <table>
                        <tr>
                            <th>Option</th>
                            <th>Min value</th>
                            <th>Max value</th>
                            <th>Default value</th>
                        </tr>
        """
    for control,values in camera.camera_controls.items():
        html += f"""
                        <tr>
                            <td>{control}</td>
                            <td>{values[0]}</td>
                            <td>{values[1]}</td>
                            <td>{values[2]}</td>
                        </tr>
                """
    html += """
                    </table>
                </body>
            </html>
            """
    return html


def process_controls(camera, controls):
    controls_dict = camera.camera_controls
    controls_dict_lower = {k.lower(): k for k, v in controls_dict.items()}
    processed_controls = []
    if controls == None:
        return None
    for key, value in controls:
        if key.lower() in controls_dict_lower.keys():
            type = get_type(value)
            k = controls_dict_lower[key.lower()]
            if bool == type:
                camera.set_controls({k: value.lower() != 'false'})
            else:
                camera.set_controls({k: type(value)})
            processed_controls.append((key, value))
    return processed_controls

def get_type(input_string):
    try:
        float_value = float(input_string)
        if float_value.is_integer():
            return int
        else:
            return float
    except ValueError:
        pass
    
    if input_string.lower() in ['true', 'false']:
        return bool
    
    return str
