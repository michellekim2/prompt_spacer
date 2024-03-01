# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import re

def main():
    empty_task_template_path = '/Users/michellekim/Documents/Emory_NLP/natural-instructions/tasks/CAPS_task_empty.json'
    caps5_var_template_path = '/Users/michellekim/Documents/Emory_NLP/var_templates/CAPS5_var_template.json'
    with open(empty_task_template_path, 'r') as file: # open template task json
        task_template = json.load(file)
    #print(task_template)

    with open(caps5_var_template_path, 'r') as file: # get information from CAPS5_var_template.json
        caps5_var_template = json.load(file)

    var_name = next(iter(caps5_var_template)) # get variable name
    var_info = caps5_var_template[var_name] # get information on a variable based on the name

    #print(f"Variable Name: {var_name}, Variable Information: {var_info}")

    task_template["Definition"] = form_sys_prompt(var_info)
    print("form_sys_prompt_test: ", task_template["Definition"])

    """
    for key in var_info.keys():
        match key:
            case "template":
                # copy the value of var_info["template"] to task_template["Definition"]
                task_template["Definition"] = var_info["template"]
                if "{keywords}" in task_template["Definition"].get("system") and "keywords" in var_info:
                    task_template["Definition"]["system"] = task_template["Definition"]["system"].replace("{keywords}",var_info["keywords"])
                else:
                    print("Error: '{keywords}' placeholder not found in the template or 'keywords' not in var_info.")

                if "{symptom}" in task_template["Definition"].get("system") and "symptom" in var_info:
                    task_template["Definition"]["system"] = task_template["Definition"]["system"].replace("{symptom}",var_info["symptom"])
                else:
                    print("Error: '{symptom}' placeholder not found in the template or 'symptom' not in var_info.")
                if "{range}" in task_template["Definition"].get("system") and "range" in var_info:
                    range_str = json.dumps(var_info["range"], indent=0)
                    task_template["Definition"]["system"] = task_template["Definition"]["system"].replace("{range}",range_str)
                else:
                    print("Error: '{range}' placeholder not found in the template or 'range' not in var_info.")
                #print(task_template["Definition"])
    """
    # print(f'task_template["Definition"]: {task_template["Definition"]}, var_info["template"]: {var_info["template"]}')

    base_file_path = '/Users/michellekim/Documents/Emory_NLP/natural-instructions/tasks/'
    new_file_path = f'{base_file_path}CAPS_task_test.json'

    with open(new_file_path, 'w') as file:
        json.dump(task_template, file, indent=4)

    #print("task_template['Definition']: ", task_template["Definition"])

def form_range(range_dict, field_type):
    range_str = "[" + ", ".join([k for k, _ in range_dict.items()]) + "]"
    range_example = "\n".join([f"{k}: {v}" for k, v in range_dict.items()])
    if field_type == "scale":
        return range_str + "\n" + "Rating Scale:\n" + range_example
    else:
        return range_str + "\n" + "Rating Choices:\n" + range_example

def form_conditions(attributes):
    condition = [
        f"{i+1}. If {attr['condition']}, the answer should be {attr['score']}."
        for i, attr in enumerate(attributes)
    ]
    return "\n\nNote that:\n" + "\n".join(condition)

def get_fileds(string) -> list:
    return re.findall(r"\{(.+?)\}", string)

def form_sys_prompt(var_template):
    #print("var_template: ", var_template["template"])
    pstring = var_template["template"]["system"]
    fields = get_fileds(pstring)
    for field in fields:
        match field:
            case "range":
                range_str = form_range(
                    var_template["range"], var_template["field_type"]
                )
                pstring = pstring.replace(f"{{{field}}}", range_str)
            case "attributes":
                if "attributes" not in var_template:
                    pstring = pstring.replace(f"{{{field}}}", "")
                else:
                    conditions = form_conditions(var_template["attributes"])
                    pstring = pstring.replace(f"{{{field}}}", conditions)
            case "slots":
                pstring = pstring.replace(
                    f"{{{field}}}", json.dumps(var_template["slots"])
                )
            case _:  # keywords, question
                if type(var_template[field]) == list:
                    content = f"[{', '.join(var_template[field])}]"
                elif type(var_template[field]) == dict:
                    content = json.dumps(var_template[field])
                else:
                    content = var_template[field]

                pstring = pstring.replace(f"{{{field}}}", content)
        pstring = pstring.replace(
            'Return the answer as a JSON object with "reason" and "answer" as the keys.',
            'Return the answer as a JSON object in the following format: {"reason": "", "answer": ""}. Please ensure you only output the JSON object.',
        )
    return pstring






    #variable = "1"
    #new_file_path = f'/Users/michellekim/Documents/Emory_NLP/natural-instructions/tasks/CAPS_task_test{variable}.json'


if __name__ == '__main__':
    main()

