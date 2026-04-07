import typer
from gaptrace.scanner import scan_project

# Create a Typer instance to enable subcommands
app = typer.Typer(help="GapTrace: Detect missing unit test scenarios in C/C++ code")


@app.command()
def scan(path: str = typer.Argument(".", help="Path to scan for test gaps")):
    """Scan a project for test gaps"""
    typer.echo(f"Scanning project at: {path}")
    scan_project(path)


@app.command()
def version():
    """Show version information"""
    typer.echo("GapTrace version 0.1.0")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()