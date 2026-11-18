import json

import resumir_mediciones


def test_sin_mediciones(tmp_path, monkeypatch, capsys):
    resumen = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(resumen))
    monkeypatch.setattr(
        resumir_mediciones.sys,
        "argv",
        ["resumir_mediciones.py", str(tmp_path / "no-existe")],
    )
    assert resumir_mediciones.main() == 0
    texto = resumen.read_text(encoding="utf-8")
    assert "No hubo mediciones" in texto
    assert "No hubo mediciones" in capsys.readouterr().out


def test_tabla(tmp_path, monkeypatch):
    mediciones = tmp_path / "mediciones"
    mediciones.mkdir()
    (mediciones / "medicion-b.json").write_text(
        json.dumps(
            {
                "variante": "b",
                "dockerfile": "Dockerfile.b",
                "cache": "sin caché",
                "segundos": 2,
                "mib": 1.5,
                "bytes": 10,
            }
        ),
        encoding="utf-8",
    )
    (mediciones / "medicion-a.json").write_text(
        json.dumps(
            {
                "variante": "a",
                "dockerfile": "Dockerfile.a",
                "cache": "sin caché",
                "segundos": 3.2,
                "mib": 4,
                "bytes": 20,
            }
        ),
        encoding="utf-8",
    )
    resumen = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(resumen))
    monkeypatch.setattr(
        resumir_mediciones.sys,
        "argv",
        ["resumir_mediciones.py", str(mediciones)],
    )
    assert resumir_mediciones.main() == 0
    texto = resumen.read_text(encoding="utf-8")
    assert texto.index("| a |") < texto.index("| b |")
    assert "3.20" in texto
    assert "Dockerfile.a" in texto
