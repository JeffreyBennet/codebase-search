import logging
from typing import Dict, List, Union
from app.agents.coder.coder import CoderAgent
from app.agents.planner.planner import PlannerAgent
from app.services.llm.llm import LLM

class AgentOrchestrator:
    def __init__(self, llm: LLM, project_dir: str):
        self.llm = llm
        self.project_dir = project_dir
        self.planner_agent = PlannerAgent(llm)
        self.coder_agent = CoderAgent(llm, project_dir)
        
    def orchestrate(self, user_prompt: str, repository_structure: List[str], repository_code: Dict[str, str], user_context: List[str] = None):
        try:
            # Step 1: Use PlannerAgent to create a step-by-step plan
            logging.info("Starting plan generation...")
            plan = self.planner_agent.execute(user_prompt, repository_structure, repository_code)
            if not plan or "status" in plan and plan["status"] == "failed":
                logging.error("PlannerAgent failed to generate a plan.")
                return "PlannerAgent failed to generate a plan."

            logging.info(f"Plan generated: {plan}")

            # Step 2: Use CoderAgent to execute each step of the plan
            repository_updates = {}
            for step in plan:
                logging.info(f"Executing step {step['step']}: {step['description']}")

                # Execute step in CoderAgent
                result = self.coder_agent.execute(plan, step, user_context, repository_code, repository_structure)
                if not result:
                    logging.error(f"CoderAgent failed at step {step}.")
                    return f"CoderAgent failed at step {step}."

                # Aggregate the repository updates
                repository_updates.update({file['file']: file['code'] for file in result})
                logging.info(f"Step {step} executed successfully. Code changes: {result}")

            logging.info("All steps executed successfully.")
            return repository_code
        except Exception as e:
            logging.error(f"An error occurred during orchestration: {str(e)}", exc_info=True)
            return {"status": "failed", "description": f"An error occurred in orchestration: {str(e)}"}
