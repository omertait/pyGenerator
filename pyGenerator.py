import os
import subprocess
import random
import traceback
from dotenv import load_dotenv
from openai import OpenAI
import colorama as color
import tqdm as tqdm  # without line it's working

load_dotenv()
file_name="generatedcode.py"
PROGRAMS_LIST=[
        {"name": "interleavings of two strings", "prompt": '''Given two strings str1 and str2, prints all interleavings of the given
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
        CAB "'''},
        {"name": "check number is palindrom", "prompt" : "a program that checks if a number is a palindrome"}
        ,
        {"name": "kth smallest element in BST", "prompt": "A program that finds the kth smallest element in a given binary search tree."}
]

temperature=0.6

def get_user_input():
    user_input = input("Tell me, which program would you like me to code for you?"\
              +" If you don't have an idea,just press enter and I will choose a random program to code\n")
    if not user_input:
        # chooses random program to generate from PROGRAMS_LIST
        user_input = {"name": "interleavings of two strings", "prompt": '''Given two strings str1 and str2, prints all interleavings of the given
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
        CAB "'''}##random.choice(PROGRAMS_LIST)
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



def get_initial_messages(user_input):
    # initial_system_role = {
        
    #     "role": "system",
    #     "content": "You are an expert python developer that cannot speak at all, you provide just python code"
      
    # }
    initial_user_message = {
                            "role": "user",
                            "content": f'''You are an expert python developer that cannot speak at all, you provide just python code
                                      Create for me a python program. 
                                        {user_input} 
                                      refer to this code as the 'program'. 
                                      Also please include unit tests (refer to it as the 'unit_tests') that check the logic of the program using 5 different inputs and expected outputs. 
                                      The 'unit_tests' should call the 'program' code in order to test properly."
                                      the code should contain two functions: the 'program' and the 'unit_tests' and also main function that check program's Command Line Argument (sys.argv).  
                                      if program's Command Line Argument is 'test' then run the unit tests. the program should return True if they all passed, and raise an exception if one of the test failes.
                                      if the program's Command Line Argument (sys.argv) is empty, run the 'program' code.   
                                      also keep in mind that the 'unit_tests' should use the 'program' code when testing.''',
                        }

    messages = [initial_user_message]
    return messages

def generate_code( messages, client ):
    print(f"---------------- Generating Code ----------------")
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=temperature,
    )
    try:
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
    code_generated_message = {"role": "assistant",
                        "content": code_generated}
    print(f"---------------- Testing {file_name} ----------------")
    test_result, response = run_and_test_code(file_name=file_name)
    return test_result, response, code_generated_message
   

def create_file(file_name, code_generated):
    # Writing the code to the file
    with open(file_name, "w") as file:
        file.write(code_generated)

def run_and_test_code(file_name):
    try: 
        test_result = subprocess.run(f"python {file_name} test", capture_output=True, text=True)
        print(test_result)
        if(test_result.returncode == 1):
            print(color.Fore.RED + f"Error running generated code! Error:{test_result.stderr}")
            return False, {"role": "user",
                            "content": "Error running unit_tests." \
                                        +  "please fix it and provide again the full code" + test_result.stderr}
        elif("fail" in test_result.stdout.lower()):
            print(test_result.stdout)
            return False, {"role": "user",
                            "content": "unit_tests doesnt raise excaption when one of the tests failed." \
                                        + "please fix it and provide again the full code"}
        else:
            print(test_result.stdout)
            return True,"Code creation completed successfully!"
        
    except Exception as e :
        full_traceback = traceback.format_exc()
        short_traceback = "line " + full_traceback.split("File")[-1].split("line")[-1]
        print(color.Fore.RED + f"Error running generated code! Error:{short_traceback}")
       
        return False, {"role": "user",
                            "content": "Error running unit_tests!." \
                                        +  "please fix it and provide again the full code" + short_traceback}




def main():
    user_input = get_user_input()
    client = init_OpenAi_client()
    messages = get_initial_messages(user_input)
    for i in range(5):
        if i > 0: ## not the first iteration
            print(color.Fore.YELLOW +  "---------------- fixing errors ----------------")

        result = generate_code(messages, client)
        
        test_result, response, code_generated_message = result
        
        if test_result:
            print(color.Fore.GREEN + response)
            subprocess.run(f"python {file_name}")
            break
        else:
            messages.extend([code_generated_message, response])
   
    if not test_result:
        print(color.Fore.RED + "Code generation FAILED")
        
    




if __name__ =="__main__":
    main()