document.addEventListener('DOMContentLoaded', () => {
    console.log('editar_curso.js cargado.');

    const formEditarCurso = document.getElementById('formulario-editar-curso');
    const alertMessage = document.getElementById('alert-message');
    const cursoIdInput = document.getElementById('curso_id');

    // Obtener el ID del curso desde la variable global definida en el HTML
    const cursoId = window.CURSO_ID;

    // **************** ESTA ES LA ÚNICA DECLARACIÓN DE firebaseIdToken ****************
    // OBTENEMOS EL TOKEN DE FIREBASE ANTES DE CUALQUIER LLAMADA A FUNCIONES QUE LO USEN.
    const firebaseIdToken = window.FIREBASE_ID_TOKEN || '';
    console.log('JS: Valor de la constante local firebaseIdToken:', firebaseIdToken); // Verificación


    // Función para cargar los datos del curso y prellenar el formulario
    async function cargarDatosCurso(id) {
        try {
            const response = await fetch(`/api/cursos/${id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${firebaseIdToken}` // Ahora firebaseIdToken ya estará inicializado
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                let errorMessage = errorData.error || `Error ${response.status}: ${response.statusText}`;
                if (response.status === 401 || response.status === 403) {
                    errorMessage = 'No autorizado para ver este curso. Redirigiendo a login...';
                    mostrarAlerta(errorMessage, 'danger');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 3000);
                }
                throw new Error(errorMessage);
            }

            const curso = await response.json();
            console.log('Datos del curso cargados:', curso);

            // Rellenar los campos del formulario
            document.getElementById('nombreCursoId').value = curso.nombre || '';
            document.getElementById('descripcionCursoId').value = curso.descripcion || '';
            document.getElementById('detalleCursoId').value = curso.detalle || '';
            document.getElementById('precioCursoId').value = curso.precio || 0;
            document.getElementById('imagenCursoId').value = curso.imagen || '';
            document.getElementById('tagsCursoId').value = (curso.tags || []).join(', ');

        } catch (error) {
            console.error('Error al cargar los datos del curso:', error);
            mostrarAlerta(`Error al cargar los datos del curso: ${error.message}`, 'danger');
        }
    }


    // Validación del ID del curso
    if (!cursoId || cursoId === 'None' || cursoId.trim() === '') {
        mostrarAlerta('Error: ID del curso no proporcionado o inválido.', 'danger');
        console.error('CURSO_ID es nulo, "None" o vacío:', cursoId);
        // Si el ID es inválido, podrías querer no llamar a cargarDatosCurso
    } else {
        // Establecer el ID en el campo oculto
        if (cursoIdInput) {
            cursoIdInput.value = cursoId;
        }
        // Llamar a cargarDatosCurso solo si el cursoId es válido.
        cargarDatosCurso(cursoId);
    }


    // Event listener para el envío del formulario
    if (formEditarCurso) {
        formEditarCurso.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (!cursoId || cursoId === 'None' || cursoId.trim() === '') {
                mostrarAlerta('Error: No se puede actualizar el curso sin un ID válido.', 'danger');
                return;
            }

            const formData = new FormData(formEditarCurso);
            const data = {
                nombre: formData.get('nombre'),
                descripcion: formData.get('descripcion'),
                detalle: formData.get('detalle'),
                precio: parseFloat(formData.get('precio')),
                imagen: formData.get('imagen'),
                tags: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag)
            };

            // Validación básica para la URL de la imagen
            if (data.imagen && !isValidUrl(data.imagen)) {
                mostrarAlerta('La URL de la imagen no es válida o no es una imagen.', 'danger');
                return;
            }

            try {
                const response = await fetch(`/api/cursos/${cursoId}`, {
                    method: 'PUT', // o PATCH según tu API
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${firebaseIdToken}` // Se usa 'firebaseIdToken' aquí
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    let errorMessage = errorData.error || `Error ${response.status}: ${response.statusText}`;
                    if (response.status === 401 || response.status === 403) {
                        errorMessage = 'No autorizado para actualizar este curso. Redirigiendo a login...';
                        mostrarAlerta(errorMessage, 'danger');
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 3000);
                    }
                    throw new Error(errorMessage);
                }

                const responseData = await response.json();
                console.log('Curso actualizado exitosamente:', responseData);
                mostrarAlerta('Curso actualizado exitosamente.', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } catch (error) {
                console.error('Error al actualizar el curso:', error);
                mostrarAlerta(`Error al actualizar el curso: ${error.message}`, 'danger');
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