#!/usr/bin/env python3

import click

import os
import sys
import csv
import hashlib
from pathlib import Path
from typing import Generator, List, Dict, Any
from datetime import datetime

from pathlib import Path
from typing import Generator

from CDMSDataCatalog import CDMSDataCatalog

def normalize_path(path: str) -> str:
    """Normalize a path to ensure it starts with '/CDMS/' and has no trailing slashes.

    This function enforces the CDMS datacat's strict path requirements:
    1. Empty or whitespace-only paths are converted to the default root '/CDMS'.
    2. Relative paths are made absolute.
    3. The '/CDMS/' prefix is enforced.
    4. Trailing slashes are stripped.

    Parameters
    ----------
    path : str
        The input path string. Can be absolute (e.g., '/CDMS/Raw') or relative
        (e.g., 'Raw/Run1'). Leading and trailing whitespace is ignored.

    Returns
    -------
    str
        The normalized path string. Guaranteed to start with '/CDMS' and not
        end with a slash (unless the path is exactly '/CDMS').

    Examples
    --------
    >>> normalize_path("")
    '/CDMS'

    >>> normalize_path("/")
    '/CDMS'

    >>> normalize_path("/CDMS/Raw/Run1/")
    '/CDMS/Raw/Run1'

    >>> normalize_path("/CUTE/Raw")
    '/CDMS/CUTE/Raw'

    >>> normalize_path("  /CDMS/Data/  ")
    '/CDMS/Data'

    >>> normalize_path("//Raw//Run1//")
    '/CDMS/Raw/Run1'

    """
    # Strip whitespace and handle empty/whitespace-only strings
    path = (path or "").strip()

    # If the path is empty, return "/CDMS" as a default
    if not path:
        return "/CDMS"

    # Ensure it starts with a single slash
    path = "/" + path.lstrip("/")

    # Enforce /CDMS prefix
    if not path.startswith("/CDMS"):
        path = "/CDMS" + "/" + path.lstrip("/")

    return path.rstrip("/")

def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    chunk_size = 1024*1024
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "ERROR_CALCULATING"

def scan_local_files(directory_path: Path, recursive: bool) -> Generator[str, None, None]:
    """
    Scan a local directory and yield all file paths.
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    if recursive:
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                yield str(file_path.absolute())
    else:
        for item in directory_path.iterdir():
            if item.is_file():
                yield str(item.absolute())

def generate_html_report(results: List[Dict[str, Any]], stats: Dict[str, int], output_path: str):
    """Generate a DARK-THEMED HTML report with Interactive Sorting."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Dark Theme Status Colors
    def get_status_color(status: str) -> str:
        if status == "VERIFIED": return "#00ff9d"
        if status == "MISSING": return "#ff4d4d"
        if status == "ERROR": return "#ff6b6b"
        return "#a0a0a0"

    # Define sort priority for Status (Verified first, then errors)
    status_priority = {
        "VERIFIED": 1,
        "MISSING": 2,
        "ERROR": 3
    }

    rows_html = ""
    for r in results:
        color = get_status_color(r['status'])
        file_display = r['file_path'] 
        cat_display = r['catalog_path']
        
        rows_html += f"""
        <tr>
            <td title="{r['file_path']}">{file_display}</td>
            <td title="{r['catalog_path']}">{cat_display}</td>
            <td style="color: {color}; font-weight: bold; text-transform: uppercase;" data-sort="{status_priority.get(r['status'], 99)}">{r['status']}</td>
            <td style="font-family: monospace; color: #d1d1d1;">{r['checksum'] or 'N/A'}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CDMS Verification Report (Dark Mode)</title>
        <style>
            :root {{
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --text-main: #e0e0e0;
                --text-muted: #a0a0a0;
                --border-color: #333333;
                --accent-blue: #2196f3;
                --neon-green: #00ff9d;
                --bright-red: #ff4d4d;
                --amber: #ffcc00;
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: var(--bg-color); 
                color: var(--text-main); 
            }}
            
            h1 {{ 
                color: var(--text-main); 
                border-bottom: 2px solid var(--accent-blue);
                padding-bottom: 10px;
            }}
            
            .container {{
                margin: 0 auto;
            }}

            .summary {{ 
                background: var(--card-bg); 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
                margin-bottom: 25px; 
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                border: 1px solid var(--border-color);
            }}
            
            .summary-item {{ 
                display: flex;
                flex-direction: column;
                min-width: 120px;
            }}
            
            .summary-label {{ 
                font-size: 0.85em; 
                color: var(--text-muted); 
                text-transform: uppercase; 
                letter-spacing: 1px;
            }}
            
            .summary-value {{ 
                font-size: 1.4em; 
                font-weight: bold; 
                margin-top: 5px;
            }}

            .table-wrapper {{
                overflow-x: auto;
                background: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                border: 1px solid var(--border-color);
            }}

            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                font-size: 0.95em;
            }}
            
            th, td {{ 
                padding: 14px 16px; 
                text-align: left; 
                border-bottom: 1px solid var(--border-color); 
            }}
            
            th {{ 
                background-color: #2c2c2c; 
                color: var(--accent-blue); 
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85em;
                letter-spacing: 0.5px;
                position: sticky;
                top: 0;
                cursor: pointer;
                user-select: none;
                transition: background-color 0.2s;
            }}
            
            th:hover {{
                background-color: #3a3a3a;
            }}

            th.sorted-asc::after {{ content: " ▲"; font-size: 0.8em; }}
            th.sorted-desc::after {{ content: " ▼"; font-size: 0.8em; }}
            
            tr:hover {{ 
                background-color: #2a2a2a; 
            }}
            
            td {{
                color: var(--text-main);
            }}

            .footer {{ 
                margin-top: 30px; 
                font-size: 0.85em; 
                color: var(--text-muted); 
                text-align: center;
                border-top: 1px solid var(--border-color);
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CDMS Data Catalog Verification Report</h1>
            
            <div class="summary">
                <div class="summary-item">
                    <span class="summary-label">Generated</span>
                    <span class="summary-value">{timestamp}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Total Files</span>
                    <span class="summary-value">{stats['total']}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Verified</span>
                    <span class="summary-value" style="color: var(--neon-green);">{stats['registered']}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Missing</span>
                    <span class="summary-value" style="color: var(--bright-red);">{stats['unregistered']}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Errors</span>
                    <span class="summary-value" style="color: var(--bright-red);">{stats['errors']}</span>
                </div>
            </div>
            
            <div class="table-wrapper">
                <table id="reportTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Local File Path</th>
                            <th onclick="sortTable(1)">Catalog Path</th>
                            <th onclick="sortTable(2)">Status</th>
                            <th onclick="sortTable(3)">Checksum</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                Generated by CDMS Verification Script • Dark Mode • Click headers to sort
            </div>
        </div>

        <script>
            function sortTable(n) {{
                var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                table = document.getElementById("reportTable");
                switching = true;
                dir = "asc"; 
                
                // Remove existing sort indicators
                var headers = table.getElementsByTagName("th");
                for (var i = 0; i < headers.length; i++) {{
                    headers[i].classList.remove("sorted-asc", "sorted-desc");
                }}

                while (switching) {{
                    switching = false;
                    rows = table.rows;
                    
                    for (i = 1; i < (rows.length - 1); i++) {{
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        
                        // Special handling for Status column (index 2) to use data-sort attribute
                        if (n === 2) {{
                            var xVal = parseInt(x.getAttribute("data-sort"));
                            var yVal = parseInt(y.getAttribute("data-sort"));
                            
                            if (dir == "asc") {{
                                if (xVal > yVal) {{ shouldSwitch = true; break; }}
                            }} else {{
                                if (xVal < yVal) {{ shouldSwitch = true; break; }}
                            }}
                        }} else {{
                            // Standard string comparison for other columns
                            var xContent = x.innerHTML.toLowerCase();
                            var yContent = y.innerHTML.toLowerCase();
                            
                            if (dir == "asc") {{
                                if (xContent > yContent) {{ shouldSwitch = true; break; }}
                            }} else {{
                                if (xContent < yContent) {{ shouldSwitch = true; break; }}
                            }}
                        }}
                    }}
                    
                    if (shouldSwitch) {{
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount ++;      
                    }} else {{
                        if (switchcount == 0 && dir == "asc") {{
                            dir = "desc";
                            switching = true;
                        }}
                    }}
                }}
                
                // Add sort indicator to clicked header
                headers[n].classList.add(dir == "asc" ? "sorted-asc" : "sorted-desc");
            }}
        </script>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_csv_report(results: List[Dict[str, Any]], output_path: str):
    """Generate a CSV report."""
    fieldnames = ['file_path', 'catalog_path', 'status', 'checksum']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    click.echo(f"CSV report saved to: {output_path}")


def extract_catalog_path(local_path : Path) -> str:
    # Covert parts to a list
    parts = local_path.parts

    try: 
        # Find the index of 'CDMS' in the path parts
        index = parts.index('CDMS')

        # Slice from 'CDMS' to the end
        extracted_path = parts[index:]

        # Reconstruct the path string
        extracted_path = "/".join(extracted_path)

        return normalize_path(extracted_path)

    except ValueError:
        return None

def get_datasets(dc : CDMSDataCatalog, path: str = "/CDMS", site: str = "All"):
    try:
        # query = "scanStatus = 'UNSCANNED' or scanStatus = 'MISSING'"
        # First retrieve all dataset within the top level directory of the
        # given path.
        datasets = dc.client.search(path, site=site)
        # This retrieves recursively retrieves the datasets of all
        # containers in the path.
        datasets.extend(
            dc.client.search(path + "**", site=site)
        )
    except datacat.error.DcClientException as err:
        logging.error("%s: %s", err, path)
        return []
    except requests.exceptions.HTTPError as err:
        logging.error("HTTPError %s" % err)
        return []

    return datasets

@click.command()
@click.option('--local-dir', '-d', required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help="Local directory containing the files to verify.")
@click.option('--site', '-s', default="SLAC", type=str,
              help="Target site to verify against (default: SLAC).")
@click.option('--recursive/--no-recursive', '-r/-nr', default=True,
              help="Scan subdirectories recursively (default: True).")
@click.option('--output-dir', '-o', default=".", type=click.Path(file_okay=False, dir_okay=True),
              help="Directory to save CSV and HTML reports (default: current directory).")
@click.option('--verbose', '-v', is_flag=True, default=False,
              help="Enable verbose output for debugging.")
def verify_catalog_registration(local_dir: str, site: str, recursive: bool, output_dir: str, verbose: bool):
    """
    Verify that local files are correctly registered in the CDMS Data Catalog.
    Generates CSV and HTML reports.
    """
    
    # Ensure output directory exists
    output_path_obj = Path(output_dir)
    output_path_obj.mkdir(parents=True, exist_ok=True)
    
    # Initialize Catalog
    try:
        catalog = CDMSDataCatalog()
        if verbose:
            click.echo(click.style("✓ CDMSDataCatalog initialized successfully.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Error initializing CDMSDataCatalog: {e}", fg="red"))
        sys.exit(1)

    local_path_obj = Path(local_dir)
    catalog_path = extract_catalog_path(local_path_obj)

    click.echo(click.style("Starting verification...", fg="cyan"))
    click.echo(f"  Local Directory : {local_dir}")
    click.echo(f"  Catalog Prefix  : {catalog_path}")
    click.echo(f"  Target Site     : {site}")
    click.echo(f"  Output Dir      : {output_dir}")
    click.echo("-" * 60)

    # Collect files
    try:
        local_files = list(scan_local_files(local_path_obj, recursive))
    except (FileNotFoundError, NotADirectoryError) as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        sys.exit(1)

    if not local_files:
        click.echo(click.style("No files found in the specified directory.", fg="yellow"))
        sys.exit(0)

    click.echo(f"Found {len(local_files)} local files. Checking catalog registration...\n")

    datasets = get_datasets(catalog, catalog_path, site=site)
    dataset_paths = [dataset.path for dataset in datasets]
    click.echo(f"Found {len(dataset_paths)} datasets registered in the catalog.")

    stats = {
        "total": 0,
        "registered": 0,
        "unregistered": 0,
        "errors": 0
    }
    
    results = []

    for local_file in local_files:
        stats["total"] += 1
        
        local_path_obj_file = Path(local_file)
        expected_catalog_path = normalize_path(extract_catalog_path(local_path_obj_file))
            
        if verbose:
            click.echo(f"Checking: {local_file} -> {expected_catalog_path}")

        # Initialize result row
        result_row = {
            "file_path": local_file,
            "catalog_path": expected_catalog_path,
            "status": "",
            "checksum": "",
        }

        # Calculate actual checksum
        result_row["checksum"] = calculate_sha256(local_file)

        if expected_catalog_path in dataset_paths:
            if verbose:
                click.echo(click.style(f"✅ VERIFIED: {local_file}", fg="green"))
            result_row["status"] = "VERIFIED"
            stats["registered"] += 1
            dataset_paths.remove(expected_catalog_path)

        else:
            result_row["status"] = "UNREGISTERED"
            click.echo(click.style(f"UNREGISTERED: {local_file}", fg="yellow"))
            stats["unregistered"] += 1
            #click.echo(click.style(f"❌ NOT REGISTERED: {local_file}", fg="red"))
            
        results.append(result_row)

    click.echo(f"Total files left in catalog {len(dataset_paths)}")

    # Generate Reports
    csv_filename = output_path_obj / "verification_report.csv"
    html_filename = output_path_obj / "verification_report.html"
    
    click.echo("\nGenerating reports...")
    generate_csv_report(results, str(csv_filename))
    generate_html_report(results, stats, str(html_filename))

    # Summary
    click.echo("\n" + "=" * 60)
    click.echo(click.style("VERIFICATION SUMMARY", fg="cyan", bold=True))
    click.echo("=" * 60)
    click.echo(f"Total Files Scanned:     {stats['total']}")
    click.echo(f"Correctly Registered:    {click.style(str(stats['registered']), fg='green')}")
    click.echo(f"Unregistered:            {click.style(str(stats['unregistered']), fg='red')}")
    click.echo(f"Errors:                  {click.style(str(stats['errors']), fg='red')}")
    
    if stats['unregistered'] > 0 or stats['errors'] > 0:
        click.echo("\n" + click.style("⚠️  Discrepancies found. Manual review or re-registration may be needed.", fg="yellow", bold=True))
        sys.exit(1)
    else:
        click.echo("\n" + click.style("✅ All local files are correctly registered in the catalog.", fg="green", bold=True))
        sys.exit(0)

if __name__ == "__main__":
    verify_catalog_registration()
