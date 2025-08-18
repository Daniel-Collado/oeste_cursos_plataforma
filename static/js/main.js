// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    // Hemos añadido "Versión 1.2" para verificar que esta versión se carga.
    console.log('main.js cargado y listo el DOM. Versión 1.2'); 
    // Aquí puedes añadir lógica general que afecte a la mayoría de las páginas,
    // por ejemplo, inicialización de componentes de Bootstrap que no sean específicos.

    const btnVolverArriba = document.getElementById('btnVolverArriba');
    if (btnVolverArriba) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                btnVolverArriba.style.display = 'block';
            } else {
                btnVolverArriba.style.display = 'none';
            }
        });
        btnVolverArriba.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});
