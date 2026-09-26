# Prerequisites & Environment Setup Guide
## JANA-GATISHAKTI / CIVIC-PULSE BRICS DPI Platform

---

### 1. System Requirements

* **Operating System**: Windows 10/11, Ubuntu 20.04+, Debian 11+, macOS 12+
* **Processor (CPU)**: Dual-core 2.0 GHz or higher (x86_64 or ARM64)
* **Memory (RAM)**: 4 GB minimum (8 GB recommended)
* **Disk Storage**: 500 MB free space for code and cached indices
* **Network**: Standard internet access for CDN dependencies (Leaflet, Tailwind) and initial pip package download.

---

### 2. Software Prerequisites

| Tool / Runtime | Minimum Version | Recommended Version | Verification Command |
|---|---|---|---|
| **Python** | 3.10.x | 3.12.x – 3.14.x | `python --version` or `py --version` |
| **pip** | 22.x | 24.x – 25.x | `python -m pip --version` |
| **Git** | 2.30.x | 2.45+ | `git --version` |
| **Modern Browser** | Chrome 90+, Edge 90+, Firefox 90+ | Latest Chrome / Edge | Web Speech API enabled for live audio |

---

### 3. Quick Verification Script (PowerShell / Bash)

#### Windows (PowerShell):
```powershell
# Check Python
py --version
# Check pip
py -m pip --version
# Check Git
git --version
```

#### Linux / macOS (Bash):
```bash
python3 --version
python3 -m pip --version
git --version
```

---

### 4. Step-by-Step Installation

#### Step 4.1: Clone or Open Repository
```bash
git clone https://github.com/brics-dpi/jana-gatishakti.git
cd jana-gatishakti
```

#### Step 4.2: Create and Activate Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 4.3: Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### 5. Running the Application

#### Development Mode with Hot Reload:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Running Tests:
```bash
python tests/test_backend.py
```

#### Access Points:
* **Interactive Web Cockpit**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **OpenAPI 3.0 Interactive Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Open Contracting Data Standard (OCDS) API**: [http://127.0.0.1:8000/api/dpg/ocds](http://127.0.0.1:8000/api/dpg/ocds)
* **OGC GeoJSON Spatial Endpoint**: [http://127.0.0.1:8000/api/dpg/geojson](http://127.0.0.1:8000/api/dpg/geojson)
* **DPGA 9-Indicator Compliance Report**: [http://127.0.0.1:8000/api/dpg/compliance](http://127.0.0.1:8000/api/dpg/compliance)
