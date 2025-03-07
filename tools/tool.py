from typing import Dict

class Tool:
    def __init__(self, 
                 model: str,
                 name: str,
                 func,
                 description: str,
                 parameters: Dict[str, str]):
        self.name_for_model = model
        self.name_for_human = name
        self.func = func
        self.description_for_model = description
        self.parameters = parameters

    def to_config(self) -> dict:
        return {
            "name_for_model": self.name_for_model,
            "name_for_human": self.name_for_human,
            "description_for_model": self.description_for_model,
            "parameters": self.parameters
        }

  