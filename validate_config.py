import difflib
import sys
import os

# Archivos a comparar
FILES = [
    (".env", ".env.produccion"),
    ("docker-compose.yml", "docker-compose.produccion.yml"),
    ("nginx/nginx.conf", "nginx/nginx.conf.produccion"),
]

def read_file(path):
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        return []
    with open(path, "r") as f:
        return f.readlines()

def compare_files(local, remote):
    local_lines = read_file(local)
    remote_lines = read_file(remote)
    diff = list(difflib.unified_diff(local_lines, remote_lines, fromfile=local, tofile=remote))
    if diff:
        print(f"\nDiferencias encontradas entre {local} y {remote}:")
        print("".join(diff))
    else:
        print(f"\nNo hay diferencias entre {local} y {remote}.")

def main():
    print("\n=== VALIDACIÓN DE CONFIGURACIÓN LOCAL VS PRODUCCIÓN ===")
    for local, remote in FILES:
        compare_files(local, remote)
    print("\nRevisa las diferencias antes de actualizar archivos en producción.")
    print("Si hay cambios en credenciales, servicios, puertos o claves secretas, realiza migraciones y reinicia servicios.")

if __name__ == "__main__":
    main()
