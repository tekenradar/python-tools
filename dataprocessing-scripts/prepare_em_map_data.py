import pandas as pd

data_file = 'path_to_the_excel_file'

# first row contains column names
data = pd.read_excel(data_file, sheet_name='EM incidentie', header=0, index_col=0)

gm_data = []

for _, row in data.iterrows():
    gm_data.append({
        "name": row['GM_NAAM'],
        "sequence": [
            row['IncEMsm.94'],
            row['IncEMsm.01'],
            row['IncEMsm.05'],
            row['IncEMsm.09'],
            row['IncEMsm.14'],
            row['IncEMsm.17'],
            row['IncEMsm.21'],
        ]
    })

map_slider_data = {
  "slider": {
    "minLabel": "1994",
    "maxLabel": "2021",
    "hideTicks": False,
    "labels": [
      "1994",
      "2001",
      "2005",
      "2009",
      "2014",
      "2017",
      "2021",
    ]
  },
  "series": [
    {
      "name": "Mensen met erythema migrans (rode ring of vlek op de huid)",
      "title": "",
      "colorScale": {
        "hoverStrokeColor": "#FD4",
        "colors": [
          {
            "max": 25,
            "color": "#ffffd4",
            "label": "0 - 25"
          },
          {
            "min": 25,
            "max": 50,
            "color": "#fff433",
            "label": "25 - 50"
          },
          {
            "min": 50,
            "max": 100,
            "color": "#fecc5c",
            "label": "50 - 100"
          },
          {
            "min": 100,
            "max": 200,
            "color": "#fd8d3c",
            "label": "100 - 200"
          },
          {
            "min": 200,
            "max": 300,
            "color": "#f03b20",
            "label": "200 - 300"
          },
          {
            "min": 300,
            "color": "#bd0026",
            "label": "> 300"
          }
        ]
      },
      "legend": {
        "show": True,
        "title": "Aantal per 100.000 inwoners",
        "position": {
          "x": "left",
          "y": "top"
        }
      },
       "data": gm_data
    }
  ]
}

import json

with open('em_map_data.json', 'w') as f:
    json.dump(map_slider_data, f, indent=2)