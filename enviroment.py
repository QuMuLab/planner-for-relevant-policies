import subprocess

def update_pddl_file(filename, task_dict):
    print("Available tasks:")
    for key in task_dict.keys():
        print(key)
    
    task = input("Please enter the task: ")
    bathroom_task = input("Do you need the bathroom? : ")
    
    # Check if task is in the dictionary
    if task not in task_dict:
        print(f"Unknown task '{task}'. Cannot proceed.")
        return
    if bathroom_task != "yes" and != "no":
        print(f"Unknown task '{bathroom_task}'. Cannot proceed, insert yes or no. ")
        return

    # Open the file and read lines
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Update lines
    if "yes" in bathroom_task:
        lines[50] = f"{task_dict[task][0]}\n"  # Line 51 (old Line 23)
    else:
        lines[50] = f" (is-fine vis1)\n"  # Line 51 (old Line 23)
    
    if len(lines) > 22:
        lines[49] = f"{task_dict[task][0]}\n"  # Line 50 (old Line 22)
    else:
        print("Warning: file has less than 22 lines. Cannot replace line 22.")
    
    if len(lines) > 32:
        lines[59] = f"{task_dict[task][1]}\n"  # Line 60 (old Line 32)
    else:
        print("Warning: file has less than 32 lines. Cannot replace line 32.")
    
    if "yes" in bathroom_task:
        lines[58] = f"{task_dict[task][1]}\n"  # Line 59 (old Line 31)
    else:
        lines[58] = f" \n"  # Line 59 (old Line 31)
        
    # Write lines back to file
    with open(filename, 'w') as file:
        file.writelines(lines)
        
    # Run bash command
    subprocess.run(["./src/prp", "./src/museum-domain.pddl", filename])

# A dictionary of tasks and corresponding 2D tuples to be inserted
task_dict = {
    "bagno" : ("(needs-restroom vis1)", "(is-fine vis1)"), #IS-FINE VA INSERITO NEL GOAL DEL PROBLEM E TESTATO!
    "quadro1_s1": ("(is-task-p1_1 task)", "(played_P1_1 vis1)"),
    "quadro2_s1": ("(is-task-p1_2 task)", "(played_P1_2 vis1)"),
    "quadro3_s1": ("(is-task-p1_3 task)", "(played_P1_3 vis1)"),
    "quadro4_s1": ("(is-task-p1_4 task)", "(played_P1_4 vis1)"),
    "quadro1_s2": ("(is-task-p2_1 task)", "(played_P2_1 vis1)"),
    "quadro2_s2": ("(is-task-p2_2 task)", "(played_P2_2 vis1)"),
    "quadro3_s2": ("(is-task-p2_3 task)", "(played_P2_3 vis1)"),
    "quadro4_s2": ("(is-task-p2_4 task)", "(played_P2_4 vis1)"),
    "tour_s1": ("(is-task-p1_1 task)(is-task-p1_2 task)(is-task-p1_3 task)(is-task-p1_4 task)", "(played_P1_1 vis1)(played_P1_2 vis1)(played_P1_3 vis1)(played_P1_4 vis1)"),
    "tour_s2": ("(is-task-p2_1 task)(is-task-p2_2 task)(is-task-p2_3 task)(is-task-p2_4 task)", "(played_P2_1 vis1)(played_P2_2 vis1)(played_P2_3 vis1)(played_P2_4 vis1)"),
    # Add more tasks if needed
}

problem_path = "./src/museum-problem.pddl"

# Call the function on your PDDL problem file
update_pddl_file(problem_path, task_dict)
