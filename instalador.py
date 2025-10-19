import os
import sys
import PyInstaller.__main__
from pathlib import Path

def get_script_directory():
    """Retorna o diretório onde está localizado este script"""
    return os.path.dirname(os.path.abspath(__file__))

def get_image_path():
    """Retorna o caminho padrão para a imagem de ícone (PNG ou ICO)"""
    script_dir = get_script_directory()
    ico_path = os.path.join(script_dir, "mico-leao-dourado.ico")
    png_path = os.path.join(script_dir, "mico-leao-dourado.png")
    
    if os.path.exists(ico_path):
        return ico_path
    elif os.path.exists(png_path):
        return png_path
    else:
        return None

def convert_png_to_ico(png_path, ico_path):
    """Converte PNG para ICO usando PIL"""
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"✅ Imagem convertida de PNG para ICO: {ico_path}")
        return True
    except ImportError:
        print("⚠️ PIL (Pillow) não está instalado. Instale com: py -m pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Erro ao converter PNG para ICO: {e}")
        return False

def get_icon_for_pyinstaller():
    """Retorna o caminho do ícone apropriado para PyInstaller (deve ser ICO)"""
    script_dir = get_script_directory()
    ico_path = os.path.join(script_dir, "mico-leao-dourado.ico")
    png_path = os.path.join(script_dir, "mico-leao-dourado.png")
    
    if os.path.exists(ico_path):
        return ico_path
    
    if os.path.exists(png_path):
        if convert_png_to_ico(png_path, ico_path):
            return ico_path
        else:
            return None
    return None

def find_main_file(folder_path):
    """Encontra automaticamente o arquivo principal em uma pasta"""
    python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
    
    if not python_files:
        return None
    
    # Prioridade para arquivos com nomes comuns de entrada
    priority_names = ['main.py', 'app.py', 'run.py', 'start.py', 'index.py']
    
    for priority_name in priority_names:
        if priority_name in python_files:
            return priority_name
    
    # Se não encontrar arquivos prioritários, usa o primeiro arquivo Python
    return python_files[0]

def create_executable_from_folder(folder_path, include_all_files=False):
    """Cria um executável a partir de uma pasta de projeto Python"""
    folder_name = os.path.basename(folder_path)
    
    # Encontra automaticamente o arquivo principal
    main_file = find_main_file(folder_path)
    
    if not main_file:
        print(f"❌ Nenhum arquivo Python encontrado na pasta {folder_name}!")
        return False
    
    main_path = os.path.join(folder_path, main_file)
    
    print(f"🎯 Arquivo principal detectado automaticamente: {main_file}")
    
    interface_choice = input("Deseja interface gráfica (sem console)? (s/n): ").lower().strip()
    
    script_dir = get_script_directory()
    args = [
        main_path,
        '--onefile',
        '--distpath', script_dir,
        '--workpath', os.path.join(script_dir, 'build'),
        '--specpath', script_dir,
        f'--name={folder_name}'
    ]

    if interface_choice in ['s', 'sim', 'y', 'yes']:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller()
    if icon_path:
        args.extend(['--icon', icon_path])
        print(f"🎨 Usando ícone: {os.path.basename(icon_path)}")

    # Incluir todos os arquivos da pasta como dados
    if include_all_files:
        for root, dirs, files in os.walk(folder_path):
            # Ignorar diretórios do sistema
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'build', 'dist']]
            for file in files:
                if file.endswith('.pyc') or file.startswith('.'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, folder_path)
                # Se estiver na raiz, usar apenas o nome do arquivo
                if rel_path == '.':
                    dest_path = file
                else:
                    dest_path = os.path.join(rel_path, file)
                args.extend(['--add-data', f"{full_path}{os.pathsep}{dest_path}"])
        print("📦 Todos os arquivos da pasta serão incluídos no executável.")

    print(f"\n🚀 Criando executável da pasta '{folder_name}'...")
    print(f"📁 Usando arquivo: {main_file}")
    
    original_dir = os.getcwd()
    os.chdir(script_dir)
    try:
        PyInstaller.__main__.run(args)
        print("✅ Executável criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar executável: {e}")
        return False
    finally:
        os.chdir(original_dir)

def create_executable_from_single_file():
    """Cria um executável de arquivo Python único"""
    script_dir = get_script_directory()
    py_files = [f for f in os.listdir(script_dir) if f.endswith('.py') and not f.startswith('instalador')]
    
    if not py_files:
        print("❌ Nenhum arquivo Python encontrado!")
        return

    print("\n📋 Arquivos Python encontrados:")
    for i, py in enumerate(py_files, 1):
        print(f"  {i}. {py}")
    
    escolha = input("Digite o número ou nome do arquivo Python: ").strip()
    if escolha.isdigit():
        num = int(escolha)
        python_file = py_files[num - 1] if 1 <= num <= len(py_files) else None
    else:
        python_file = escolha if escolha.endswith('.py') else escolha+'.py'

    if not python_file or python_file not in py_files:
        print(f"❌ Arquivo {python_file} não encontrado!")
        return

    python_path = os.path.join(script_dir, python_file)
    
    # Remover extensão .py para o nome do executável
    exe_name = os.path.splitext(python_file)[0]

    interface_choice = input("Deseja interface gráfica (sem console)? (s/n): ").lower().strip()
    
    args = [
        python_path,
        '--onefile',
        '--distpath', script_dir,
        '--workpath', os.path.join(script_dir, 'build'),
        '--specpath', script_dir,
        f'--name={exe_name}'
    ]

    if interface_choice in ['s', 'sim', 'y', 'yes']:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller()
    if icon_path:
        args.extend(['--icon', icon_path])
        print(f"🎨 Usando ícone: {os.path.basename(icon_path)}")
    else:
        print("⚠️ Nenhum ícone encontrado (adicione mico-leao-dourado.png ou .ico)")

    print(f"\n🚀 Criando executável de {python_file}...")
    original_dir = os.getcwd()
    os.chdir(script_dir)
    try:
        PyInstaller.__main__.run(args)
        print("✅ Executável criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar executável: {e}")
    finally:
        os.chdir(original_dir)

def process_all_folders():
    """Processa automaticamente todas as pastas válidas"""
    script_dir = get_script_directory()
    folders = [f for f in os.listdir(script_dir) 
               if os.path.isdir(os.path.join(script_dir, f)) 
               and not f.startswith('.') 
               and f not in ['build', 'dist', '__pycache__', 'venv', 'env']]

    if not folders:
        print("❌ Nenhuma pasta encontrada para converter!")
        return

    print("\n📁 Pastas que serão processadas:")
    for i, folder in enumerate(folders, 1):
        print(f"  {i}. {folder}")
    
    include_all = input("Incluir todos os arquivos de cada pasta? (s/n): ").lower().strip()
    include_all_files = (include_all in ['s','sim','y','yes'])
    
    interface_choice = input("Deseja interface gráfica para todas as pastas? (s/n): ").lower().strip()
    use_noconsole = (interface_choice in ['s','sim','y','yes'])
    
    success_count = 0
    for folder in folders:
        folder_path = os.path.join(script_dir, folder)
        print(f"\n{'='*50}")
        print(f"🔄 Processando pasta: {folder}")
        
        main_file = find_main_file(folder_path)
        if not main_file:
            print(f"❌ Nenhum arquivo Python encontrado em {folder}, pulando...")
            continue
        
        if create_executable_for_folder(folder_path, include_all_files, use_noconsole):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Processamento concluído! {success_count}/{len(folders)} pastas convertidas com sucesso.")

def create_executable_for_folder(folder_path, include_all_files=False, use_noconsole=False):
    """Função auxiliar para criar executável de uma pasta específica"""
    folder_name = os.path.basename(folder_path)
    main_file = find_main_file(folder_path)
    
    if not main_file:
        return False
    
    main_path = os.path.join(folder_path, main_file)
    script_dir = get_script_directory()
    
    args = [
        main_path,
        '--onefile',
        '--distpath', script_dir,
        '--workpath', os.path.join(script_dir, 'build'),
        '--specpath', script_dir,
        f'--name={folder_name}'
    ]

    if use_noconsole:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller()
    if icon_path:
        args.extend(['--icon', icon_path])

    if include_all_files:
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'build', 'dist']]
            for file in files:
                if file.endswith('.pyc') or file.startswith('.'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, folder_path)
                if rel_path == '.':
                    dest_path = file
                else:
                    dest_path = os.path.join(rel_path, file)
                args.extend(['--add-data', f"{full_path}{os.pathsep}{dest_path}"])

    original_dir = os.getcwd()
    os.chdir(script_dir)
    try:
        PyInstaller.__main__.run(args)
        print(f"✅ {folder_name} - Executável criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ {folder_name} - Erro ao criar executável: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    print("=== 🚀 CONVERSOR PYTHON PARA EXECUTÁVEL ===")
    print("Diretório atual:", get_script_directory())
    
    icon_path = get_image_path()
    if icon_path:
        print(f"🎨 Ícone encontrado: {os.path.basename(icon_path)}")
    else:
        print("⚠️ Nenhum ícone encontrado")

    while True:
        print("\nEscolha uma opção:")
        print("1 - Converter arquivo Python único (.py)")
        print("2 - Converter pasta específica com projeto Python")
        print("3 - Converter TODAS as pastas automaticamente")
        print("q - Sair")
        
        choice = input("Digite sua escolha: ").strip().lower()
        
        if choice in ['q', 'quit', 'sair']:
            print("👋 Saindo...")
            break
        elif choice == '1' or choice == '':
            create_executable_from_single_file()
        elif choice == '2':
            script_dir = get_script_directory()
            folders = [f for f in os.listdir(script_dir) 
                       if os.path.isdir(os.path.join(script_dir, f)) 
                       and not f.startswith('.') 
                       and f not in ['build', 'dist', '__pycache__', 'venv', 'env']]

            if not folders:
                print("❌ Nenhuma pasta encontrada!")
                continue

            print("\n📁 Pastas encontradas:")
            for i, folder in enumerate(folders, 1):
                print(f"  {i}. {folder}")
            
            escolha = input("Digite o número ou nome da pasta: ").strip()
            if escolha.isdigit():
                num = int(escolha)
                folder_name = folders[num - 1] if 1 <= num <= len(folders) else None
            else:
                folder_name = escolha

            if not folder_name or folder_name not in folders:
                print("❌ Pasta inválida!")
                continue

            folder_path = os.path.join(script_dir, folder_name)
            include_all = input("Incluir todos os arquivos da pasta? (s/n): ").lower().strip()
            create_executable_from_folder(folder_path, include_all_files=(include_all in ['s','sim','y','yes']))
        elif choice == '3':
            process_all_folders()
        else:
            print("❌ Opção inválida! Escolha 1, 2, 3 ou q")

if __name__ == "__main__":
    main()
