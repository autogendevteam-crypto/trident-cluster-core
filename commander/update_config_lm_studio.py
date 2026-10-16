import json
import pathlib

p = pathlib.Path('config.json')
c = json.loads(p.read_text(encoding='utf-8-sig'))

c.setdefault('paths', {})
c['paths']['lm_studio_exe'] = r'C:\Program Files\Bionic\Bionic.exe'
c['paths']['lms_cli'] = r'C:\Program Files\Bionic\resources\app\.webpack-bionic\lms.exe'
c['paths'].setdefault('gateway_script', r'C:\ecosistema\TRIDENT_Project\gateway\gateway.py')
c['paths'].setdefault('work_dir', r'C:\ecosistema\TRIDENT_Project\gateway')
c['paths'].setdefault('python_exe', '')

c.setdefault('ports', {})
c['ports'].setdefault('gateway', 4000)
c['ports'].setdefault('lm_studio', 1234)

c.setdefault('commands', {})
c['commands'].setdefault('start_gateway', ['python', 'gateway.py'])
c['commands'].setdefault('check_health_endpoint', 'http://localhost:4000/v1/models')

c.setdefault('lm_studio', {})
c['lm_studio']['auto_load_models'] = [
    'text-embedding-bge-m3'
]
c['lm_studio']['known_models'] = [
    'text-embedding-bge-m3',
    'qwen2.5-coder-7b-instruct',
    'qwen2.5-vl-7b-instruct',
    'text-embedding-nomic-embed-text-v1.5'
]
c['lm_studio'].setdefault('load_timeout_seconds', 90)
c['lm_studio'].setdefault('restart_server_before_load', True)
c['lm_studio'].setdefault('verify_loaded_models_endpoint', '/v1/models')

c.setdefault('health', {})
c['health'].setdefault('model', 'bionic')
c['health'].setdefault('prompt', 'ping')
c['health'].setdefault('max_latency_s', 5)
c['health'].setdefault('timeout_s', 30)
c['health'].setdefault('api_key_env', '')
c['health'].setdefault('required_embedding_model', 'text-embedding-bge-m3')
c['health'].setdefault('optional_chat_model', 'bionic')
c['health'].setdefault('test_embeddings', False)
c['health'].setdefault('test_chat_if_model_loaded', True)

c.setdefault('options', {})
c['options'].setdefault('max_log_lines', 1000)
c['options'].setdefault('poll_interval_s', 2)
c['options'].setdefault('stop_gateway_on_exit', True)
c['options'].setdefault('kill_lm_studio_on_exit', False)

p.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding='utf-8')
print('CONFIG UPDATED')
