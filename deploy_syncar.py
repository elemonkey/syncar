import difflib
import os
import subprocess

# Archivos a comparar y copiar
FILES = [
    (".env", ".env.produccion"),
    ("docker-compose.yml", "docker-compose.produccion.yml"),
    ("nginx/nginx.conf", "nginx/nginx.conf.produccion"),
]

# Configuración del servidor
SERVER_USER = "root"
SERVER_IP = "vmi2793682.contaboserver.net"
SERVER_PATH = "/www/wwwroot/syncar.cl/"

# Validación de diferencias

def read_file(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return f.readlines()

def compare_files(local, remote):
    local_lines = read_file(local)
    remote_lines = read_file(remote)
    diff = list(difflib.unified_diff(local_lines, remote_lines, fromfile=local, tofile=remote))
    return diff

def validate_and_deploy():
    print("\n=== VALIDACIÓN Y DEPLOY AUTOMÁTICO SYNCAR ===")
    all_ok = True
    for local, remote in FILES:
        diff = compare_files(local, remote)
        if diff:
            print(f"\nDiferencias encontradas entre {local} y {remote}:")
            print("".join(diff))
            # Si hay diferencias críticas, marca como no OK
            for line in diff:
                if any(word in line for word in ["POSTGRES", "SECRET_KEY", "depends_on", "ports", "volumes"]):
                    all_ok = False
    if not all_ok:
        print("\n⚠️  Hay diferencias críticas. Revisa antes de continuar el deploy.")
        return
    print("\nNo hay diferencias críticas. Procediendo con copia automática de archivos...")
    # 1. Verificar migraciones Alembic local
    print("\nVerificando migraciones Alembic en local...")
    result_local = subprocess.run(["alembic", "current"], capture_output=True, text=True)
    print("Migración actual local:", result_local.stdout.strip())

    # 2. Verificar migraciones Alembic en producción (por SSH)
    print("\nVerificando migraciones Alembic en producción...")
    ssh_cmd = f"ssh {SERVER_USER}@{SERVER_IP} 'cd {SERVER_PATH}backend && alembic current'"
    result_prod = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    print("Migración actual producción:", result_prod.stdout.strip())

    if result_local.stdout.strip() != result_prod.stdout.strip():
        print("\n⚠️  Las migraciones Alembic no coinciden entre local y producción. Deteniendo deploy.")
        return

    # 3. Copiar .env.produccion como .env en el servidor
    env_src = ".env.produccion"
    env_dest = SERVER_PATH + ".env"
    print(f"Copiando {env_src} a {env_dest} en el servidor...")
    subprocess.run(["scp", env_src, f"{SERVER_USER}@{SERVER_IP}:{env_dest}"])

    # 4. Copiar los demás archivos normalmente
    for local, _ in FILES:
        if local == ".env":
            continue  # No copiar el .env local
        dest = SERVER_PATH + os.path.basename(local)
        print(f"Copiando {local} a {dest} en el servidor...")
        subprocess.run(["scp", local, f"{SERVER_USER}@{SERVER_IP}:{dest}"])

    # 5. Reiniciar servicios Docker Compose en el servidor
    print("\nReiniciando servicios Docker Compose en el servidor...")
    restart_cmd = f"ssh {SERVER_USER}@{SERVER_IP} 'cd {SERVER_PATH} && docker-compose down && docker-compose up -d'"
    subprocess.run(restart_cmd, shell=True)
    print("\n✔️  Archivos copiados y servicios reiniciados automáticamente.")

if __name__ == "__main__":
    validate_and_deploy()
