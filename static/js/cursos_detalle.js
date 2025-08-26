document.addEventListener('DOMContentLoaded', function () {
    const detalleCursoContainer = document.getElementById('detalle-curso-container');

    if (!detalleCursoContainer) {
        console.error('Contenedor de curso no encontrado');
        return; // Salir si no estamos en la página de detalle del curso
    }

    // Extraer el ID del curso desde el path de la URL
    const path = window.location.pathname;
    const cursoIdMatch = path.match(/\/cursos_detalle\/(.+)/);
    const cursoId = cursoIdMatch ? cursoIdMatch[1] : null;

    if (!cursoId) {
        detalleCursoContainer.innerHTML = '<div class="alert alert-danger col-12" role="alert">ID de curso no especificado en la URL.</div>';
        console.error('ID de curso no especificado en la URL');
        return;
    }

    // Hacer solicitud a la API para obtener los datos del curso
    fetch(`/api/cursos/${cursoId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(curso => {
        if (curso) {
            detalleCursoContainer.innerHTML = ''; // Limpiar

            const col = document.createElement('div');
            col.classList.add('col-lg-8', 'col-md-10', 'mx-auto'); 

            const card = document.createElement('div');
            card.classList.add('card', 'h-100', 'border-0', 'shadow-lg', 'card-detalle'); 

            const imagenSrc = curso.imagen || '/static/images/placeholder.jpg';
            const imgElement = document.createElement('img');
            imgElement.src = imagenSrc;
            imgElement.classList.add('card-img-top-detail');
            imgElement.alt = curso.nombre || 'Imagen del curso';
            imgElement.style = 'max-height: 500px; object-fit: cover;'; 

            const cardBody = document.createElement('div');
            cardBody.classList.add('card-body');

            const titulo = document.createElement('h1');
            titulo.classList.add('card-title', 'mb-3');
            titulo.textContent = curso.nombre || 'Nombre del Curso';

            const descripcion = document.createElement('p');
            descripcion.classList.add('card-text', 'lead');
            descripcion.textContent = curso.descripcion || 'Descripción detallada no disponible.';
            
            const detalleCompleto = document.createElement('p');
            detalleCompleto.classList.add('card-text');
            detalleCompleto.innerHTML = `<strong>Detalles completos:</strong> ${curso.detalle || 'No hay detalles adicionales.'}`;

            const duracion = document.createElement('p');
            duracion.classList.add('card-text');
            duracion.innerHTML = `<strong>Duración:</strong> ${curso.duracion || 'N/A'}`;

            const precio = document.createElement('p');
            precio.classList.add('card-text', 'h4', 'text-primary');
            precio.textContent = `Precio: $${curso.precio || '0'}`;

            const tagsContainer = document.createElement('div');
            tagsContainer.classList.add('d-flex', 'flex-wrap', 'gap-2', 'mt-3', 'mb-3');
            if (curso.tags) {
                const tags = Array.isArray(curso.tags) ? curso.tags : curso.tags.split(',');
                tags.forEach(tag => {
                    const tagBadge = document.createElement('span');
                    tagBadge.classList.add('badge', 'bg-secondary', 'me-1');
                    tagBadge.textContent = tag.trim();
                    tagsContainer.appendChild(tagBadge);
                });
            }


    // Crear el botón para adquirir los cursos
    const botonAdquirir = document.createElement('button');
    botonAdquirir.classList.add('btn', 'btn-primary', 'mt-auto');
    botonAdquirir.textContent = 'Adquirir';

    // Listener para el botón de adquirir
    botonAdquirir.addEventListener('click', async (e) => {
        e.preventDefault();

        // Obtenemos el token de la variable global que inyecta Flask
        const idToken = window.FIREBASE_ID_TOKEN;
        console.log("Token recibido en el front-end:", idToken);
        // Si el token no existe, significa que el usuario no está logueado
        if (!idToken) {
            alert('Debes iniciar sesión para adquirir un curso.');
            window.location.href = '/login';
            return;
        }

        try {
            const response = await fetch(`/api/adquirir_curso/${cursoId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Enviamos el token en el header de Authorization
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({}) // Cuerpo de la solicitud, puede estar vacío
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert(result.message);
                window.location.href = '/dashboard';
            } else {
                // Manejo de errores específicos del servidor
                if (response.status === 401 || response.status === 403) {
                    alert('Error de autenticación. Por favor, inicia sesión de nuevo.');
                    window.location.href = '/login';
                } else {
                    alert(`Error: ${result.error}`);
                }
            }
        } catch (error) {
            console.error('Error al procesar la compra:', error);
            alert('Hubo un error al procesar la compra. Intenta de nuevo.');
        }
    });


            cardBody.appendChild(titulo);
            cardBody.appendChild(descripcion);
            cardBody.appendChild(detalleCompleto);
            cardBody.appendChild(duracion);
            cardBody.appendChild(precio);
            cardBody.appendChild(tagsContainer);
            cardBody.appendChild(botonAdquirir);
            
            card.appendChild(imgElement);
            card.appendChild(cardBody);
            col.appendChild(card);
            detalleCursoContainer.appendChild(col);
        } else {
            detalleCursoContainer.innerHTML = '<div class="alert alert-warning col-12" role="alert">Curso no encontrado.</div>';
        }
    })
    .catch(error => {
        console.error('Error al obtener los detalles del curso:', error);
        detalleCursoContainer.innerHTML = '<div class="alert alert-danger col-12" role="alert">Error al cargar los detalles del curso. Por favor, inténtalo de nuevo más tarde.</div>';
    });
});