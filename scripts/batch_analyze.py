#!/usr/bin/env python3
"""
Batch Document Analyzer - Automation Script

Demonstrates workflow automation by processing multiple documents
from a directory and generating analysis reports.

Usage:
    python scripts/batch_analyze.py --input ./sample_data --output ./reports

Features:
    - Bulk ingestion of PDF, CSV, and TXT files
    - Automatic AI analysis with cost tracking
    - JSON/CSV report generation
    - Progress tracking and error handling

This script can be scheduled via cron or integrated into CI/CD pipelines.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

# Default API endpoint
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


async def upload_file(client: httpx.AsyncClient, file_path: Path) -> Optional[dict]:
    """Upload a single file to the API."""
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = await client.post(
                f"{API_BASE_URL}/api/missions/upload",
                files=files,
                timeout=30.0
            )
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ❌ Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error uploading {file_path.name}: {e}")
        return None


async def run_analysis(client: httpx.AsyncClient, mission_id: str) -> Optional[dict]:
    """Run AI analysis on a mission."""
    try:
        response = await client.post(
            f"{API_BASE_URL}/api/analysis/{mission_id}",
            timeout=60.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ⚠️ Analysis failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ⚠️ Analysis error: {e}")
        return None


async def process_directory(input_dir: Path, output_dir: Path, skip_analysis: bool = False):
    """Process all supported files in a directory."""
    
    # Supported extensions
    supported_extensions = {".pdf", ".csv", ".txt"}
    
    # Find files
    files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not files:
        print(f"No supported files found in {input_dir}")
        print(f"Supported types: {', '.join(supported_extensions)}")
        return
    
    print(f"\n{'='*60}")
    print(f"CACI Mission Copilot - Batch Processor")
    print(f"{'='*60}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Files to process: {len(files)}")
    print(f"Skip analysis: {skip_analysis}")
    print(f"{'='*60}\n")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Results tracking
    results = {
        "run_timestamp": datetime.now().isoformat(),
        "input_directory": str(input_dir),
        "total_files": len(files),
        "successful_uploads": 0,
        "successful_analyses": 0,
        "failed": 0,
        "missions": []
    }
    
    async with httpx.AsyncClient() as client:
        # Check API connectivity
        try:
            health = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            if health.status_code != 200:
                print("❌ API is not responding. Make sure the backend is running.")
                return
        except Exception:
            print(f"❌ Cannot connect to API at {API_BASE_URL}")
            print("   Start the backend with: cd backend && uvicorn main:app --reload")
            return
        
        print("✅ Connected to API\n")
        
        # Process each file
        for i, file_path in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Processing: {file_path.name}")
            
            # Upload file
            mission = await upload_file(client, file_path)
            
            if mission:
                results["successful_uploads"] += 1
                mission_data = {
                    "filename": file_path.name,
                    "mission_id": mission["mission_id"],
                    "source_type": mission["source_type"],
                    "status": mission["status"],
                    "analysis": None
                }
                
                # Run analysis if not skipped
                if not skip_analysis:
                    print(f"  🔄 Running AI analysis...")
                    analysis = await run_analysis(client, mission["mission_id"])
                    
                    if analysis:
                        results["successful_analyses"] += 1
                        mission_data["analysis"] = {
                            "risk_level": analysis.get("risk_level"),
                            "summary": analysis.get("summary_text", "")[:200],
                            "total_tokens": analysis.get("total_tokens"),
                            "estimated_cost": analysis.get("estimated_cost")
                        }
                        print(f"  ✅ Analyzed - Risk: {analysis.get('risk_level', 'N/A')}")
                    else:
                        print(f"  ⚠️ Analysis skipped or failed")
                else:
                    print(f"  ✅ Uploaded (analysis skipped)")
                
                results["missions"].append(mission_data)
            else:
                results["failed"] += 1
            
            print()
    
    # Generate reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON report
    json_report = output_dir / f"batch_report_{timestamp}.json"
    with open(json_report, "w") as f:
        json.dump(results, f, indent=2)
    
    # Summary CSV
    csv_report = output_dir / f"batch_summary_{timestamp}.csv"
    with open(csv_report, "w") as f:
        f.write("filename,mission_id,source_type,status,risk_level,tokens,cost\n")
        for m in results["missions"]:
            analysis = m.get("analysis") or {}
            f.write(f'{m["filename"]},{m["mission_id"]},{m["source_type"]},'
                    f'{m["status"]},{analysis.get("risk_level", "N/A")},'
                    f'{analysis.get("total_tokens", 0)},{analysis.get("estimated_cost", 0)}\n')
    
    # Print summary
    print(f"\n{'='*60}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful uploads: {results['successful_uploads']}/{results['total_files']}")
    print(f"✅ Successful analyses: {results['successful_analyses']}/{results['total_files']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"\nReports saved to:")
    print(f"  📄 {json_report}")
    print(f"  📄 {csv_report}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Batch process documents through CACI Mission Copilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process sample data
  python scripts/batch_analyze.py --input ./sample_data --output ./reports

  # Skip AI analysis (ingestion only)
  python scripts/batch_analyze.py --input ./data --output ./reports --skip-analysis

  # Use custom API endpoint
  API_BASE_URL=http://prod:8000 python scripts/batch_analyze.py --input ./data
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input directory containing documents to process"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("./reports"),
        help="Output directory for reports (default: ./reports)"
    )
    
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip AI analysis, only ingest documents"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input directory does not exist: {args.input}")
        sys.exit(1)
    
    if not args.input.is_dir():
        print(f"Error: Input path is not a directory: {args.input}")
        sys.exit(1)
    
    asyncio.run(process_directory(args.input, args.output, args.skip_analysis))


if __name__ == "__main__":
    main()
