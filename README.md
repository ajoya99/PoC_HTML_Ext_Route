# PoC_HTML_Ext_Route

## Project Structure

```text
PoC_HTML_Ext_Route/
├── index.html
├── python/
│   ├── baseline.ipynb
│   ├── Google_maps_model_5.ipynb
│   ├── server.py
│   ├── requirements.txt
│   ├── heatmap_maken.ipynb
│   ├── heatmap.html
│   ├── map.html
│   ├── meerdere_locaties.ipynb
│   ├── order_en_gps_combinatie.ipynb
│   ├── orders_handmatig.ipynb
│   ├── ritten_naar_routes.ipynb
│   ├── VRP_model_1_en_2.html
│   ├── VRP_model_1_en_2.ipynb
│   ├── VRP_model_3_en_4.html
│   ├── VRP_model_3_en_4.ipynb
│   ├── data/
│   │   ├── Bezoeken per voertuig 01-01-2025 - 31-12-2025.Csv
│   │   ├── df04_latest.csv
│   │   ├── Ritten per voertuig 01-01-2025 - 31-12-2025.Csv
│   │   └── Januari 2025/
│   └── oud/
│       ├── csv_bestand.ipynb
│       ├── Data_combinere_jan25.ipynb
│       ├── data_opschonen_order.ipynb
│       └── medux_test.ipynb
│   └── web/
│       └── landing.html
```

## Notes

- Main work appears to be under the `python/` directory.
- The `data/` folder contains CSV datasets and monthly subfolders.
- The `oud/` folder appears to contain older notebook versions.

## Landing Page + Routing API

This project now includes a simple web UI where a user enters exactly 4 locations and clicks **GO**.
The backend loads the `haversine` routing function from `Google_maps_model_5.ipynb`, finds the best route, and returns a Google Maps directions link.

### Run Locally

From the project root:

```powershell
cd python
pip install -r requirements.txt
python server.py
```

Then open:

- `http://127.0.0.1:5000/`

### How It Works

- Frontend: `python/web/landing.html`
- Backend API: `python/server.py`
- Endpoint: `POST /api/route`
- Input body: `{ "locations": ["loc1", "loc2", "loc3", "loc4"] }`
- Output: ordered route + total distance + Google Maps link

## GitHub Pages (Phone Access)

GitHub Pages can only host static files. Because of that, `index.html` contains a browser-only routing mode:

- It accepts 4 locations.
- It geocodes in the browser (OpenStreetMap Nominatim).
- It computes the best route order for 4 points and generates a Google Maps link.

### Publish Steps

1. Push this repository to GitHub.
2. Open repository settings on GitHub.
3. Go to **Pages**.
4. Under **Build and deployment**:
	- Source: **Deploy from a branch**
	- Branch: **main** (or your default branch)
	- Folder: **/ (root)**
5. Save and wait until GitHub publishes.

Your public URL will be:

- `https://<your-username>.github.io/<your-repo>/`

You can open that URL on your phone.

### Important Note

- The local Flask app (`python/server.py`) can run notebook-linked logic locally.
- GitHub Pages cannot directly run Python or Jupyter notebooks.
