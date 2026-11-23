#!/usr/bin/env python3
"""Parche de build para los juegos del usuario (aplicado al clon de nxnative antes de compilar):

1. Traduce al español los textos del lanzador DmIOS (pantalla de inicio y ajustes):
   - dm/games/settings.tsv  (etiquetas, notas y valores de los ajustes; la columna de
     sección NO se toca: settings.py la valida contra ('Game','Controls','Performance'))
   - dm/ios/Sources/Launcher.swift (textos fijos + los títulos de sección, que se
     traducen al mostrarlos) y dm/ios/Sources/front_ios.m (textos fijos)
2. Ajustes de GRÁFICOS AL MÁXIMO por defecto (petición del usuario, 2026-11-22:
   «dame los mejores gráficos... quiero todos los modos, para que yo elija»;
   siguen siendo cambiables por el usuario en el lanzador, nada queda fijo):
   - DM_OPMODE (modo de consola) -> 1 = Televisor (Docked, 1080p)
   - DM_PRESENT_UPSCALE (reescalado de presentación) -> metalfx
   - DM_UPSCALER (reescalado del juego) -> metalfx
   - DM_DYNAMIC_RESOLUTION ya viene desactivada (0) en upstream y
     DM_RENDER_SCALE al 100% (1.0): resolución completa siempre, sin bajarla.
     (No hay ajuste de calidad de texturas en el lanzador: modo Televisor +
     escala al 100% es el máximo gráfico posible.)
   - DM_PRESENT_SNAP (frame buffering) -> 1 = activado
   (Metal 4 pipelines y Encode thread ya vienen activados por defecto en iOS.)

Falla con error si alguna cadena esperada no aparece, para detectar cambios de upstream.
Uso: python3 traducir_y_ajustes.py <ruta-al-clon-de-nxnative>
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
missing = []


def patch(relpath, pairs):
    p = root / relpath
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            missing.append(f"{relpath}: no encontrado: {old!r}")
        else:
            text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")


def patch_default(relpath, var, old_default, new_default):
    """Cambia la columna 'default' de la fila que empieza por <var> en un TSV."""
    p = root / relpath
    lines = p.read_text(encoding="utf-8").split("\n")
    done = False
    for i, line in enumerate(lines):
        if line.startswith(var + "\t"):
            cols = line.split("\t")
            # columnas: variable, kind, values, default, ...
            for j, c in enumerate(cols):
                if c == old_default:
                    cols[j] = new_default
                    done = True
                    break
            lines[i] = "\t".join(cols)
    if not done:
        missing.append(f"{relpath}: default {old_default!r} no encontrado en la fila {var}")
    p.write_text("\n".join(lines), encoding="utf-8")


TSV = "dm/games/settings.tsv"

patch(TSV, [
    # Valores de las opciones
    ("1=Docked,0=Handheld", "1=Televisor,0=Portátil"),
    ("0=Window,1=Fullscreen", "0=Ventana,1=Pantalla completa"),
    ("fit=Fit,fill=Fill", "fit=Ajustar,fill=Rellenar"),
    ("off=Standard,metalfx=MetalFX", "off=Estándar,metalfx=MetalFX"),
    ("game=Game's own,metalfx=MetalFX", "game=El del juego,metalfx=MetalFX"),
    ("auto=Match screen", "auto=Según la pantalla"),
    ("iPhone Duo screen (1.43:1)", "pantalla iPhone Duo (1,43:1)"),
    # Etiquetas
    ("Frame rate", "Velocidad de fotogramas"),
    ("Dynamic resolution", "Resolución dinámica"),
    ("Render scale", "Escala de render"),
    ("Console mode", "Modo de consola"),
    ("Upscaling", "Reescalado"),
    ("Game's upscaler", "Reescalado del juego"),
    ("Game language", "Idioma del juego"),
    ("Display mode", "Modo de pantalla"),
    ("Picture shape", "Forma de la imagen"),
    ("\tPicture\t", "\tImagen\t"),
    ("Frame-rate counter", "Contador de FPS"),
    ("Touch feedback", "Vibración táctil"),
    ("Game rumble", "Vibración del juego"),
    ("Rumble strength", "Intensidad de la vibración"),
    ("Rumble cutoff", "Corte de vibración"),
    ("Press a button to join", "Pulsa un botón para unirte"),
    ("Switch 2 controllers", "Mandos de Switch 2"),
    ("Frame buffering", "Buffer de fotogramas"),
    ("Metal 4 pipelines", "Pipelines Metal 4"),
    ("Pipeline prebuild", "Precompilación de pipelines"),
    ("Encode thread", "Hilo de codificación"),
    ("Hold frames when late", "Retener fotogramas si hay retraso"),
    ("Performance HUD", "HUD de rendimiento"),
    # Notas
    ("Lets the game lower its resolution under load. Turn off to keep full resolution for the selected console mode.",
     "Permite que el juego baje su resolución cuando va cargado. Desactívalo para mantener la resolución completa del modo de consola elegido."),
    ("Uses more GPU time and can increase heat.",
     "Usa más tiempo de GPU y puede aumentar el calor."),
    ("Fill crops the game's 16:9 picture to cover the screen. Health bars, subtitles or maps near the edges can be cut off. A full-screen picture without cropping needs a patch for each game.",
     "Rellenar recorta la imagen 16:9 del juego para cubrir la pantalla. Las barras de vida, los subtítulos o los mapas cerca de los bordes pueden cortarse. Una imagen a pantalla completa sin recorte necesita un parche para cada juego."),
    ("Plays Joy-Con 2 and Pro Controller 2 over Bluetooth: hold Sync on one during the game to pair it. macOS asks once for Bluetooth access.",
     "Juega con Joy-Con 2 y Pro Controller 2 por Bluetooth: mantén Sync en uno durante el juego para enlazarlo. macOS pide el acceso Bluetooth una vez."),
    ("Taller shapes render more pixels and can increase GPU time and heat.",
     "Las formas más altas renderizan más píxeles y pueden aumentar el tiempo de GPU y el calor."),
    ("Up to one frame more display latency.",
     "Hasta un fotograma más de latencia de pantalla."),
    ("Keeps a pipeline archive; uses more memory.",
     "Mantiene un archivo de pipelines; usa más memoria."),
    ("The first start waits a few minutes for it, once.",
     "El primer inicio espera unos minutos por ello, una sola vez."),
])

patch_default(TSV, "DM_OPMODE", "DM_GAME_OPMODE", "1")
patch_default(TSV, "DM_PRESENT_UPSCALE", "off", "metalfx")
patch_default(TSV, "DM_UPSCALER", "game", "metalfx")
patch_default(TSV, "DM_PRESENT_SNAP", "DM_GAME_PRESENT_SNAP", "1")

patch("dm/ios/Sources/Launcher.swift", [
    # Los títulos de sección se traducen al mostrarlos (en el TSV son claves fijas)
    ("Section(section) {",
     'Section(["Game": "Juego", "Controls": "Controles", "Performance": "Rendimiento"][section] ?? section) {'),
    ('"Play"', '"Jugar"'),
    ("Reset to tested defaults", "Restablecer los valores probados"),
    ("Brings back all settings this game was tested with.",
     "Recupera todos los ajustes con los que se probó este juego."),
    ("Memory available", "Memoria disponible"),
    ("Cloud saves", "Guardados en la nube"),
    ("Checking the cloud save", "Comprobando el guardado en la nube"),
    ("Choose a different folder", "Elige otra carpeta"),
    ("Choose a folder in iCloud Drive", "Elige una carpeta en iCloud Drive"),
    ("Saved. The game uses this folder when you press Play.",
     "Guardado. El juego usa esta carpeta cuando pulsas Jugar."),
    ("That folder could not be remembered", "No se pudo recordar esa carpeta"),
    ("try a different one.", "prueba con otra."),
    ("Turn off cloud saves", "Desactivar los guardados en la nube"),
    ("Play This iPhone's Save", "Jugar con la partida de este iPhone"),
    ("Play Without It", "Jugar sin ella"),
    ("Try Again", "Intentar de nuevo"),
    ('"Cancel"', '"Cancelar"'),
    ('"Version \\(', '"Versión \\('),
])

patch("dm/ios/Sources/front_ios.m", [
    ("Game files unusable.", "Los archivos del juego no se pueden usar."),
    ('"Game files"', '"Archivos del juego"'),
    ("Tap to start", "Toca para empezar"),
    ("Open the app again to start", "Abre la app otra vez para empezar"),
    ("The game restarts.", "El juego se reinicia."),
    ("Open the app again to continue.", "Abre la app otra vez para continuar."),
    ("Starting %@", "Iniciando %@"),
    ("This device is not supported.", "Este dispositivo no es compatible."),
    ('"Save failed"', '"Error al guardar"'),
    ("Saving failed (errno %d); progress was not saved.",
     "Error al guardar (errno %d); el progreso no se guardó."),
    ('"Cancel"', '"Cancelar"'),
])

if missing:
    print("FALTAN PATRONES (¿cambió upstream?):")
    for m in missing:
        print(" -", m)
    sys.exit(1)

# Autocomprobación estructural: la columna de sección del TSV debe seguir usando
# solo las claves que settings.py acepta (fue el fallo de la build nº 1, que no
# se descubrió hasta el paso [6/7], una hora dentro de la build).
SECCIONES_OK = {"Game", "Controls", "Performance"}
for n, line in enumerate((root / TSV).read_text(encoding="utf-8").split("\n"), 1):
    if not line or line.startswith("#"):
        continue
    cols = line.split("\t")
    if len(cols) >= 6 and cols[5] not in SECCIONES_OK:
        print(f"ERROR ESTRUCTURAL: {TSV}:{n}: sección no válida: {cols[5]!r}")
        sys.exit(1)
print("Parche aplicado: lanzador en español + defaults de gráficos al máximo.")
