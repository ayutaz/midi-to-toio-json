# midi-to-toio-json
toioで処理するためのmidiをjsonに変換するコード

# requirement
* python 3.11 >=

# setup

install python packages
```bash
pip install -r requirements.txt
```

# usage

```bash
python midi_to_toio.py midi_file_path
```

# data format
```json
[
  {
    "track_name": "ALBENIZ: Aragon Op 47/6",
    "priority": 1,
    "notes": [
      {
        "note_number": 77,
        "start_time_ms": 0,
        "duration_units": 26
      },
      {

      },
  },
    {
    "track_name": "apurdam@pcug.org.au",
    "priority": 2,
    "notes": [
        {
        "note_number": 53,
        "start_time_ms": 0,
        "duration_units": 58
        },
    ]
    }
]
```