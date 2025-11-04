import os
import sys

print("=" * 60)
print("DIAGNÓSTICO - Sistema de Viagens")
print("=" * 60)
print()

# 1. Diretório atual
print("1. Diretório atual:")
print(f"   {os.getcwd()}")
print()

# 2. Arquivos na raiz
print("2. Arquivos na raiz do projeto:")
root_files = os.listdir('.')
for f in sorted(root_files):
    tipo = "DIR " if os.path.isdir(f) else "FILE"
    print(f"   [{tipo}] {f}")
print()

# 3. Verificar manage.py
print("3. Verificar manage.py:")
if os.path.exists('manage.py'):
    print("   ✓ manage.py existe")
    with open('manage.py', 'r', encoding='utf-8') as f:
        for line in f:
            if 'DJANGO_SETTINGS_MODULE' in line:
                print(f"   Settings: {line.strip()}")
else:
    print("   ✗ manage.py NÃO EXISTE!")
print()

# 4. Estrutura travel_system
print("4. Estrutura de travel_system/:")
if os.path.exists('travel_system'):
    print("   ✓ travel_system/ existe")
    ts_contents = os.listdir('travel_system')
    for item in sorted(ts_contents):
        print(f"     - {item}")

    # Verificar travel_system/travel_system
    if os.path.exists('travel_system/travel_system'):
        print("   ✓ travel_system/travel_system/ existe")
        ts_ts_contents = os.listdir('travel_system/travel_system')
        for item in sorted(ts_ts_contents):
            print(f"     - {item}")
    else:
        print("   ✗ travel_system/travel_system/ NÃO EXISTE!")
else:
    print("   ✗ travel_system/ NÃO EXISTE!")
print()

# 5. Verificar settings.py
print("5. Verificar settings.py:")
settings_path = 'travel_system/travel_system/settings.py'
if os.path.exists(settings_path):
    print(f"   ✓ {settings_path} existe")
else:
    print(f"   ✗ {settings_path} NÃO EXISTE!")
    # Verificar se está no lugar errado
    if os.path.exists('travel_system/settings.py'):
        print("   ! ENCONTRADO EM: travel_system/settings.py (LUGAR ERRADO!)")
print()

# 6. Verificar app travels
print("6. Verificar app travels/:")
if os.path.exists('travels'):
    print("   ✓ travels/ existe na raiz")
    travels_contents = os.listdir('travels')
    for item in sorted(travels_contents)[:10]:  # Primeiros 10
        print(f"     - {item}")
else:
    print("   ✗ travels/ NÃO EXISTE na raiz!")
    if os.path.exists('travel_system/travels'):
        print("   ! ENCONTRADO EM: travel_system/travels/ (LUGAR ERRADO!)")
print()

# 7. Python path
print("7. Python sys.path:")
for p in sys.path[:5]:
    print(f"   - {p}")
print()

print("=" * 60)
print("INSTRUÇÕES:")
print("=" * 60)
print()
print("Se você vir erros acima (marcados com ✗ ou !), siga estas etapas:")
print()
print("1. Certifique-se de ter feito git pull:")
print("   git pull origin claude/python-web-system-011CUnvy6V18t2okhcMagtMQ")
print()
print("2. A estrutura correta deve ser:")
print("   ✓ manage.py (na raiz)")
print("   ✓ travel_system/travel_system/settings.py")
print("   ✓ travels/ (na raiz)")
print()
print("3. Se settings.py estiver em travel_system/settings.py (sem duplicar pasta),")
print("   então você precisa fazer git pull novamente.")
print()
