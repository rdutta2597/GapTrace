from pathlib import Path

import typer

from gaptrace.analyzer import GapAnalyzer
from gaptrace.coverage import parse_lcov_and_merge
from gaptrace.llm import MockLLMClient, OpenAIClient
from gaptrace.parser import ASTParser
from gaptrace.scanner import scan_project

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
def analyze(
    src: str = typer.Option(..., "--src", help="Path to C/C++ source file to analyze"),
    coverage: str = typer.Option(..., "--coverage", help="Path to lcov .info coverage file"),
    output: str = typer.Option(None, "--output", help="Output file for JSON results (optional)"),
    use_openai: bool = typer.Option(False, "--openai", help="Use OpenAI API for scenario descriptions (requires OPENAI_API_KEY)"),
):
    """Analyze C/C++ file and find missing test scenarios (Phase 2)"""
    
    try:
        # Parse the source file
        typer.echo("🔍 Phase 1: Parsing source code...")
        parser = ASTParser()
        result = parser.parse_file(src)
        
        # Apply coverage
        typer.echo("📊 Phase 1: Loading coverage data...")
        parse_lcov_and_merge(coverage, result)
        
        # Analyze gaps
        typer.echo("⚙️  Phase 2: Analyzing test gaps...")
        analyzer = GapAnalyzer()
        gaps = analyzer.analyze(result)
        
        # Get LLM client for scenario descriptions
        if use_openai:
            typer.echo("🤖 Connecting to OpenAI API...")
            llm_client = OpenAIClient()
        else:
            typer.echo("📝 Using mock LLM (install OpenAI with --openai flag for real descriptions)")
            llm_client = MockLLMClient()
        
        # Display results
        typer.echo("")
        typer.echo("=" * 60)
        typer.echo("📄 GapTrace Analysis Report")
        typer.echo("=" * 60)
        typer.echo(f"File: {src}")
        typer.echo(f"Functions: {len(result.functions)}")
        typer.echo(f"Decision Points: {result.total_decision_points}")
        typer.echo(f"Coverage: {result.coverage_percentage():.1f}%")
        typer.echo("")
        
        # Display gap summary
        summary = analyzer.gap_summary()
        typer.echo(f"📈 Gap Summary:")
        typer.echo(f"  Total Gaps: {summary['total']}")
        typer.echo(f"  🔴 Critical: {summary['critical']}")
        typer.echo(f"  🟠 High: {summary['high']}")
        typer.echo(f"  🟡 Medium: {summary['medium']}")
        typer.echo(f"  🔵 Low: {summary['low']}")
        typer.echo("")
        
        # Display critical gaps with descriptions
        if gaps:
            typer.echo("🎯 Missing Test Scenarios:")
            typer.echo("")
            for gap in gaps[:10]:  # Show top 10
                # Get AI description
                scenario = llm_client.describe_gap(
                    gap.function_name,
                    gap.decision_type,
                    gap.line_number
                )
                
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                }.get(gap.severity, "⚪")
                
                typer.echo(f"{severity_icon} {gap.function_name}() - Line {gap.line_number}")
                typer.echo(f"   Type: {gap.decision_type}")
                typer.echo(f"   Scenario: {scenario}")
                typer.echo("")
            
            if len(gaps) > 10:
                typer.echo(f"... and {len(gaps) - 10} more gaps")
        else:
            typer.echo("✅ No gaps found! Code coverage is complete.")
        
        # Export to JSON if requested
        if output:
            import json
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                "file": src,
                "coverage_percentage": result.coverage_percentage(),
                "total_functions": len(result.functions),
                "total_decision_points": result.total_decision_points,
                "gaps": [
                    {
                        "function": gap.function_name,
                        "line": gap.line_number,
                        "type": gap.decision_type,
                        "severity": gap.severity,
                        "scenario": gap.description,
                    }
                    for gap in gaps
                ],
                "gap_summary": summary,
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            typer.echo(f"✅ Results exported to: {output}")
        
    except FileNotFoundError as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"❌ Configuration Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Analysis failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    typer.echo("GapTrace version 0.2.0 (Phase 1-2)")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()