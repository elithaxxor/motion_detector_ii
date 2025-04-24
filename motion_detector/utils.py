import yaml
import logging
import os

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    return logging.getLogger('MotionDetector')

def ensure_log_file(log_file):
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write('Motion Detection Log\n')
