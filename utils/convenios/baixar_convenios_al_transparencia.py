from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, cli_default


BASE_URL = "https://transparencia.al.gov.br/convenio"
LEGACY_ZIP_URL = "https://transparencia.al.gov.br/media/arquivo/convenio-{year}.zip"
DEFAULT_START_YEAR = 1990
DEFAULT_LIMIT = 500
REQUEST_TIMEOUT = (10, 45)
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://transparencia.al.gov.br/convenio/convenios-por-beneficiados/",
}


def parse_args() -> argparse.Namespace:
    no_args = len(sys.argv) == 1
    parser = argparse.ArgumentParser(
        description="Baixa os endpoints de convenios do Portal da Transparencia de Alagoas."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_DIR / "AL" / "portal_transparencia_json"),
        help="Diretorio de saida dos JSONs baixados.",
    )
    parser.add_argument(
        "--legacy-dir",
        default=cli_default(BASES_CONVENIOS_DIR / "AL" / "convenios"),
        help="Diretorio de saida dos ZIPs legados convenio-AAAA.zip.",
    )
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument("--end-year", type=int, default=datetime.now().year)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--sleep", type=float, default=0.25, help="Pausa entre requisicoes.")
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--force", action="store_true", help="Rebaixa arquivos ja existentes.")
    parser.add_argument(
        "--status",
        action="store_true",
        default=no_args,
        help="Mostra o que ja foi baixado sem chamar a rede. Padrao quando o script roda sem argumentos.",
    )
    parser.add_argument("--details-only", action="store_true", help="Usa os agregados ja salvos e baixa apenas detalhes.")
    parser.add_argument("--skip-details", action="store_true", help="Baixa apenas agregados por concedente/beneficiado.")
    parser.add_argument("--skip-legacy-zip", action="store_true", help="Nao tenta baixar os ZIPs anuais legados.")
    return parser.parse_args()


def request_json(
    session: requests.Session,
    path: str,
    params: dict[str, Any],
    retries: int,
    sleep_seconds: float,
) -> dict[str, Any]:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001 - coleta deve registrar e tentar novamente.
            last_error = exc
            wait = sleep_seconds * attempt * 4
            print(f"[aviso] tentativa {attempt}/{retries} falhou em {url}: {exc}")
            time.sleep(wait)
    raise RuntimeError(f"Falha apos {retries} tentativas em {url}") from last_error


def fetch_paginated(
    session: requests.Session,
    path: str,
    date_params: dict[str, str],
    limit: int,
    retries: int,
    sleep_seconds: float,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    detalhe: dict[str, Any] = {}
    titulo = ""
    total: int | None = None
    offset = 0

    while True:
        params = {**date_params, "limit": limit, "offset": offset}
        payload = request_json(session, path, params, retries, sleep_seconds)
        page_rows = payload.get("rows") or []
        if not isinstance(page_rows, list):
            raise ValueError(f"Resposta sem lista em rows para {path}: {type(page_rows).__name__}")

        if total is None:
            total = int(payload.get("total") or len(page_rows))
            detalhe = payload.get("detalhe") or {}
            titulo = payload.get("titulo") or ""

        rows.extend(page_rows)
        offset += limit
        time.sleep(sleep_seconds)

        if not page_rows or len(rows) >= total:
            break

    return {"titulo": titulo, "total": total or 0, "detalhe": detalhe, "rows": rows}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def yearly_date_params(year: int) -> dict[str, str]:
    return {"data_inicio_dti_": f"01/01/{year}", "data_inicio_dtf_": f"31/12/{year}"}


def save_dataset(year_dir: Path, stem: str, payload: dict[str, Any], metadata: dict[str, Any]) -> None:
    envelope = {**metadata, **{key: value for key, value in payload.items() if key != "rows"}}
    write_json(year_dir / f"{stem}.json", {**envelope, "rows": payload["rows"]})
    write_jsonl(year_dir / f"{stem}.jsonl", payload["rows"])


def read_saved_rows(year_dir: Path, stem: str) -> list[dict[str, Any]]:
    path = year_dir / f"{stem}.json"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo agregado nao encontrado: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise ValueError(f"Arquivo sem lista rows: {path}")
    return rows


def count_jsonl_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def local_year_status(output_dir: Path, legacy_dir: Path, year: int) -> dict[str, Any]:
    year_dir = output_dir / str(year)
    summary_path = year_dir / "summary.json"
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

    zip_path = legacy_dir / str(year) / f"convenio-{year}.zip"
    txt_dir = legacy_dir / str(year) / "extraidos"
    return {
        "ano": year,
        "summary": summary_path.exists(),
        "concedentes": int(summary.get("concedentes_rows") or count_jsonl_rows(year_dir / "concedentes.jsonl")),
        "beneficiados": int(summary.get("beneficiados_rows") or count_jsonl_rows(year_dir / "beneficiados.jsonl")),
        "beneficiarios": int(
            summary.get("beneficiarios_por_concedente_rows")
            or count_jsonl_rows(year_dir / "beneficiarios_por_concedente.jsonl")
        ),
        "detalhes": int(summary.get("detalhes_rows") or count_jsonl_rows(year_dir / "detalhes.jsonl")),
        "erros": len(summary.get("errors") or []),
        "zip": zip_path.exists(),
        "txts": len(list(txt_dir.glob("*.txt"))) if txt_dir.exists() else 0,
    }


def print_status(output_dir: Path, legacy_dir: Path, years: list[int]) -> None:
    statuses = [local_year_status(output_dir, legacy_dir, year) for year in years]
    print("ano  summary  concedentes  beneficiados  beneficiarios  detalhes  erros  zip  txts")
    for status in statuses:
        print(
            "{ano:<4} {summary:<7} {concedentes:<11} {beneficiados:<12} "
            "{beneficiarios:<13} {detalhes:<8} {erros:<5} {zip:<4} {txts}".format(**status)
        )

    missing_summary = [str(item["ano"]) for item in statuses if not item["summary"]]
    missing_details = [
        str(item["ano"])
        for item in statuses
        if item["beneficiados"] and not item["detalhes"] and item["erros"]
    ]
    if missing_summary:
        print(f"\nAnos sem summary local: {', '.join(missing_summary)}")
    if missing_details:
        print(f"Anos com agregados mas sem detalhes por falha anterior: {', '.join(missing_details)}")


def download_legacy_zip(
    session: requests.Session,
    legacy_dir: Path,
    year: int,
    force: bool,
    retries: int,
    sleep_seconds: float,
) -> dict[str, Any]:
    year_dir = legacy_dir / str(year)
    extract_dir = year_dir / "extraidos"
    zip_path = year_dir / f"convenio-{year}.zip"
    if zip_path.exists() and not force:
        return {"year": year, "status": "exists", "path": str(zip_path)}

    year_dir.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    url = LEGACY_ZIP_URL.format(year=year)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, stream=True, timeout=REQUEST_TIMEOUT)
            if response.status_code == 404:
                return {"year": year, "status": "not_found", "url": url}
            response.raise_for_status()
            with zip_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        handle.write(chunk)
            try:
                with zipfile.ZipFile(zip_path) as zip_ref:
                    zip_ref.extractall(extract_dir)
                return {"year": year, "status": "downloaded", "path": str(zip_path)}
            except zipfile.BadZipFile as exc:
                zip_path.unlink(missing_ok=True)
                return {"year": year, "status": "bad_zip", "url": url, "error": str(exc)}
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"[aviso] ZIP {year} tentativa {attempt}/{retries} falhou: {exc}")
            time.sleep(sleep_seconds * attempt * 4)
    return {"year": year, "status": "error", "url": url, "error": str(last_error)}


def collect_year(
    session: requests.Session,
    output_dir: Path,
    year: int,
    limit: int,
    retries: int,
    sleep_seconds: float,
    skip_details: bool,
    force: bool,
    details_only: bool,
) -> dict[str, Any]:
    year_dir = output_dir / str(year)
    summary_path = year_dir / "summary.json"
    if summary_path.exists() and not force and not details_only:
        return json.loads(summary_path.read_text(encoding="utf-8"))

    captured_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "fonte": BASE_URL,
        "ano": year,
        "data_inicio": f"01/01/{year}",
        "data_fim": f"31/12/{year}",
        "capturado_em_utc": captured_at,
    }
    date_params = yearly_date_params(year)
    errors: list[dict[str, str]] = []

    if details_only:
        print(f"[AL] {year}: reutilizando agregados salvos")
        concedente_rows = read_saved_rows(year_dir, "concedentes")
        beneficiado_rows = read_saved_rows(year_dir, "beneficiados")
        concedentes = {"titulo": "", "total": len(concedente_rows), "detalhe": {}, "rows": concedente_rows}
        beneficiados = {"titulo": "", "total": len(beneficiado_rows), "detalhe": {}, "rows": beneficiado_rows}
    else:
        print(f"[AL] {year}: baixando agregados", flush=True)
        concedentes = fetch_paginated(
            session, "json-convenios-entidades/", date_params, limit, retries, sleep_seconds
        )
        beneficiados = fetch_paginated(
            session, "json-convenios-beneficiados/", date_params, limit, retries, sleep_seconds
        )
        save_dataset(year_dir, "concedentes", concedentes, metadata)
        save_dataset(year_dir, "beneficiados", beneficiados, metadata)

    beneficiarios_rows: list[dict[str, Any]] = []
    detalhes_rows: list[dict[str, Any]] = []

    if not skip_details and concedentes["rows"]:
        print(f"[AL] {year}: baixando detalhes de {len(concedentes['rows'])} concedentes", flush=True)
        for concedente in concedentes["rows"]:
            concedente_id = str(concedente.get("concedente") or "").strip()
            if not concedente_id:
                continue
            try:
                beneficiarios = fetch_paginated(
                    session,
                    f"json-convenios-entidades-beneficiado/{concedente_id}/",
                    date_params,
                    limit,
                    retries,
                    sleep_seconds,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append({"endpoint": "beneficiarios_por_concedente", "id": concedente_id, "error": str(exc)})
                continue

            for beneficiario in beneficiarios["rows"]:
                enriched_beneficiario = {
                    **concedente,
                    **beneficiario,
                    "concedente": concedente_id,
                    "ano_referencia": year,
                }
                beneficiarios_rows.append(enriched_beneficiario)
                beneficiado_id = str(beneficiario.get("beneficiado") or "").strip()
                if not beneficiado_id:
                    continue
                try:
                    detalhes = fetch_paginated(
                        session,
                        f"json-convenios-entidades-detalhes/{concedente_id}/{beneficiado_id}/",
                        date_params,
                        limit,
                        retries,
                        sleep_seconds,
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(
                        {
                            "endpoint": "detalhes",
                            "concedente": concedente_id,
                            "beneficiado": beneficiado_id,
                            "error": str(exc),
                        }
                    )
                    continue
                for detalhe in detalhes["rows"]:
                    detalhes_rows.append(
                        {
                            **concedente,
                            **beneficiario,
                            **detalhe,
                            "concedente": concedente_id,
                            "beneficiado": beneficiado_id,
                            "ano_referencia": year,
                        }
                    )
            write_jsonl(year_dir / "beneficiarios_por_concedente.jsonl", beneficiarios_rows)
            write_json(year_dir / "beneficiarios_por_concedente.json", {**metadata, "rows": beneficiarios_rows})
            write_jsonl(year_dir / "detalhes.jsonl", detalhes_rows)
            write_json(year_dir / "detalhes.json", {**metadata, "rows": detalhes_rows})
            print(
                f"[AL] {year}: concedente {concedente_id} concluido; "
                f"beneficiarios={len(beneficiarios_rows)} detalhes={len(detalhes_rows)} erros={len(errors)}",
                flush=True,
            )

    if not skip_details:
        write_jsonl(year_dir / "beneficiarios_por_concedente.jsonl", beneficiarios_rows)
        write_json(year_dir / "beneficiarios_por_concedente.json", {**metadata, "rows": beneficiarios_rows})
        write_jsonl(year_dir / "detalhes.jsonl", detalhes_rows)
        write_json(year_dir / "detalhes.json", {**metadata, "rows": detalhes_rows})

    summary = {
        **metadata,
        "concedentes_rows": len(concedentes["rows"]),
        "concedentes_total": concedentes["total"],
        "beneficiados_rows": len(beneficiados["rows"]),
        "beneficiados_total": beneficiados["total"],
        "beneficiarios_por_concedente_rows": len(beneficiarios_rows),
        "detalhes_rows": len(detalhes_rows),
        "errors": errors,
    }
    write_json(summary_path, summary)
    return summary


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    legacy_dir = Path(args.legacy_dir)
    session = requests.Session()
    session.headers.update(HEADERS)

    years = list(range(args.start_year, args.end_year + 1))
    if args.status:
        print_status(output_dir, legacy_dir, years)
        return

    run_summary = {
        "capturado_em_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "legacy_dir": str(legacy_dir),
        "years": years,
        "json": [],
        "legacy_zip": [],
    }

    for year in years:
        try:
            summary = collect_year(
                session=session,
                output_dir=output_dir,
                year=year,
                limit=args.limit,
                retries=args.retries,
                sleep_seconds=args.sleep,
                skip_details=args.skip_details,
                force=args.force,
                details_only=args.details_only,
            )
            run_summary["json"].append(summary)
            print(
                "[AL] {year}: concedentes={concedentes} beneficiados={beneficiados} detalhes={detalhes}".format(
                    year=year,
                    concedentes=summary["concedentes_rows"],
                    beneficiados=summary["beneficiados_rows"],
                    detalhes=summary["detalhes_rows"],
                )
            )
        except Exception as exc:  # noqa: BLE001
            run_summary["json"].append({"ano": year, "status": "error", "error": str(exc)})
            print(f"[erro] {year}: {exc}", flush=True)

        if not args.skip_legacy_zip and year >= 2000:
            zip_summary = download_legacy_zip(
                session=session,
                legacy_dir=legacy_dir,
                year=year,
                force=args.force,
                retries=args.retries,
                sleep_seconds=args.sleep,
            )
            run_summary["legacy_zip"].append(zip_summary)
            print(f"[AL] {year}: ZIP legado {zip_summary['status']}", flush=True)

    write_json(output_dir / "run_summary.json", run_summary)
    print(f"Resumo salvo em: {output_dir / 'run_summary.json'}")


if __name__ == "__main__":
    main()
