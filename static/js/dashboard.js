// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', async () => {
    console.log('dashboard.js cargado.');

    // Obtener el rol del usuario de la variable global inyectada por Flask
    const userRole = window.USER_ROLE;
    
    console.log("Rol del usuario en dashboard.js:", userRole);

    // Elementos del dashboard de ADMIN
    const adminDashboardSection = document.getElementById('admin-dashboard-section');
    const btnGestionarCursos = document.getElementById('btn-gestionar-cursos');
    const gestionCursosContainer = document.getElementById('gestion-cursos-container');
    const cursosAdminList = document.getElementById('cursos-admin-list');
    const btnGestionarUsuarios = document.getElementById('btn-gestionar-usuarios');
    const gestionUsuariosContainer = document.getElementById('gestion-usuarios-container');
    const usuariosAdminList = document.getElementById('usuarios-admin-list');

    // Elementos del dashboard de USUARIO COMÚN
    const userDashboardSection = document.getElementById('user-dashboard-section');
    const btnMisCursos = document.getElementById('btn-mis-cursos');
    const misCursosContainer = document.getElementById('mis-cursos-container');
    const misCursosList = document.getElementById('mis-cursos-list');
    const btnMiPerfil = document.getElementById('btn-mi-perfil');
    const miPerfilContainer = document.getElementById('mi-perfil-container');
    const miPerfilData = document.getElementById('mi-perfil-data');


    // Función para ocultar todos los contenedores de contenido dinámico
    function ocultarTodosLosContenedores() {
        if (gestionCursosContainer) gestionCursosContainer.style.display = 'none';
        if (gestionUsuariosContainer) gestionUsuariosContainer.style.display = 'none';
        if (misCursosContainer) misCursosContainer.style.display = 'none';
        if (miPerfilContainer) miPerfilContainer.style.display = 'none';
    }

    // --- CAMBIO CLAVE AQUÍ ---
    // Esta función ahora simplemente devuelve el token que Flask ya ha refrescado
    // y pasado a la variable global window.FIREBASE_ID_TOKEN.
    async function getCurrentFirebaseIdToken() {
        const idToken = window.FIREBASE_ID_TOKEN;
        if (!idToken) {
            console.warn('No se encontró FIREBASE_ID_TOKEN en window. Redirigiendo a login.');
            // Redirige al login si no hay token, ya que es crítico para las operaciones API
            alert('Tu sesión ha expirado o es inválida. Por favor, vuelve a iniciar sesión.');
            window.location.href = '/login';
            return null;
        }
        return idToken;
    }
    // --- FIN CAMBIO CLAVE ---

    // Lógica para cargar cursos para administración (solo para ADMIN)
    async function cargarCursosParaAdministracion() {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins carguen esto
        ocultarTodosLosContenedores();
        gestionCursosContainer.style.display = 'block';
        cursosAdminList.innerHTML = '<p class="text-center">Cargando cursos...</p>';
        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                cursosAdminList.innerHTML = '<p class="text-danger">Error: Token de autenticación no disponible. Por favor, inicia sesión de nuevo.</p>';
                return;
            }

            const response = await fetch('/api/cursos', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${firebaseIdToken}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            cursosAdminList.innerHTML = '';
            if (!data || Object.keys(data).length === 0) {
                cursosAdminList.innerHTML = '<p class="text-center text-muted">No hay cursos disponibles para gestionar.</p>';
                return;
            }
            const row = document.createElement('div');
            row.classList.add('row', 'row-cols-1', 'row-cols-md-2', 'row-cols-lg-3', 'g-3');

            for (let key in data) {
                const curso = data[key];
                if (!curso || !curso.nombre || !curso.descripcion || !curso.precio) {
                    continue;
                }

                const col = document.createElement('div');
                col.classList.add('col');
                const card = document.createElement('div');
                card.classList.add('card', 'h-100', 'shadow-sm');
                card.style.display = 'flex';
                card.style.flexDirection = 'column';

                const cardBody = document.createElement('div');
                cardBody.classList.add('card-body', 'd-flex', 'flex-column');

                const titulo = document.createElement('h5');
                titulo.classList.add('card-title');
                titulo.textContent = curso.nombre;

                const descripcion = document.createElement('p');
                descripcion.classList.add('card-text', 'flex-grow-1');
                descripcion.textContent = curso.descripcion;

                const precio = document.createElement('p');
                precio.classList.add('card-text', 'fw-bold');
                precio.textContent = `Precio: $${curso.precio}`;

                const btnGroup = document.createElement('div');
                btnGroup.classList.add('d-flex', 'justify-content-between', 'mt-3');

                const btnEditar = document.createElement('a');
                btnEditar.classList.add('btn', 'btn-primary', 'btn-sm', 'w-48', 'editar-curso-btn');
                btnEditar.textContent = 'Editar';
                btnEditar.href = `/editar_curso/${key}`;
                btnEditar.dataset.cursoId = key;

                const btnEliminar = document.createElement('button');
                btnEliminar.classList.add('btn', 'btn-danger', 'btn-sm', 'w-48');
                btnEliminar.textContent = 'Eliminar';
                btnEliminar.addEventListener('click', () => {
                    if (confirm(`¿Estás seguro de eliminar el curso "${curso.nombre}"?`)) {
                        eliminarCurso(key);
                    }
                });

                btnGroup.appendChild(btnEditar);
                btnGroup.appendChild(btnEliminar);

                cardBody.appendChild(titulo);
                cardBody.appendChild(descripcion);
                cardBody.appendChild(precio);
                cardBody.appendChild(btnGroup);

                card.appendChild(cardBody);
                col.appendChild(card);
                row.appendChild(col);
            }
            cursosAdminList.appendChild(row);
        } catch (error) {
            console.error('Error al cargar cursos para administración:', error);
            cursosAdminList.innerHTML = `<p class="text-danger">Error al cargar los cursos: ${error.message}</p>`;
        }
    }

    // Lógica para cargar usuarios para administración (solo para ADMIN)
    async function cargarUsuariosParaAdministracion() {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins carguen esto
        ocultarTodosLosContenedores();
        gestionUsuariosContainer.style.display = 'block';
        usuariosAdminList.innerHTML = '<p class="text-center">Cargando usuarios...</p>';
        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                alert('Error: Token de autenticación no disponible para cargar usuarios. Por favor, recarga la página.');
                return;
            }

            const response = await fetch('/api/users', {
                headers: {
                    'Authorization': `Bearer ${firebaseIdToken}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            const users = await response.json();

            usuariosAdminList.innerHTML = '';
            if (!users || users.length === 0) {
                usuariosAdminList.innerHTML = '<p class="text-center text-muted">No hay usuarios registrados para gestionar.</p>';
                return;
            }

            const table = document.createElement('table');
            table.classList.add('table', 'table-striped', 'table-hover', 'shadow-sm');
            table.innerHTML = `
                <thead class="table-dark">
                    <tr>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Rol</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            `;
            const tbody = table.querySelector('tbody');

            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.nombre}</td>
                    <td>${user.email}</td>
                    <td><span id="rol-${user.id}">${user.rol}</span></td>
                    <td>
                        <button class="btn btn-warning btn-sm me-2" data-user-id="${user.id}" data-current-rol="${user.rol}">Editar Rol</button>
                        <button class="btn btn-danger btn-sm" data-user-id="${user.id}">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            usuariosAdminList.appendChild(table);

            usuariosAdminList.querySelectorAll('.btn-warning[data-user-id]').forEach(button => {
                button.addEventListener('click', (e) => {
                    const userId = e.target.dataset.userId;
                    const currentRol = e.target.dataset.currentRol;
                    editarRolUsuario(userId, currentRol);
                });
            });

            usuariosAdminList.querySelectorAll('.btn-danger[data-user-id]').forEach(button => {
                button.addEventListener('click', (e) => {
                    const userId = e.target.dataset.userId;
                    const userRow = e.target.closest('tr');
                    const userEmail = userRow.querySelector('td:nth-child(2)').textContent;
                    if (confirm(`¿Estás seguro de eliminar al usuario ${userEmail}?`)) {
                        eliminarUsuarioAdmin(userId);
                    }
                });
            });
        } catch (error) {
            console.error('Error al cargar usuarios para administración:', error);
            usuariosAdminList.innerHTML = `<p class="text-danger">Error al cargar los usuarios: ${error.message}</p>`;
        }
    }

    // Lógica para eliminar curso (solo para ADMIN)
    async function eliminarCurso(cursoId) {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins puedan eliminar
        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                alert('Error: Token de autenticación no disponible para eliminar. Por favor, inicia sesión de nuevo.');
                return;
            }

            const response = await fetch(`/api/cursos/${cursoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${firebaseIdToken}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}`);
            }
            const data = await response.json();
            alert(data.message || 'Curso eliminado exitosamente!');
            cargarCursosParaAdministracion();
        } catch (error) {
            console.error('Error eliminando curso:', error);
            alert('Hubo un error al eliminar el curso: ' + error.message);
        }
    }

    // Lógica para actualizar curso (solo para ADMIN)
    async function actualizarCursoViaApi(cursoId, updatedData) {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins puedan actualizar
        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                alert('Error: Token de autenticación no disponible para actualizar. Por favor, inicia sesión de nuevo.');
                return;
            }

            const response = await fetch(`/api/cursos/${cursoId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${firebaseIdToken}`
                },
                body: JSON.stringify(updatedData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}`);
            }
            const data = await response.json();
            alert(data.message || 'Curso actualizado exitosamente!');
            cargarCursosParaAdministracion();
        } catch (error) {
            console.error('Error actualizando curso:', error);
            alert('Hubo un error al actualizar el curso: ' + error.message);
        }
    }

    // Lógica para editar rol de usuario (solo para ADMIN)
    async function editarRolUsuario(userId, currentRol) {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins puedan editar roles
        const newRol = prompt(`Editar rol para el usuario (ID: ${userId}). Rol actual: ${currentRol}.\nIngresa el nuevo rol (ej. 'admin' o 'user'):`);
        if (newRol === null || newRol.trim() === '') {
            return;
        }
        
        const normalizedNewRol = newRol.toLowerCase(); 

        if (normalizedNewRol !== 'admin' && normalizedNewRol !== 'user') {
            alert("Rol inválido. Por favor, ingresa 'admin' o 'user'.");
            return;
        }

        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                alert('Error: Token de autenticación no disponible para editar rol. Por favor, recarga la página.');
                return;
            }

            const response = await fetch(`/api/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${firebaseIdToken}`
                },
                body: JSON.stringify({ rol: normalizedNewRol })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}`);
            }
            const data = await response.json();
            alert(data.message || 'Rol de usuario actualizado exitosamente.');
            const rolSpan = document.getElementById(`rol-${userId}`);
            if (rolSpan) {
                rolSpan.textContent = normalizedNewRol;
                const editButton = document.querySelector(`.btn-warning[data-user-id="${userId}"]`);
                if (editButton) {
                    editButton.dataset.currentRol = normalizedNewRol;
                }
            }
        } catch (error) {
            console.error('Error al actualizar el rol del usuario:', error);
            alert('Hubo un error al actualizar el rol: ' + error.message);
        }
    }

    // Lógica para eliminar usuario (solo para ADMIN)
    async function eliminarUsuarioAdmin(userId) {
        if (userRole !== 'admin') return; // Asegurarse de que solo admins puedan eliminar
        try {
            const firebaseIdToken = await getCurrentFirebaseIdToken();
            if (!firebaseIdToken) {
                alert('Error: Token de autenticación no disponible para eliminar usuario. Por favor, inicia sesión de nuevo.');
                return;
            }

            const response = await fetch(`/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${firebaseIdToken}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}`);
            }
            const data = await response.json();
            alert(data.message || 'Usuario eliminado exitosamente!');
            cargarUsuariosParaAdministracion();
        } catch (error) {
            console.error('Error eliminando usuario:', error);
            alert('Hubo un error al eliminar el usuario: ' + error.message);
        }
    }

    async function cargarMisCursos() {
        if (userRole !== 'user') return;
        ocultarTodosLosContenedores();
        misCursosContainer.style.display = 'block';
        misCursosList.innerHTML = '<p class="text-center">Cargando tus cursos...</p>';
    
        try {
            const firebaseIdToken = window.FIREBASE_ID_TOKEN;
            const userId = window.FIREBASE_AUTH_UID;
            
            if (!firebaseIdToken || !userId) {
                misCursosList.innerHTML = '<p class="text-center text-muted">Debes iniciar sesión para ver tus cursos.</p>';
                console.warn("Faltan FIREBASE_ID_TOKEN o FIREBASE_AUTH_UID");
                return;
            }
    
            const userResponse = await fetch(`/api/users/${userId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${firebaseIdToken}`,
                    'Content-Type': 'application/json'
                }
            });
    
            if (!userResponse.ok) {
                const errorData = await userResponse.json();
                throw new Error(errorData.error || `Error ${userResponse.status}`);
            }
            const userData = await userResponse.json();
            const cursosAdquiridosIds = userData.cursos_adquiridos || [];
    
            misCursosList.innerHTML = '';
            if (cursosAdquiridosIds.length === 0) {
                misCursosList.innerHTML = '<p class="text-center text-muted">Aún no tienes cursos adquiridos. ¡Explora nuestra <a href="/cursos">galería de cursos</a>!</p>';
                return;
            }
    
            const misCursos = [];
            for (const cursoId of cursosAdquiridosIds) {
                const cursoResponse = await fetch(`/api/cursos/${cursoId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${firebaseIdToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (cursoResponse.ok) {
                    const cursoData = await cursoResponse.json();
                    misCursos.push({ id: cursoId, ...cursoData });
                } else {
                    console.warn(`No se pudo obtener el curso ${cursoId}`);
                }
            }
    
            const row = document.createElement('div');
            row.classList.add('row', 'row-cols-1', 'row-cols-md-2', 'row-cols-lg-3', 'g-3');
            
            misCursos.forEach(curso => {
                const colDiv = document.createElement('div');
                colDiv.classList.add('col');
                
                const cardDiv = document.createElement('div');
                cardDiv.classList.add('card', 'h-100', 'border-0', 'shadow-sm');
                
                const imgElement = document.createElement('img');
                imgElement.classList.add('card-img-top');
                imgElement.src = curso.imagen || '/static/images/placeholder.jpg';
                imgElement.alt = `Imagen de ${curso.nombre}`;
                
                const cardBodyDiv = document.createElement('div');
                cardBodyDiv.classList.add('card-body', 'd-flex', 'flex-column');
                
                const cardTitle = document.createElement('h5');
                cardTitle.classList.add('card-title');
                cardTitle.textContent = curso.nombre;
                
                const cardText = document.createElement('p');
                cardText.classList.add('card-text');
                cardText.textContent = curso.descripcion;
                
                const cardFooter = document.createElement('div');
                cardFooter.classList.add('card-footer', 'bg-white', 'border-0', 'text-center');
                
                const linkVerCurso = document.createElement('a');
                linkVerCurso.classList.add('btn', 'btn-primary', 'w-100');
                linkVerCurso.href = `/cursos_detalle/${curso.id}`;
                linkVerCurso.textContent = 'Ver Curso';
                
                cardBodyDiv.appendChild(cardTitle);
                cardBodyDiv.appendChild(cardText);
                cardDiv.appendChild(imgElement);
                cardDiv.appendChild(cardBodyDiv);
                cardFooter.appendChild(linkVerCurso);
                cardDiv.appendChild(cardFooter);
                colDiv.appendChild(cardDiv);
                row.appendChild(colDiv);
            });
            misCursosList.appendChild(row);
        } catch (error) {
            console.error("Error al cargar mis cursos:", error);
            misCursosList.innerHTML = '<p class="text-center text-danger">Error al cargar tus cursos. Por favor, inténtalo de nuevo más tarde.</p>';
        }
    }

    // Lógica para cargar Mi Perfil (para USUARIO COMÚN)
    async function cargarMiPerfil() {
        if (userRole !== 'user') return; // Asegurarse de que solo usuarios comunes carguen esto
        ocultarTodosLosContenedores();
        miPerfilContainer.style.display = 'block';
        // La información básica ya está en la plantilla HTML (email, rol).
        // Si necesitas más datos del perfil desde la DB (ej. nombre completo, dirección),
        // tendrías que hacer una llamada a la API aquí.
        // Ejemplo:
        // const firebaseIdToken = await getCurrentFirebaseIdToken();
        // const response = await fetch(`/api/users/${firebase.auth().currentUser.uid}`, {
        //     headers: { 'Authorization': `Bearer ${firebaseIdToken}` }
        // });
        // const userData = await response.json();
        // miPerfilData.innerHTML = `
        //     <p><strong>Nombre:</strong> ${userData.nombre || 'N/A'}</p>
        //     <p><strong>Email:</strong> ${userData.email || 'N/A'}</p>
        //     <p><strong>Rol:</strong> ${userData.rol || 'N/A'}</p>
        // `;
    }

    // Asignar Event Listeners basados en el rol
    if (userRole === 'admin') {
        if (btnGestionarCursos) {
            btnGestionarCursos.addEventListener('click', (e) => {
                e.preventDefault();
                cargarCursosParaAdministracion();
            });
        }
        if (btnGestionarUsuarios) {
            btnGestionarUsuarios.addEventListener('click', (e) => {
                e.preventDefault();
                cargarUsuariosParaAdministracion();
            });
        }
    } else if (userRole === 'user') {
        if (btnMisCursos) {
            btnMisCursos.addEventListener('click', (e) => {
                e.preventDefault();
                cargarMisCursos();
            });
        }
        if (btnMiPerfil) {
            btnMiPerfil.addEventListener('click', (e) => {
                e.preventDefault();
                cargarMiPerfil();
            });
        }
    }
});
