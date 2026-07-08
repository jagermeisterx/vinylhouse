import io
import time
import requests
import discogs_client
from django.conf import settings

_last_call = 0.0
_min_interval = 1.0


def _throttle():
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < _min_interval:
        time.sleep(_min_interval - elapsed)
    _last_call = time.time()


def get_client():
    return discogs_client.Client(
        settings.DISCOGS_USER_AGENT,
        user_token=settings.DISCOGS_USER_TOKEN,
    )


def search_releases(query, page=0):
    if not query.strip():
        return {"results": [], "pages": 0, "count": 0, "page": page}
    _throttle()
    d = get_client()
    results = d.search(query, type="release")
    count = results.count
    pages = results.pages
    items = results.page(page)
    normalized = []
    for r in items:
        normalized.append({
            "discogs_id": r.id,
            "titulo": getattr(r, "title", "Desconocido"),
            "year": getattr(r, "year", None),
            "thumb": getattr(r, "thumb", None),
            "format": ", ".join(
                f.get("name", "") for f in (getattr(r, "formats", []) or []) if f
            ) if hasattr(r, "formats") else None,
        })
    return {"results": normalized, "pages": pages, "count": count, "page": page}


def get_release(discogs_id):
    _throttle()
    d = get_client()
    r = d.release(discogs_id)
    artistas = " & ".join(
        a.name.replace(" (2)", "") for a in (getattr(r, "artists", []) or [])
    ) or "Artista desconocido"
    generos = list(getattr(r, "genres", []) or [])
    estilos = list(getattr(r, "styles", []) or [])
    genero_principal = generos[0] if generos else (estilos[0] if estilos else "Rock")
    labels = getattr(r, "labels", []) or []
    sello = labels[0].name if labels else ""
    catno = getattr(labels[0], "catno", "") if labels else ""
    formats = getattr(r, "formats", []) or []
    formato = ", ".join(
        f"{f.get('name', '')} ({f.get('qty', '1')})" for f in formats if f
    ) if formats else ""
    tracklist = getattr(r, "tracklist", []) or []
    tracks = []
    for t in tracklist:
        pos = getattr(t, "position", "") or ""
        title = getattr(t, "title", "") or ""
        dur = getattr(t, "duration", "") or ""
        track = f"{pos}. {title}"
        if dur:
            track += f" ({dur})"
        tracks.append(track)
    tracklist_text = "\n".join(tracks)
    imagen_url = None
    images = getattr(r, "images", []) or []
    if images:
        for img in images:
            if img.get("type") == "primary":
                imagen_url = img.get("uri")
                break
        if not imagen_url and images:
            imagen_url = images[0].get("uri")
    descripcion_parts = []
    if sello:
        descripcion_parts.append(f"Sello: {sello}" + (f" ({catno})" if catno else ""))
    if formato:
        descripcion_parts.append(f"Formato: {formato}")
    if estilos:
        descripcion_parts.append(f"Estilos: {', '.join(estilos)}")
    descripcion = "\n".join(descripcion_parts)
    return {
        "discogs_id": r.id,
        "titulo": getattr(r, "title", "") or "",
        "artista": artistas,
        "anio_lanzamiento": getattr(r, "year", None),
        "genero": genero_principal,
        "sello": sello,
        "formato": formato,
        "tracklist": tracklist_text,
        "descripcion": descripcion,
        "imagen_url": imagen_url,
    }


def download_image(url):
    _throttle()
    resp = requests.get(url, headers={"User-Agent": settings.DISCOGS_USER_AGENT}, timeout=30)
    resp.raise_for_status()
    ext = "jpg"
    if "." in url.split("?")[0].split("/")[-1]:
        ext = url.split("?")[0].split("/")[-1].rsplit(".", 1)[-1].lower()
        if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
            ext = "jpg"
    filename = url.split("?")[0].split("/")[-1].rsplit(".", 1)[0]
    if not filename:
        filename = f"discogs_{int(time.time())}"
    return filename, ext, resp.content