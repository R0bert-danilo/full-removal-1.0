import os
import winreg
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from win32com.client import GetObject
from elevate import elevate

elevate(show_console=False)

# Cores e fontes
cor_fundo = '#f5f5f5'
cor_botoes = '#007bff'
cor_texto = '#333'
fonte_padrao = ("Segoe UI", 12)
fonte_titulo = ("Segoe UI", 14, "bold")

def select_files():
    file_paths = filedialog.askopenfilenames(title="Selecione os arquivos para excluir")
    if file_paths:
        listbox_files.delete(0, END)
        for path in file_paths:
            listbox_files.insert(END, path)

def delete_files():
    file_paths = listbox_files.get(0, END)
    if not file_paths:
        messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
        return

    num_files = len(file_paths)
    if num_files == 1:
        confirm_message = f"Deseja apagar o arquivo:\n{file_paths[0]}?"
    else:
        confirm_message = f"Deseja apagar {num_files} arquivos selecionados?"

    if messagebox.askyesno("Confirmação", confirm_message):
        for path in file_paths:
            try:
                os.remove(path)
                listbox_files.delete(listbox_files.get(0, END).index(path))
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir o arquivo {path}. Erro: {e}")

        messagebox.showinfo("Sucesso", "Arquivos excluídos com sucesso!")

def delete_registry_entry():
    key_paths = listbox_registry_paths.get(0, END)
    value_name = entry_value_name.get()

    if not key_paths:
        messagebox.showwarning("Aviso", "Nenhum caminho de chave do registro fornecido.")
        return

    for key_path in key_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if value_name:
                    winreg.DeleteValue(key, value_name)
                else:
                    winreg.DeleteKey(key, "")
            listbox_registry_paths.delete(0, END)
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Chave ou valor do registro {key_path} não encontrado.")
        except PermissionError:
            messagebox.showerror("Erro", "Permissões insuficientes para excluir a entrada do registro.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir a entrada do registro: {e}")

    messagebox.showinfo("Sucesso", "Entradas do registro excluídas com sucesso!")

def add_registry_path():
    key_path = entry_key_path.get()
    if key_path:
        listbox_registry_paths.insert(END, key_path)
        entry_key_path.delete(0, END)

def get_installed_programs():
    programs = []
    try:
        obj = GetObject("winmgmts://")
        col_items = obj.ExecQuery("Select * from Win32_Product")
        for item in col_items:
            programs.append(item.Name)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao listar programas instalados: {e}")
    return programs

def uninstall_program():
    program_name = combo_programs.get()
    if not program_name:
        messagebox.showwarning("Aviso", "Nenhum programa selecionado.")
        return

    try:
        subprocess.run(["wmic", "product", "where", f"name='{program_name}'", "call", "uninstall"], check=True)
        messagebox.showinfo("Sucesso", "Programa desinstalado com sucesso!")
        update_programs_list()
    except subprocess.CalledProcessError:
        messagebox.showerror("Erro", "Erro ao desinstalar o programa. Verifique se o nome do programa está correto.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao desinstalar o programa: {e}")

def update_programs_list():
    programs = get_installed_programs()
    combo_programs['values'] = programs
    if programs:
        combo_programs.set(programs[0])
    else:
        combo_programs.set("Nenhum programa encontrado")

janela = Tk()
janela.title('Full Removal')
janela.geometry('800x600')
janela.config(bg=cor_fundo)
janela.iconphoto(False, PhotoImage(file='raio.png'))
janela.resizable(width=False, height=False)

notebook = ttk.Notebook(janela)
notebook.pack(expand=True, fill=BOTH)

frame_files = Frame(notebook, bg=cor_fundo)
notebook.add(frame_files, text="Manipulação de Arquivos")

label_files = Label(frame_files, text="Arquivos Selecionados:", bg=cor_fundo, fg=cor_texto, font=fonte_titulo)
label_files.pack(pady=10)

scrollbar_files = Scrollbar(frame_files)
scrollbar_files.pack(side=RIGHT, fill=Y)

listbox_files = Listbox(frame_files, width=80, height=10, bg='white', fg=cor_texto, font=fonte_padrao,
                        selectbackground=cor_botoes, selectforeground='white', yscrollcommand=scrollbar_files.set, bd=1, relief=SOLID)
listbox_files.pack(pady=5)
scrollbar_files.config(command=listbox_files.yview)

button_select = Button(frame_files, text="Selecionar Arquivos", command=select_files, bg=cor_botoes, fg='white', font=fonte_padrao, relief=RAISED)
button_select.pack(pady=5, fill=X)

button_delete = Button(frame_files, text="Excluir Arquivos", command=delete_files, bg=cor_botoes, fg='white', font=fonte_padrao, relief=RAISED)
button_delete.pack(pady=5, fill=X)


frame_registry = Frame(notebook, bg=cor_fundo)
notebook.add(frame_registry, text="Manipulação de Registro")

label_registry = Label(frame_registry, text="Caminhos do Registro:", bg=cor_fundo, fg=cor_texto, font=fonte_titulo)
label_registry.pack(pady=10)

scrollbar_registry = Scrollbar(frame_registry)
scrollbar_registry.pack(side=RIGHT, fill=Y)

listbox_registry_paths = Listbox(frame_registry, width=80, height=10, bg='white', fg=cor_texto, font=fonte_padrao,
                                 selectbackground=cor_botoes, selectforeground='white', yscrollcommand=scrollbar_registry.set, bd=1, relief=SOLID)
listbox_registry_paths.pack(pady=5)
scrollbar_registry.config(command=listbox_registry_paths.yview)

entry_key_path = Entry(frame_registry, width=80, font=fonte_padrao, bd=1, relief=SOLID)
entry_key_path.pack(pady=5)

button_add_path = Button(frame_registry, text="Adicionar Caminho", command=add_registry_path, bg=cor_botoes,
                         fg='white', font=fonte_padrao, relief=RAISED)
button_add_path.pack(pady=5, fill=X)

Label(frame_registry, text="Nome do Valor (deixe em branco para excluir a chave):", bg=cor_fundo, fg=cor_texto,
      font=fonte_padrao).pack(pady=10)
entry_value_name = Entry(frame_registry, width=80, font=fonte_padrao, bd=1, relief=SOLID)
entry_value_name.pack(pady=5)

button_delete_registry = Button(frame_registry, text="Excluir Entradas do Registro", command=delete_registry_entry,
                                bg=cor_botoes, fg='white', font=fonte_padrao, relief=RAISED)
button_delete_registry.pack(pady=10, fill=X)

frame_uninstall = Frame(notebook, bg=cor_fundo)
notebook.add(frame_uninstall, text="Desinstalação de Programas")

label_program = Label(frame_uninstall, text="Selecione o Programa:", bg=cor_fundo, fg=cor_texto, font=fonte_titulo)
label_program.pack(pady=10)

combo_programs = ttk.Combobox(frame_uninstall, width=80, font=fonte_padrao)
combo_programs.pack(pady=5)

button_uninstall = Button(frame_uninstall, text="Desinstalar Programa", command=uninstall_program, bg=cor_botoes, fg='white', font=fonte_padrao, relief=RAISED)
button_uninstall.pack(pady=10, fill=X)

update_programs_list()

janela.mainloop()