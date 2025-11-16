from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from digit_pipeline import PipelineResult, run_pipeline
from strtraductor import (
    Organizarcadena,
    depurar_parentesis,
    depurar_trigonometria,
    exponentes,
    modificar_indices,
    raices,
)


def build_expression(
    cadena: List[str],
    sort_list: List[Tuple[np.ndarray, Tuple[int, int, int, int]]],
    centros: List[Tuple[int, int]],
) -> str:
    cadena_organizada, indices = Organizarcadena(cadena, sort_list, centros)
    cadenafinaltrigonometrica = depurar_trigonometria(cadena_organizada)
    indicesparaexponentes = modificar_indices(cadenafinaltrigonometrica, indices)
    cadenarepuesto, indicesrepuesto = raices(
        cadenafinaltrigonometrica,
        indicesparaexponentes,
        sort_list,
        centros,
    )
    cadenarepuesto = depurar_parentesis(cadenarepuesto, indicesrepuesto)
    cadenarepuesto, indicesrepuesto = exponentes(
        cadenarepuesto,
        indicesrepuesto,
        sort_list,
        centros,
    )

    cadenarepuesto = cadenarepuesto.replace("¿", "(")
    cadenarepuesto = cadenarepuesto.replace("?", ")")
    cadenarepuesto = cadenarepuesto.replace("p", "π")
    cadenarepuesto = cadenarepuesto.replace("r", "root")
    cadenarepuesto = cadenarepuesto.replace("q", "sqrt")
    cadenarepuesto = cadenarepuesto.replace("d", "/")
    return cadenarepuesto


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_image(path: Path, image: np.ndarray) -> None:
    ensure_dir(path.parent)
    cv2.imwrite(str(path), image)


def draw_predictions(
    base_image: np.ndarray,
    result: PipelineResult,
) -> np.ndarray:
    overlay = base_image.copy()
    for symbol in result.symbol_predictions:
        x, y, w, h = symbol.bbox
        label = symbol.label
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 200, 255), 2)
        cv2.putText(
            overlay,
            label,
            (x, y - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 200, 255),
            2,
            cv2.LINE_AA,
        )
    return overlay


def export_digits(
    digits_dir: Path,
    result: PipelineResult,
) -> List[Dict[str, object]]:
    ensure_dir(digits_dir)
    digits_summary: List[Dict[str, object]] = []

    for symbol in result.symbol_predictions:
        label = symbol.label
        index = symbol.index

        original_path = digits_dir / f"{index:02d}_{label}_original.png"
        processed_path = digits_dir / f"{index:02d}_{label}_processed.png"

        cv2.imwrite(str(original_path), symbol.original_crop)
        cv2.imwrite(str(processed_path), symbol.processed_crop)

        digits_summary.append(
            {
                "index": index,
                "label": label,
                "bbox": {
                    "x": symbol.bbox[0],
                    "y": symbol.bbox[1],
                    "w": symbol.bbox[2],
                    "h": symbol.bbox[3],
                },
                "center": {"x": symbol.center[0], "y": symbol.center[1]},
                "source": symbol.source,
                "original_path": str(original_path),
                "processed_path": str(processed_path),
            }
        )

    return digits_summary


def _save_debug_images(
    color_bgr: np.ndarray,
    gray_image: np.ndarray,
    result: PipelineResult,
    output_dir: Path,
) -> List[Dict[str, object]]:
    save_image(output_dir / "01_entrada_color.png", color_bgr)
    save_image(output_dir / "02_entrada_grises.png", gray_image)

    threshold_img = result.debug.get("umbralizada")
    if threshold_img is not None:
        save_image(output_dir / "03_umbralizacion.png", threshold_img)

    contornos = result.debug.get("contornos_originales", [])
    contour_image = color_bgr.copy()
    if contornos:
        cv2.drawContours(contour_image, contornos, -1, (0, 255, 0), 2)
    save_image(output_dir / "04_contornos.png", contour_image)

    annotated = draw_predictions(color_bgr, result)
    save_image(output_dir / "05_predicciones.png", annotated)

    digits_summary = export_digits(output_dir / "digits", result)
    return digits_summary


def process_image_array(
    gray_image: np.ndarray,
    output_dir: Path,
    model_path: Optional[Path] = None,
    color_image: Optional[np.ndarray] = None,
    source_image: Optional[str] = None,
) -> Dict[str, object]:
    ensure_dir(output_dir)

    if gray_image.ndim == 3:
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)

    if color_image is None:
        color_bgr = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    else:
        if color_image.ndim == 2:
            color_bgr = cv2.cvtColor(color_image, cv2.COLOR_GRAY2BGR)
        else:
            if color_image.shape[2] == 3:
                color_bgr = color_image.copy()
            elif color_image.shape[2] == 4:
                color_bgr = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
            else:
                raise ValueError("La imagen de color debe tener 1, 3 o 4 canales.")

    pipeline_result = run_pipeline(
        gray_image,
        collect_debug=True,
        model_path=model_path,
    )

    digits_summary = _save_debug_images(color_bgr, gray_image, pipeline_result, output_dir)

    cadena = pipeline_result.raw_sequence
    lista_digitos_sorted = [
        (symbol.processed_crop, symbol.bbox) for symbol in pipeline_result.symbol_predictions
    ]
    centros = pipeline_result.centers
    final_expression = build_expression(cadena, lista_digitos_sorted, centros)

    report = {
        "image": source_image or "array",
        "output_dir": str(output_dir),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "raw_sequence": cadena,
        "final_expression": final_expression,
        "digits": digits_summary,
    }

    with open(output_dir / "reporte.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    with open(output_dir / "expresion.txt", "w", encoding="utf-8") as f:
        f.write(final_expression + "\n")

    return report


def run_monitoring_pipeline(
    image_path: Path,
    output_dir: Path,
    model_path: Optional[Path] = None,
) -> Dict[str, object]:
    color_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if color_image is None:
        raise ValueError(f"No se pudo abrir la imagen: {image_path}")

    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

    return process_image_array(
        gray_image=gray_image,
        output_dir=output_dir,
        model_path=model_path,
        color_image=color_image,
        source_image=str(image_path),
    )


__all__ = [
    "build_expression",
    "process_image_array",
    "run_monitoring_pipeline",
]
