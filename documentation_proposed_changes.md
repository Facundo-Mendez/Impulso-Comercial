# Documentación de Cambios Propuestos

Este documento describe las mejoras sugeridas para los archivos **HTML**, **CSS** y **JS** del proyecto, con el objetivo de optimizar la **usabilidad**, **accesibilidad**, **rendimiento** y **consistencia visual**.

---

## 1. Unificación de scripts JS
- **Problema:** Múltiples `DOMContentLoaded` separados, provocando código repetido y posible conflicto.
- **Solución propuesta:** 
  - Consolidar toda la inicialización en un único `DOMContentLoaded` en `main.js`.
  - Agrupar funcionalidades: menú móvil, acordeón, validaciones y scroll.

---

## 2. Mejora de la accesibilidad
- **Problemas detectados:**
  - Falta de etiquetas `<label>` en formularios.
  - Acordeón sin soporte de teclado ni atributos ARIA.
  - Ausencia de “skip link” para navegación por teclado.
- **Soluciones propuestas:**
  - Añadir `<label>` y atributos `aria-*` a todos los elementos interactivos.
  - Implementar acordeón accesible con control de foco y navegación por teclado.
  - Agregar enlace “Saltar al contenido” al inicio del `body`.

---

## 3. Optimización de formularios
- **Problema:** Validación de usuario/contraseña realizada en el cliente.
- **Solución propuesta:**
  - Mover validación al backend (Flask).
  - Implementar `aria-live` para mostrar errores de forma accesible.
  - Usar atributos HTML5 (`type="email"`, `required`, `autocomplete`) para validaciones nativas.

---

## 4. Consistencia visual
- **Problema:** Estilos dispersos entre múltiples archivos CSS sin un sistema de diseño unificado.
- **Solución propuesta:**
  - Crear un set de variables CSS (`--color-primary`, `--space-1`, `--radius`, etc.).
  - Aplicar estas variables a todos los estilos para mantener consistencia.
  - Unificar tipografías, espaciados y sombras.

---

## 5. Rendimiento y Core Web Vitals
- **Problemas detectados:**
  - Imágenes sin dimensiones (`width`/`height`), provocando “layout shift”.
  - Carga innecesaria de imágenes fuera de pantalla.
  - Scripts sin `defer`.
- **Soluciones propuestas:**
  - Agregar `width`, `height` y `loading="lazy"` a imágenes no críticas.
  - Usar `defer` en scripts JS.
  - Preload de imágenes críticas (ej. imagen hero).

---

## 6. Mejoras opcionales
- **Modo oscuro:** Implementar soporte con `prefers-color-scheme` o toggle manual.
- **Animaciones accesibles:** Usar `prefers-reduced-motion` para respetar preferencias de usuarios.

---

## Checklist de implementación
- [ ] Corregir rutas y nombres de archivo.
- [ ] Eliminar duplicados de plantillas HTML.
- [ ] Consolidar `main.js` en un único bloque `DOMContentLoaded`.
- [ ] Añadir accesibilidad a formularios y acordeón.
- [ ] Crear y aplicar sistema de variables CSS.
- [ ] Optimizar imágenes y carga de scripts.
- [ ] Revisar validaciones y mover lógica sensible al backend.
- [ ] (Opcional) Implementar modo oscuro.

---

## Beneficios esperados
- **Usabilidad:** Navegación más clara, formularios comprensibles y mejor experiencia móvil.
- **Accesibilidad:** Cumplimiento con estándares WCAG, mejor soporte para teclado y lectores de pantalla.
- **Rendimiento:** Reducción de CLS, tiempos de carga más rápidos y menor consumo de recursos.
- **Mantenibilidad:** Código más limpio, centralizado y fácil de actualizar.
