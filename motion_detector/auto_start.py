import os
import sys
import getpass

SYSTEMD_SERVICE_TEMPLATE = '''
[Unit]
Description=Motion Detector Camera Service
After=network.target

[Service]
ExecStart={python_exe} {script_path}
Restart=always
User={user}
WorkingDirectory={workdir}

[Install]
WantedBy=multi-user.target
'''

def install_systemd_service(service_name, script_path):
    python_exe = sys.executable
    user = getpass.getuser()
    workdir = os.path.dirname(script_path)
    service_content = SYSTEMD_SERVICE_TEMPLATE.format(
        python_exe=python_exe,
        script_path=script_path,
        user=user,
        workdir=workdir
    )
    service_path = f'/etc/systemd/system/{service_name}.service'
    with open('/tmp/tmp_motion_service.service', 'w') as f:
        f.write(service_content)
    print(f"Run the following as root to enable auto-start:\nsudo mv /tmp/tmp_motion_service.service {service_path}\nsudo systemctl daemon-reload\nsudo systemctl enable {service_name}\nsudo systemctl start {service_name}")

def uninstall_systemd_service(service_name):
    print(f"Run the following as root to disable auto-start:\nsudo systemctl stop {service_name}\nsudo systemctl disable {service_name}\nsudo rm /etc/systemd/system/{service_name}.service\nsudo systemctl daemon-reload")
