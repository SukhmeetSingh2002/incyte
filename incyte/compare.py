import os
import time
import subprocess
import argparse
from random import randint
import sys

from rich import print
from rich.progress import Progress
from rich.console import Console
from rich.progress import track

# import config
from . import config

console = Console()

def generate_input_file(testcases, filename):
    with open(filename, "w") as f:
        f.write(f"{testcases}\n")
        for _ in track(range(testcases), description="Generating Test Cases..."):
            n = randint(2, 3000)
            f.write(f"{n}\n")
            for _ in range(n):
                f.write(f"{randint(1, 1000)} ")
            f.write("\n")
            for _ in range(n):
                f.write(f"{randint(1, 1000)} ")
            f.write("\n")
            f.write("\n")


def get_build_and_run_commands(args, custom_config, file_extension):
    if file_extension == '.py':
        # Python file
        build_command = config.get_build_command(args, custom_config['python'])
        run_command = config.get_run_command(args, custom_config['python'])
    elif file_extension == '.cpp':
        # C++ file
        build_command = config.get_build_command(args, custom_config['cpp'])
        run_command = config.get_run_command(args, custom_config['cpp'])
    else:
        build_command = config.get_build_command(args, custom_config['other'])
        run_command = config.get_run_command(args, custom_config['other'])

        if build_command is None and run_command is None:
            console.print(f"[bold red]Error:[/bold red] Cannot find build or run command for file extension [bold blue]{file_extension}[/bold blue]")
            sys.exit(1)
        elif run_command is None:
            console.print(f"[bold red]Error:[/bold red] Cannot find run command for file extension [bold blue]{file_extension}[/bold blue]")
            sys.exit(1)
        else:
            console.print(f"[bold blue]Info:[/bold blue] Using build command [bold blue]{build_command}[/bold blue] and run command [bold blue]{run_command}[/bold blue]")

    if build_command is not None:
        build_command = build_command.split()
    run_command = run_command.split()

    return build_command, run_command


def main():
    parser = argparse.ArgumentParser(description='Test your program with custom or random inputs')
    parser.add_argument('-t', '--testcases', type=int, default=10, help='Number of test cases (default: 10)')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the program to be tested')
    parser.add_argument('--good-file', type=str, default='Good.cpp', help='Path to the reference (good) program file (default: Good.cpp)')
    parser.add_argument('--input-file', type=str, default='input.txt', help='Input file for your program (default: input.txt)')
    parser.add_argument('--output-file', type=str, default='output.txt', help='Output file generated by your program (default: output.txt)')
    parser.add_argument('--good_output-file', type=str, default='output_good.txt', help='Reference (good) program\'s output file (default: output_good.txt)')
    parser.add_argument('--custom-generator', type=str, default=None, help='Path to a custom input generator function. The custom generator function should be defined in a Python file and named "generate_input." It is responsible for generating input files for your program. You can specify the path to this file here. If not provided, random input will be generated. (default: None)')


    args = parser.parse_args()

    try:

        with console.status("[bold green]Testing...", spinner="aesthetic") as status:

            # Generate input file with progress
            console.print(f"Writting test cases to [bold blue]{args.input_file}[/bold blue]...")
            if args.custom_generator:
                # Import the user-defined generator function from the specified file
                sys.path.append(os.path.dirname(args.custom_generator))
                custom_generator_module = os.path.splitext(os.path.basename(args.custom_generator))[0]
                try:
                    custom_generator = __import__(custom_generator_module)
                except ModuleNotFoundError:
                    console.print(f"[bold red]Error:[/bold red] Cannot find module [bold blue]{custom_generator_module}[/bold blue]")
                    sys.exit(1)

                # Use the user's generator function to generate input
                try:
                    custom_generator.generate_input(args.testcases, args.input_file)
                except AttributeError:
                    console.print(f"[bold red]Error:[/bold red] Cannot find function [bold blue]generate_input[/bold blue] in module [bold blue]{custom_generator_module}[/bold blue]")
                    console.print(f"[bold red]Error:[/bold red] Please make sure the function name is [bold blue]generate_input[/bold blue] and it takes 2 arguments: [bold blue]testcases[/bold blue] and [bold blue]filename[/bold blue]")
                    current_function_name = custom_generator.__dir__()
                    current_function_name = [x for x in current_function_name if not x.startswith('__')]
                    console.print(f"[bold blue]Info:[/bold blue] Currently you have the following imports and functions in your file: [bold blue]{current_function_name}[/bold blue]")
                    sys.exit(1)
            else:
                # Use the built-in random input generator
                generate_input_file(args.testcases, args.input_file)

            # Load the custom configuration
            custom_config = config.load_custom_config()

            # Usage example:
            file_extension = os.path.splitext(args.file)[1]
            file_extension_good = os.path.splitext(args.good_file)[1]

            build_command, run_command = get_build_and_run_commands(args, custom_config, file_extension)
            build_command_good, run_command_good = get_build_and_run_commands(args, custom_config, file_extension_good)


            if build_command is not None:
                compile_command = build_command + [args.file]
                console.print(f"Compile command: [bold blue]{compile_command}[/bold blue]")
                # Compile and run the program to check
                console.print(f"Compiling [bold blue]{args.file}[/bold blue]...")
                subprocess.Popen(compile_command, stdout=subprocess.DEVNULL).wait()

            startT = time.time()
            console.print(f"Running [bold blue]{args.file}[/bold blue]...")
            subprocess.Popen(run_command, stdout=subprocess.DEVNULL).wait()
            endT = time.time()
            
            if build_command is not None:
                compile_command = build_command_good + [args.good_file]
                # Compile and run the reference C++ program
                console.print(f"Compiling [bold blue]{args.good_file}[/bold blue]...")
                subprocess.Popen(compile_command, stdout=subprocess.DEVNULL).wait()

            startT2 = time.time()
            console.print(f"Running [bold blue]{args.good_file}[/bold blue]...")
            subprocess.Popen(run_command_good, stdout=subprocess.DEVNULL).wait()
            endT2 = time.time()

            # Read output files
            console.print(f"Reading output files...")
            with open(args.output_file, "r") as output, open(args.good_output_file, "r") as good_output:
                outputR = output.readlines()
                goodR = good_output.readlines()

            # Compare outputs
            console.print(f"Comparing outputs...")
            failed_tests = 0

            for x in range(args.testcases):
                if outputR[x] != goodR[x]:
                    failed_tests += 1
                    print(f"TestCase : [bold]{x+1}[/bold]")
                    print(f"Good : [green]{goodR[x]}[/green]")
                    print(f"Bad  : [red]{outputR[x]}[/red]")

        success_rate = (1 - failed_tests / args.testcases) * 100

        console.print(f"Test Cases: [bold]{args.testcases}[/bold]")
        console.print(f"Failed Tests: [bold red]{failed_tests}[/bold red]")
        console.print(f"Success Rate: [bold]{success_rate:.2f}%[/bold]")
        console.print(f"Time Taken: [bold]{endT - startT:.2f}s[/bold]")
        console.print(f"Good Time Taken: [bold]{endT2 - startT2:.2f}s[/bold]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
