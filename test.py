import os

files = ['pipeline.py', 'Agentes.py', 'Agentes/Redactor.py', 'Agentes/Editor.py', 'Agentes/Pulido.py']

for file in files:
    if os.path.exists(file):
        try:
            with open(file, 'rb') as f:
                content = f.read()
                if b'\x00' in content:
                    print(f"Archivo con null bytes: {file}")
        except Exception as e:
            print(f"Error leyendo {file}: {e}")