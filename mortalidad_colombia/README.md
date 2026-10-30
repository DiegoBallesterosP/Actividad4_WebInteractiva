# Mortalidad en Colombia 2019

Tablero web interactivo, hecho con **Dash** y **Plotly**, sobre las defunciones no fetales registradas por el DANE en 2019.

- **Autor:** Diego Fernando Pulido Ballesteros
- **Asignatura:** Aplicaciones 1 · Maestría en Inteligencia Artificial · Universidad de La Salle
- **Aplicación en línea:** `<URL de Render>`
- **Repositorio:** `<URL de GitHub>`

![Vista general](docs/screenshots/01_vista_general.png)

## Introducción

En 2019 se registraron 244.355 defunciones no fetales en Colombia. Este tablero las resume en un mapa, gráficos y una tabla, y todo se actualiza con filtros por departamento, sexo y meses.

## Objetivo

Identificar patrones demográficos, regionales y temporales de la mortalidad en Colombia durante 2019.

## Estructura del proyecto

```
mortalidad_colombia/
├── app.py               Punto de entrada
├── requirements.txt     Dependencias
├── render.yaml          Configuración de Render
├── assets/              Estilos
├── data/                Datos originales (raw) y procesados (processed)
├── mortality/
│   ├── data/            Limpieza y carga de datos
│   ├── analytics.py     Cálculos de cada visualización
│   └── ui/              Gráficos, diseño de la página e interactividad
└── tests/               Pruebas
```

## Requisitos

- Python 3.12 o superior
- dash 4.4.1, plotly 7.1.0, pandas 3.1.0, gunicorn 26.2.0, openpyxl 3.1.5 (en `requirements.txt`)

## Instalación

```bash
git clone <URL de GitHub>
cd mortalidad_colombia
python -m venv .venv
.venv\Scripts\activate          # en macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

La app queda en <http://127.0.0.1:8050>.

## Despliegue

La app está publicada en **Render**:

1. Subir el proyecto a un repositorio público de GitHub.
2. En [render.com](https://render.com), crear un **Web Service** conectado al repositorio.
3. Render lee `render.yaml`, que define:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:server --workers 2 --timeout 120`
   - **Variable:** `PYTHON_VERSION = 3.12.8`

## Software

Python, Dash, Plotly, pandas, Gunicorn, Render, Git/GitHub y Visual Studio Code.

## Visualizaciones y resultados

El tablero tiene tres filtros que se quedan fijos arriba: departamento, sexo y rango de meses. Todos los gráficos, la tabla y los cuatro indicadores responden a ellos. Además, al hacer clic en un departamento del mapa el tablero se filtra por él, y **Restablecer filtros** vuelve a la vista nacional.

Las cifras de esta sección corresponden a la vista nacional, sin filtros.

### 1. Mapa: defunciones por departamento

![Mapa](docs/screenshots/02_mapa_departamentos.png)

Un azul más oscuro indica más defunciones. Al pasar el mouse se ve el nombre del departamento y su total.

**Hallazgos:** Bogotá (38.760), Antioquia (34.473) y Valle del Cauca (28.443) suman el **41.6%** de las muertes del país. En el otro extremo están Vaupés (87), Guainía (115) y Vichada (188). El patrón sigue la distribución de la población, porque son totales y no tasas.

### 2. Gráfico de líneas: defunciones por mes

![Línea por mes](docs/screenshots/03_linea_meses.png)

**Hallazgos:** la mortalidad es estable durante el año, entre 18.000 y 21.700 muertes al mes. **Diciembre** es el mes más alto (21.678) y **febrero** el más bajo (17.974). Febrero baja sobre todo porque tiene menos días: por día fueron 642 muertes, frente a 699 en diciembre. Enero, julio y diciembre forman pequeños picos que coinciden con las temporadas de vacaciones.

### 3. Gráfico de barras: las 5 ciudades más violentas

![Ciudades más violentas](docs/screenshots/04_barras_ciudades_violentas.png)

Se cuentan los homicidios con código CIE-10 **X95** (agresión con disparo de armas de fuego y casos no especificados). En todo el país hubo 9.273.

**Hallazgos:** **Santiago de Cali** encabeza con **971** homicidios, muy por encima de Bogotá (601), aunque Bogotá tiene más del triple de población. Siguen Medellín (428), Barranquilla (260) y Cúcuta (206). Entre las cinco reúnen el **26.6%** de los homicidios por arma de fuego del país, y el **93.5%** de las víctimas son hombres, la mayoría entre 20 y 44 años.

### 4. Gráfico circular: las 10 ciudades con menor mortalidad

![Ciudades con menor mortalidad](docs/screenshots/05_circular_menor_mortalidad.png)

Los datos del DANE no incluyen población, así que no se puede calcular una tasa. Por eso el índice se toma como el **total de defunciones** de los municipios con al menos una muerte registrada. Hay 13 municipios empatados con una sola defunción, y los empates se resuelven por orden alfabético.

**Hallazgos:** son municipios muy pequeños o áreas no municipalizadas de la Amazonía y el Chocó, como Alto Baudó, El Encanto y Mapiripana. Una sola muerte puede reflejar poca población, pero también **subregistro** en zonas apartadas. El gráfico dice más al filtrar por departamento: en Valle del Cauca, por ejemplo, muestra municipios con entre 3 y 17 defunciones.

### 5. Tabla: las 10 principales causas de muerte

![Tabla de causas](docs/screenshots/06_tabla_causas.png)

**Hallazgos:** el **infarto agudo del miocardio** (35.088 casos) causa el **14.4%** de todas las muertes, casi cinco veces más que la segunda causa, la EPOC (7.210). Predominan las enfermedades crónicas: cardiovasculares, respiratorias y cáncer. Aun así, el **homicidio con arma de fuego en la vía pública (X954)** aparece en el puesto 7, por encima del cáncer de mama y de próstata.

### 6. Barras apiladas: defunciones por sexo y departamento

![Sexo por departamento](docs/screenshots/08_apiladas_sexo_departamento.png)

**Hallazgos:** el **55.1%** de las muertes corresponde a hombres. La diferencia es pequeña en Bogotá (1.07 hombres por cada mujer) y Atlántico (1.11), y mucho mayor en Guaviare (3.4), Guainía (2.1) y Amazonas (1.9), donde pesan más las muertes violentas y accidentales. Solo 93 casos tienen sexo indeterminado.

### 7. Histograma: defunciones por grupo de edad

![Histograma de edad](docs/screenshots/07_histograma_edad.png)

Los códigos `GRUPO_EDAD1` se agrupan en las 11 etapas de la tabla de referencia, desde la mortalidad neonatal (códigos 0 a 4) hasta la edad desconocida (29).

**Hallazgos:** el **70.2%** de las muertes ocurre desde los 60 años. La barra más alta es **Vejez, de 60 a 84 años** (115.453), seguida de 85 años o más (56.061). La mortalidad neonatal (4.520) supera a la de la primera infancia y la niñez juntas. Entre los 20 y los 44 años aparece un aumento ligado a las muertes violentas.

### Ejemplo de interacción

![Filtro Valle del Cauca mujeres](docs/screenshots/09_filtro_valle_mujeres.png)

Con el filtro **Valle del Cauca + Mujer** todo el tablero se recalcula: el total baja a **12.616** defunciones, los homicidios por arma de fuego pasan a 95, el cáncer de mama sube al **segundo lugar** entre las causas y el mapa resalta solo ese departamento.

## Conclusiones

- La mortalidad de 2019 estuvo dominada por **enfermedades crónicas en personas mayores**, con el infarto muy por delante del resto.
- La **violencia con armas de fuego** marca el perfil colombiano: está entre las 10 primeras causas, afecta sobre todo a hombres jóvenes y se concentra en ciudades como Cali.
- Las muertes se concentran en los departamentos más poblados. Para comparar regiones de forma justa habría que cruzar estos datos con las proyecciones de población del DANE y calcular tasas.

Fuente: [DANE, Estadísticas Vitales 2019](https://microdatos.dane.gov.co/index.php/catalog/696).
