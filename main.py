import argparse
from src.agents.orchestration.workflow import AgentWorkflow


def main():
    parser = argparse.ArgumentParser(description="Run agent workflow")
    parser.add_argument("--query", "-q", required=True)
    args = parser.parse_args()

    workflow = AgentWorkflow()
    result = workflow.full_pipeline(args.query)
    print(result["final_answer"])

if __name__ == "__main__":
    main()