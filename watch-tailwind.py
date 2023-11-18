import subprocess

commandline = ('npx tailwindcss -i ./dj_admin_plus/static/dj-admin-plus/scss/style.scss '
               '-o ./dj_admin_plus/static/dj-admin-plus/css/style.css --watch')
subprocess.call(commandline.split(' '))
