# PDF Page Images

[English](README.md) · [Guías en español](https://pdf.findfindata.com/es/) · [English guides](https://pdf.findfindata.com/)

Herramienta de línea de comandos para Python 3.11+ que convierte páginas de un PDF local en imágenes PNG o JPEG. Permite elegir páginas, intervalos o el documento completo. El script procesa los archivos en tu equipo, sin servidor, cuenta, clave API, subida de documentos ni backend.

## Instalación

```sh
git clone https://github.com/faigvain-ang/pdf-page-images.git
cd pdf-page-images
python -m venv .venv
```

Activa el entorno en PowerShell para Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

O en una terminal de macOS/Linux:

```sh
source .venv/bin/activate
```

Instala las dependencias con versiones fijadas:

```sh
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, utiliza `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos de instalación y ejecución. No es necesario instalar el script como paquete. Las dependencias son `pypdfium2==4.30.0` y `Pillow==11.1.0`; las pruebas incluidas se ejecutaron con Python 3.13.11 en Windows. La instalación descarga paquetes de terceros; la conversión no realiza solicitudes de red. Tu plataforma necesita una rueda binaria de PDFium compatible.

## Exportar páginas concretas

El repositorio incluye `examples/statement.pdf`, un PDF sintético de tres páginas sin información personal ni financiera real.

```sh
python pdf_page_images.py examples/statement.pdf --pages 1,3 --dpi 144 --format png --output-dir out
```

Resultado:

```text
out/statement-page-001.png
out/statement-page-003.png
```

La numeración empieza en **1** y corresponde a la página del PDF original, no a la posición del archivo exportado. Las tres páginas del ejemplo tienen un MediaBox de 612 × 792 puntos. A 144 DPI, las páginas 1 y 2 producen imágenes de 1224 × 1584 píxeles. La página 3 incorpora una rotación de 90° en sentido horario y produce 1584 × 1224 píxeles; la herramienta respeta esa rotación.

### Intervalos y JPEG

```sh
python pdf_page_images.py examples/statement.pdf --pages 1-2 --dpi 144 --format jpeg --output-dir jpg-out
```

Genera `statement-page-001.jpg` y `statement-page-002.jpg`. Se aceptan los nombres de formato `jpeg` y `jpg`. JPEG usa calidad 95 y compresión con pérdida; PNG no tiene pérdida. Ambos formatos usan color RGB y fondo blanco opaco.

### Todas las páginas

```sh
python pdf_page_images.py examples/statement.pdf --all --output-dir all-out
python pdf_page_images.py examples/statement.pdf --output-dir another-out
```

Si omites tanto `--pages` como `--all`, también se exportan todas las páginas. Valores predeterminados: 144 DPI, PNG y directorio `out/`. No se pueden combinar `--all` y `--pages`. La selección `3,1-2,2` exporta las páginas 3, 1 y 2 una sola vez cada una y en ese orden. Los nombres usan al menos tres dígitos; las páginas superiores a 999 conservan su número completo.

## Errores y límites

- Rechaza la página 0, páginas fuera del documento, intervalos descendentes, selecciones incorrectas, PDF inválidos y archivos inexistentes. Los errores devuelven código 2; una conversión correcta devuelve 0 e imprime las rutas generadas.
- Rechaza documentos cifrados o protegidos con contraseña, incluso si se abren con una contraseña vacía. Esta versión no permite introducir contraseñas.
- No sobrescribe imágenes existentes. Elige otro directorio o elimina por tu cuenta los archivos que ya no necesites. Se comprueban la selección y los nombres antes de renderizar; un fallo posterior de escritura o renderizado puede dejar imágenes anteriores en el directorio.
- Los DPI deben ser un número positivo y finito. Una resolución mayor consume más memoria. Se procesa una página a la vez, sin límite de memoria ni aislamiento del motor PDF. Procesa únicamente documentos de confianza.
- Renderiza la página visible; no extrae las imágenes originales incrustadas. Las fuentes y las características del documento pueden afectar al resultado. No conserva funciones interactivas.
- **Sin OCR y sin censura segura de datos.** Exportar una imagen no equivale a eliminar información confidencial de forma segura. Todo lo que siga visible en la página seguirá visible en la imagen.
- Las imágenes **no** conservan firmas digitales PDF, su validez, texto seleccionable, capas de texto buscable, enlaces ni campos de formulario editables. La apariencia de una firma renderizada son solo píxeles, no una firma digital válida.
- El PDF original se abre para lectura y nunca se reescribe. Eres responsable de gestionar los documentos sensibles y las imágenes exportadas en tu equipo.

## Reproducir el ejemplo y las pruebas

Solo hacen falta las dependencias de ejecución. El generador usa la biblioteca estándar de Python y crea un PDF válido con tabla xref. Su cifrado antiguo opcional sirve exclusivamente para generar casos de prueba de rechazo, no para proteger documentos.

```sh
python examples/make_sample.py
python tests/test_pdf_page_images.py
```

Los 11 métodos de prueba verifican lectura y renderizado reales, decodificación PNG/JPEG, correspondencia entre páginas y nombres, dimensiones a 144 DPI, rotación interna, fondo blanco, intervalos, exportación de todas las páginas por defecto, entradas incorrectas, rechazo de contraseñas, protección contra sobrescritura y conservación de los bytes originales. Los archivos temporales se crean dentro del directorio ignorado `tmp/` del repositorio y se eliminan al finalizar cada prueba.

## Más flujos de trabajo con PDF

Utilice [KomoPDF](https://komopdf.com/) para editar texto o añadir anotaciones antes de exportar una imagen. Este CLI realiza el renderizado local a PNG/JPEG con selección de páginas y PPP explícitos.

## Licencia

El código original, la documentación y los ejemplos sintéticos se distribuyen con la [licencia MIT](LICENSE). Las dependencias tienen sus propias licencias; consulta [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
