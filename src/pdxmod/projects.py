import sys

from pdxmod.project.project import create_project, initialize, list_projects

initialize()


def main():
    if len(sys.argv) == 1:
        help()
        return
    else:
        
        if sys.argv[1] == "create":
            create_project()
        elif sys.argv[1] == "manage":
            pass
        elif sys.argv[1] == "list":
            projects = list_projects()
            for project in projects:
                print(project)
            if len(projects) == 0:
                print("No projects found")
        else:
            print("Unknown command: {cmd}".format(cmd = sys.argv[1]))
            help()

def help():
    print("Paradox' mod project management tool.")
    print("Usage: pdxmod [command] [args]...")
    print("Commands:")
    print("  create [project_name]: create a new project")
    print("  manage: Enter interactive management mode")
    print("  list: List projects in current workspace")
    print("  compile [project_name]: Compile a project in to ready for distribution mod")