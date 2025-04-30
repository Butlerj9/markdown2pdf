import os
import subprocess
import sys

def run_command(cmd):
    """
    Run the given command using shell=True and return the subprocess.CompletedProcess.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def check_mermaid_cli():
    """
    Check for the Mermaid CLI by trying to run 'mmdc -V'.
    Returns the absolute command if found, or None if not found.
    """
    # First, try running 'mmdc -V' directly
    print("Trying 'mmdc -V' from PATH...")
    result = run_command("mmdc -V")
    
    if result and result.returncode == 0:
        version = result.stdout.strip()
        print("Success! Mermaid CLI version from PATH:", version)
        return "mmdc"
    else:
        print("Failed to run 'mmdc -V' from PATH.")
        if result:
            print("stdout:", result.stdout.strip())
            print("stderr:", result.stderr.strip())
        
        # Try using the absolute path to mmdc.CMD (adjust this path if needed)
        absolute_mmdc = r"C:\Users\joshd\AppData\Roaming\npm\mmdc.CMD"
        print(f"Trying absolute path: '{absolute_mmdc} -V'")
        result = run_command(f'"{absolute_mmdc}" -V')
        if result and result.returncode == 0:
            version = result.stdout.strip()
            print("Success! Mermaid CLI version using absolute path:", version)
            return f'"{absolute_mmdc}"'
        else:
            print("Failed to run Mermaid CLI even using the absolute path.")
            if result:
                print("stdout:", result.stdout.strip())
                print("stderr:", result.stderr.strip())
            return None

def create_sample_mermaid_file(filename):
    """
    Create a simple Mermaid diagram definition file.
    """
    mermaid_content = """\
%%{init: {'theme': 'default'}}%%
graph LR
    A[Start] --> B{Is it working?}
    B -- Yes --> C[Great!]
    B -- No --> D[Fix it!]
    C --> E[End]
    D --> E[End]
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(mermaid_content)
    print(f"Created sample Mermaid diagram file: {filename}")

def generate_diagram(cli_cmd, input_file, output_file):
    """
    Run the Mermaid CLI to generate a diagram from the given input file.
    """
    cmd = f'{cli_cmd} -i "{input_file}" -o "{output_file}"'
    print("Running command:", cmd)
    result = run_command(cmd)
    if result and result.returncode == 0:
        print(f"Diagram successfully generated: {output_file}")
    else:
        print("Error generating diagram.")
        if result:
            print("stdout:", result.stdout.strip())
            print("stderr:", result.stderr.strip())

def main():
    # Print the current PATH so you can verify it includes the npm binaries directory
    current_path = os.environ.get("PATH", "")
    print("Current PATH:")
    print(current_path)
    print("-" * 80)

    # Check for Mermaid CLI
    cli_cmd = check_mermaid_cli()
    if cli_cmd is None:
        print("Mermaid CLI is not available. Exiting.")
        sys.exit(1)
    
    # Create a sample Mermaid diagram definition file
    sample_input = "sample_diagram.mmd"
    create_sample_mermaid_file(sample_input)
    
    # Generate an SVG diagram from the sample file
    output_file = "sample_diagram.svg"
    generate_diagram(cli_cmd, sample_input, output_file)

if __name__ == "__main__":
    main()
