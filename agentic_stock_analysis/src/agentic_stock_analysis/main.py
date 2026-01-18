#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from pathlib import Path

from agentic_stock_analysis.crew import AgenticStockAnalysis

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def ensure_reports_directory():
    Path("reports").mkdir(exist_ok=True)


def run():
    ensure_reports_directory()
    
    inputs = {
        'current_date': datetime.now().strftime("%A, %B %d, %Y"),
        'current_year': str(datetime.now().year),
        'report_date': datetime.now().strftime("%Y-%m-%d"),
    }

    print("\n" + "="*60)
    print("🚀 AUTONOMOUS STOCK RESEARCH SYSTEM")
    print("="*60)
    print(f"\n📅 Report Date: {inputs['current_date']}")
    print("\n" + "-"*60)
    print("⚠️  DISCLAIMER: Informational analysis only, not investment advice.")
    print("-"*60 + "\n")

    try:
        result = AgenticStockAnalysis().crew().kickoff(inputs=inputs)
        print("\n" + "="*60)
        print("✅ DAILY STOCK REPORT COMPLETED")
        print("="*60)
        print(f"\n📄 Report saved to: reports/daily_stock_report_{inputs['report_date']}.md\n")
        return result
    except Exception as e:
        print(f"\n❌ Error running stock research crew: {e}")
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    ensure_reports_directory()
    inputs = {'current_date': datetime.now().strftime("%A, %B %d, %Y"), 'current_year': str(datetime.now().year)}
    try:
        AgenticStockAnalysis().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    try:
        AgenticStockAnalysis().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    ensure_reports_directory()
    inputs = {'current_date': datetime.now().strftime("%A, %B %d, %Y"), 'current_year': str(datetime.now().year)}
    try:
        AgenticStockAnalysis().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    run()





