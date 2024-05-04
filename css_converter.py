PIXEL_THRESHOLD = 5.0

def has_one_child_named (obj, name):
    return len(obj.children) == 1 and layout_is(obj.children[0], name)

def layout_is(obj, name):
    return obj.type == "text" and obj.value.lower().replace(" ", "") == name.lower()

def generate_html_from_layout(layout, indent_level=0):
    html_code = ""
    indent = "\t" * indent_level
    
    # check for image or button
    if has_one_child_named (layout, "img") or layout_is(layout, "img"):
        return f'{indent}<img src="img.png" alt="image" class="{" ".join(generate_box_classes(layout))}" />\n'
    elif has_one_child_named (layout, "button") or layout_is(layout, "button"):
        return f'{indent}<button class="{" ".join(generate_box_classes(layout))}">Button</button>\n'

    if layout.type == "box":
        if (indent_level == 0):
            html_code += f'{indent}<div class="fixed w-[{layout.size[0]}px] h-[{layout.size[1]}px]">\n'
        else:
            html_code += f'{indent}<div class="{" ".join(generate_box_classes(layout))}">\n'
        for child in layout.children:
            html_code += generate_html_from_layout(child, indent_level + 1)
        html_code += f'{indent}</div>\n'
    elif layout.type == "text":
        html_code += f'{indent}<span class="{" ".join(generate_text_classes(layout))}">{layout.value}</span>\n'
    return html_code

def generate_box_classes(layout):
    return [f"fixed w-[{layout.size[0]}px]", f"h-[{layout.size[1]}px]", f"left-[{layout.position[0]}px]",  f"top-[{layout.position[1]}px]", "border-2"]

def generate_text_classes(layout):
    return ["truncate", "fixed", f"left-[{layout.position[0]}px]", f"top-[{layout.position[1]}px]", f"text-[{layout.size[1]}px]"]    


def generate_circle_classes(layout):
    size_x, size_y = layout.size
    classes = [f"size-{size_x * 4 // 16}", "rounded-full", "fixed", "border-2"]
    return classes

def generate_html(layout):
    file = open("index.html", "w")
    file.write("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
    <body>
""")
    file.write(generate_html_from_layout(layout))
    file.write("</body>\n</html>")