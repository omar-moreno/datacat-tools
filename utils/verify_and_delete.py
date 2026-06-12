#!/usr/bin/env python3

import click
import polars as pl

import hashlib

from pathlib import Path

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


@click.command()
@click.option('--manifest', '-m', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help="List of files that have been transferred.")
@click.option('--prefix', '-p', required=True, type=str, 
              help="Prefix of location where files originally existed.")
@click.option('--verbose', '-v', is_flag=True, default=False,
              help="Enable verbose output for debugging.")
def verify_and_delete(manifest: str, prefix: str, verbose: bool):
    """
    """
    manifest_df = pl.read_csv(
        manifest, 
        has_header=True,
        ignore_errors=False,
    )

    file_deletion_count = 0

    click.echo(f"Total number of files that have been transferred: {manifest_df.height}")

    for row in manifest_df.iter_rows(named=True):
        if row['status'] == 'UNREGISTERED':
            continue

        file_path = prefix + row['catalog_path']
        path = Path(file_path)
        if not path.exists():
            if verbose:
                click.echo(click.style(f"⚠️ {file_path} has already been deleted.", fg="yellow", bold=True))
            #continue
    
        checksum = calculate_sha256(file_path)
        if checksum != row['checksum']:
            click.echo(click.style(f"❌ The checksums do not match: {checksum} vs {row['checksum']}", fg="red"))
            #continue

        if path.is_file():
            click.echo(click.style("✅ {row['catalog_path']} has been succesfully transferred, deleting.", fg="green", bold=True))
            file_deletion_count += 1
            #path.unlink()

    click.echo("\n" + "=" * 60)
    click.echo(click.style("SUMMARY", fg="cyan", bold=True))
    click.echo("=" * 60)
    click.echo(f"Total Files Transffered:     {manifest_df.height}")
    click.echo(f"Total Files Deleted:    {file_deletion_count}")

if __name__ == "__main__":
    verify_and_delete()
