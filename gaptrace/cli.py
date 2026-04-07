import typer
from pathlib import Path
from gaptrace.scanner import scan_project
from gaptrace.parser import ASTParser
from gaptrace.coverage import parse_lcov_and_merge

# Create a Typer instance to enable subcommands
app = typer.Typer(help="GapTrace: Detect missing unit test scenarios in C/C++ code")


@app.command()
def scan(path: str = typer.Argument(".", help="Path to scan for test gaps")):
    """Scan a project for test gaps"""
    typer.echo(f"Scanning project at: {path}")
    scan_project(path)


@app.command()
def parse(
    src: str = typer.Option(..., "--src", help="Path to C/C++ source file to parse"),
    coverage: str = typer.Option(None, "--coverage", help="Path to lcov .info coverage file (optional)"),
    output: str = typer.Option(None, "--output", help="Output file for JSON results (optional)"),
):
    """Parse C/C++ file and extract decision points with optional coverage mapping"""
    
    try:
        # Parse the source file
        parser = ASTParser()
        result = parser.parse_file(src)
        
        # Apply coverage if provided
        if coverage:
            parse_lcov_and_merge(coverage, result)
            typer.echo(f"✅ Parsed {src} with coverage from {coverage}")
        else:
            typer.echo(f"✅ Parsed {src}")
        
        # Display results
        typer.echo("")
        typer.echo(f"📊 Analysis Results")
        typer.echo(f"  Functions: {len(result.functions)}")
        typer.echo(f"  Decision Points: {result.total_decision_points}")
        typer.echo(f"  Coverage: {result.coverage_percentage():.1f}%")
        
        # Show critical gaps if any
        critical = result.critical_gaps()
        if critical:
            typer.echo("")
            typer.echo(f"⚠️  Critical Gaps (uncovered critical paths):")
            for func_name, gaps in critical.items():
                typer.echo(f"  {func_name}():")
                for gap in gaps:
                    typer.echo(f"    - Line {gap.line_number}: {gap.decision_type.value}")
        
        # Export to JSON if requested
        if output:
            import json
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            typer.echo(f"\n✅ Results exported to: {output}")
        
    except FileNotFoundError as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Parsing failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    typer.echo("GapTrace version 0.1.0")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()