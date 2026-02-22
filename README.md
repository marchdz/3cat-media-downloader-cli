# 3Cat Media Downloader (CLI)

**3Cat Media Downloader (CLI)** és un script que permet descarregar contingut multimèdia de la plataforma **3Cat** (que agrupa l'antic **TV3 a la carta**, **Catalunya Ràdio** i nous continguts exclusius) per poder-ne gaudir sense connexió a Internet. Permet obtenir vídeos, pòdcasts, pistes d'àudio i subtítols simplement a partir de la URL del navegador.

## ✨ Característiques

- **Fàcil d'utilitzar:** Només cal copiar i enganxar l'URL de la barra del navegador (ex.: `https://www.3cat.cat/3cat/...`) i prémer **Retorn**.
- **Descàrregues directes:** Suport per a vídeos, pòdcasts i subtítols.
- **Suport DASH (Dynamic Adaptive Streaming over HTTP):**
  - **Selecció de qualitat:** Permet triar entre les diferents resolucions de vídeo disponibles.
  - **Només àudio:** Opció per descarregar exclusivament la pista d'àudio dels continguts de vídeo.
- **Subtítols en format SRT:** Descàrrega i conversió automàtica de VTT a SRT.
- **Multiplataforma:** Compatible amb Windows, macOS i Linux.

---

## 🛠️ Requisits previs

### 1. Python

Aquest script està programat en Python. Si no el tens instal·lat, segueix les instruccions segons el teu sistema operatiu:

**Windows (mètode recomanat amb winget):**

1. Obre **PowerShell**, **CMD** o **Windows Terminal**.

2. Comprova quines versions de Python estan disponibles al repositori de winget:

```powershell
winget search --id Python.Python.3
```

Això mostrarà els IDs exactes i versions publicades (per exemple, Python.Python.3.13, Python.Python.3.14, etc.), i així podràs triar la versió que vols instal·lar.

3. Instal·la la versió escollida (per exemple):

```powershell
winget install --id Python.Python.3.14 -e --source winget
```

4. Tanca i torna a obrir la terminal.
5. Comprova la instal·lació:

```powershell
python --version
```

Aquest mètode afegeix Python automàticament al `PATH`.

**Windows (mètode alternatiu manual):**

Descarrega'l des de https://www.python.org/downloads/ i, durant la instal·lació, **marca la casella "Add Python to PATH"**.

**macOS:**

Si tens Homebrew (https://brew.sh/), obre la terminal i executa:

```bash
brew install python
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Linux (Fedora):**

```bash
sudo dnf install python3 python3-pip
```

---

### 2. FFmpeg (molt recomanat)

FFmpeg és l’eina que permet fusionar els fluxos de vídeo i d’àudio en un únic fitxer.

**Què passa si no instal·les FFmpeg?**

- No tindràs disponibles les opcions de descàrrega per a vídeos DASH (transmissió adaptativa), on generalment es pot trobar l'opció amb millor qualitat.

#### Instal·lació de FFmpeg

**Windows (mètode recomanat amb winget):**

1. Obre **Terminal**, **PowerShell** o **CMD**.
2. Executa:

```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

3. Tanca i torna a obrir la terminal.
4. Comprova que funciona:

```powershell
ffmpeg -version
```

Aquest mètode afegeix automàticament FFmpeg al `PATH`.

**Windows (mètode manual alternatiu):**

Baixa els binaris de https://www.gyan.dev/ffmpeg/builds/, extreu el contingut a `C:\ffmpeg` i afegeix `C:\ffmpeg\bin` a les variables d'entorn (Path).

**macOS:**

```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora):**

```bash
sudo dnf install ffmpeg
```

---

## 📦 Instal·lació i ús

1. **Baixa el projecte:** Descarrega el fitxer `3cat_media_downloader_cli.py` d'aquest repositori i guarda'l en una carpeta.
2. **Obre una terminal:**
   - **Windows:** Prem la tecla `Windows`, escriu `cmd` i prem **Retorn**.
   - **macOS/Linux:** Obre l'aplicació "Terminal".
3. **Navega a la carpeta:** Escriu `cd` seguit d'un espai, arrossega la carpeta del projecte a la terminal i prem **Retorn**.
4. **Executa l'eina:**

```bash
python 3cat_media_downloader_cli.py
```

5. **Descarrega:** Enganxa la URL del contingut de 3Cat, prem **Retorn**, tria entre les opcions disponibles, prem **Retorn** de nou i l'script farà la resta.

---

## 📂 Subtítols

Aquest script genera els subtítols amb el mateix nom base que el vídeo i hi afegeix el codi d’idioma al fitxer SRT.

Per exemple:

`video.mp4` → `video.ca.srt`

(on `ca` indica l’idioma català).

---

## 🤝 Contribucions

Si vols millorar l'script o has trobat algun error, no dubtis a obrir un _Issue_ o enviar una _Merge Request_.

---

## ⚖️ Llicència

Aquest projecte està sota la llicència **MIT**. Ets lliure d'utilitzar, modificar i distribuir el codi sempre que mantinguis l'atribució original. Consulta el fitxer `LICENSE` per a més detalls.

---

## ⚠️ Avís legal (Disclaimer)

Aquest projecte s'ha desenvolupat com un exercici de programació en Python amb finalitats purament educatives, sense cap ànim de lucre i per a un ús estrictament personal.

- **Responsabilitat:** L'autor no es fa responsable de l'ús que els usuaris puguin fer d'aquesta eina. L'usuari final és l'únic responsable d'assegurar-se que el seu ús del contingut multimèdia compleix els Termes i Condicions de la plataforma 3Cat i la legislació vigent sobre propietat intel·lectual.
- **Propietat:** Totes les marques (3Cat, TV3, Catalunya Ràdio, etc.) i continguts descarregats són propietat de la CCMA o dels seus respectius titulars. Aquest script no allotja ni distribueix cap tipus de contingut protegit.
- **Garantia:** Segons la llicència MIT, aquest programari s'ofereix "tal com és", sense garanties de cap tipus respecte al seu funcionament futur si la plataforma original realitza canvis tècnics.
