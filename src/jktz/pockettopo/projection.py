"""Auditable survey overlays in source sketch millimetres (x right, y down).

The overlay uses P04 export decisions and P03 means. It never edits a sketch,
infers a datum from a reference, or silently averages unnamed confirmations.
"""

from __future__ import annotations

from collections import defaultdict
from heapq import heappop, heappush
from math import cos, hypot, radians, sin

from jktz.pockettopo.model import TopFile, XSection

MAX_SECTION_SPLAY_LINES = 100_000


def _vector(group: dict, source: TopFile) -> tuple[float, float, float, float]:
    if group["kind"] == "zero_link":
        return (0.0, 0.0, 0.0, 0.0)
    mean = group["average"]
    distance = mean["distance_m"] * 1000
    azimuth = radians(mean["azimuth_deg"] + group["export"]["declination_degrees"])
    inclination = radians(mean["inclination_deg"])
    horizontal = distance * cos(inclination)
    flipped = source.shots[group["source_indices"][0]].flipped
    return (
        horizontal * sin(azimuth),
        horizontal * cos(azimuth),
        distance * sin(inclination),
        -horizontal if flipped else horizontal,
    )


def _add(start: tuple, delta: tuple, sign: int = 1) -> tuple:
    return tuple(value + sign * step for value, step in zip(start, delta))


def _coordinates(position: tuple, view: str) -> list[float]:
    if view == "plan":
        return [position[0], -position[1]]
    return [position[3], -position[2]]


def _adjacency(groups: list[dict]) -> dict:
    adjacency = defaultdict(list)
    for group in groups:
        start, end = group["from_raw"], group["to_raw"]
        adjacency[start]
        if group["kind"] != "splay":
            adjacency[start].append((end, group["id"], 1))
            adjacency[end].append((start, group["id"], -1))
    return adjacency


def _oriented_delta(vector: tuple, sign: int) -> tuple:
    # Flip describes left/right from the attachment station, even when the
    # source FROM/TO direction must be reversed to attach the leg.
    return (*[value * sign for value in vector[:3]], vector[3])


def _attach_component(
    root: int,
    component: int,
    adjacency: dict,
    by_id: dict,
    vectors: dict,
    positions: dict,
    components: dict,
    attachments: dict,
    defining: dict,
) -> None:
    positions[root] = (0.0, 0.0, 0.0, 0.0)
    components[root] = component
    defining[root] = None
    pending = []
    for _, group_id, _ in adjacency[root]:
        heappush(pending, group_id)
    while pending:
        group_id = heappop(pending)
        if group_id in attachments:
            continue
        group = by_id[group_id]
        start, end = group["from_raw"], group["to_raw"]
        sign = 1
        if start not in positions:
            start, end, sign = end, start, -1
        attachments[group_id] = (start, end, sign)
        if end in positions:
            continue
        positions[end] = _add(positions[start], _oriented_delta(vectors[group_id], sign))
        components[end] = component
        defining[end] = (group_id, sign)
        for _, adjacent_id, _ in adjacency[end]:
            heappush(pending, adjacent_id)


def _locate(groups: list[dict], vectors: dict) -> tuple:
    adjacency = _adjacency(groups)
    positions, components, attachments, defining = {}, {}, {}, {}
    by_id = {group["id"]: group for group in groups}
    count = 0
    for root in adjacency:
        if root not in positions:
            _attach_component(
                root, count, adjacency, by_id, vectors, positions, components, attachments, defining
            )
            count += 1
    return positions, components, attachments, defining, count


def _line(group: dict, start: list, end: list, component: int) -> dict:
    return {
        "group_id": group["id"],
        "source_indices": list(group["source_indices"]),
        "start": start,
        "end": end,
        "component": component,
    }


def _survey_lines(
    groups: list[dict],
    positions: dict,
    vectors: dict,
    components: dict,
    attachments: dict,
    view: str,
):
    survey = []
    diagnostics = []
    for group in groups:
        if group["kind"] == "splay":
            continue
        from_raw, to_raw, sign = attachments[group["id"]]
        start = positions[from_raw]
        end = _add(start, _oriented_delta(vectors[group["id"]], sign))
        line = _line(
            group, _coordinates(start, view), _coordinates(end, view), components[group["from_raw"]]
        )
        target = _coordinates(positions[to_raw], view)
        line["reverse_attachment"] = sign == -1
        residual = hypot(*(actual - predicted for actual, predicted in zip(target, line["end"])))
        line.update(target_station_position=target, closure_residual_mm=residual)
        survey.append(line)
        if residual > 1e-6:
            diagnostics.append(
                {
                    "code": "unadjusted_closure",
                    "view": view,
                    "group_id": group["id"],
                    "residual_mm": residual,
                }
            )
    return survey, diagnostics


def _splay_delta(group: dict, vector: tuple, defining: dict, by_id: dict, source: TopFile) -> tuple:
    parent = defining[group["from_raw"]]
    horizontal = 0.0
    if parent is not None and by_id[parent[0]]["kind"] != "zero_link":
        parent_id, sign = parent
        parent_group = by_id[parent_id]
        axis = parent_group["average"]["azimuth_deg"] + (180 if sign == -1 else 0)
        bearing = group["average"]["azimuth_deg"]
        horizontal = hypot(vector[0], vector[1]) * cos(radians(bearing - axis))
        if source.shots[parent_group["source_indices"][0]].flipped:
            horizontal = -horizontal
    return (*vector[:3], horizontal)


def _splay_lines(
    groups: list[dict],
    positions: dict,
    vectors: dict,
    components: dict,
    defining: dict,
    source: TopFile,
    view: str,
):
    splays = []
    by_id = {group["id"]: group for group in groups}
    for group in groups:
        if group["kind"] != "splay":
            continue
        start = positions[group["from_raw"]]
        delta = _splay_delta(group, vectors[group["id"]], defining, by_id, source)
        end = _add(start, delta)
        splays.append(
            _line(
                group,
                _coordinates(start, view),
                _coordinates(end, view),
                components[group["from_raw"]],
            )
        )
    return splays


def _section_delta(vector: tuple, direction: int, correction: float) -> list[float]:
    if direction == -1:
        return [vector[0], -vector[1]]
    angle = radians(direction * 360 / 65536 + correction)
    return [vector[0] * cos(angle) - vector[1] * sin(angle), -vector[2]]


def _section_index(source: TopFile, groups: list[dict]) -> dict:
    splays = defaultdict(list)
    for group in groups:
        if group["kind"] == "splay":
            splays[group["from_raw"]].append(group)
    count = sum(
        len(splays.get(element.station.raw, ()))
        for drawing in (source.outline, source.sideview)
        for element in drawing.elements
        if isinstance(element, XSection)
    )
    if count > MAX_SECTION_SPLAY_LINES:
        raise ValueError("xsection_projection_limit_exceeded: " + str(count))
    return splays


def _sections(
    source: TopFile, splays: dict, positions: dict, vectors: dict, components: dict, view: str
):
    drawing = source.outline if view == "plan" else source.sideview
    sections = []
    for index, element in enumerate(drawing.elements):
        if not isinstance(element, XSection):
            continue
        position = [element.position.x, element.position.y]
        known = element.station.raw in positions
        section = {
            "element_index": index,
            "position": position,
            "station_raw": element.station.raw,
            "direction": element.direction,
            "status": "projected" if known else "station_not_in_active_overlay",
            "connector": {
                "start": position,
                "end": _coordinates(positions[element.station.raw], view),
            }
            if known
            else None,
            "splays": [],
        }
        for group in splays.get(element.station.raw, ()):
            delta = _section_delta(
                vectors[group["id"]], element.direction, group["export"]["declination_degrees"]
            )
            end = [value + step for value, step in zip(position, delta)]
            section["splays"].append(_line(group, position, end, components[element.station.raw]))
        sections.append(section)
    return sections


def project_geometry(source: TopFile, report: dict) -> dict:
    """Project active P04 groups without changing the report or source model.

    Named stations use a deterministic source-order attachment spanning
    forest, without loop adjustment. Every measured leg has its own endpoint;
    residuals to an already located station remain explicit. Each disconnected
    component has its own local zero and no inferred relationship to the sketch.
    """
    groups = [group for group in report["groups"] if group["export"]["status"] == "exported"]
    section_splays = _section_index(source, groups)
    vectors = {group["id"]: _vector(group, source) for group in groups}
    positions, components, attachments, defining, count = _locate(groups, vectors)
    labels = {station["raw"]: station["source_text"] for station in report["station_map"]}
    result = {
        "views": {},
        "diagnostics": [],
        "policy": "source_order_attachment_unadjusted_forest",
        "units": "millimetres",
        "axes": "x_right_y_down",
        "components": count,
        "loop_adjustment": False,
        "references_applied": False,
        "mapping_applied": False,
        "mixed_flip_policy": "first_source_reading_unconfirmed_side_direction",
    }
    for group in groups:
        if "mixed_flip_preserved_for_drawing_review" in group["warnings"]:
            result["diagnostics"].append(
                {
                    "code": "mixed_flip_first_source_reading",
                    "group_id": group["id"],
                    "source_indices": list(group["source_indices"]),
                    "source_flags": [
                        source.shots[index].flags for index in group["source_indices"]
                    ],
                    "selected_source_index": group["source_indices"][0],
                    "side_direction_status": "unconfirmed",
                }
            )
    if count > 1:
        result["diagnostics"].append(
            {"code": "disconnected_components_local_origins", "components": count}
        )
    for view in ("plan", "side"):
        survey, diagnostics = _survey_lines(
            groups, positions, vectors, components, attachments, view
        )
        result["diagnostics"].extend(diagnostics)
        result["views"][view] = {
            "survey": survey,
            "splays": _splay_lines(groups, positions, vectors, components, defining, source, view),
            "stations": [
                {
                    "raw": raw,
                    "label": labels[raw],
                    "position": _coordinates(position, view),
                    "component": components[raw],
                }
                for raw, position in positions.items()
            ],
            "xsections": _sections(source, section_splays, positions, vectors, components, view),
        }
    return result
