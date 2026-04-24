import time
import random
import sys
import re
from pyparsing import line
import requests


FILE_NAME = "RankCache.txt"

def art_print(text):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.0001)


def scrape(commander_name):
    slug = commander_name.lower() #convert to lowercase
    slug = re.sub(r"[^a-z0-9\s-]", "", slug) #remove special characters
    slug = re.sub(r"\s+", "-", slug.strip()) #replace spaces with dashes

    url = f"https://edhrec.com/commanders/{slug}"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

    match = re.search(r"Rank #\s*(?:<!-- -->\s*)?([\d,]+)", html)

    if match:
        return int(match.group(1).replace(",", ""))

    return 0




def update_cache():
    top = "█"
    bottom = "╚"
    
    try:
        with open(FILE_NAME, "r") as f:
            lines = f.readlines()

        updated_lines = []

        for line in lines:
            if not line:
                continue
            
            top += "█"
            bottom += "═"
            print(top)
            print(bottom)

            owner, name, rank = line.split("%")
            new_rank = scrape(name)

            sys.stdout.write("\033[2A")   # go up 2 lines
            sys.stdout.write("\033[2K")   # clear line 1
            sys.stdout.write("\033[1B")   # down 1 line
            sys.stdout.write("\033[2K")   # clear line 2
            sys.stdout.write("\033[1A")   # back up to top line
            

            updated_line = f"{owner}%{name}%{new_rank}\n"
            updated_lines.append(updated_line)

        with open(FILE_NAME, "w") as f:
            f.writelines(updated_lines)
        top += "█╗"
        bottom += "═╝"
        print(top)
        print(bottom)
        sort()

    except Exception as e:
        print("Error updating cache:", e)
                

    except FileNotFoundError:
        return {}
    
    
def sort():
    try:
        with open(FILE_NAME, "r") as f:
            lines = f.readlines()

        entries = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            owner, name, rank = line.split("%")

            # capitalize first letter of every word in name
            name = name.title()

            # convert rank safely to int for correct numeric sorting
            try:
                rank_int = int(rank.replace(",", ""))
            except:
                rank_int = float("inf")  # pushes bad/missing ranks to bottom

            entries.append((owner, name, rank_int))

        # sort by owner, then by rank
        entries.sort(key=lambda x: (x[0].lower(), -x[2]))

        with open(FILE_NAME, "w") as f:
            for owner, name, rank in entries:
                f.write(f"{owner}%{name}%{rank}\n")

    except Exception as e:
        print("Error sorting cache:", e)

def add(owner=None):
    if owner is None:
        owner = input("Enter deck Owner: ")
    owner = owner.title()
    name = input("Enter Commander Name Exactly: ")
    name = name.title()
    rank = scrape(name)
    if rank == 0:
        print(f"Could not find rank for '{name}'. Please check the commander name and try again.")
        return
    try:
        # append new entry to file
        with open(FILE_NAME, "a") as f:
            f.write(f"{owner}%{name}%{rank}\n")

        # re-sort file after adding
        sort()
        print(f"Entry added for '{name}' with rank {rank}.")


    except Exception as e:
        print("Error adding entry:", e)

def calc():
    try:
        with open(FILE_NAME, "r") as f:
            data = {}

            for line in f:
                line = line.rstrip("\n")
                if line:
                    owner, name, rank = line.split("%", 2)

                    owner = owner.strip()
                    name = name.strip()
                    rank = int(rank.strip())

                    if owner not in data:
                        data[owner] = {
                            "names": [],
                            "ranks": []
                        }

                    data[owner]["names"].append(name)
                    data[owner]["ranks"].append(rank)
    
            for owner in data:
                ranks = data[owner]["ranks"]

                if ranks:
                    avg = sum(ranks) / len(ranks)
                    avg_str = f"{avg:.1f}"
                else:
                    avg_str = "N/A"

                print(f"Owner: {owner} (Avg Rank: {avg_str})")
    except FileNotFoundError:
        return {}


def display():
    try:
        with open(FILE_NAME, "r") as f:
            data = {}
            print()

            for line in f:
                line = line.rstrip("\n")
                if line:
                    owner, name, rank = line.split("%", 2)

                    owner = owner.strip()
                    name = name.strip()
                    rank = int(rank.strip())

                    if owner not in data:
                        data[owner] = {
                            "names": [],
                            "ranks": []
                        }

                    data[owner]["names"].append(name)
                    data[owner]["ranks"].append(rank)
    
            for owner in data:
                ranks = data[owner]["ranks"]

                if ranks:
                    avg = sum(ranks) / len(ranks)
                    avg_str = f"{avg:.1f}"
                else:
                    avg_str = "N/A"

                print(f"Owner: {owner} (Avg Rank: {avg_str})")

                for name, rank in zip(data[owner]["names"], data[owner]["ranks"]):
                    print(f"  {rank} - {name}")

            print()

    except FileNotFoundError:
        return {}


def quit():
    top = "█"
    bottom = "╚"
    for i in range(60):
        top += "█"
        bottom += "═"

        # print updated bars
        print(top)
        print(bottom)

        time.sleep(0.03 + random.uniform(-0.029, 0.02))

        # Move cursor up 2 lines and clear them
        sys.stdout.write("\033[2A")  # go up 2 lines
        sys.stdout.write("\033[2K")   # clear line 1
        sys.stdout.write("\033[1B")   # down 1 line
        sys.stdout.write("\033[2K")   # clear line 2
        sys.stdout.write("\033[1A")   # back up to top line

    top += "█╗"
    bottom += "═╝"
    print(top)
    print(bottom)
    
    print("DEREZZ COMPLETE")
    

def main():
    while True:
        user_input = input("[Enter Command]> ").strip()

        parts = user_input.split(" ", 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None

        match command:
            case "quit" | "exit" | "q" | "stop":
                quit()
                break

            case "update" | "refresh":
                print("Updating cache...")
                update_cache()
                print("Cache updated.")

            case "niche" | "average":
                calc()

            case "display" | "print" | "all" | "ls":
                print("Displaying cache...")
                display()

            case "add" | "new":
                if arg:
                    add(arg)
                else:
                    add()

            case "help" | "options" | "?":
                print("Available commands:")
                print("  add <owner> - Add a new entry for that owner")
                print("  display - Display all decks")
                print("  update - Update the cache")
                print("  quit - Exit the program")

            case _:
                print("Unknown command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()


