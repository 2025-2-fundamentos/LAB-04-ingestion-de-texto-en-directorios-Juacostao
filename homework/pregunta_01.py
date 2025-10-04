# pylint: disable=import-outside-toplevel
# pylint: disable=line-too-long
# flake8: noqa
"""
Escriba el codigo que ejecute la accion solicitada en cada pregunta.
"""


def pregunta_01():
    """
    La información requerida para este laboratio esta almacenada en el
    archivo "files/input.zip" ubicado en la carpeta raíz.
    Descomprima este archivo.

    Como resultado se creara la carpeta "input" en la raiz del
    repositorio, la cual contiene la siguiente estructura de archivos:


    ```
    train/
        negative/
            0000.txt
            0001.txt
            ...
        positive/
            0000.txt
            0001.txt
            ...
        neutral/
            0000.txt
            0001.txt
            ...
    test/
        negative/
            0000.txt
            0001.txt
            ...
        positive/
            0000.txt
            0001.txt
            ...
        neutral/
            0000.txt
            0001.txt
            ...
    ```

    A partir de esta informacion escriba el código que permita generar
    dos archivos llamados "train_dataset.csv" y "test_dataset.csv". Estos
    archivos deben estar ubicados en la carpeta "output" ubicada en la raiz
    del repositorio.

    Estos archivos deben tener la siguiente estructura:

    * phrase: Texto de la frase. hay una frase por cada archivo de texto.
    * sentiment: Sentimiento de la frase. Puede ser "positive", "negative"
      o "neutral". Este corresponde al nombre del directorio donde se
      encuentra ubicado el archivo.

    Cada archivo tendria una estructura similar a la siguiente:

    ```
    |    | phrase                                                                                                                                                                 | target   |
    |---:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
    |  0 | Cardona slowed her vehicle , turned around and returned to the intersection , where she called 911                                                                     | neutral  |
    |  1 | Market data and analytics are derived from primary and secondary research                                                                                              | neutral  |
    |  2 | Exel is headquartered in Mantyharju in Finland                                                                                                                         | neutral  |
    |  3 | Both operating profit and net sales for the three-month period increased , respectively from EUR16 .0 m and EUR139m , as compared to the corresponding quarter in 2006 | positive |
    |  4 | Tampere Science Parks is a Finnish company that owns , leases and builds office properties and it specialises in facilities for technology-oriented businesses         | neutral  |
    ```


    """
# pylint: disable=import-outside-toplevel
# pylint: disable=line-too-long
# flake8: noqa
"""
Laboratorio 4 - Ingestión de texto en directorios

Objetivo:
Leer archivos de texto desde carpetas organizadas por sentimiento
y crear dos datasets CSV: train_dataset.csv y test_dataset.csv
"""

from pathlib import Path
import zipfile
import pandas as pd

def pregunta_01():
    repo_root = Path(__file__).resolve().parent.parent
    files_dir = repo_root / "files"
    zip_path = files_dir / "input.zip"
    input_dir = files_dir / "input"
    output_dir = files_dir / "output"

    # Extraer ZIP si la carpeta input no existe y el ZIP sí existe
    if not input_dir.exists() and zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(files_dir)

    # Si aún no existe input_dir, intentar localizar una carpeta 'input' en el repo
    if not input_dir.exists():
        candidates = list(repo_root.rglob("input"))
        input_dir = candidates[0] if candidates else input_dir

    # Si no existe, buscar padre que contenga 'train' y 'test'
    if not input_dir.exists():
        found = None
        for d in repo_root.rglob("*"):
            if not d.is_dir():
                continue
            try:
                names = {p.name for p in d.iterdir() if p.is_dir()}
            except Exception:
                continue
            if {"train", "test"}.issubset(names):
                found = d
                break
        if found:
            input_dir = found

    # Si finalmente no existe, lanzar error claro
    if not input_dir.exists():
        raise FileNotFoundError(
            "No se encontró 'files/input' ni 'files/input.zip'. Coloca input.zip en files/ o la carpeta input/ descomprimida."
        )

    # Función para construir dataset (train o test)
    def build_dataset(split: str) -> pd.DataFrame:
        split_dir = input_dir / split

        # intentar localizar si no está exactamente ahí
        if not split_dir.exists():
            alt = None
            for cand in input_dir.rglob(split):
                if cand.is_dir():
                    alt = cand
                    break
            if alt:
                split_dir = alt

        rows = []
        if not split_dir.exists():
            return pd.DataFrame(columns=["phrase", "target"])

        # recorrer las carpetas de sentimiento en orden alfabético (determinista)
        for sentiment_dir in sorted([p for p in split_dir.iterdir() if p.is_dir()], key=lambda p: p.name):
            target = sentiment_dir.name
            # leer archivos .txt en orden
            for txt in sorted(sentiment_dir.glob("*.txt"), key=lambda p: p.name):
                try:
                    text = txt.read_text(encoding="utf-8")
                except Exception:
                    text = txt.read_text(encoding="latin-1", errors="ignore")
                rows.append({"phrase": text.strip(), "target": target})

        return pd.DataFrame(rows, columns=["phrase", "target"])

    # Construir y guardar datasets
    train_df = build_dataset("train")
    test_df = build_dataset("test")

    output_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(output_dir / "train_dataset.csv", index=False)
    test_df.to_csv(output_dir / "test_dataset.csv", index=False)

    return