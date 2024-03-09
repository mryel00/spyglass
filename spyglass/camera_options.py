def parse_dictionary_to_html_page(camera, parsed_controls='None', processed_controls='None'):
    html =  """
            <!DOCTYPE html>
            <html lang="en">
            """
    html += f"""
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Camera Settings</title>
                    <style>{get_style()}</style>
                </head>
            """
    html += f"""
                <body>
                    <h1>Available camera options</h1>
                    <h3>Parsed Controls: {parsed_controls}</h3>
                    <h3>Processed Controls: {processed_controls}</h3>
            """
    for control, values in camera.camera_controls.items():
        html += f"""
                    <div class="card-container">
                        <div class="card">
                            <h2>{control}</h2>
                            <div class="card-content">
                            <div class="setting">
                                <span class="label">Min:</span>
                                <span class="value">{values[0]}</span>
                            </div>
                            <div class="setting">
                                <span class="label">Max:</span>
                                <span class="value">{values[1]}</span>
                            </div>
                            <div class="setting">
                                <span class="label">Default:</span>
                                <span class="value">{values[2]}</span>
                            </div>
                            </div>
                        </div>
                    </div>
                """
    html += """
                </body>
            </html>
            """
    return html

def get_style():
    with (open('resources/controls_style.css', 'r')) as f:
        return f.read()

def process_controls(camera, controls: list[tuple[str, str]]) -> dict[str, any]:
    controls_dict_lower = { k.lower(): k for k in camera.camera_controls.keys() }
    if controls == None:
        return {}
    processed_controls = {}
    for key, value in controls:
        key = key.lower().strip()
        if key.lower() in controls_dict_lower.keys():
            value = value.lower().strip()
            type = get_type(value)
            k = controls_dict_lower[key]
            if bool == type:
                v = value.lower() != 'false'
            else:
                v = type(value)
            processed_controls[k] = v
    return processed_controls

def get_type(input_string: str):
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
