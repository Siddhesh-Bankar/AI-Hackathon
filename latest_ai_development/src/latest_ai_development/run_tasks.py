import yaml
import json
from crewai import TaskExecutor  # Assuming TaskExecutor is the class to execute tasks in CrewAI

# Load tasks from tasks.yaml file
with open('tasks.yaml', 'r') as file:
    tasks = yaml.safe_load(file)

# Initialize the TaskExecutor (assuming this is the class responsible for executing tasks)
executor = TaskExecutor()

# Loop through each task defined in the tasks.yaml file
for task in tasks['tasks']:
    task_name = task['task_name']
    task_input = task['input']
    task_output = task['output']
    
    try:
        # Execute the task
        result = executor.execute_task(task_name, task_input)
        
        # Process the output
        if task_output['format'] == 'json':
            # Save result as JSON file
            with open(f'{task_name}_result.json', 'w') as json_file:
                json.dump(result, json_file)
            print(f"Task '{task_name}' executed with JSON output.")
        
        # Handle sending to email or other outputs as needed
        if 'send_to_email' in task_output:
            print(f"Sending results to {task_output['send_to_email']}...")
            # send_email(task_output['send_to_email'], result)  # Uncomment when you have an email handler

    except Exception as e:
        print(f"Error executing task '{task_name}': {e}")
