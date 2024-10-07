import logging
from jinja2 import Environment, BaseLoader
import os
from app.services.llm.llm import LLM

class PlannerAgent:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.data = self._initialize_data()
        self.env = Environment(loader=BaseLoader())
    
    def execute(self, user_prompt, repository_structure, repository_code, prompt_path=None):
        try:
            prompt_template = self._load_prompt(prompt_path or f"app/agents/planner/prompt.jinja2")
            prompt = self._generate_prompt(prompt_template, repository_structure, repository_code, user_prompt)
            response = self._get_llm_response(prompt)
            self._parse_response(response)

            logging.info(self.data.get('plan')) # log the plan

            return self.data.get('plan')
        except Exception as e:
            return {"status": "failed", "description": f"An error occurred in planner exec: {str(e)}"} 

    def _initialize_data(self):
        return {
            "current_focus": "",
            "plan": []
        }

    def _load_prompt(self, path):
        try:
            with open(path) as file:
                return file.read().strip()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found at {path}")
    
    def _generate_prompt(self, template_str, repository_structure, repository_code, user_prompt, output=None, error=None, commands=None):
        if not template_str:
            raise ValueError("Prompt template is empty.")
        
        template = self.env.from_string(template_str)
        return template.render(
            prompt=user_prompt,
            repository_code=repository_code,
            repository_structure=repository_structure,
            output=output,
            error=error,
            commands=commands
        )

    def _get_llm_response(self, prompt):
        return self.llm.execute_query(prompt)

    def _parse_response(self, response):
        try:
            lines = response.split("\n")
            current_section = None
            current_step = {}
            steps = []

            for line in lines:
                line = line.strip()

                if line.startswith("Current Focus:"):
                    self.data["current_focus"] = line.split("Current Focus:")[1].strip()
                    current_section = "current_focus"

                elif line.startswith("Plan:"):
                    current_section = "plan"

                elif current_section == "plan":
                    if line.startswith("- Step"):
                        if current_step:
                            steps.append(current_step)
                        step_number = line.split(":")[0].strip().split(" ")[2]
                        current_step = {
                            "step": step_number,
                            "file": "",
                            "action": "",
                            "description": ""
                        }
                    elif line.startswith("- File:"):
                        current_step["file"] = line.split(": ")[1].strip()
                    elif line.startswith("- Action:"):
                        current_step["action"] = line.split(": ")[1].strip()
                    elif line.startswith("- Description:"):
                        current_step["description"] = line.split(": ")[1].strip()
                    elif line and current_step["description"]:
                        current_step["description"] += " " + line.strip()

            if current_step:
                steps.append(current_step)

            # Remove triple backticks from the last step's description
            if steps:
                steps[-1]["description"] = steps[-1]["description"].replace("```", "")

            self.data["plan"] = steps
        except Exception as e:
            return {"status": "failed", "description": f"An error occurred in planner parse response: {str(e)}"}