import os
import subprocess
import random
import traceback
from dotenv import load_dotenv
from openai import OpenAI
import colorama as color
import time
from threading import Thread

load_dotenv()
file_name = "generatedcode.py"
PROGRAMS_LIST = [
    {
        "name": "interleavings of two strings",
        "prompt": '''Given two strings str1 and str2, prints all interleavings of the given
        two strings. You may assume that all characters in both strings are
        different.Input: str1 = "AB", str2 = "CD"
        Output:
        ABCD
        ACBD
        ACDB
        CABD
        CADB
        CDAB
        Input: str1 = "AB", str2 = "C"
        Output:
        ABC
        ACB
        CAB "''',
    },
    {
        "name": "check number is palindrom",
        "prompt": "a program that checks if a number is a palindrome",
    },
    {
        "name": "kth smallest element in BST",
        "prompt": "A program that finds the kth smallest element in a given binary search tree.",
    },
]

temperature = 0.7

def parse_tracback(full_traceback):
    return "line " + full_traceback.split("File")[-1].split("line")[-1]

def get_user_input():
    user_input = input(color.Fore.WHITE +
        "Tell me, which program would you like me to code for you?"
        + " If you don't have an idea,just press enter and I will choose a random program to code\n"
    )
    if not user_input:
        # chooses random program to generate from PROGRAMS_LIST
        user_input = random.choice(PROGRAMS_LIST)
        print(color.Fore.YELLOW + "generating: ", user_input["name"])
        user_input = user_input["prompt"]
    else:
        print(color.Fore.YELLOW + "generating your code ")
    return user_input


def init_OpenAi_client():
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    return client

def get_GPT_Response(client, messages, temperature, chat_completion):
    chat_completion[0] = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=temperature,
    )

def get_initial_messages(user_input):
    # initial_system_role = {

    #     "role": "system",
    #     "content": "You are an expert python developer that cannot speak at all, you provide just python code"

    # }
    example = """an example of generating such code for the prompt: "make a calculator with the operation +":
import sys
def program(operation, a, b):
    try:
        if operation == '+':
            answer = a + b
            return answer
        else:
            return "Invalid operation"
    except TypeError:
        return "Invalid input. Please enter a number."

def unit_tests():
    # Test for addition
    assert program('+', 3, 4) == 7.0
    assert program('+', 100000000, 100000000) == 200000000.0
    assert program('+', 0, 0) == 0.0
    # Test for invalid operation
    assert program('-', 3, 4) == "Invalid operation", "Invalid operation test failed"

    # Test for invalid input
    assert program('+', 'three', 4) == "Invalid input. Please enter a number.", "Invalid input test failed"
    return True
                                   
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        try:
            unit_tests()
            print("all tests passed")
        except Exception as e:
            raise e
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))
        print(str(program("+", a, b)))

if __name__ == "__main__":
    main()"""
    initial_user_message = {
        "role": "user",
        "content": f"""You are an expert python developer that cannot speak at all, you provide just python code
Create python program for: 
  {user_input}.
refer to this code as the 'program'. 
include unit tests (refer to it as the 'unit_tests') that check the logic of the program using 5 different inputs and expected outputs. 
The 'unit_tests' should call the 'program' code in order to test properly."
the code should contain three functions: the 'program', 'unit_tests' and also main function that check program's Command Line Argument (sys.argv).  
if program's Command Line Argument is 'test' then run the unit tests. the program should return True if they all passed, and raise an exception if one of the test failes.
if the program's Command Line Argument (sys.argv) is empty, run the 'program' code.   
""",
    }

    messages = [initial_user_message]
    return messages


def generate_code(messages, client):
    print(f"---------------- Generating Code ----------------")
    chat_completion = [None]
    call_API_thread = Thread(target=get_GPT_Response, args=(client,messages, temperature, chat_completion))
    call_API_thread.start()


    while Thread.is_alive(call_API_thread):
        time.sleep(1)
        print(". ", end=" ", flush=True)

    call_API_thread.join()
    print(" ")
    
    try:
        chat_completion = chat_completion[0]
        code_generated = chat_completion.choices[0].message.content
        if "```python" in code_generated:
            code_generated = code_generated.split("```")[1].split("python")[1]
    except Exception as e:
        print(color.Fore.RED + "error with response from model")
        print(color.Fore.RED + e)

    print(f"---------------- Creating File {file_name} ----------------")
    create_file(code_generated=code_generated, file_name=file_name)

    print(f"---------------- auto-format {file_name} using black ----------------")
    subprocess.run(f"black {file_name}")
    with open(file_name) as f:
        code_generated = f.read()
    # set code_generated_message as the code after black auto format
    code_generated_message = {"role": "assistant", "content": code_generated}

    print(f"---------------- Testing {file_name} ----------------")
    test_result, response, traceback = run_and_test_code(file_name=file_name)
    return test_result, response, code_generated_message, traceback


def create_file(file_name, code_generated):
    # Writing the code to the file
    with open(file_name, "w") as file:
        file.write(code_generated)


def run_and_test_code(file_name):
    try:
        test_result = subprocess.run(
            f"python {file_name} test", capture_output=True, text=True
        )
        # tests failed
        if test_result.returncode == 1:
            full_traceback = test_result.stderr
            short_traceback = parse_tracback(full_traceback)
            return False, {
                "role": "user",
                "content": "Error running unit_tests."
                + "please fix it and provide again the full code"
                + short_traceback,
            }, short_traceback
        
        # tests failed but it was printed into stdout
        elif "fail" in test_result.stdout.lower():
            return False, {
                "role": "user",
                "content": f"unit_tests doesnt raise excaption when one of the tests failed. it prints to stdout instead : {test_result.stdout}"
                + "please fix it and provide again the full code",
            }, test_result.stdout
        
        else:
            # All test Passed
            return True, "Code creation completed successfully!", None

    except:
        full_traceback = traceback.format_exc()
        short_traceback = parse_tracback(full_traceback)
        return False, {
            "role": "user",
            "content": "Error running unit_tests!."
            + "please fix it and provide again the full code"
            + short_traceback,
        }, short_traceback


def main():
    user_input = get_user_input()
    client = init_OpenAi_client()
    messages = get_initial_messages(user_input)
    for i in range(5):
        if i > 0:  ## not the first iteration
            print(color.Fore.YELLOW + "---------------- fixing errors ----------------")

        test_result, response, code_generated_message, traceback = generate_code(messages, client)

        if test_result:
            print(color.Fore.GREEN + response)
            print(color.Fore.YELLOW + "---------------- Running Generated Code ----------------")
            print(color.Fore.WHITE)
            subprocess.run(f"python {file_name}")
            break
        else:
            print(
                color.Fore.RED
                + f"excaption Error running generated code! Error:{traceback}"
            )
            messages.extend([code_generated_message, response])

    if not test_result:
        print(color.Fore.RED + "Code generation FAILED")


if __name__ == "__main__":
    main()
