# `pages` Folder

This folder contains all of the individual pages that make up the Farmers Market Streamlit application. Each `.py` file is a single page that Streamlit automatically discovers and renders. Rather than exposing every page to every user, the application gates access by **role/persona** (farmer, policy maker, researcher) so that each user only sees the pages relevant to them.

## Page Ordering

Streamlit orders the pages in the sidebar alphabetically by filename. To control that order, every page is prefixed with a two-digit number (e.g. `01_`, `12_`, `27_`). The leading number determines where a page appears, and the numbers are grouped into ranges by persona:

| Range | Persona | Pages |
| ----- | ------- | ----- |
| `00`–`09` | Farmer | Farmer Home, Farm Info, Crop Predictions, Farmer Blog |
| `10`–`19` | Policy Maker | Policy Home, Map, Compare, Report, Predictions, Blog |
| `20`–`29` | Researcher | Researcher Home, Map, Conditions, Trends, Data Export, Blog, Compare |
| `30`+ | Shared | About |

Gaps are left in the numbering (e.g. `03`, `16`, `22`, `26`) so that new pages can be inserted in the right position later without renaming the entire set.

## Role-Based Access

Although every page file lives in this folder, the sidebar links are not shown to everyone. Navigation is built dynamically in [`../modules/nav.py`](../modules/nav.py): when a user logs in on `Home.py`, their role is stored in `st.session_state`, and `SideBarLinks()` renders only the links for that role. The `About` page is shown when no one is logged in. We use this to limit functionality access by persona.

## Pages by Persona

### Farmer
- **`01_Farmer_Home.py`** — Farmer landing page.
- **`02_Farm_Info.py`** — View and manage your farm and crop information.
- **`04_Crop_Predictions.py`** — Crop type suggestions powered by the ML model.
- **`05_Farmer_Blog.py`** — Community discussion board.

### Policy Maker
- **`11_Policy_Home.py`** — Policy maker landing page.
- **`12_Policy_Map.py`** — Crop price map.
- **`13_Policy_Compare.py`** — Compare farm prices across regions.
- **`14_Policy_Report.py`** — Generate reports for planning and decision-making.
- **`15_Policy_Predictions.py`** — Crop price / regional suitability predictions.
- **`17_Policy_Blog.py`** — Community discussion board.

### Researcher
- **`21_Researcher_Home.py`** — Researcher landing page.
- **`23_Researcher_Map.py`** — Map of environmental and agricultural data.
- **`24_Researcher_Conditions.py`** — Explore crop observations and growing conditions.
- **`25_Researcher_Trends.py`** — Explore long-term crop and environmental trends.
- **`27_Researcher_Data_Export.py`** — Export filtered datasets.
- **`28_Researcher_Blog.py`** — Community discussion board.
- **`29_Researcher_Compare.py`** — Compare crops.

### Shared
- **`30_About.py`** — Information about the project; also shown to logged-out users.

## Documentation

- Streamlit multipage apps: <https://docs.streamlit.io/develop/concepts/multipage-apps>
- Project blog & development process: <https://lauryngong.github.io/Belgium-Politics/>
