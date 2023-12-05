import mysql.connector as sql
import xyron_script as Xyron
import sys
import os

from rich.console import Console
from rich.style import Style
from rich.table import Column, Table
from rich.prompt import Prompt, IntPrompt, Confirm

console = Console()

###
# NOTE
# Write update_project()
# Do final UI formatting and changes
# Bug fixes (if any)
###

# Styles
warning_style = Style(color="bright_red", bold=True)
success_style = Style(color="bright_green", bold=True)
caution_style = Style(color="bright_yellow", bold=True)
neutral_style = Style(color="blue", bold=True)

console.log("Executing pre-launch setups..", style=neutral_style)

# MySQL Connection
console.log("Attempting to connect to mysql..")
xyron_sql = sql.connect(host="localhost", user="root", password="Mercury2017!")

if xyron_sql.is_connected() == False:
    console.log(":warning: Error Connecting", style=warning_style)

# Cursor Object
console.log("Setting cursor..")
cursor = xyron_sql.cursor()

def wait_for_keypress():
    console.print("Press enter to continue..")
    keypress = input()

def check_for_database():
    console.log("Checking for database..", style=neutral_style)
    cursor.execute("show databases")
    database_list = []
    for dbs in cursor:
        database_list.append(dbs[0])
    if "xyron_database" in database_list:
        console.log("Database found", style=success_style)
        cursor.execute("use xyron_database")
        console.log("Connected to database", style=success_style)
    else:
        console.log("Database not found! Creating new database..", style=caution_style)
        cursor.execute("create database xyron_database")
        cursor.execute("use xyron_database")
        console.log("New database created", style=success_style)
        console.log("Creating Table..", style=caution_style)
        cursor.execute("create table main_table(project_id int auto_increment primary key, project_name varchar(1200), project_table varchar(1203), project_author varchar(120), project_summary varchar(5000))")
        console.log("Table created successfully", style=success_style)

def get_project_details():
    project_id = IntPrompt.ask("Enter project ID: ")

    cursor.execute("select project_id, project_name, project_table from main_table")
    projects_list = cursor.fetchall()

    found = False

    for projects in projects_list:
        if project_id in projects:
            found = True
            project_name, project_table = projects[1], projects[2]
            break
        else:
            pass
    
    if found == False:
        console.print("Project not found! Please enter valid ID")
    else:
        return project_id, project_name, project_table

def create_project(): # REQUIRES RICH TEXT
    project_name = console.input("Enter project name: ")

    # Check if duplicate
    cursor.execute("select project_name from main_table")
    project_list = cursor.fetchall()
    duplicate = False
    for project in project_list:
        if project_name in project:
            duplicate = True
            console.print(f"{project_name} already exists!")
        else:
            pass
    if duplicate == False:
        # Insert into main_table
        project_table = project_name + "_table"
        sql_string = "insert into main_table (project_name, project_table) values (%s, %s)"
        values = (project_name, project_table)
        cursor.execute(sql_string, values)
        xyron_sql.commit()

        # Make project_table
        cursor.execute(f"create table {project_table}(ch_no int primary key, tl varchar(10), pr varchar(10), ts varchar(10), qc varchar(10), status varchar(20))")

        console.print(f"Successfully created {project_name}!")

    wait_for_keypress()

def list_projects(): # REQUIRES RICH TEXT
    cursor.execute("select project_id, project_name from main_table")
    projects_list = cursor.fetchall()

    if len(projects_list) >= 1:
        table = Table(Column(header="Project ID", justify="right"), "Project Name", title="Projects", row_styles=["", "dim"])

        for projects in projects_list:
            table.add_row(str(projects[0]), projects[1])
        
        console.print(table, justify="center")
    else:
        console.print("No projects available..", justify="center")

    wait_for_keypress()

def view_project(): # REQUIRES RICH TEXT
    project_id, project_name, project_table = get_project_details()

    while True:
        # Render Menu with Header
        os.system('cls')
        header("View Project")
        console.print(f"{Xyron.view_menu_options}", style="#74c69d", justify="center")
        console.print("[#ff97b7 bold]↓ ↓  Enter Your Choice ↓ ↓ [/]", justify="center")
        choice = Prompt.ask("[purple]►[/]", choices=Xyron.view_menu_list)

        if choice == "add":
            # Get Chapter Number from User
            ch_no = IntPrompt.ask("Input chapter number: ")

            # Check if duplicate
            cursor.execute(f"select ch_no from {project_table}")
            chapter_no_list = cursor.fetchall()
            duplicate = False
            for chapter in chapter_no_list:
                if ch_no in chapter:
                    duplicate = True
                    console.print(f"Chapter {ch_no} already exists!")
                    break
                else:
                    pass
            if duplicate == False:
                # Commit to table
                sql_string = f"insert into {project_table} (ch_no, tl, pr, ts, qc, status) values (%s, %s, %s, %s, %s, %s)"
                values = (ch_no, "pending", "pending", "pending", "pending", "pending")
                cursor.execute(sql_string, values)
                xyron_sql.commit()

                console.print(f"Added chapter {ch_no}!")

            wait_for_keypress()

        elif choice == "list":
            # Get chapter list from table
            cursor.execute(f"select * from {project_table}")
            chapters_list = cursor.fetchall()
            
            if len(chapters_list) >= 1:
                table = Table(Column(header="Chapter No.", justify="right"),
                                        Column(header="TL", justify="center"),
                                        Column(header="PR", justify="center"),
                                        Column(header="TS", justify="center"),
                                        Column(header="QC", justify="center"),
                                        Column(header="Status", justify="left"),
                                        title=f"{project_name}",
                                        row_styles=["", "dim"])

                for chapters in chapters_list:
                    table.add_row(str(chapters[0]), chapters[1], chapters[2], chapters[3], chapters[4], chapters[5])
                
                console.print(table, justify="center")
            else:
                console.print("No chapters available..", justify="center")

            wait_for_keypress()

        elif choice == "update":
            # Get Chapter Details from User
            ch_no = IntPrompt.ask("Input chapter number: ")

            # Check if chapter exists
            cursor.execute(f"select ch_no from {project_table}")
            chapter_no_list = cursor.fetchall()
            
            found = False

            for chapter in chapter_no_list:
                if ch_no in chapter:
                    found = True
                    # Update details
                    tl = Prompt.ask("Enter TL status - ", choices=Xyron.role_status_list)
                    pr = Prompt.ask("Enter PR status - ", choices=Xyron.role_status_list)
                    ts = Prompt.ask("Enter TS status - ", choices=Xyron.role_status_list)
                    qc = Prompt.ask("Enter QC status - ", choices=Xyron.role_status_list)
                    status = Prompt.ask("Enter chapter status - ", choices=Xyron.chapter_status_list)
                    
                    cursor.execute(f"update {project_table} set tl = '{tl}', pr = '{pr}', ts = '{ts}', qc = '{qc}', status = '{status}' where ch_no = '{ch_no}'")

                    console.print(f"Updated chapter {ch_no}")
                else:
                    pass
            
            if found == False:
                console.print(f"{ch_no} not found! Try again!")
            
            wait_for_keypress()

        elif choice == "delete":
            # Get Chapter Number from User
            ch_no = IntPrompt.ask("Input chapter number: ")
            
            #Check if chapter exists
            cursor.execute(f"select ch_no from {project_table}")
            chapter_no_list = cursor.fetchall()

            for chapter in chapter_no_list:
                if ch_no in chapter:
                    confirm = Confirm.ask(f"Do you want to delete chapter {ch_no}?")

                    if confirm == True:
                        cursor.execute(f"delete from {project_table} where ch_no = '{ch_no}'")
                        xyron_sql.commit()
                        console.print(f"Deleted chapter {ch_no}!")
                    else:
                        pass
            
            wait_for_keypress()

        elif choice == "home":
            break

        else:
            console.print(":warning: Error", style=warning_style)

def update_project():
    pass

def delete_project():
    project_id, project_name, project_table = get_project_details()

    confirm = Confirm.ask(f"Do you want to delete {project_name}?")

    if confirm == True:
        cursor.execute(f"drop table {project_table}")
        cursor.execute(f"delete from main_table where project_id = {project_id}")
    else:
        pass

    console.print(f"Deleted project {project_name}")

    wait_for_keypress()

def header(text, on_start_text = None):
    console.print(f"{Xyron.title_name}", style="#90be6d", justify="center")
    console.print("A Project by Senpai Spinicle\nA.K.A  Yadunandana Reddy M\n", style="#f9c74f", justify="center")
    if on_start_text == None:
        pass
    else:
        console.print(f"{on_start_text}\n", style="purple", justify="center")
    console.rule(f"[#43aa8b]{text}", style="#90be6d")

def main_menu(start_text = False, text = None):
    if start_text == True:
        header("Home Page", text)
    else:
        header("Home Page")
    console.print(f"{Xyron.main_menu_options}", style="#74c69d", justify="center")

def main_menu_parser(choice):
    if choice == "exit":
        sys.exit()
    elif choice == "create":
        create_project()
    elif choice == "list":
        list_projects()
    elif choice == "view":
        view_project()
    elif choice == "update":
        update_project()
    elif choice == "delete":
        delete_project()
    else:
        console.print(":warning: Error", style=warning_style)

if __name__ == "__main__" :

    with console.status("Doing pre-launch checks...", spinner="arc"):
        check_for_database()

    # Clear Screen Before Rendering
    os.system("cls")
    # Main Loop
    while True:
        os.system("cls")
        # Render Main Menu with Header
        main_menu(False)
        console.print("[#ff97b7 bold]↓ ↓  Enter Your Choice ↓ ↓ [/]", justify="center")
        choice = Prompt.ask("[purple]►[/]", choices=Xyron.main_menu_list)
        main_menu_parser(choice)