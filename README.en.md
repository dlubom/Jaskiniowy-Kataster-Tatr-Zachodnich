[🇵🇱 Polski](README.md) | 🇬🇧 **English** | [🇸🇰 Slovenčina](README.sk.md)

# Tatra Cave Registry

![Walls 2D screen](doc/walls_2d_screen.png)
![Walls 2D screen](doc/walls_3d_screen.png)
![Survex Aven](doc/Survex.jpeg)

[![Latest Release](https://img.shields.io/github/v/release/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich)](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/releases/latest)

[Download the latest release](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/releases/latest)

[3D Model online](https://dlubom.github.io/Jaskiniowy-Kataster-Tatr-Zachodnich/)

### Project Description
The project aims to compile all cartographic data related to the caves of the Tatra Mountains in one place. Utilizing the Walls software, the primary goal is to create a spatial compilation of measurement sequences, cave entrance coordinates, and terrain models. The project is open to all who are interested, to facilitate exploratory and educational activities, and to support scientific research. Gathering comprehensive and accurate data presents a challenge due to the diversity of methods and times of their execution.

### Complementary Data Sets

The registry contains objects for which cave survey data is available. Two related data sets complement it by also covering objects that are not yet present in this repository:

- [GPS Kataster Obiektów Tatr](https://github.com/dlubom/gps-kataster-obiektow-tatr) — a database of GPS locations for cave entrances and other field objects. This project uses its published best GPS measurements to determine entrance coordinates. Ready-to-use GIS and field data can be downloaded from the [latest release](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/latest).
- [Georeferencer](https://github.com/dlubom/Georeferencer) — georeferenced scans of cave plans in GeoTIFF format, including objects without survey data in this registry. A ready-to-use GeoTIFF package can be downloaded from the [latest release](https://github.com/dlubom/Georeferencer/releases/latest).

The project is based on the Walls software – you can find the [latest version of the program and its manual here](http://texasspeleologicalsurvey.org/Walls/tsswalls.htm).

The project also works with [Survex](https://survex.com/) — just install the latest version and open `KATASTER.wpj` in Aven, or compile from the command line: `cavern KATASTER.wpj`. In Aven you can also load the terrain model `Powierzchnia/Survex/N49E019_VF1.hgt`.

### How Can You Help?
We encourage collaboration on the project as well as sharing your own measurements. Contact: [darek.lubomski@gmail.com](mailto:darek.lubomski@gmail.com).

Environment setup instructions for new developers and their agents are in
[CONTRIBUTING.md](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/master/CONTRIBUTING.md). After cloning the repository, start with
`python scripts/initial-setup.py`.

### License
[Creative Commons Attribution-ShareAlike 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

### Project Contents
The current list of caves included in the project can be found in the file [List of Caves](LISTA_JASKIN.md).

### Related Projects
Worth mentioning is the [Caves of the Tatra Mountains](https://github.com/RadostW/jaskinie) project run by Speleoklub Warszawski. They follow a different philosophy — relying on their own contemporary field surveys rather than sourcing data from historical records. They also use secondary digitization of cave plans, without depth information. It's an interesting approach, though surveying all Tatra caves this way will be a significant challenge. The project uses the Survex format and is licensed under CC BY-SA 4.0.

### Changelog
All project changes are documented in the [CHANGELOG.md](CHANGELOG.md).

### Raw source files `_RAW/`
The release ZIP does not include `_RAW/` directories with original survey source files. These are used for data verification and archival purposes. To access them, clone the repository or download the [master branch](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/archive/refs/heads/master.zip).
