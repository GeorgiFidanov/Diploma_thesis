import subprocess
import platform


python_command = 'python' if platform.system().lower() == 'windows' else 'python3'

subprocess.Popen(['cmd', '/c', 'start', python_command, 'loader.py'])

subprocess.Popen(['cmd', '/c', 'start', python_command, 'server.py'])

subprocess.Popen(['cmd', '/c', 'start', python_command, 'main.py'])
