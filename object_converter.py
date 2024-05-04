class Object:
    def __init__ (self, type, position, size, value=None):
        self.type = type
        self.position = position
        self.size = size
        self.value = value
        self.children = []
    
    def find_parent (self, position):
        x, y = position
        for obj in self.children:
            if x >= obj.position[0] and x <= obj.position[0] + obj.size[0] and y >= obj.position[1] and y <= obj.position[1] + obj.size[1]:
                return obj.find_parent(position)
        return self
    
    def sort_by_y (self):
        self.children = sorted(self.children, key=lambda obj: obj.position[1])
        for obj in self.children:
            obj.sort_by_y()

    def sort_by_x (self):
        self.children = sorted(self.children, key=lambda obj: obj.position[0])
        for obj in self.children:
            obj.sort_by_x()

    def __str__(self, level=0):
        result = f"{'    '*level}{self.type}, position={self.position}, size={self.size}{f', value={self.value}' if self.value != None else ''}"
        for child in self.children:
            result += f"\n{child.__str__(level + 1)}"
        return result

"""
 Helper function to convert the layout detected from the cv_object_detector into
 python Object class format.
"""
def convert_layout_to_objects (shapes, text):
    # ensure shapes are added from largest to smallest
    shapes = sorted(shapes, key=lambda shape: shape.w * shape.h)
    shapes.reverse()
    # the global parent will always be the largest shape
    global_parent = Object("box", (0, 0), (shapes[0].w, shapes[0].h))
    for shape in shapes:
        parent = global_parent.find_parent((shape.x, shape.y))
        parent.children.append(Object(shape.type, (shape.x, shape.y), (shape.w, shape.h)))
    for t in text:
        parent = global_parent.find_parent((t.x, t.y))
        parent.children.append(Object("text", (t.x, t.y), (t.w, t.h), t.text))
    global_parent.sort_by_y()
    global_parent.sort_by_x()
    return global_parent
    