document.addEventListener('DOMContentLoaded', () => {
    const formCrearCurso = document.getElementById('form-crear-curso');
    const alertMessage = document.getElementById('alert-message');

    console.log("Token en crear_curso.js al DOMContentLoaded:", window.FIREBASE_ID_TOKEN ? "Presente" : "Ausente o vacío");

    if (formCrearCurso) {
        formCrearCurso.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Obtener valores del formulario
            const nombre = document.getElementById('nombreCurso').value.trim();
            const descripcion = document.getElementById('descripcionCurso').value.trim();
            const detalle = document.getElementById('detalleCurso').value.trim();
            const duracion = document.getElementById('duracionCurso').value.trim();
            const precio = parseFloat(document.getElementById('precioCurso').value);
            const imagen = document.getElementById('imagenCurso').value.trim();
            const tagsInput = document.getElementById('tagsCurso').value.trim();
            const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag) : [];

            // Validaciones en el frontend
            if (!nombre || !descripcion || isNaN(precio)) {
                mostrarAlerta('Por favor, completa los campos requeridos (Nombre, Descripción, Precio).', 'danger');
                return;
            }
            if (precio < 0) {
                mostrarAlerta('El precio no puede ser negativo.', 'danger');
                return;
            }
            if (imagen && !isValidUrl(imagen)) {
                mostrarAlerta('La URL de la imagen no es válida.', 'danger');
                return;
            }
            if (tags.length > 0 && tags.some(tag => tag.length > 50)) {
                mostrarAlerta('Cada tag debe tener menos de 50 caracteres.', 'danger');
                return;
            }

            // Verificar que FIREBASE_ID_TOKEN esté definido
            if (!window.FIREBASE_ID_TOKEN) {
                mostrarAlerta('Error de autenticación. Por favor, inicia sesión nuevamente.', 'danger');
                console.error("FIREBASE_ID_TOKEN está vacío en el momento del submit."); // Nuevo log
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
                return;
            }

            const nuevoCurso = {
                nombre,
                descripcion,
                detalle,
                duracion,
                precio,
                imagen,
                tags,
                fechaCreacion: new Date().toISOString()
            };

            try {
                const response = await fetch('/api/cursos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${window.FIREBASE_ID_TOKEN}`
                    },
                    body: JSON.stringify(nuevoCurso)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    let errorMessage = errorData.error || `Error HTTP: ${response.status}`;
                    // Mapear errores específicos a mensajes amigables
                    if (errorMessage.includes('URL de la imagen no es válida')) {
                        errorMessage = 'La URL de la imagen proporcionada no es válida.';
                    } else if (errorMessage.includes('validators no instalado')) {
                        errorMessage = 'Error del servidor. Contacta al administrador.';
                    } else if (errorMessage.includes('Faltan campos requeridos')) {
                        errorMessage = 'Asegúrate de completar todos los campos requeridos.';
                    }
                    throw new Error(errorMessage);
                }

                const data = await response.json();
                console.log('Curso creado exitosamente:', data);
                mostrarAlerta('Curso creado exitosamente!', 'success');
                formCrearCurso.reset();
                // Redirigir al dashboard después de 2 segundos
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } catch (error) {
                console.error('Error al crear el curso:', error);
                mostrarAlerta(`Error al crear el curso: ${error.message}`, 'danger');
            }
        });
    }

    function mostrarAlerta(message, type) {
        if (alertMessage) {
            alertMessage.textContent = message;
            alertMessage.className = `alert mt-3 alert-${type}`;
            alertMessage.style.display = 'block';
            setTimeout(() => {
                alertMessage.style.display = 'none';
            }, 5000);
        } else {
            console.warn('Elemento alert-message no encontrado. Mostrando alerta en consola:', message);
            alert(message); // Fallback para depuración
        }
    }

    // Función para validar URLs
    function isValidUrl(string) {
        try {
            new URL(string);
            return string.match(/\.(jpeg|jpg|png|gif|webp)$/i) !== null; // Asegurar que sea una imagen
        } catch (_) {
            return false;
        }
    }
});