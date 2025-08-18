// static/js/cursos_listado.js
// Variables globales
let allFetchedCursos = []; // Almacena todos los cursos obtenidos de la API
let uniqueTags = new Set(); // Almacena tags únicos para el filtro de categorías
let currentSelectedCategory = 'all'; // Rastrea la categoría seleccionada actualmente, por defecto "Todas"

// Función para renderizar los cursos en el DOM
function displayCursos(cursosToDisplay) {
    const cursosContainer = document.getElementById('cursos-container');
    if (!cursosContainer) {
        console.warn('Contenedor de cursos no encontrado.');
        return;
    }
    cursosContainer.innerHTML = ''; // Limpia cualquier curso que estuviera visible

    if (cursosToDisplay.length > 0) {
        cursosToDisplay.forEach(curso => {
            const colDiv = document.createElement('div');
            colDiv.classList.add('col');

            const cardDiv = document.createElement('div');
            cardDiv.classList.add('card', 'h-100', 'border-0', 'shadow-sm');

            const imgElement = document.createElement('img');
            imgElement.classList.add('card-img-top');
            imgElement.style.height = '200px';
            imgElement.style.objectFit = 'cover';
            imgElement.alt = curso.nombre || 'Curso';
            imgElement.src = curso.imagen || '/static/images/placeholder.jpg';

            const cardBodyDiv = document.createElement('div');
            cardBodyDiv.classList.add('card-body', 'd-flex', 'flex-column');

            const cardTitle = document.createElement('h5');
            cardTitle.classList.add('card-title');
            cardTitle.textContent = curso.nombre || 'Nombre del Curso';

            const cardText = document.createElement('p');
            cardText.classList.add('card-text');
            cardText.textContent = curso.descripcion || 'Descripción no disponible.';

            const cardPrice = document.createElement('p');
            cardPrice.classList.add('card-text', 'fw-bold');
            cardPrice.textContent = `Precio: $${curso.precio || 'Consultar'}`;

            const acquireButton = document.createElement('a');
            acquireButton.href = `/cursos_detalle/${curso.id}`; // Ruta Flask
            acquireButton.classList.add('btn', 'btn-primary', 'mt-auto');
            acquireButton.textContent = 'Ver Detalles';

            cardBodyDiv.appendChild(cardTitle);
            cardBodyDiv.appendChild(cardText);
            cardBodyDiv.appendChild(cardPrice);
            cardBodyDiv.appendChild(acquireButton);

            cardDiv.appendChild(imgElement);
            cardDiv.appendChild(cardBodyDiv);
            colDiv.appendChild(cardDiv);
            cursosContainer.appendChild(colDiv);
        });
    } else {
        cursosContainer.innerHTML = '<div class="col-12"><p class="text-center text-muted">No hay cursos disponibles que coincidan con los filtros.</p></div>';
    }
}

// Función para filtrar los cursos basados en la búsqueda y la categoría seleccionada
function filterAndDisplayCursos() {
    const searchInput = document.getElementById('search-input');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';

    let filteredCursos = allFetchedCursos.filter(curso => {
        const categoryMatch = currentSelectedCategory === 'all' ||
                            (curso.tags && curso.tags.some(tag => tag.toLowerCase() === currentSelectedCategory.toLowerCase()));
        const matchesSearch =
            (curso.nombre && curso.nombre.toLowerCase().includes(searchQuery)) ||
            (curso.descripcion && curso.descripcion.toLowerCase().includes(searchQuery));
        return categoryMatch && matchesSearch;
    });

    displayCursos(filteredCursos);
}

// Función para rellenar el dropdown de categorías dinámicamente
function populateCategoryFilterDropdown() {
    const categoryDropdownMenu = document.getElementById('category-dropdown-menu');
    const categoryDropdownButton = document.getElementById('categoryDropdown');
    if (!categoryDropdownMenu || !categoryDropdownButton) {
        console.warn('Elementos de dropdown de categorías no encontrados.');
        return;
    }

    categoryDropdownMenu.innerHTML = '';

    const allOptionLi = document.createElement('li');
    const allOptionLink = document.createElement('a');
    allOptionLink.classList.add('dropdown-item', 'category-item');
    allOptionLink.href = '#';
    allOptionLink.setAttribute('data-value', 'all');
    allOptionLink.textContent = 'Todas las Categorías';
    allOptionLi.appendChild(allOptionLink);
    categoryDropdownMenu.appendChild(allOptionLi);

    const sortedTags = Array.from(uniqueTags).sort();
    sortedTags.forEach(tag => {
        if (typeof tag === 'string' && tag.trim() !== '' && tag.toLowerCase() !== 'all') {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.classList.add('dropdown-item', 'category-item');
            link.href = '#';
            link.setAttribute('data-value', tag.toLowerCase());
            link.textContent = tag.charAt(0).toUpperCase() + tag.slice(1);
            li.appendChild(link);
            categoryDropdownMenu.appendChild(li);
        }
    });

    const categoryItems = categoryDropdownMenu.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            const selectedValue = this.getAttribute('data-value');
            const selectedText = this.textContent;

            currentSelectedCategory = selectedValue;
            categoryDropdownButton.textContent = selectedText;
            categoryItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            filterAndDisplayCursos();
        });
    });

    const initialActiveItem = categoryDropdownMenu.querySelector('.category-item[data-value="all"]');
    if (initialActiveItem) {
        initialActiveItem.classList.add('active');
        categoryDropdownButton.textContent = initialActiveItem.textContent;
    }
}

// Función auxiliar para procesar un objeto de curso individual
function processAndMapCourse(courseId, courseData) {
    const mappedCourse = {
        id: courseId,
        nombre: courseData.nombre || courseData.nombrecurso,
        descripcion: courseData.detalle || courseData.presentacion || courseData.objetivogeneral || courseData.descripcion,
        imagen: courseData.imagen,
        precio: courseData.precio || courseData.valor || 'Consultar',
        tags: Array.isArray(courseData.tags) ? courseData.tags.map(tag => String(tag).trim()) :
              (typeof courseData.tags === 'string' && courseData.tags.trim() !== '' ? courseData.tags.split(',').map(tag => tag.trim()) : [])
    };

    let missingFields = [];
    if (!mappedCourse.nombre) missingFields.push('nombre');
    if (!mappedCourse.descripcion) missingFields.push('descripcion');
    if (!mappedCourse.imagen) missingFields.push('imagen');

    if (missingFields.length === 0) {
        allFetchedCursos.push(mappedCourse);
        if (mappedCourse.tags && mappedCourse.tags.length > 0) {
            mappedCourse.tags.forEach(tag => {
                if (typeof tag === 'string' && tag.trim() !== '') {
                    uniqueTags.add(tag.toLowerCase());
                }
            });
        }
    } else {
        console.warn(`Curso omitido (ID: ${courseId}): faltan los campos necesarios: ${missingFields.join(', ')}. Objeto de curso:`, courseData);
    }
}

// Función principal para obtener todos los cursos de la API
async function fetchAllCursos() {
    const loadingMessage = document.getElementById('loading-message');
    const alertMessage = document.getElementById('alert-message'); // This variable is not used after declaration.
    if (loadingMessage) {
        loadingMessage.style.display = 'block';
    }

    try {
        const response = await fetch('/api/cursos', {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        allFetchedCursos = [];
        uniqueTags.clear();

        for (const courseId in data) {
            if (data.hasOwnProperty(courseId)) {
                const course = data[courseId];
                if (typeof course === 'object' && course !== null) {
                    processAndMapCourse(courseId, course);
                }
            }
        }

        populateCategoryFilterDropdown();
        filterAndDisplayCursos();

    } catch (error) {
        console.error('Error al obtener los cursos:', error);
        document.getElementById('cursos-container').innerHTML = '<div class="col-12"><p class="text-center text-danger">Error al cargar los cursos: ' + error.message + '</p></div>';
        mostrarAlerta(`Error al cargar los cursos: ${error.message}`, 'danger');
    } finally {
        if (loadingMessage) {
            loadingMessage.style.display = 'none';
        }
    }
}

// Función para mostrar alertas
function mostrarAlerta(message, type) {
    const alertMessage = document.getElementById('alert-message');
    if (alertMessage) {
        alertMessage.textContent = message;
        alertMessage.className = `alert mt-3 alert-${type}`;
        alertMessage.style.display = 'block';
        setTimeout(() => {
            alertMessage.style.display = 'none';
        }, 5000);
    } else {
        console.error('Elemento alert-message no encontrado. Mostrando alerta en consola:', message);
        alert(message); // Fallback para depuración
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchAllCursos();

    const searchInput = document.getElementById('search-input');
    const clearFiltersButton = document.querySelector('#clear-filters'); // Changed to #clear-filters based on previous HTML

    if (searchInput) {
        searchInput.addEventListener('input', filterAndDisplayCursos); // Corrected syntax
    } else {
        console.log("No se encontro el elemento de búsqueda");
    }

    if (clearFiltersButton) {
        clearFiltersButton.addEventListener('click', () => { // Corrected syntax
            if (searchInput) {
                searchInput.value = '';
            }
            currentSelectedCategory = 'all';
            const categoryDropdownButton = document.getElementById('categoryDropdown');
            if (categoryDropdownButton) {
                categoryDropdownButton.textContent = 'Todas las Categorías';
            }
            const categoryDropdownMenu = document.getElementById('category-dropdown-menu');
            if (categoryDropdownMenu) {
                categoryDropdownMenu.querySelectorAll('.category-item').forEach(item => item.classList.remove('active'));
                const allOption = categoryDropdownMenu.querySelector('.category-item[data-value="all"]');
                if (allOption) {
                    allOption.classList.add('active');
                }
            }
            filterAndDisplayCursos();
        });
    }
});