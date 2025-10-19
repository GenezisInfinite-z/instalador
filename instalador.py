import os
import sys
import PyInstaller.__main__
from pathlib import Path

def get_script_directory():
    """Retorna o diretório onde está localizado este script"""
    return os.path.dirname(os.path.abspath(__file__))

def get_user_config():
    """Solicita configurações do usuário (nome da imagem e diretório de trabalho)"""
    print("\n=== CONFIGURAÇÕES ===")
    
    # Nome da imagem
    default_image_name = "chefe-de-cozinha"
    image_name = input(f"Nome da imagem (sem extensão) [{default_image_name}]: ").strip()
    if not image_name:
        image_name = default_image_name
    
    # Diretório de trabalho (onde estão os arquivos Python, imagens e onde serão salvos os executáveis)
    script_dir = get_script_directory()
    print(f"Diretório do script instalador: {script_dir}")
    work_dir = input(f"Diretório de trabalho (onde estão seus arquivos Python): ").strip()
    
    if not work_dir:
        print("❌ É necessário especificar um diretório de trabalho!")
        return get_user_config()
    
    # Normalizar o caminho
    work_dir = os.path.abspath(work_dir)
    
    # Verificar se o diretório existe
    if not os.path.exists(work_dir):
        create_dir = input(f"Diretório '{work_dir}' não existe. Criar? (s/n): ").lower().strip()
        if create_dir in ['s', 'sim', 'y', 'yes']:
            try:
                os.makedirs(work_dir, exist_ok=True)
                print(f"✅ Diretório criado: {work_dir}")
            except Exception as e:
                print(f"❌ Erro ao criar diretório: {e}")
                return get_user_config()
        else:
            return get_user_config()
    
    print(f"📂 Diretório de trabalho definido: {work_dir}")
    return image_name, work_dir

def list_directory_contents(directory):
    """Lista o conteúdo de um diretório para debugging"""
    try:
        print(f"\n🔍 Conteúdo do diretório '{directory}':")
        items = os.listdir(directory)
        if not items:
            print("  (vazio)")
            return
        
        for item in sorted(items):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                print(f"  📁 {item}/")
            elif item.endswith('.py'):
                print(f"  🐍 {item}")
            elif item.endswith(('.png', '.ico')):
                print(f"  🎨 {item}")
            else:
                print(f"  📄 {item}")
    except Exception as e:
        print(f"❌ Erro ao listar diretório: {e}")

def get_image_path(image_name=None, work_dir=None):
    """Retorna o caminho para a imagem de ícone (PNG ou ICO) no diretório de trabalho"""
    if image_name is None:
        image_name = "chefe-de-cozinha"
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return None
    
    ico_path = os.path.join(work_dir, f"{image_name}.ico")
    png_path = os.path.join(work_dir, f"{image_name}.png")
    
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

def get_icon_for_pyinstaller(image_name=None, work_dir=None):
    """Retorna o caminho do ícone apropriado para PyInstaller (deve ser ICO)"""
    if image_name is None:
        image_name = "chefe-de-cozinha"
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return None
    
    ico_path = os.path.join(work_dir, f"{image_name}.ico")
    png_path = os.path.join(work_dir, f"{image_name}.png")
    
    if os.path.exists(ico_path):
        return ico_path
    
    if os.path.exists(png_path):
        if convert_png_to_ico(png_path, ico_path):
            return ico_path
        else:
            return None
    return None

def find_main_file(folder_path):
    """Encontra automaticamente o arquivo principal Python em uma pasta"""
    try:
        py_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
        
        if not py_files:
            return None
        
        # Prioridades de busca
        priority_names = ['main.py', 'app.py', 'run.py', '__main__.py']
        
        # Verificar arquivos prioritários
        for priority in priority_names:
            if priority in py_files:
                return priority
        
        # Se não encontrou arquivo prioritário, usar o primeiro arquivo Python
        return py_files[0]
    except Exception as e:
        print(f"❌ Erro ao buscar arquivos Python em '{folder_path}': {e}")
        return None

def create_executable_from_folder(folder_path, include_all_files=False, work_dir=None, image_name=None):
    """Cria um executável a partir de uma pasta de projeto Python"""
    folder_name = os.path.basename(folder_path)
    
    print(f"\n🔍 Analisando pasta: {folder_path}")
    
    # Verificar se a pasta existe
    if not os.path.exists(folder_path):
        print(f"❌ Pasta '{folder_path}' não existe!")
        return False
    
    # Encontra automaticamente o arquivo principal
    main_file = find_main_file(folder_path)
    
    if not main_file:
        print(f"❌ Nenhum arquivo Python encontrado na pasta {folder_name}!")
        list_directory_contents(folder_path)
        return False
    
    main_path = os.path.join(folder_path, main_file)
    
    print(f"🎯 Arquivo principal detectado automaticamente: {main_file}")
    
    interface_choice = input("Deseja interface gráfica (sem console)? (s/n): ").lower().strip()
    
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return False
    
    args = [
        main_path,
        '--onefile',
        '--distpath', work_dir,
        '--workpath', os.path.join(work_dir, 'build'),
        '--specpath', work_dir,
        f'--name={folder_name}'
    ]

    if interface_choice in ['s', 'sim', 'y', 'yes']:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller(image_name, work_dir)
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
    print(f"📂 Destino: {work_dir}")
    
    original_dir = os.getcwd()
    os.chdir(work_dir)
    try:
        PyInstaller.__main__.run(args)
        print("✅ Executável criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar executável: {e}")
        return False
    finally:
        os.chdir(original_dir)

def create_executable_from_single_file(work_dir=None, image_name=None):
    """Cria um executável de arquivo Python único"""
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return
    
    print(f"\n🔍 Procurando arquivos Python em: {work_dir}")
    
    # Verificar se o diretório existe
    if not os.path.exists(work_dir):
        print(f"❌ Diretório '{work_dir}' não existe!")
        return
    
    try:
        # Buscar arquivos Python no diretório de trabalho
        # Só excluir se for exatamente o mesmo arquivo do script instalador
        py_files = []
        for f in os.listdir(work_dir):
            if f.endswith('.py'):
                file_path = os.path.join(work_dir, f)
                try:
                    # Só excluir se for o mesmo arquivo físico do instalador atual
                    if os.path.samefile(file_path, __file__):
                        continue  # Pular o próprio script instalador
                except:
                    pass  # Se der erro na comparação, incluir o arquivo
                py_files.append(f)
    except Exception as e:
        print(f"❌ Erro ao acessar diretório '{work_dir}': {e}")
        return
    
    if not py_files:
        print("❌ Nenhum arquivo Python encontrado!")
        list_directory_contents(work_dir)
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

    python_path = os.path.join(work_dir, python_file)
    
    # Remover extensão .py para o nome do executável
    exe_name = os.path.splitext(python_file)[0]

    interface_choice = input("Deseja interface gráfica (sem console)? (s/n): ").lower().strip()
    
    args = [
        python_path,
        '--onefile',
        '--distpath', work_dir,
        '--workpath', os.path.join(work_dir, 'build'),
        '--specpath', work_dir,
        f'--name={exe_name}'
    ]

    if interface_choice in ['s', 'sim', 'y', 'yes']:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller(image_name, work_dir)
    if icon_path:
        args.extend(['--icon', icon_path])
        print(f"🎨 Usando ícone: {os.path.basename(icon_path)}")
    else:
        print(f"⚠️ Nenhum ícone encontrado (adicione {image_name or 'chefe-de-cozinha'}.png ou .ico no diretório {work_dir})")

    print(f"\n🚀 Criando executável de {python_file}...")
    print(f"📂 Destino: {work_dir}")
    original_dir = os.getcwd()
    os.chdir(work_dir)
    try:
        PyInstaller.__main__.run(args)
        print("✅ Executável criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar executável: {e}")
    finally:
        os.chdir(original_dir)

def process_all_folders(work_dir=None, image_name=None):
    """Processa automaticamente todas as pastas válidas"""
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return
    
    print(f"\n🔍 Procurando pastas em: {work_dir}")
    
    # Verificar se o diretório existe
    if not os.path.exists(work_dir):
        print(f"❌ Diretório '{work_dir}' não existe!")
        return
    
    try:
        folders = [f for f in os.listdir(work_dir) 
                   if os.path.isdir(os.path.join(work_dir, f)) 
                   and not f.startswith('.') 
                   and f not in ['build', 'dist', '__pycache__', 'venv', 'env']]
    except Exception as e:
        print(f"❌ Erro ao acessar diretório '{work_dir}': {e}")
        return

    if not folders:
        print("❌ Nenhuma pasta encontrada para converter!")
        list_directory_contents(work_dir)
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
        folder_path = os.path.join(work_dir, folder)
        print(f"\n{'='*50}")
        print(f"🔄 Processando pasta: {folder}")
        
        main_file = find_main_file(folder_path)
        if not main_file:
            print(f"❌ Nenhum arquivo Python encontrado em {folder}, pulando...")
            continue
        
        if create_executable_for_folder(folder_path, include_all_files, use_noconsole, work_dir, image_name):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Processamento concluído! {success_count}/{len(folders)} pastas convertidas com sucesso.")

def create_executable_for_folder(folder_path, include_all_files=False, use_noconsole=False, work_dir=None, image_name=None):
    """Função auxiliar para criar executável de uma pasta específica"""
    folder_name = os.path.basename(folder_path)
    main_file = find_main_file(folder_path)
    
    if not main_file:
        return False
    
    main_path = os.path.join(folder_path, main_file)
    
    if work_dir is None:
        print("❌ Diretório de trabalho não especificado!")
        return False
    
    args = [
        main_path,
        '--onefile',
        '--distpath', work_dir,
        '--workpath', os.path.join(work_dir, 'build'),
        '--specpath', work_dir,
        f'--name={folder_name}'
    ]

    if use_noconsole:
        args.append('--noconsole')

    icon_path = get_icon_for_pyinstaller(image_name, work_dir)
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
    os.chdir(work_dir)
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
    print("Diretório do script instalador:", get_script_directory())
    
    # Obter configurações do usuário uma vez
    image_name, work_dir = get_user_config()
    
    icon_path = get_image_path(image_name, work_dir)
    if icon_path:
        print(f"🎨 Ícone encontrado: {os.path.basename(icon_path)}")
    else:
        print(f"⚠️ Nenhum ícone encontrado para '{image_name}' em: {work_dir}")

    while True:
        print(f"\n📂 Diretório de trabalho atual: {work_dir}")
        print("\nEscolha uma opção:")
        print("1 - Converter arquivo Python único (.py)")
        print("2 - Converter pasta específica com projeto Python")
        print("3 - Converter TODAS as pastas automaticamente")
        print("l - Listar conteúdo do diretório atual")
        print("c - Alterar configurações")
        print("q - Sair")
        
        choice = input("Digite sua escolha: ").strip().lower()
        
        if choice in ['q', 'quit', 'sair']:
            print("👋 Saindo...")
            break
        elif choice == 'l':
            list_directory_contents(work_dir)
        elif choice == 'c':
            image_name, work_dir = get_user_config()
            icon_path = get_image_path(image_name, work_dir)
            if icon_path:
                print(f"🎨 Ícone encontrado: {os.path.basename(icon_path)}")
            else:
                print(f"⚠️ Nenhum ícone encontrado para '{image_name}' em: {work_dir}")
        elif choice == '1' or choice == '':
            create_executable_from_single_file(work_dir, image_name)
        elif choice == '2':
            try:
                folders = [f for f in os.listdir(work_dir) 
                           if os.path.isdir(os.path.join(work_dir, f)) 
                           and not f.startswith('.') 
                           and f not in ['build', 'dist', '__pycache__', 'venv', 'env']]
            except Exception as e:
                print(f"❌ Erro ao acessar diretório '{work_dir}': {e}")
                continue

            if not folders:
                print("❌ Nenhuma pasta encontrada!")
                list_directory_contents(work_dir)
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

            folder_path = os.path.join(work_dir, folder_name)
            include_all = input("Incluir todos os arquivos da pasta? (s/n): ").lower().strip()
            create_executable_from_folder(folder_path, include_all_files=(include_all in ['s','sim','y','yes']), work_dir=work_dir, image_name=image_name)
        elif choice == '3':
            process_all_folders(work_dir, image_name)
        else:
            print("❌ Opção inválida! Escolha 1, 2, 3, l, c ou q")

if __name__ == "__main__":
    main()
