// CODIGO DE EL HEADER

const logo = document.getElementById("logo");  //  Selecciona el elemento con el ID "logo"

const barraLateral = document.querySelector(".barra-lateral"); //  Selecciona el elemento con la clase "barra-lateral", que representa la barra lateral en el diseño.

const spans = document.querySelectorAll("span"); //  Selecciona todos los elementos <span> dentro del documento uqe se utilizan para mostrar o ocultar texto en la barra lateral.

const menu = document.querySelector(".menu") //  Selecciona el elemento con la clase "menu" que es el botón flotante en la esquina superior derecha.

const main = document.querySelector("main"); //  Selecciona el elemento <main>, que contiene el contenido principal de la página.

menu.addEventListener("click", ()=> {
    barraLateral.classList.toggle("max-barra-lateral");
//  Esto es para que si la pantalla tiene un tamaño de 320 aparezca siempre en mini menu

    if(window.innerWidth<=320){
        barraLateral.classList.add("mini-barra-lateral");
        main.classList.add("min-main");
     // es decir si se abre el menu solo se veria los iconos

        spans.forEach((span)=>{
            span.classList.add("oculto");
            //  lo que hace que el texto se muestre u oculte según el estado de la barra lateral.
        })
    }
})


// Para minimizar la barra lateral al darle click
logo.addEventListener('click', () => {
    barraLateral.classList.toggle("mini-barra-lateral");
    main.classList.toggle("min-main");
    // para cuando la barra este minimizada el texto se acomode esto permite que la barra lateral se minimice y ajuste el contenido principal.

    spans.forEach((span) => {
        span.classList.toggle("oculto");
        //  lo que hace que el texto se muestre u oculte según el estado de la barra lateral.
    })

});





// Crear funcion para cuando de click en el boton lo lleve a la pagina correspondiente 
function agendarCita () {
    window.location.href = "/agendarcitas/usuario/";
}

function  volverCita () {
    window.location.href = "/guarderia/usuario/";
}


function verCita() {
    window.location.href = '/citas/agendadas/usuario/';
}

function guarderiaAgen() {
    window.location.href = '/guarderia/cita/usuario/';
}
 
// Función para abrir el modal
function abrirModal() {
    var modal = document.getElementById('modal');
    modal.style.display = 'block'; // Mostrar el modal
    document.body.style.overflow = 'hidden'; // Evitar scroll en el body detrás del modal
}


// Función para cerrar el modal
function cerrarModal() {
    var modal = document.getElementById('modal');
    modal.style.display = 'none'; // Ocultar el modal
    document.body.style.overflow = ''; // Restaurar scroll en el body
}


