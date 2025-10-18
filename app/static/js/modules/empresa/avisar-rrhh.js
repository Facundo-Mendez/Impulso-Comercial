/**
 * Modulo para integracion Empresa -> RRHH
 *
 * Este archivo contiene las funciones necesarias para que las empresas
 * puedan avisar a RRHH sobre postulantes interesantes.
 *
 * INSTRUCCIONES DE USO:
 * 1. Importar este archivo en el dashboard de empresas
 * 2. Llamar a avisarRRHH() cuando el usuario haga clic en "Avisar a RRHH"
 * 3. Asegurarse de tener empresa_id y solicitud_id disponibles
 */

/**
 * Envía un aviso a RRHH sobre un postulante interesante
 *
 * @param {number} empresaId - ID de la empresa que envía el aviso
 * @param {number} solicitudId - ID de la solicitud de empleo relacionada
 * @param {number} postulanteId - ID del postulante
 * @param {string} observaciones - Observaciones opcionales sobre el postulante
 * @returns {Promise<Object>} Resultado del aviso
 */
async function avisarRRHH(empresaId, solicitudId, postulanteId, observaciones = '') {
    try {
        // Validar que tengamos los datos necesarios
        if (!empresaId || !solicitudId || !postulanteId) {
            throw new Error('Faltan datos requeridos para enviar el aviso');
        }

        // Mostrar indicador de carga
        const btnAvisar = event?.target;
        if (btnAvisar) {
            btnAvisar.disabled = true;
            btnAvisar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        }

        // Enviar aviso a RRHH
        const response = await fetch('/api/rrhh/avisar-postulante', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                empresa_id: empresaId,
                solicitud_id: solicitudId,
                postulante_id: postulanteId,
                observaciones: observaciones
            })
        });

        const data = await response.json();

        if (data.ok) {
            // Mostrar mensaje de exito
            mostrarNotificacionExito(data.mensaje, data.actualizado);

            // Actualizar UI
            if (btnAvisar) {
                btnAvisar.innerHTML = '<i class="fas fa-check"></i> RRHH Notificado';
                btnAvisar.classList.add('btn-success');
                btnAvisar.classList.remove('btn-primary');
            }

            return data;
        } else {
            throw new Error(data.error || 'Error enviando aviso');
        }
    } catch (error) {
        console.error('Error avisando a RRHH:', error);

        // Restaurar boton
        if (btnAvisar) {
            btnAvisar.disabled = false;
            btnAvisar.innerHTML = '<i class="fas fa-bell"></i> Avisar a RRHH';
        }

        mostrarNotificacionError('Error enviando aviso a RRHH: ' + error.message);
        return null;
    }
}

/**
 * Funcion para avisar a RRHH con prompt para observaciones
 *
 * @param {number} postulanteId - ID del postulante
 */
async function avisarRRHHConObservaciones(postulanteId) {
    // Obtener IDs del contexto actual
    const empresaId = window.empresaActual?.id || getCurrentEmpresaId();
    const solicitudId = window.solicitudActual?.id || getCurrentSolicitudId();

    if (!empresaId || !solicitudId) {
        alert('Error: No se pudo obtener la informacion de la empresa o solicitud');
        return;
    }

    // Pedir observaciones al usuario
    const observaciones = prompt(
        'Que te interesa de este candidato?\n\n(Opcional - puedes dejar en blanco)',
        ''
    );

    // Si el usuario cancela, no enviar
    if (observaciones === null) return;

    // Enviar aviso
    await avisarRRHH(empresaId, solicitudId, postulanteId, observaciones);
}

/**
 * Verifica si ya se envio un aviso para este postulante
 *
 * @param {number} postulanteId - ID del postulante
 * @returns {Promise<boolean>} true si ya existe un aviso
 */
async function verificarAvisoExistente(postulanteId) {
    try {
        const empresaId = window.empresaActual?.id || getCurrentEmpresaId();
        const solicitudId = window.solicitudActual?.id || getCurrentSolicitudId();

        const response = await fetch(
            `/api/rrhh/avisos-postulantes?empresa_id=${empresaId}&postulante_id=${postulanteId}`,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const data = await response.json();

        return data.ok && data.avisos && data.avisos.length > 0;
    } catch (error) {
        console.error('Error verificando aviso:', error);
        return false;
    }
}

/**
 * Actualiza el boton de avisar segun si ya existe un aviso
 *
 * @param {HTMLElement} boton - Elemento del boton
 * @param {number} postulanteId - ID del postulante
 */
async function actualizarBotonAvisar(boton, postulanteId) {
    const existe = await verificarAvisoExistente(postulanteId);

    if (existe) {
        boton.innerHTML = '<i class="fas fa-check"></i> RRHH Notificado';
        boton.classList.add('btn-success');
        boton.classList.remove('btn-primary');
        boton.title = 'Ya has enviado un aviso a RRHH sobre este postulante';
    } else {
        boton.innerHTML = '<i class="fas fa-bell"></i> Avisar a RRHH';
        boton.classList.add('btn-primary');
        boton.classList.remove('btn-success');
        boton.title = 'Enviar aviso a RRHH para revisar este candidato';
    }
}

/**
 * Muestra una notificacion de exito
 */
function mostrarNotificacionExito(mensaje, actualizado = false) {
    const icono = actualizado ? 'Actualizado:' : 'Exito:';

    // Usar sistema de notificaciones si existe
    if (window.showNotification) {
        window.showNotification(icono + ' ' + mensaje, 'success');
    } else {
        alert(icono + ' ' + mensaje);
    }
}

/**
 * Muestra una notificacion de error
 */
function mostrarNotificacionError(mensaje) {
    // Usar sistema de notificaciones si existe
    if (window.showNotification) {
        window.showNotification('Error: ' + mensaje, 'error');
    } else {
        alert('Error: ' + mensaje);
    }
}

/**
 * Obtiene el ID de la empresa actual
 * NOTA: Esta funcion debe ser implementada segun la estructura del modulo empresas
 */
function getCurrentEmpresaId() {
    // Implementar segun la estructura del modulo empresas
    // Opciones:
    // 1. Desde variable global: return window.empresaActual?.id;
    // 2. Desde localStorage: return localStorage.getItem('empresa_id');
    // 3. Desde atributo data: return document.body.dataset.empresaId;

    console.warn('getCurrentEmpresaId() debe ser implementada');
    return null;
}

/**
 * Obtiene el ID de la solicitud actual
 * NOTA: Esta funcion debe ser implementada segun la estructura del modulo empresas
 */
function getCurrentSolicitudId() {
    // Implementar segun la estructura del modulo empresas
    // Opciones:
    // 1. Desde variable global: return window.solicitudActual?.id;
    // 2. Desde URL: return new URLSearchParams(window.location.search).get('solicitud_id');
    // 3. Desde atributo data: return document.body.dataset.solicitudId;

    console.warn('getCurrentSolicitudId() debe ser implementada');
    return null;
}

// Exportar funciones para uso global
window.avisarRRHH = avisarRRHH;
window.avisarRRHHConObservaciones = avisarRRHHConObservaciones;
window.verificarAvisoExistente = verificarAvisoExistente;
window.actualizarBotonAvisar = actualizarBotonAvisar;

console.log('Modulo de integracion Empresa -> RRHH cargado correctamente');