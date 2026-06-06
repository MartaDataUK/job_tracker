import os
import sys
import subprocess
import time

def run_script(script_name):
    """
    Executes a python script safely, tracks its execution time,
    and ensures it exits successfully before moving forward.
    """
    if not os.path.exists(script_name):
        print(f"\nERROR: Could not find '{script_name}' in the current directory.")
        print("Please check the file name and ensure it is placed in this folder.")
        return False

    print("\n" + "="*60)
    print(f"STARTING STEP: {script_name}")
    print("="*60)

    start_time = time.time()

    try:
        # sys.executable points safely to the exact active Python/VirtualEnv environment
        process = subprocess.run(
            [sys.executable, script_name],
            check=True,       # Automatically raises an error if the script crashes
            text=True         # Ensures terminal print streams are read correctly
        )

        elapsed_time = time.time() - start_time
        print(f"SUCCESS: '{script_name}' completed cleanly in {elapsed_time:.1f} seconds.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\nCRITICAL FAILURE: '{script_name}' crashed with exit code {e.returncode}.")
        print("The master pipeline has been halted to prevent data corruption.")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED SYSTEM ERROR while running '{script_name}': {e}")
        return False

def main():
    print("==================================================== 🤖")
    print("   UK DATA ENGINEERING JOB TRACKER PIPELINE ENGINE  🤖")
    print("==================================================== 🤖")

    pipeline_start_time = time.time()

    # Define the exact execution order of your files
    pipeline_steps = [
        "Linkedin_jobs.py",   # Step 1: Extract LinkedIn data to CSV
        "adzuna_jobs.py",     # Step 2: Extract Adzuna data to CSV
        "compile_tracker.py"     # Step 3: Run Layout Cleaning, Filtering & Advanced Scoring
    ]

    for step_number, script in enumerate(pipeline_steps, start=1):
        print(f"\n[Step {step_number}/{len(pipeline_steps)}] Initializing execution thread...")

        success = run_script(script)

        # If any step fails, break immediately so you can fix errors without messing up your spreadsheet
        if not success:
            print("\nPIPELINE ABORTED: Please resolve the script errors shown above.")
            sys.exit(1)

    total_pipeline_time = time.time() - pipeline_start_time
    print(f"ALL STEPS COMPLETE! Total Execution Time: {total_pipeline_time:.1f} seconds.")
    print("Your fresh 'UK_Data_Engineering_Job_Tracker.xlsx' dashboard is fully baked and ready to open!")

if __name__ == "__main__":
    main()