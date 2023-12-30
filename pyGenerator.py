import os
import subprocess
import random
from dotenv import load_dotenv
from openai import OpenAI
import colorama as color
import tqdm as tqdm  # without line it's working

load_dotenv()

PROGRAMS_LIST=[
        '''Given two strings str1 and str2, prints all interleavings of the given
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
        "a program that checks if a number is a palindrome"
        ,
        "A program that finds the kth smallest element in a given binary search tree."
]

input = input("Tell me, which program would you like me to code for you?"\
              +" If you don't have an idea,just press enter and I will choose a random program to code\n")
if not input:
    # chooses random program to generate from PROGRAMS_LIST
    input = random.choice(PROGRAMS_LIST)
    print(color.Fore.YELLOW + "generating: ", input)
client = OpenAI(
    api_key=os.environ.get("ORGANIZATION_API_KEY"),
)


initial_user_message = {
                        "role": "user",
                        "content": "You are an expert python developer." \
                                +  "Create for me a python program." \
                                + input \
                                +  "refer to this code as the 'program'." \
                                +  "Do not write any explanations, just show me the code itself and nothing more." \
                                +  "just response with python code ready to run." \
                                +  "Also please include unit tests (refer to it as the 'unit_tests') that check the logic of the program using 5 different inputs and expected outputs." \
                                +  "the code should contain two functions: the 'program' and the unit_tests and also main function that check program's Command Line Argument (sys.argv). if program's Command Line Argument is 'test' then run the unit tests and return true if it passed, throw an exception if one of the test failes. if the program's Command Line Argument (sys.argv) is empty, run the 'program' code",
                    }

messages = [initial_user_message]

for i in range(5):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    try:
        if i > 0: 
            print(color.Fore.YELLOW +  "fixing errors")
        code_generated = chat_completion.choices[0].message.content.split("```")[1].split("python")[1]
        messages.append({"role": "assistant",
                        "content": code_generated})
    


        file_name = "generatedcode.py"
        # Writing the code to the file
        with open(file_name, "w") as file:
            file.write(code_generated)
    except Exception as e :
        print(e)
        print(chat_completion)
        continue
    try: 
        result = subprocess.run("python generatedcode.py test", capture_output=True, text=True)
        if(result.stderr):
            print(color.Fore.RED + f"Error running generated code! Error:{result.stderr}")
            messages.append({"role": "user",
                            "content": result.stderr})
        else:
            print(color.Fore.GREEN + "Code creation completed successfully!")
            print(result) 
            break
          
    except Exception as e :
        print(color.Fore.RED + f"Error running generated code! Error:{e}")
        messages.append({"role": "user",
                            "content": e})
if i == 5:   
    print(color.Fore.RED + "Code generation FAILED")



        


