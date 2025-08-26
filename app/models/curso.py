class Curso:
    def __init__(self, id, nombre, descripcion, precio, duracion=None, tags=None, detalle=None, imagen=None, fechaCreacion=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.duracion = duracion
        self.tags = tags or []
        self.detalle = detalle
        self.imagen = imagen
        self.fechaCreacion = fechaCreacion

    @staticmethod
    def from_dict(curso_id, data):
        return Curso(
            id=curso_id,
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            precio=data.get('precio', 0),
            duracion=data.get('duracion', ''),
            tags=data.get('tags', []),
            detalle=data.get('detalle', ''),
            imagen=data.get('imagen', ''),
            fechaCreacion=data.get('fechaCreacion', '')
        )