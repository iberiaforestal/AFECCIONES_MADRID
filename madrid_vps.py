import streamlit as st
import folium
from streamlit.components.v1 import html
from fpdf import FPDF
from pyproj import Transformer
import requests
import xml.etree.ElementTree as ET
import geopandas as gpd
import tempfile
import os
from shapely.geometry import Point
import uuid
from datetime import datetime
from docx import Document
from branca.element import Template, MacroElement
from io import BytesIO
from staticmap import StaticMap, CircleMarker
import textwrap
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import shutil
import zipfile
import io
from PIL import Image
def normalize_name(name):
    # Mantener espacios intactos
    name = name.upper()\
               .replace("Á", "A")\
               .replace("É", "E")\
               .replace("Í", "I")\
               .replace("Ó", "O")\
               .replace("Ú", "U")\
               .replace("Ü", "U")\
               .replace("º", "")\
               .replace("ª", "")

    return name.strip()

# Sesión segura con reintentos
session = requests.Session()
retry = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504, 429])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Diccionario con los nombres de municipios y sus nombres base de archivo
shp_urls = {
    "AJALVIR": "AJALVIR",
    "ALAMEDA DEL VALLE": "ALAMEDA DEL VALLE",
    "ALCALA DE HENARES": "ALCALA DE HENARES",
    "ALCOBENDAS": "ALCOBENDAS",
    "ALCORCON": "ALCORCON",
    "ALDEA DEL FRESNO": "ALDEA DEL FRESNO",
    "ALGETE": "ALGETE",
    "ALPEDRETE": "ALPEDRETE",
    "AMBITE": "AMBITE",
    "ANCHUELO": "ANCHUELO",
    "ARANJUEZ": "ARANJUEZ",
    "ARGANDA DEL REY": "ARGANDA DEL REY",
    "ARROYOMOLINOS": "ARROYOMOLINOS",
    "BATRES": "BATRES",
    "BECERRIL DE LA SIERRA": "BECERRIL DE LA SIERRA",
    "BELMONTE DE TAJO": "BELMONTE DE TAJO",
    "BERZOSA DEL LOZOYA": "BERZOSA DEL LOZOYA",
    "BOADILLA DEL MONTE": "BOADILLA DEL MONTE",
    "BRAOJOS": "BRAOJOS",
    "BREA DE TAJO": "BREA DE TAJO",
    "BRUNETE": "BRUNETE",
    "BUITRAGO DEL LOZOYA": "BUITRAGO DEL LOZOYA",
    "BUSTARVIEJO": "BUSTARVIEJO",
    "CABANILLAS DE LA SIERRA": "CABANILLAS DE LA SIERRA",
    "CADALSO DE LOS VIDRIOS": "CADALSO DE LOS VIDRIOS",
    "CAMARMA DE ESTERUELAS": "CAMARMA DE ESTERUELAS",
    "CAMPO REAL": "CAMPO REAL",
    "CANENCIA": "CANENCIA",
    "CARABAÑA": "CARABAÑA",
    "CASARRUBUELOS": "CASARRUBUELOS",
    "CENICIENTOS": "CENICIENTOS",
    "CERCEDILLA": "CERCEDILLA",
    "CERVERA DE BUITRAGO": "CERVERA DE BUITRAGO",
    "CHAPINERIA": "CHAPINERIA",
    "CHINCHON": "CHINCHON",
    "CIEMPOZUELOS": "CIEMPOZUELOS",
    "COBEÑA": "COBEÑA",
    "COLLADO MEDIANO": "COLLADO MEDIANO",
    "COLLADO VILLALBA": "COLLADO VILLALBA",
    "COLMENAR DE OREJA": "COLMENAR DE OREJA",
    "COLMENAR DEL ARROYO": "COLMENAR DEL ARROYO",
    "COLMENAR VIEJO": "COLMENAR VIEJO",
    "COLMENAREJO": "COLMENAREJO",
    "CORPA": "CORPA",
    "COSLADA": "COSLADA",
    "CUBAS DE LA SAGRA": "CUBAS DE LA SAGRA",
    "DAGANZO DE ARRIBA": "DAGANZO DE ARRIBA",
    "EL ALAMO": "EL ALAMO",
    "EL ATAZAR": "EL ATAZAR",
    "EL BERRUECO": "EL BERRUECO",
    "EL BOALO": "EL BOALO",
    "EL ESCORIAL": "EL ESCORIAL",
    "EL MOLAR": "EL MOLAR",
    "EL VELLON": "EL VELLON",
    "ESTREMERA": "ESTREMERA",
    "FRESNEDILLAS DE LA OLIVA": "FRESNEDILLAS DE LA OLIVA",
    "FRESNO DE TOROTE": "FRESNO DE TOROTE",
    "FUENLABRADA": "FUENLABRADA",
    "FUENTE EL SAZ DE JARAMA": "FUENTE EL SAZ DE JARAMA",
    "FUENTIDUEÑA DE TAJO": "FUENTIDUEÑA DE TAJO",
    "GALAPAGAR": "GALAPAGAR",
    "GARGANTA DE LOS MONTES": "GARGANTA DE LOS MONTES",
    "GARGANTILLA DEL LOZOYA Y PINIL": "GARGANTILLA DEL LOZOYA Y PINIL",
    "GASCONES": "GASCONES",
    "GETAFE": "GETAFE",
    "GRIÑON": "GRIÑON",
    "GUADALIX DE LA SIERRA": "GUADALIX DE LA SIERRA",
    "GUADARRAMA": "GUADARRAMA",
    "HORCAJO DE LA SIERRA AOSLOS": "HORCAJO DE LA SIERRA AOSLOS",
    "HORCAJUELO DE LA SIERRA": "HORCAJUELO DE LA SIERRA",
    "HOYO DE MANZANARES": "HOYO DE MANZANARES",
    "HUMANES DE MADRID": "HUMANES DE MADRID",
    "LA ACEBEDA": "LA ACEBEDA",
    "LA CABRERA": "LA CABRERA",
    "LA HIRUELA": "LA HIRUELA",
    "LA SERNA DEL MONTE": "LA SERNA DEL MONTE",
    "LAS ROZAS DE MADRID": "LAS ROZAS DE MADRID",
    "LEGANES": "LEGANES",
    "LOECHES": "LOECHES",
    "LOS MOLINOS": "LOS MOLINOS",
    "LOS SANTOS DE LA HUMOSA": "LOS SANTOS DE LA HUMOSA",
    "LOZOYA": "LOZOYA",
    "LOZOYUELA NAVAS SIETEIGLESIAS": "LOZOYUELA NAVAS SIETEIGLESIAS",
    "MADARCOS": "MADARCOS",
    "MADRID": "MADRID",
    "MAJADAHONDA": "MAJADAHONDA",
    "MANZANARES EL REAL": "MANZANARES EL REAL",
    "MECO": "MECO",
    "MEJORADA DEL CAMPO": "MEJORADA DEL CAMPO",
    "MIRAFLORES DE LA SIERRA": "MIRAFLORES DE LA SIERRA",
    "MONTEJO DE LA SIERRA": "MONTEJO DE LA SIERRA",
    "MORALEJA DE ENMEDIO": "MORALEJA DE ENMEDIO",
    "MORALZARZAL": "MORALZARZAL",
    "MORATA DE TAJUÑA": "MORATA DE TAJUÑA",
    "MOSTOLES": "MOSTOLES",
    "NAVACERRADA": "NAVACERRADA",
    "NAVALAFUENTE": "NAVALAFUENTE",
    "NAVALAGAMELLA": "NAVALAGAMELLA",
    "NAVALCARNERO": "NAVALCARNERO",
    "NAVARREDONDA Y SAN MAMES": "NAVARREDONDA Y SAN MAMES",
    "NAVAS DEL REY": "NAVAS DEL REY",
    "NUEVO BAZTAN": "NUEVO BAZTAN",
    "OLMEDA DE LAS FUENTES": "OLMEDA DE LAS FUENTES",
    "ORUSCO DE TAJUÑA": "ORUSCO DE TAJUÑA",
    "PARACUELLOS DE JARAMA": "PARACUELLOS DE JARAMA",
    "PARLA": "PARLA",
    "PATONES": "PATONES",
    "PEDREZUELA": "PEDREZUELA",
    "PELAYOS DE LA PRESA": "PELAYOS DE LA PRESA",
    "PERALES DE TAJUÑA": "PERALES DE TAJUÑA",
    "PEZUELA DE LAS TORRES": "PEZUELA DE LAS TORRES",
    "PIÑUECAR GANDULLAS": "PIÑUECAR GANDULLAS",
    "PINILLA DEL VALLE": "PINILLA DEL VALLE",
    "PINTO": "PINTO",
    "POZUELO DE ALARCON": "POZUELO DE ALARCON",
    "POZUELO DEL REY": "POZUELO DEL REY",
    "PRADENA DEL RINCON": "PRADENA DEL RINCON",
    "PUEBLA DE LA SIERRA": "PUEBLA DE LA SIERRA",
    "PUENTES VIEJAS": "PUENTES VIEJAS",
    "QUIJORNA": "QUIJORNA",
    "RASCAFRIA": "RASCAFRIA",
    "REDUEÑA": "REDUEÑA",
    "RIBATEJADA": "RIBATEJADA",
    "RIVAS VACIAMADRID": "RIVAS VACIAMADRID",
    "ROBLEDILLO DE LA JARA": "ROBLEDILLO DE LA JARA",
    "ROBLEDO DE CHAVELA": "ROBLEDO DE CHAVELA",
    "ROBREGORDO": "ROBREGORDO",
    "ROZAS DE PUERTO REAL": "ROZAS DE PUERTO REAL",
    "SAN AGUSTIN DEL GUADALIX": "SAN AGUSTIN DEL GUADALIX",
    "SAN FERNANDO DE HENARES": "SAN FERNANDO DE HENARES",
    "SAN LORENZO DE EL ESCORIAL": "SAN LORENZO DE EL ESCORIAL",
    "SAN MARTIN DE LA VEGA": "SAN MARTIN DE LA VEGA",
    "SAN MARTIN DE VALDEIGLESIAS": "SAN MARTIN DE VALDEIGLESIAS",
    "SAN SEBASTIAN DE LOS REYES": "SAN SEBASTIAN DE LOS REYES",
    "SANTA MARIA DE LA ALAMEDA": "SANTA MARIA DE LA ALAMEDA",
    "SANTORCAZ": "SANTORCAZ",
    "SERRANILLOS DEL VALLE": "SERRANILLOS DEL VALLE",
    "SEVILLA LA NUEVA": "SEVILLA LA NUEVA",
    "SOMOSIERRA": "SOMOSIERRA",
    "SOTO DEL REAL": "SOTO DEL REAL",
    "TALAMANCA DE JARAMA": "TALAMANCA DE JARAMA",
    "TIELMES": "TIELMES",
    "TITULCIA": "TITULCIA",
    "TORREJON DE ARDOZ": "TORREJON DE ARDOZ",
    "TORREJON DE LA CALZADA": "TORREJON DE LA CALZADA",
    "TORREJON DE VELASCO": "TORREJON DE VELASCO",
    "TORRELAGUNA": "TORRELAGUNA",
    "TORRELODONES": "TORRELODONES",
    "TORREMOCHA DE JARAMA": "TORREMOCHA DE JARAMA",
    "TORRES DE LA ALAMEDA": "TORRES DE LA ALAMEDA",
    "TRES CANTOS": "TRES CANTOS",
    "VALDARACETE": "VALDARACETE",
    "VALDEAVERO": "VALDEAVERO",
    "VALDELAGUNA": "VALDELAGUNA",
    "VALDEMANCO": "VALDEMANCO",
    "VALDEMAQUEDA": "VALDEMAQUEDA",
    "VALDEMORILLO": "VALDEMORILLO",
    "VALDEMORO": "VALDEMORO",
    "VALDEOLMOS ALALPARDO": "VALDEOLMOS ALALPARDO",
    "VALDEPIELAGOS": "VALDEPIELAGOS",
    "VALDETORRES DE JARAMA": "VALDETORRES DE JARAMA",
    "VALDILECHA": "VALDILECHA",
    "VALVERDE DE ALCALA": "VALVERDE DE ALCALA",
    "VELILLA DE SAN ANTONIO": "VELILLA DE SAN ANTONIO",
    "VENTURADA": "VENTURADA",
    "VILLA DEL PRADO": "VILLA DEL PRADO",
    "VILLACONEJOS": "VILLACONEJOS",
    "VILLALBILLA": "VILLALBILLA",
    "VILLAMANRIQUE DE TAJO": "VILLAMANRIQUE DE TAJO",
    "VILLAMANTA": "VILLAMANTA",
    "VILLAMANTILLA": "VILLAMANTILLA",
    "VILLANUEVA DE LA CAÑADA": "VILLANUEVA DE LA CAÑADA",
    "VILLANUEVA DE PERALES": "VILLANUEVA DE PERALES",
    "VILLANUEVA DEL PARDILLO": "VILLANUEVA DEL PARDILLO",
    "VILLAR DEL OLMO": "VILLAR DEL OLMO",
    "VILLAREJO DE SALVANES": "VILLAREJO DE SALVANES",
    "VILLAVICIOSA DE ODON": "VILLAVICIOSA DE ODON",
    "VILLAVIEJA DEL LOZOYA": "VILLAVIEJA DEL LOZOYA",
    "ZARZALEJO": "ZARZALEJO",

}

# Función para cargar shapefiles desde GitHub
@st.cache_data(ttl=86400, show_spinner=False)
def cargar_shapefile_desde_github(municipio_file):
    base_url = f"https://raw.githubusercontent.com/iberiaforestal/AFECCIONES_MADRID/master/CATASTRO/{municipio_file}/"
    base_url = base_url.replace(" ", "%20")
    exts = [".shp", ".shx", ".dbf", ".prj", ".cpg"]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        local_paths = {}
        for ext in exts:
            url = f"{base_url}{municipio_file}{ext}"
            try:
                response = session.get(url, timeout=60)  # usamos tu session con reintentos
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                st.error(f"Error al descargar {url}: {str(e)}")
                return None
           
            local_path = os.path.join(tmpdir, municipio_file + ext)
            with open(local_path, "wb") as f:
                f.write(response.content)
            local_paths[ext] = local_path
       
        shp_path = local_paths[".shp"]
        try:
            gdf = gpd.read_file(shp_path, encoding="cp1252")
            gdf = gdf.to_crs(epsg=25830)  # aseguramos ETRS89 UTM 30N
            return gdf
        except Exception as e:
            st.error(f"Error al leer shapefile: {str(e)}")
            return None
            
# Función para encontrar municipio, polígono y parcela a partir de coordenadas
def encontrar_municipio_poligono_parcela(x, y):
    try:
        punto = Point(x, y)
        for municipio, archivo_base in shp_urls.items():
            gdf = cargar_shapefile_desde_github(archivo_base)
            if gdf is None:
                continue
            seleccion = gdf[gdf.contains(punto)]
            if not seleccion.empty:
                parcela_gdf = seleccion.iloc[[0]]
                masa = parcela_gdf["MASA"].iloc[0]
                parcela = parcela_gdf["PARCELA"].iloc[0]
                return municipio, masa, parcela, parcela_gdf
        return "N/A", "N/A", "N/A", None
    except Exception as e:
        st.error(f"Error al buscar parcela: {str(e)}")
        return "N/A", "N/A", "N/A", None

# Función para transformar coordenadas de ETRS89 a WGS84
def transformar_coordenadas(x, y):
    try:
        x, y = float(x), float(y)
        if not (380000 <= x <= 510000 and 4430000 <= 4535000):
            st.error("Coordenadas fuera del rango esperado para ETRS89 UTM Zona 30")
            return None, None
        transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(x, y)
        return lon, lat
    except ValueError:
        st.error("Coordenadas inválidas. Asegúrate de ingresar valores numéricos.")
        return None, None

# === DESCARGA CON CACHÉ SOLO PARA WFS (GeoJSON) ===
@st.cache_data(show_spinner=False, ttl=604800)
def _descargar_geojson(url):
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        if not hasattr(st, "_wfs_warnings"):
            st._wfs_warnings = set()
        warning_key = url.split('/')[-1]
        if warning_key not in st._wfs_warnings:
            st.warning(f"Servicio no disponible: {warning_key}")
            st._wfs_warnings.add(warning_key)
        return None


# === FUNCIÓN UNIFICADA: WFS + ArcGIS FeatureServer ===
def consultar_wfs_seguro(geom, url, nombre_afeccion, campo_nombre=None, campos_mup=None):
    """
    Consulta segura que soporta:
    - WFS (GeoJSON)
    - ArcGIS FeatureServer / MapServer (REST)
    - Campos personalizados (MUP)
    """

    try:
        # --- Detectar ArcGIS REST ----
        if "FeatureServer" in url or "MapServer" in url:

            # GeoPandas lo puede leer directamente si terminas en /query?...
            if "query" not in url:
                if not url.endswith("/"):
                    url += "/"
                url += "query?where=1=1&outFields=*&f=geojson"

            gdf = gpd.read_file(url)

        # --- Caso WFS normal ---
        else:
            data = _descargar_geojson(url)
            if data is None:
                return f"Indeterminado: {nombre_afeccion} (servicio no disponible)"
            gdf = gpd.read_file(data)

        # --- Intersección ---
        seleccion = gdf[gdf.intersects(geom)]

        if seleccion.empty:
            return f"No afecta a {nombre_afeccion}"

        # ============================
        #  MODO MUP (campos personalizados)
        # ============================
        if campos_mup:
            info = []
            for _, row in seleccion.iterrows():
                valores = [str(row.get(c.split(":")[0], "Desconocido")) for c in campos_mup]
                etiquetas = [c.split(":")[1] for c in campos_mup]
                info.append("\n".join(f"{etiquetas[i]}: {valores[i]}" for i in range(len(campos_mup))))
            return f"Dentro de {nombre_afeccion}:\n" + "\n\n".join(info)

        # ============================
        #  MODO NORMAL
        # ============================
        nombres = ', '.join(seleccion[campo_nombre].dropna().unique())
        return f"Dentro de {nombre_afeccion}: {nombres}"

    except Exception as e:
        return f"Indeterminado: {nombre_afeccion} (error de datos)"
        
# Función para crear el mapa con afecciones específicas
def crear_mapa(lon, lat, afecciones=[], parcela_gdf=None):
    if lon is None or lat is None:
        st.error("Coordenadas inválidas para generar el mapa.")
        return None, afecciones
    
    m = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker([lat, lon], popup=f"Coordenadas transformadas: {lon}, {lat}").add_to(m)

    # ==========================================
    # 1) DIBUJAR PARCELA (robusto para cualquier formato)
    # ==========================================
    if parcela_gdf is not None:
        try:
            if hasattr(parcela_gdf, 'geometry') and not hasattr(parcela_gdf, 'to_crs'):
                parcela_gdf = gpd.GeoDataFrame([parcela_gdf], crs="EPSG:25830")

            parcela_4326 = parcela_gdf.to_crs("EPSG:4326")
            folium.GeoJson(
                parcela_4326.to_json(),
                name="Parcela",
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'blue',
                    'weight': 3,
                    'dashArray': '5, 5'
                }
            ).add_to(m)

        except Exception as e:
            st.warning(f"No se pudo dibujar la parcela en el mapa: {str(e)}")

    # ==========================================
    # 2) CAPAS WMS
    # ==========================================
    capas = {
        "Red Natura 2000 (WMS)": ("LugaresProtegidos", "IDEM_MA_RED_NATURA_LIC_ZEC"),
        "Montes (WMS)": ("Montes", "IDEM_MA_MONTES_UP"),
        "Vías Pecuarias (WMS)": ("ViasPecuarias", "IDEM_MA_VIAS_PECUARIAS")
    }
    
    for name, (servicio, layer) in capas.items():
        url = f"https://idem.comunidad.madrid/geoidem/ows?"
        try:
            folium.raster_layers.WmsTileLayer(
                url=url,
                name=name,
                fmt="image/png",
                layers=layer,
                transparent=True,
                opacity=0.25,
                control=True
            ).add_to(m)
        except Exception as e:
            st.error(f"Error al cargar la capa WMS {name}: {str(e)}")

    folium.LayerControl().add_to(m)

    # ===============================
    # LEYENDA
    # ===============================
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        background-color: white;
        border: 1px solid grey;
        z-index: 9999;
        font-size: 10px;
        padding: 5px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        line-height: 1.1em;
        width: auto;
        transform: scale(0.75);
        transform-origin: top left;
    ">
        <b>Leyenda</b><br>

        <div>
            <span style="display:inline-block;width:20px;height:20px;background:#00FF00;border:1px solid #008000;"></span>
            Red Natura 2000<br>
    
            <span style="display:inline-block;width:20px;height:20px;background:#FF00FF;border:1px solid #8B008B;"></span>
            Montes Utilidad Pública<br>

            <span style="display:inline-block;width:20px;height:20px;background:#FFA500;border:1px solid #FF8C00;"></span>
            Vías Pecuarias<br>
        </div>
    </div>
    {% endmacro %}
    """

    legend = MacroElement()
    legend._template = Template(legend_html)
    m.get_root().add_child(legend)

    # Añadir marcadores de afecciones
    for afeccion in afecciones:
        folium.Marker([lat, lon], popup=afeccion).add_to(m)

    uid = uuid.uuid4().hex[:8]
    mapa_html = f"mapa_{uid}.html"
    m.save(mapa_html)

    return mapa_html, afecciones

# Función para generar la imagen estática del mapa usando py-staticmaps
def generar_imagen_estatica_mapa(x, y, zoom=16, size=(800, 600)):
    lon, lat = transformar_coordenadas(x, y)
    if lon is None or lat is None:
        return None
    
    try:
        m = StaticMap(size[0], size[1], url_template='http://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
        marker = CircleMarker((lon, lat), 'red', 12)
        m.add_marker(marker)
        
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "mapa.png")
        image = m.render(zoom=zoom)
        image.save(output_path)
        return output_path
    except Exception as e:
        st.error(f"Error al generar la imagen estática del mapa: {str(e)}")
        return None

# Clase personalizada para el PDF con encabezado y pie de página
class CustomPDF(FPDF):
    def __init__(self, logo_path):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # --- ÁREA IMPRIMIBLE (SIN MÁRGENES) ---
                available_width = self.w - self.l_margin - self.r_margin  # ¡CORRECTO!

                max_logo_height = 16  # ← tamaño reducido (prueba 16-20)

                from PIL import Image
                img = Image.open(self.logo_path)
                ratio = img.width / img.height

                # Escalar al ancho disponible
                target_width = available_width
                target_height = target_width / ratio

                if target_height > max_logo_height:
                    target_height = max_logo_height
                    target_width = target_height * ratio

                # --- CENTRAR DENTRO DEL ÁREA IMPRIMIBLE ---
                x = self.l_margin + 5 # a la izquierda
                y = 8 # 8 mm desde arriba

                self.image(self.logo_path, x=x, y=y, w=target_width, h=target_height)
                self.set_y(y + target_height + 3)

            except Exception as e:
                st.warning(f"Error al cargar logo: {e}")
                self.set_y(30)
        else:
            self.set_y(30)

    def footer(self):
        if self.page_no() > 0:
            self.set_y(-15)
            self.set_draw_color(0, 0, 255)
            self.set_line_width(0.5)
            page_width = self.w - 2 * self.l_margin
            self.line(self.l_margin, self.get_y(), self.l_margin + page_width, self.get_y())
            
            self.set_y(-15)
            self.set_font("Arial", "", 9)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, f"Página {self.page_no()}", align="R")

# Función para generar el PDF con los datos de la solicitud
def hay_espacio_suficiente(pdf, altura_necesaria, margen_inferior=20):
    """
    Verifica si hay suficiente espacio en la página actual.
    margen_inferior: espacio mínimo que debe quedar debajo
    """
    espacio_disponible = pdf.h - pdf.get_y() - margen_inferior
    return espacio_disponible >= altura_necesaria

def generar_pdf(datos, x, y, filename):
    logo_path = "logos.jpg"

    if not os.path.exists(logo_path):
        st.error("FALTA EL ARCHIVO: 'logos.jpg' en la raíz del proyecto.")
        st.markdown(
            "Descárgalo aquí: [logos.jpg](https://raw.githubusercontent.com/iberiaforestal/AFECCIONES_MADRID/master/logos.jpg)"
        )
        logo_path = None
    else:
        pass

    # === RECUPERAR query_geom ===
    query_geom = st.session_state.get('query_geom')
    if query_geom is None:
        query_geom = Point(x, y)

    # === OBTENER URLs DESDE SESSION_STATE ===
    urls = st.session_state.get('wfs_urls', {})
    vp_url = urls.get('vp')
    zepa_url = urls.get('zepa')
    lic_url = urls.get('lic')
    enp_url = urls.get('enp')
    corredores_url = urls.get('corredores')
    uso_suelo_url = urls.get('uso_suelo')
    humedales_url = urls.get('humedales')
    biosfera_url = urls.get('biosfera')
    nitratos_url = urls.get('nitratos')            
    
    # Crear instancia de la clase personalizada
    pdf = CustomPDF(logo_path)
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_page()

    # TÍTULO GRANDE SOLO EN LA PRIMERA PÁGINA
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, "Informe preliminar de Afecciones al Medio Natural", ln=True, align="C")
    pdf.ln(10)

    azul_rgb = (141, 179, 226)

    campos_orden = [
        ("Fecha informe", datos.get("fecha_informe", "").strip()),
        ("Nombre", datos.get("nombre", "").strip()),
        ("Apellidos", datos.get("apellidos", "").strip()),
        ("DNI", datos.get("dni", "").strip()),
        ("Dirección", datos.get("dirección", "").strip()),
        ("Teléfono", datos.get("teléfono", "").strip()),
        ("Email", datos.get("email", "").strip()),
    ]

    def seccion_titulo(texto):
        pdf.set_fill_color(*azul_rgb)
        ancho_deseado = 190
        x = (pdf.w - ancho_deseado) / 2
        pdf.cell(ancho_deseado, 10, "", ln=False, fill=True)
        pdf.set_x(x)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 10, texto, ln=True, fill=True)
        pdf.ln(2)

    def campo_orden(pdf, titulo, valor):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 7, f"{titulo}:", ln=0)
        pdf.set_font("Arial", "", 12)
        
        valor = valor.strip() if valor else "No especificado"
        wrapped_text = textwrap.wrap(valor, width=60)
        if not wrapped_text:
            wrapped_text = ["No especificado"]
        
        for line in wrapped_text:
            pdf.cell(0, 7, line, ln=1)

    seccion_titulo("1. Datos del solicitante")
    for titulo, valor in campos_orden:
        campo_orden(pdf, titulo, valor)

    objeto = datos.get("objeto de la solicitud", "").strip()
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "Objeto de la solicitud:", ln=True)
    pdf.set_font("Arial", "", 11)
    wrapped_objeto = textwrap.wrap(objeto if objeto else "No especificado", width=60)
    for line in wrapped_objeto:
        pdf.cell(0, 7, line, ln=1)
        
    seccion_titulo("2. Localización")
    for campo in ["municipio", "polígono", "parcela"]:
        valor = datos.get(campo, "").strip()
        campo_orden(pdf, campo.capitalize(), valor if valor else "No disponible")

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, f"Coordenadas ETRS89: X = {x:.2f}, Y = {y:.2f}", ln=True)

    imagen_mapa_path = generar_imagen_estatica_mapa(x, y)
    if imagen_mapa_path and os.path.exists(imagen_mapa_path):
        epw = pdf.w - 2 * pdf.l_margin
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, "Mapa de localización:", ln=True, align="C")
        image_width = epw * 0.5
        x_centered = pdf.l_margin + (epw - image_width) / 2  # Calcular posición x para centrar
        pdf.image(imagen_mapa_path, x=x_centered, w=image_width)
    else:
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 7, "No se pudo generar el mapa de localización.", ln=True)

    pdf.add_page()
    pdf.ln(10)
    seccion_titulo("3. Afecciones detectadas")
        
    afecciones_keys = []
    vp_key = "afección VP"
    mup_key = "afección MUP"
    zepa_key = "afección ZEPA"
    lic_key = "afección LIC"
    enp_key = "afección ENP"
    corredores_key = "afección CORREDORES"
    uso_suelo_key = "Afección PLANEAMIENTO"
    humedales_key = "Afección HUMEDALES"
    biosfera_key = "Afección RESERVA DE LA BIOSFERA"
    nitratos_key = "Afección CONTAMINACION POR NITRATOS"
        
# === PROCESAR TODAS LAS CAPAS ===
    def procesar_capa(url, key, valor_inicial, campos, detectado_list):
        valor = datos.get(key, "").strip()
        if valor and not valor.startswith("No afecta") and not valor.startswith("Error"):
            try:
                data = _descargar_geojson(url)
                if data is None:
                    return "Error al consultar"
                gdf = gpd.read_file(data)
                seleccion = gdf[gdf.intersects(query_geom)]
                if not seleccion.empty:
                    for _, props in seleccion.iterrows():
                        fila = tuple(props.get(campo, "N/A") for campo in campos)
                        detectado_list.append(fila)
                    return ""
                return valor_inicial
            except Exception as e:
                st.error(f"Error al procesar {key}: {e}")
                return "Error al consultar"
        return valor_inicial if not detectado_list else ""

    # === VP ===
    vp_detectado = []
    vp_valor = procesar_capa(
        vp_url, "afección VP", "No afecta a ninguna Vía Pecuaria",
        ["CD_VP", "DS_NOMBRE", "DS_MUNI", "DS_TIPO"],
        vp_detectado
    )

    # === ZEPA ===
    zepa_detectado = []
    zepa_valor = procesar_capa(
        zepa_url, "afección ZEPA", "No afecta a ninguna Zona de Especial Protección para las Aves",
        ["CD_ZEPA", "DS_ZEPA"],
        zepa_detectado
    )

    # === LIC ===
    lic_detectado = []
    lic_valor = procesar_capa(
        lic_url, "afección LIC", "No afecta a ningún Lugar de Interés Comunitario",
        ["CD_ZEC_CODE", "DS_ZEC_NAME"],
        lic_detectado
    )

    # === ENP ===
    enp_detectado = []
    enp_valor = procesar_capa(
        enp_url, "afección ENP", "No afecta a ningún Espacio Natural Protegido",
        ["DS_FIGURA", "DS_NOMBRE"],
        enp_detectado
    )

    # === USO DEL SUELO ===
    uso_suelo_detectado = []
    uso_suelo_valor = procesar_capa(
        uso_suelo_url, "afección uso_suelo", "No afecta a ningún uso del suelo protegido",
        ["DS_CALI", "DS_CLASI"],
        uso_suelo_detectado
    )
    
    # === CORREDORES ===
    corredores_detectado = []
    corredores_valor = procesar_capa(
        corredores_url, "afección corredores", "No afecta a Corredores Ecológicos",
        ["DS_TIPO_CORREDOR", "DS_NOMCORREDOR"],
        corredores_detectado
    )

    # === HUMEDALES ===
    humedales_detectado = []
    humedales_valor = procesar_capa(
        humedales_url, "afección humedales", "No afecta a Humedales",
        ["DS_ZONA", "DS_HUMEDAL"],
        humedales_detectado
    ) 

    # === RESERVA DE LA BIOSFERA ===
    biosfera_detectado = []
    biosfera_valor = procesar_capa(
        biosfera_url, "afección biosfera", "No afecta a Reserva de la Biosfera",
        ["CD_RESERVA", "DS_RESERVA"],
        biosfera_detectado
    )

    # === NITRATOS ===    
    nitratos_detectado = []
    nitratos_valor = procesar_capa(
        nitratos_url, "afección nitratos", "No afecta a Zonas Contaminadas por Nitratos",
        ["CD_ZONA", "DS_DESCRIPCIO"],
        nitratos_detectado
    )    

    # === MUP (ya funciona bien, lo dejamos igual) ===
    mup_valor = datos.get("afección MUP", "").strip()
    mup_detectado = []
    if mup_valor and not mup_valor.startswith("No afecta") and not mup_valor.startswith("Error"):
        entries = mup_valor.replace("Dentro de MUP:\n", "").split("\n\n")
        for entry in entries:
            lines = entry.split("\n")
            if lines:
                mup_detectado.append((
                    lines[0].replace("ID: ", "").strip() if len(lines) > 0 else "N/A",
                    lines[1].replace("Nombre: ", "").strip() if len(lines) > 1 else "N/A",
                    lines[2].replace("Municipio: ", "").strip() if len(lines) > 2 else "N/A",
                    lines[3].replace("Propiedad: ", "").strip() if len(lines) > 3 else "N/A"
                ))
        mup_valor = ""

    # Procesar otras afecciones como texto
    otras_afecciones = []
    if afecciones_keys:
        for key in afecciones_keys:
            valor = datos.get(key, "").strip()
            if not valor:
                valor = "No afecta"
    
            otras_afecciones.append((key, valor))

    # Solo incluir en "otras afecciones" si NO tienen detecciones
    if not nitratos_detectado:
        otras_afecciones.append(("Afección a nitratos", nitratos_valor if nitratos_valor else "No afecta a Contaminación por Nitratos"))
    if not biosfera_detectado:
        otras_afecciones.append(("Reserva de la Biosfera", biosfera_valor if biosfera_valor else "No afecta a Reserva de la Biosfera"))
    if not humedales_detectado:
        otras_afecciones.append(("Afección a humedales", humedales_valor if humedales_valor else "No afecta a Humedales"))
    if not uso_suelo_detectado:
        otras_afecciones.append(("Afección Uso del Suelo", uso_suelo_valor if uso_suelo_valor else "No afecta a ningún uso del suelo protegido"))
    if not corredores_detectado:
        otras_afecciones.append(("Corredores Ecológicos", corredores_valor if corredores_valor else "No afecta a Corredores Ecológicos"))
    if not enp_detectado:
        otras_afecciones.append(("Afección ENP", enp_valor if enp_valor else "No se encuentra en ningún ENP"))
    if not lic_detectado:
        otras_afecciones.append(("Afección LIC", lic_valor if lic_valor else "No afecta a ningún LIC"))
    if not zepa_detectado:
        otras_afecciones.append(("Afección ZEPA", zepa_valor if zepa_valor else "No afecta a ninguna ZEPA"))
    if not vp_detectado:
        otras_afecciones.append(("Afección VP", vp_valor if vp_valor else "No afecta a ninguna VP"))
    if not mup_detectado:
        otras_afecciones.append(("Afección MUP", mup_valor if mup_valor else "No afecta a ningún MUP"))
   
    # Mostrar otras afecciones con títulos en negrita    
    if otras_afecciones:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Otras afecciones:", ln=True)
        pdf.ln(2)

        line_height = 6
        label_width = 55
        text_width = pdf.w - 2 * pdf.l_margin - label_width

        for titulo, valor in otras_afecciones:
            if valor:
                x = pdf.get_x()
                y = pdf.get_y()

                # Título
                pdf.set_xy(x, y)
                pdf.set_font("Arial", "B", 11)
                pdf.cell(label_width, line_height, f"{titulo}:", border=0)

                # Valor
                pdf.set_xy(x + label_width, y)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(text_width, line_height, valor, border=0)

                pdf.ln(line_height)  # Avanzar solo lo necesario
        pdf.ln(2)

    # === TABLA USO DEL SUELO ===
    uso_suelo_detectado = list(set(tuple(row) for row in uso_suelo_detectado))  # ← ELIMINA DUPLICADOS
    if uso_suelo_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(uso_suelo_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afección a Planeamiento Urbano (PGOU):", ln=True)
        pdf.ln(2)
    
        col_w_uso = 50
        col_w_clas = 190 - col_w_uso
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_uso, row_height, "Uso", border=1, fill=True)
        pdf.cell(col_w_clas, row_height, "Clasificación", border=1, fill=True)
        pdf.ln()
    
        # Filas
        pdf.set_font("Arial", "", 10)
    
        for DS_CALI, DS_CLASI in uso_suelo_detectado:
    
            # Calcular número de líneas (sin imprimir)
            uso_lines = pdf.multi_cell(col_w_uso, line_height, str(DS_CALI), split_only=True) or [""]
            clas_lines = pdf.multi_cell(col_w_clas, line_height, str(DS_CLASI), split_only=True) or [""]
    
            # Altura real de fila
            row_h = max(row_height, len(uso_lines)*line_height, len(clas_lines)*line_height)
    
            # ⇩ Evitar salto de página a mitad de fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_uso, row_h)
            pdf.rect(x + col_w_uso, y, col_w_clas, row_h)
    
            # ---- Uso ----
            uso_h = len(uso_lines) * line_height
            pdf.set_xy(x, y)  # sin centrado vertical para evitar desalineación en multilínea
            pdf.multi_cell(col_w_uso, line_height, str(DS_CALI), align="L")
    
            # ---- Clasificación ----
            pdf.set_xy(x + col_w_uso, y)
            pdf.multi_cell(col_w_clas, line_height, str(DS_CLASI), align="L")
    
            # Siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)
        
    # === TABLA VP ===
    if vp_detectado:
    
        # Estimamos altura: título + cabecera + filas + espacio
        altura_estimada = 5 + 5 + (len(vp_detectado) * 6) + 10
    
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Vías Pecuarias (VP):", ln=True)
        pdf.ln(2)
    
        # Configurar tabla
        col_widths = [30, 70, 60, 30]  # Código, Nombre, Municipio, Tipo
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_widths[0], row_height, "Código", border=1, fill=True)
        pdf.cell(col_widths[1], row_height, "Nombre", border=1, fill=True)
        pdf.cell(col_widths[2], row_height, "Municipio", border=1, fill=True)
        pdf.cell(col_widths[3], row_height, "Tipo", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        for CD_VP, DS_NOMBRE, DS_MUNI, DS_TIPO in vp_detectado:
    
            # Calcular alturas reales por multilínea
            nombre_lines = pdf.multi_cell(col_widths[1], line_height, str(DS_NOMBRE), split_only=True) or [""]
            muni_lines = pdf.multi_cell(col_widths[2], line_height, str(DS_MUNI), split_only=True) or [""]
            tipo_lines = pdf.multi_cell(col_widths[3], line_height, str(DS_TIPO), split_only=True) or [""]
            row_h = max(row_height, len(nombre_lines)*line_height, len(muni_lines)*line_height, len(tipo_lines)*line_height)
    
            # ⇩ NUEVO: Evitar saltos de página a mitad de fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            # Guardar posición
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar rectángulos
            pdf.rect(x, y, col_widths[0], row_h)
            pdf.rect(x + col_widths[0], y, col_widths[1], row_h)
            pdf.rect(x + col_widths[0] + col_widths[1], y, col_widths[2], row_h)
            pdf.rect(x + col_widths[0] + col_widths[1] + col_widths[2], y, col_widths[3], row_h)
    
            # Código
            pdf.set_xy(x, y)
            pdf.multi_cell(col_widths[0], line_height, str(CD_VP), align="L")
    
            # Nombre
            pdf.set_xy(x + col_widths[0], y)
            pdf.multi_cell(col_widths[1], line_height, str(DS_NOMBRE), align="L")
    
            # Municipio
            pdf.set_xy(x + col_widths[0] + col_widths[1], y)
            pdf.multi_cell(col_widths[2], line_height, str(DS_MUNI), align="L")
    
            # Tipo
            pdf.set_xy(x + col_widths[0] + col_widths[1] + col_widths[2], y)
            pdf.multi_cell(col_widths[3], line_height, str(DS_TIPO), align="L")
    
            # Siguiente fila
            pdf.set_xy(x, y + row_h)
    
        pdf.ln(5)

    # === TABLA MUP === 
    if mup_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(mup_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Montes (MUP):", ln=True)
        pdf.ln(2)
    
        # Configurar la tabla MUP
        line_height = 5
        col_widths = [30, 80, 40, 40]
        row_height = 5
    
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
    
        # Cabecera
        pdf.cell(col_widths[0], 5, "ID", border=1, fill=True)
        pdf.cell(col_widths[1], 5, "Nombre", border=1, fill=True)
        pdf.cell(col_widths[2], 5, "Municipio", border=1, fill=True)
        pdf.cell(col_widths[3], 5, "Propiedad", border=1, fill=True)
        pdf.ln()
    
        # Filas
        pdf.set_font("Arial", "", 10)
    
        for CD_UP, DS_NOMBRE, DS_MUNICIPIO, DS_PROPIETARIO in mup_detectado:
    
            # Calcular líneas necesarias por columna
            id_lines   = pdf.multi_cell(col_widths[0], line_height, str(CD_UP), split_only=True) or [""]
            nombre_lines = pdf.multi_cell(col_widths[1], line_height, str(DS_NOMBRE), split_only=True) or [""]
            mun_lines  = pdf.multi_cell(col_widths[2], line_height, str(DS_MUNICIPIO), split_only=True) or [""]
            prop_lines = pdf.multi_cell(col_widths[3], line_height, str(DS_PROPIETARIO), split_only=True) or [""]
    
            # Altura real de fila
            row_h = max(
                row_height,
                len(id_lines) * line_height,
                len(nombre_lines) * line_height,
                len(mun_lines) * line_height,
                len(prop_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar bordes
            pdf.rect(x, y, col_widths[0], row_h)
            pdf.rect(x + col_widths[0], y, col_widths[1], row_h)
            pdf.rect(x + col_widths[0] + col_widths[1], y, col_widths[2], row_h)
            pdf.rect(x + col_widths[0] + col_widths[1] + col_widths[2], y, col_widths[3], row_h)
    
            # ---- Escribir contenido (sin centrado vertical, para multilínea correcto) ----
    
            # ID
            pdf.set_xy(x, y)
            pdf.multi_cell(col_widths[0], line_height, str(CD_UP), align="L")
    
            # Nombre
            pdf.set_xy(x + col_widths[0], y)
            pdf.multi_cell(col_widths[1], line_height, str(DS_NOMBRE), align="L")
    
            # Municipio
            pdf.set_xy(x + col_widths[0] + col_widths[1], y)
            pdf.multi_cell(col_widths[2], line_height, str(DS_MUNICIPIO), align="L")
    
            # Propiedad
            pdf.set_xy(x + col_widths[0] + col_widths[1] + col_widths[2], y)
            pdf.multi_cell(col_widths[3], line_height, str(DS_PROPIETARIO), align="L")
    
            # Siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)

    # === TABLA ZEPA === 
    if zepa_detectado:

        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(zepa_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Zonas de Especial Protección para las Aves (ZEPA):", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Código", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for CD_ZEPA, DS_ZEPA in zepa_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(CD_ZEPA), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_ZEPA), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(CD_ZEPA), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_ZEPA), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)

    # === TALBA LIC === 
    if lic_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(lic_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Lugares de Importancia Comunitaria (LIC):", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Código", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for CD_ZEC_CODE, DS_ZEC_NAME in lic_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(CD_ZEC_CODE), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_ZEC_NAME), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(CD_ZEC_CODE), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_ZEC_NAME), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)
        
    # === TABLA ENP === 
    enp_detectado = list(set(tuple(row) for row in enp_detectado))  # ← ELIMINA DUPLICADOS
    if enp_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(enp_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Espacio Natural Protegido (ENP):", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Figura", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for DS_FIGURA, DS_NOMBRE in enp_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(DS_FIGURA), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_NOMBRE), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(DS_FIGURA), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_NOMBRE), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)

    # === TABLA CORREDORES === 
    corredores_detectado = list(set(tuple(row) for row in corredores_detectado))  # ← ELIMINA DUPLICADOS
    if corredores_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(corredores_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Corredores Ecológicos:", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Tipo", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for DS_TIPO_CORREDOR, DS_NOMCORREDOR in corredores_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(DS_TIPO_CORREDOR), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_NOMCORREDOR), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(DS_TIPO_CORREDOR), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_NOMCORREDOR), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)

    # === TABLA HUMEDALES === 
    humedales_detectado = list(set(tuple(row) for row in humedales_detectado))  # ← ELIMINA DUPLICADOS
    if humedales_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(humedales_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Humedales:", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Zona", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for DS_ZONA, DS_HUMEDAL in humedales_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(DS_ZONA), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_HUMEDAL), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(DS_ZONA), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_HUMEDAL), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)

    # === TABLA BIOSFERA === 
    biosfera_detectado = list(set(tuple(row) for row in biosfera_detectado))  # ← ELIMINA DUPLICADOS
    if biosfera_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(biosfera_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Reserva de la Biosfera:", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Zona", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for CD_RESERVA, DS_RESERVA in biosfera_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(CD_RESERVA), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_RESERVA), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(CD_RESERVA), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_RESERVA), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)    
           
    # === TABLA NITRATOS === 
    nitratos_detectado = list(set(tuple(row) for row in nitratos_detectado))  # ← ELIMINA DUPLICADOS
    if nitratos_detectado:
    
        # Estimamos altura inicial
        altura_estimada = 5 + 5 + (len(nitratos_detectado) * 6) + 10
        if not hay_espacio_suficiente(pdf, altura_estimada):
            pdf.add_page()
    
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 5, "Afecciones a Contaminación por Nitratos:", ln=True)
        pdf.ln(2)
    
        col_w_code = 30
        col_w_name = 190 - col_w_code
        line_height = 5
        row_height = 5
    
        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(*azul_rgb)
        pdf.cell(col_w_code, row_height, "Zona", border=1, fill=True)
        pdf.cell(col_w_name, row_height, "Nombre", border=1, fill=True)
        pdf.ln()
    
        pdf.set_font("Arial", "", 10)
    
        # Bucle con nombres correctos
        for CD_ZONA, DS_DESCRIPCIO in nitratos_detectado:
    
            # Calcular líneas necesarias
            code_lines = pdf.multi_cell(col_w_code, line_height, str(CD_ZONA), split_only=True) or [""]
            name_lines = pdf.multi_cell(col_w_name, line_height, str(DS_DESCRIPCIO), split_only=True) or [""]
    
            # Altura real
            row_h = max(
                row_height,
                len(code_lines) * line_height,
                len(name_lines) * line_height
            )
    
            # ⇩ Evitar salto de página dentro de la fila
            if not hay_espacio_suficiente(pdf, row_h):
                pdf.add_page()
    
            x = pdf.get_x()
            y = pdf.get_y()
    
            # Dibujar celdas
            pdf.rect(x, y, col_w_code, row_h)
            pdf.rect(x + col_w_code, y, col_w_name, row_h)
    
            # Escribir código 
            pdf.set_xy(x, y)
            pdf.multi_cell(col_w_code, line_height, str(CD_ZONA), align="L")
    
            # Escribir nombre 
            pdf.set_xy(x + col_w_code, y)
            pdf.multi_cell(col_w_name, line_height, str(DS_DESCRIPCIO), align="L")
    
            # Mover a la siguiente fila
            pdf.set_y(y + row_h)
    
        pdf.ln(5)    
         
    # Nueva sección para el texto en cuadro
    # Procedimientos sin negrita
    pdf.set_font("Arial", "", 8)  # Fuente normal para los procedimientos
    procedimientos_con_enlace = [
        ("70090", "Presentación de escritos y comunicaciones. Formulario genérico.", "https://sede.comunidad.madrid/prestacion-social/formulario-solicitud-generica"),        
        ("L209", "Concesiones para usos privativos en montes de utilidad pública.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/concesion-uso-privativo-montes-up"),
        ("24859", "Autorización de aprovechamiento de madera y leña en montes no gestionados por la Comunidad de Madrid.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/autorizacion-aprov-montes-no-gestionados"),
        ("L250", "Autorización de cambio de uso forestal a agrícola.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/cambio-uso-forestal-agricola-0"),
        ("L221", "Informe sectorial en materia de biodiversidad y gestión forestal.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/informe-sectorial-biodiversidad"),
        ("2468", "Autorizaciones e informes para actividades en el medio natural o espacios protegidos.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/autorizacion-actividades-medio-natural"),
        ("89970", "Autorizaciones para actividades en el Parque Nacional de la Sierra de Guadarrama.", "https://sede.comunidad.madrid/autorizaciones-licencias-permisos-carnes/autorizacion-p-n-sierra-guadarrama"),
    ]

    texto_rojo = (
        "Este informe se emite a efectos ambientales, sin perjuicio de terceros, no prejuzga derechos de propiedad y se habrán de obtener cuantas autorizaciones, licencias o permisos sean preceptivos conforme a la Ley."
    )
    texto_resto = (
        "En caso de ser detectadas afecciones a Dominio público forestal o pecuario, así como a Espacios Naturales Protegidos o RN2000, debe solicitar informe oficial a la Dirección General de Biodiversidad y Gestión Forestal, a través de los procedimientos establecidos en sede electrónica:\n"
    )

    # === 1. CALCULAR ALTURA TOTAL ANTES DE DIBUJAR NADA ===
    margin = pdf.l_margin
    line_height = 4
    codigo_width = 9
    espacio_entre = 2
    x_codigo = margin
    x_texto = margin + codigo_width + espacio_entre
    ancho_texto = 190

    # Medir cuadro rojo
    lineas_rojo = len(pdf.multi_cell(pdf.w - 2*margin, 5, texto_rojo, border=0, align="J", split_only=True))
    altura_cuadro = max(1, lineas_rojo) * 5 + 2  # + ln(2)

    # Medir texto en negrita
    lineas_resto = len(pdf.multi_cell(pdf.w - 2*margin, 5, texto_resto, border=0, align="J", split_only=True))
    altura_resto = max(1, lineas_resto) * 5 + 2  # + ln(2)

    # Medir procedimientos
    altura_procedimientos = 0
    for codigo, texto, url in procedimientos_con_enlace:
        lineas = len(pdf.multi_cell(ancho_texto, line_height, texto, border=0, align="J", split_only=True))
        altura_procedimientos += max(1, lineas) * line_height

    # Espacios
    espacio_inicial = 10
    espacio_entre = 4
    espacio_final = 5
    altura_total = espacio_inicial + altura_cuadro + espacio_entre + altura_resto + altura_procedimientos + espacio_final

    # === 2. SI NO CABE TODO → NUEVA PÁGINA ===
    if not hay_espacio_suficiente(pdf, altura_total):
        pdf.add_page()

    # === 3. AHORA SÍ: DIBUJAR TODO JUNTO (sin cortes) ===
    pdf.ln(10)  # Espacio inicial

    # --- CUADRO ROJO (completo) ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(255, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.set_fill_color(251, 228, 213)
    pdf.multi_cell(190, 5, texto_rojo, border=1, align="J", fill=True)
    pdf.ln(2)

    # --- TEXTO EN NEGRITA ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 8)
    pdf.multi_cell(190, 5, texto_resto, border=0, align="J")
    pdf.ln(2)

    # --- PROCEDIMIENTOS ---
    pdf.set_font("Arial", "", 8)
    y = pdf.get_y()

    for codigo, texto, url in procedimientos_con_enlace:
        lineas = len(pdf.multi_cell(ancho_texto, line_height, texto, border=0, align="J", split_only=True))
        altura_linea = max(1, lineas) * line_height

        if pdf.get_y() + altura_linea > pdf.h - pdf.b_margin:
            pdf.add_page()
            y = pdf.get_y()

        pdf.set_xy(x_codigo, y)
        if url:
            pdf.set_text_color(0, 0, 255)
            pdf.cell(codigo_width, line_height, f"- {codigo}", border=0)
            pdf.link(x_codigo, y, codigo_width, line_height, url)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.cell(codigo_width, line_height, f"- {codigo}", border=0)

        pdf.set_xy(x_texto, y)
        pdf.multi_cell(ancho_texto, line_height, texto, border=0, align="J")
        y += altura_linea

    pdf.ln(espacio_final)

        # Volver a negrita para el resto del texto
    pdf.set_font("Arial", "B", 9)  # Restaurar negrita
    texto_final = (
        "\nLas afecciones del presente informe se basan en cartografía oficial de la Comunidad Autónoma y de la Dirección General del Catastro, cumpliendo el estándar técnico Web Feature Service (WFS) definido por el Open Geospatial Consortium (OGC) y la Directiva INSPIRE, eximiendo a IBERIA FORESTAL INGENIERÍA S.L de cualquier error en la cartografía.\n\n"
        "El Planeamiento se regirá por la Ley 9/2001, de 17 de julio, del Suelo, de la Comunidad de Madrid, y por el PGOU del termino municipal. El Régimen del suelo no urbanizable de protección se recoge en el artículo 29 de la citada Ley.\n\n"
        "En suelo no urbanizable se prestara especial atención a la definición de monte dada en el artículo 3 de la Ley 16/1995, de 4 de mayo, Forestal y de Protección de la Naturaleza de la Comunidad de Madrid, y artículo 5 de la Ley 43/2003, de 21 de noviembre, de Montes. Solicitando para posibles cambios de uso lo establecido en la normativa de referencia.\n\n"
        "De acuerdo con lo establecido en el artículo 22.1 de la ley 43/2003 de 21 de noviembre de Montes, toda inmatriculación o inscripción de exceso de cabida en el Registro de la Propiedad de un monte o de una finca colindante con monte demanial o ubicado en un término municipal en el que existan montes demaniales requerirá el previo informe favorable de los titulares de dichos montes y, para los montes catalogados, el del órgano forestal de la Comunidad Autónoma.\n\n"
        "De acuerdo con lo establecido en el artículo 25.5 de la ley 43/2003 de 21 de noviembre de Montes, para posibilitar el ejercicio del derecho de adquisición preferente a través de la acción de tanteo, el transmitente deberá notificar fehacientemente a la Administración pública titular de ese derecho los datos relativos al precio y características de la transmisión proyectada, la cual dispondrá de un plazo de tres meses, a partir de dicha notificación, para ejercitar dicho derecho, mediante el abono o consignación de su importe en las referidas condiciones.\n\n"
        "En relación al Dominio Público Pecuario, salvaguardando lo que pudiera resultar de los futuros deslindes, en la parcela objeto este informe, cualquier construcción, plantación, vallado, obras, instalaciones, etc., no deberían realizarse dentro del área delimitada como Dominio Público Pecuario provisional para evitar invadir este.\n\n"
        "En todo caso, no podrá interrumpirse el tránsito por las Vías Pecuarias, dejando siempre el paso adecuado para el tránsito ganadero y otros usos legalmente establecidos en la Ley 3/1995, de 23 de marzo, de Vías Pecuarias."
    )
    pdf.multi_cell(190, 5, texto_final, border=0, align="J")
    pdf.ln(2)
        
    # === PIE ===
    pdf.ln(10)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6,        
        "Para mas información:\n"
        "E-mail: info@iberiaforestal.es",
        align="J"
    )

    pdf.output(filename)
    return filename

# Interfaz de Streamlit
st.image(
    "https://raw.githubusercontent.com/iberiaforestal/AFECCIONES_MADRID/master/logos.jpg",
    width=250 # ← más pequeño (prueba 160-200)
)
st.title("Informe basico de Afecciones al Medio Natural")

modo = st.radio("Seleccione el modo de búsqueda. Recuerde que la busqueda por parcela analiza afecciones al total de la superficie de la parcela, por el contrario la busqueda por coodenadas analiza las afecciones del punto", ["Por coordenadas", "Por parcela"])

x = 0.0
y = 0.0
municipio_sel = ""
masa_sel = ""
parcela_sel = ""
parcela = None

if modo == "Por parcela":
    municipio_sel = st.selectbox("Municipio", sorted(shp_urls.keys()))
    archivo_base = shp_urls[municipio_sel]
    
    gdf = cargar_shapefile_desde_github(archivo_base)
    
    if gdf is not None:
        masa_sel = st.selectbox("Polígono", sorted(gdf["MASA"].unique()))
        parcela_sel = st.selectbox("Parcela", sorted(gdf[gdf["MASA"] == masa_sel]["PARCELA"].unique()))
        parcela = gdf[(gdf["MASA"] == masa_sel) & (gdf["PARCELA"] == parcela_sel)]
        
        if parcela.geometry.geom_type.isin(['Polygon', 'MultiPolygon']).all():
            centroide = parcela.geometry.centroid.iloc[0]
            x = centroide.x
            y = centroide.y         
                    
            st.success("Parcela cargada correctamente.")
            st.write(f"Municipio: {municipio_sel}")
            st.write(f"Polígono: {masa_sel}")
            st.write(f"Parcela: {parcela_sel}")
        else:
            st.error("La geometría seleccionada no es un polígono válido.")
    else:
        st.error(f"No se pudo cargar el shapefile para el municipio: {municipio_sel}")

with st.form("formulario"):
    if modo == "Por coordenadas":
        x = st.number_input("Coordenada X (ETRS89)", format="%.2f", help="Introduce coordenadas en metros, sistema ETRS89 / UTM zona 30")
        y = st.number_input("Coordenada Y (ETRS89)", format="%.2f")
        if x != 0.0 and y != 0.0:
            municipio_sel, masa_sel, parcela_sel, parcela = encontrar_municipio_poligono_parcela(x, y)
            if municipio_sel != "N/A":
                st.success(f"Parcela encontrada: Municipio: {municipio_sel}, Polígono: {masa_sel}, Parcela: {parcela_sel}")
            else:
                st.warning("No se encontró una parcela para las coordenadas proporcionadas.")
    else:
        st.info(f"Coordenadas obtenidas del centroide de la parcela: X = {x}, Y = {y}")
        
    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    dni = st.text_input("DNI")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Correo electrónico")
    objeto = st.text_area("Objeto de la solicitud", max_chars=255)
    submitted = st.form_submit_button("Generar informe")

if 'mapa_html' not in st.session_state:
    st.session_state['mapa_html'] = None
if 'pdf_file' not in st.session_state:
    st.session_state['pdf_file'] = None
if 'afecciones' not in st.session_state:
    st.session_state['afecciones'] = []

if submitted:
# === 1. LIMPIAR ARCHIVOS DE BÚSQUEDAS ANTERIORES ===
    for key in ['mapa_html', 'pdf_file']:
        if key in st.session_state and st.session_state[key]:
            try:
                if os.path.exists(st.session_state[key]):
                    os.remove(st.session_state[key])
            except:
                pass
    st.session_state.pop('mapa_html', None)
    st.session_state.pop('pdf_file', None)

    # === 2. VALIDAR CAMPOS OBLIGATORIOS ===
    if not nombre or not apellidos or not dni or x == 0 or y == 0:
        st.warning("Por favor, completa todos los campos obligatorios y asegúrate de que las coordenadas son válidas.")
    else:
        # === 3. TRANSFORMAR COORDENADAS ===
        lon, lat = transformar_coordenadas(x, y)
        if lon is None or lat is None:
            st.error("No se pudo generar el informe debido a coordenadas inválidas.")
        else:
            # === 4. DEFINIR query_geom (UNA VEZ) ===
            if modo == "Por parcela":
                query_geom = parcela.geometry.iloc[0]
            else:
                query_geom = Point(x, y)

            # === 5. GUARDAR query_geom Y URLs EN SESSION_STATE ===
            st.session_state['query_geom'] = query_geom
            corredores_url = "https://idem.comunidad.madrid/geoidem/Zonas/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=Zonas:IDEM_CORREDORES_ECO&outputFormat=application/json"
            humedales_url = "https://idem.comunidad.madrid/geoidem/Zonas/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=Zonas:IDEM_MA_CEH_HUMEDALES&outputFormat=application/json"
            biosfera_url = "https://idem.comunidad.madrid/geoidem/LugaresProtegidos/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=LugaresProtegidos:IDEM_MA_RESERVA_BIOS&outputFormat=application/json"
            nitratos_url = "https://idem.comunidad.madrid/geoidem/Zonas/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=Zonas:IDEM_MA_ZONAS_VULNERAB&outputFormat=application/json"                           
            uso_suelo_url = "https://idem.comunidad.madrid/geoidem/UsoDelSuelo/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=UsoDelSuelo:IDEM_URB_GEN_CALI_CLASI_10&outputFormat=application/json"
            enp_url = "https://idem.comunidad.madrid/geoidem/LugaresProtegidos/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=LugaresProtegidos:IDEM_MA_ENP&outputFormat=application/json"
            zepa_url = "https://idem.comunidad.madrid/geoidem/LugaresProtegidos/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=LugaresProtegidos:IDEM_MA_RED_NATURA_ZEPA&outputFormat=application/json"
            lic_url = "https://idem.comunidad.madrid/geoidem/LugaresProtegidos/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=LugaresProtegidos:IDEM_MA_RED_NATURA_LIC_ZEC&outputFormat=application/json"
            vp_url = "https://idem.comunidad.madrid/geoidem/Zonas/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=Zonas:IDEM_MA_VIAS_PECUARIAS&outputFormat=application/json"
            mup_url = "https://idem.comunidad.madrid/geoidem/Zonas/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=Zonas:IDEM_MA_MONTES_UP&outputFormat=application/json"
            st.session_state['wfs_urls'] = {
                'enp': enp_url, 'zepa': zepa_url, 'lic': lic_url,
                'vp': vp_url, 'mup': mup_url, 
                'corredores': corredores_url,
                'uso_suelo': uso_suelo_url,
                'humedales': humedales_url,
                'biosfera': biosfera_url,
                'nitratos': nitratos_url
            }

            # === 6. CONSULTAR AFECCIONES ===
            afeccion_corredores = consultar_wfs_seguro(query_geom, corredores_url, "CORREDOR", campo_nombre="DS_TIPO_CORREDOR")
            afeccion_humedales = consultar_wfs_seguro(query_geom, humedales_url, "HUMEDALES", campo_nombre="DS_ZONA")
            afeccion_biosfera = consultar_wfs_seguro(query_geom, biosfera_url, "BIOESFERA", campo_nombre="CD_RESERVA")
            afeccion_nitratos = consultar_wfs_seguro(query_geom, nitratos_url, "NATRATOS", campo_nombre="CD_ZONA")           
            afeccion_uso_suelo = consultar_wfs_seguro(query_geom, uso_suelo_url, "PLANEAMIENTO", campo_nombre="DS_CLASI")            
            afeccion_enp = consultar_wfs_seguro(query_geom, enp_url, "ENP", campo_nombre="DS_NOMBRE")
            afeccion_zepa = consultar_wfs_seguro(query_geom, zepa_url, "ZEPA", campo_nombre="DS_ZEPA")
            afeccion_lic = consultar_wfs_seguro(query_geom, lic_url, "LIC", campo_nombre="DS_ZEC_NAME")
            afeccion_vp = consultar_wfs_seguro(query_geom, vp_url, "VP", campo_nombre="DS_NOMBRE")            
            afeccion_mup = consultar_wfs_seguro(
                query_geom, mup_url, "MUP",
                campos_mup=["CD_UP:ID", "DS_NOMBRE:Nombre", "DS_MUNICIPIO:Municipio", "DS_PROPIETARIO:Propiedad"]
            )
            afecciones = [afeccion_corredores, afeccion_humedales, afeccion_biosfera, afeccion_nitratos, afeccion_uso_suelo, afeccion_enp, afeccion_zepa, afeccion_lic, afeccion_vp, afeccion_mup]

            # === 7. CREAR DICCIONARIO `datos` ===
            datos = {
                "fecha_informe": datetime.today().strftime('%d/%m/%Y'),
                "nombre": nombre, "apellidos": apellidos, "dni": dni,
                "dirección": direccion, "teléfono": telefono, "email": email,
                "objeto de la solicitud": objeto,
                "afección MUP": afeccion_mup, "afección VP": afeccion_vp,
                "afección ENP": afeccion_enp, "afección ZEPA": afeccion_zepa,
                "afección LIC": afeccion_lic, "afección uso_suelo": afeccion_uso_suelo,
                "afección corredores": afeccion_corredores,
                "afección humedales": afeccion_humedales,
                "afección biosfera": afeccion_biosfera,
                "afección nitratos": afeccion_nitratos,
                "coordenadas_x": x, "coordenadas_y": y,
                "municipio": municipio_sel, "polígono": masa_sel, "parcela": parcela_sel 
            }

            # === 8. MOSTRAR RESULTADOS EN PANTALLA ===
            st.write(f"Municipio seleccionado: {municipio_sel}")
            st.write(f"Polígono seleccionado: {masa_sel}")
            st.write(f"Parcela seleccionada: {parcela_sel}")

            # === 9. GENERAR MAPA ===
            mapa_html, afecciones_lista = crear_mapa(lon, lat, afecciones, parcela_gdf=parcela)
            if mapa_html:
                st.session_state['mapa_html'] = mapa_html
                st.session_state['afecciones'] = afecciones_lista
                st.subheader("Resultado de las afecciones")
                for afeccion in afecciones_lista:
                    st.write(f"• {afeccion}")
                with open(mapa_html, 'r') as f:
                    html(f.read(), height=500)

            # === 10. GENERAR PDF (AL FINAL, CUANDO `datos` EXISTE) ===
            pdf_filename = f"informe_{uuid.uuid4().hex[:8]}.pdf"
            try:
                generar_pdf(datos, x, y, pdf_filename)
                st.session_state['pdf_file'] = pdf_filename
            except Exception as e:
                st.error(f"Error al generar el PDF: {str(e)}")

            # === 11. LIMPIAR DATOS TEMPORALES ===
            st.session_state.pop('query_geom', None)
            st.session_state.pop('wfs_urls', None)
if st.session_state.get('mapa_html') and st.session_state.get('pdf_file'):
    try:
        # Crear un ZIP en memoria con los dos archivos
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Añadir el PDF
            with open(st.session_state['pdf_file'], "rb") as f:
                zip_file.writestr("informe_afecciones.pdf", f.read())
            
            # Añadir el mapa HTML
            with open(st.session_state['mapa_html'], "rb") as f:
                zip_file.writestr("mapa_interactivo.html", f.read())
        
        zip_buffer.seek(0)
        
        st.download_button(
            label="Descargar informe completo (PDF + Mapa interactivo)",
            data=zip_buffer,
            file_name="informe_completo_afecciones.zip",
            mime="application/zip"
        )
        
    except Exception as e:
        st.error(f"Error al crear el archivo ZIP: {str(e)}")
