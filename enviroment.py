import subprocess

def update_pddl_file(filename, task_dict):
    print("Available tasks:")
    for key in task_dict.keys():
        print(key)
    
    task = input("Please enter the task: ")
    
    # Check if task is in the dictionary
    if task not in task_dict:
        print(f"Unknown task '{task}'. Cannot proceed.")
        return

    # Open the file and read lines
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Update lines
    if len(lines) > 22:
        lines[21] = f"{task_dict[task][0]}\n"  # Line 22
    else:
        print("Warning: file has less than 22 lines. Cannot replace line 22.")
    
    if len(lines) > 32:
        lines[31] = f"{task_dict[task][1]}\n"  # Line 32
    else:
        print("Warning: file has less than 32 lines. Cannot replace line 32.")
    
    # Write lines back to file
    with open(filename, 'w') as file:
        file.writelines(lines)
        
    # Run bash command
    subprocess.run(["./src/prp", "./src/museum-domain.pddl", filename])

# A dictionary of tasks and corresponding 2D tuples to be inserted
task_dict = {
    "quadro1_s1": ("(is-task-p1_1 task)", "(played_P1_1 vis1)"),
    "quadro2_s1": ("(is-task-p1_2 task)", "(played_P1_2 vis1)"),
    "quadro3_s1": ("(is-task-p1_3 task)", "(played_P1_3 vis1)"),
    # Add more tasks if needed
}

problem_path = "./src/museum-problem.pddl"

# Call the function on your PDDL problem file
update_pddl_file(problem_path, task_dict)
