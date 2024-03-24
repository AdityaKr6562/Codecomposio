import json
import types
import logging
import requests
from inspect import Parameter, Signature
from typing import Union, List, Dict, Any, Type, Annotated

import autogen
from composio import ComposioCore, App, Action
from pydantic import BaseModel, create_model, Field
from autogen.agentchat.conversable_agent import ConversableAgent


logger = logging.getLogger(__name__)


schema_type_python_type_dict = {
    'string': str,
    'number': float,
    'boolean': bool,
    'array': List,
    # 'object': dict
}

fallback_values = {
    'string': "",
    'number': 0.0,
    'boolean': False,
    'object': {},
    'array': []
}

def pydantic_model_from_param_schema(param_schema):
    fields = {}
    param_title = param_schema['title'].replace(" ", "")
    required_props = param_schema.get('required', [])
    for prop_name, prop_info in param_schema['properties'].items():
        prop_type = prop_info["type"]
        prop_title = prop_info['title'].replace(" ", "")
        prop_default = prop_info.get('default', fallback_values[prop_type])
        if prop_type in schema_type_python_type_dict:
            signature_prop_type = schema_type_python_type_dict[prop_type]
        else:
            signature_prop_type = pydantic_model_from_param_schema(prop_info)

        if prop_name in required_props:
            fields[prop_name] = (signature_prop_type, 
                                Field(..., 
                                    title=prop_title, 
                                    description=prop_info.get('description', 
                                                              prop_info.get('desc', 
                                                                             prop_title))
                                    ))
        else:
            fields[prop_name] = (signature_prop_type, 
                                Field(title=prop_title, 
                                    default=prop_default
                                    ))
    fieldModel = create_model(param_title, **fields)
    return fieldModel
        

    

def get_signature_format_from_schema_params(
        schema_params
):
    parameters = []
    required_params = schema_params.get('required', [])

    for param_name, param_schema in schema_params['properties'].items():
        param_type = param_schema['type']
        param_title = param_schema['title'].replace(" ", "")

        if param_type in schema_type_python_type_dict:
            signature_param_type = schema_type_python_type_dict[param_type]
        else:
            signature_param_type = pydantic_model_from_param_schema(param_schema)

        # param_type = schema_type_python_type_dict[param_schema['type']]
        # param_name = param_schema['name']
        param_default = param_schema.get('default', fallback_values[param_type])
        param_annotation = Annotated[signature_param_type, param_schema.get('description', 
                                                                            param_schema.get('desc',
                                                                                             param_title))]
        param = Parameter(
            name=param_name,
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=param_annotation,
            default=Parameter.empty if param_name in required_params else param_default 
        )
        parameters.append(param)
        print(param_name)
    return parameters


class ComposioAutogenToolset:
    def __init__(self, caller = None, executor = None):
        self.caller = caller
        self.executor = executor
        self.client =  ComposioCore()


    def register_tools(
            self,
            tools: Union[App, List[App]],
            caller: ConversableAgent = None,
            executor: ConversableAgent = None
        ):
        if isinstance(tools, App):
            tools = [tools]
        assert caller or self.caller, "If caller hasn't been specified during initialization, has to be specified during registration"
        assert executor or self.executor, "If executor hasn't been specified during initialization, has to be specified during registration"

        action_schemas = self.client.sdk.get_list_of_actions(
                                                apps=tools)
        
        for schema in action_schemas:
            self._register_schema_to_autogen(action_schema=schema,
                                            caller = caller if caller else self.caller,
                                            executor = executor if executor else self.executor)

            
        print("Tools registered successfully!")

    def register_actions(
            self,
            actions: Union[Action, List[Action]],
            caller: ConversableAgent = None,
            executor: ConversableAgent = None
        ):
        if isinstance(actions, Action):
            actions = [actions]

        assert caller or self.caller, "If caller hasn't been specified during initialization, has to be specified during registration"
        assert executor or self.executor, "If executor hasn't been specified during initialization, has to be specified during registration"

        action_schemas = self.client.sdk.get_list_of_actions(
                                                actions=actions)
        
        for schema in action_schemas:
            self._register_schema_to_autogen(action_schema=schema,
                                            caller = caller if caller else self.caller,
                                            executor = executor if executor else self.executor)

            
        print("Actions registered successfully!")

    def _register_schema_to_autogen(self, 
                                    action_schema, 
                                    caller: ConversableAgent,
                                    executor: ConversableAgent):

        name = action_schema["name"]
        appName = action_schema["appName"]
        description = action_schema["description"]

        parameters = get_signature_format_from_schema_params(
                                            action_schema["parameters"])
        action_signature = Signature(parameters=parameters)
        
        placeholder_function = lambda **kwargs: self.client.execute_action(
                                                    self.client.get_action_enum(name, appName), 
                                                    kwargs)
        action_func = types.FunctionType(
                                    placeholder_function.__code__, 
                                    globals=globals(), 
                                    name=name, 
                                    closure=placeholder_function.__closure__
                          )
        action_func.__signature__ = action_signature
        action_func.__doc__ = description

        autogen.agentchat.register_function(
            action_func,
            caller=caller,
            executor=executor,
            name=name,
            description=description
        )

if __name__ == "__main__":


    import os

    os.environ['OAI_CONFIG_LIST'] ='''[{"model": "gpt-4-1106-preview","api_key": "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"}]'''
    # {"model": "accounts/fireworks/models/fw-function-call-34b-v0","api_key": "FIREWORKS_API_KEY", "base_url":"https://api.fireworks.ai/inference/v1"},
    # {"model": "accounts/fireworks/models/mixtral-8x7b-instruct","api_key": "FIREWORKS_API_KEY", "base_url":"https://api.fireworks.ai/inference/v1"},


    import autogen

    llm_config={
        "timeout": 600,
        "cache_seed": 57,  # change the seed for different trials
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={"model": [
                "gpt-4-1106-preview",
                # "accounts/fireworks/models/fw-function-call-34b-v0"
                ]},
            ),
        "temperature": 0.5,
    }

    chatbot = autogen.AssistantAgent(
        name="chatbot",
        system_message="""For github analysis task,
        only use the functions you have been provided with.
        Reply TERMINATE when the task is done.
        Reply TERMINATE when user's content is empty.""",
        llm_config=llm_config,
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().find("TERMINATE") >= 0,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config = {
            "use_docker": False
        }
    )
    from pprint import pprint
    mycomposio = ComposioAutogenToolset(caller=chatbot,
                                        executor=user_proxy)
    
    # mycomposio.register_actions(actions=[Action.GITHUB_GET_REPOSITORY])
    mycomposio.register_tools(tools=[
                                App.GITHUB                
                                ])
    pprint(chatbot.llm_config["tools"])

    response = user_proxy.initiate_chat(
        chatbot,
        message="Write a short but informative summary about my github profile",
    )

    print(response)


    # client = ComposioCore()
    # actions = client.sdk.get_list_of_actions([
    #                                         App.GITHUB, 
    #                                         # App.ZENDESK, 
    #                                         # App.TRELLO
    #                                         ], [])
    # from pprint import pprint

    # for action in actions:
    #     pprint(action)
    

