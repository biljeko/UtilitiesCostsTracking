import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3

class CategoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Catégories")

        # Ajuster la taille de la fenêtre
        self.root.geometry("500x700")

        self.create_widgets()
        self.load_categories()

    def create_widgets(self):
        # Créer un cadre pour la liste des catégories
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill=tk.BOTH, expand=True)

        # Créer un tableau pour afficher les catégories
        self.tree = ttk.Treeview(self.list_frame, columns=("Nom", "Groupe"), show="headings")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Groupe", text="Groupe")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Ajouter une barre de défilement
        self.scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.scrollbar.set)

        # Créer un cadre pour les boutons de gestion
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="Ajouter", command=self.add_category)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Supprimer", command=self.delete_category)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.edit_button = tk.Button(self.button_frame, text="Modifier", command=self.edit_category)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.move_up_button = tk.Button(self.button_frame, text="Déplacer Haut", command=self.move_up)
        self.move_up_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.move_down_button = tk.Button(self.button_frame, text="Déplacer Bas", command=self.move_down)
        self.move_down_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Sauvegarder", command=self.save_changes)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_categories(self):
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom, groupe, position FROM services ORDER BY position")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_category(self):
        # Demander le nom et le groupe de la nouvelle catégorie
        new_name = simpledialog.askstring("Nouvelle Catégorie", "Nom de la nouvelle catégorie :")
        new_group = simpledialog.askstring("Nouveau Groupe", "Nom du groupe :")

        if new_name and new_group:
            # Ajouter la catégorie dans l'affichage
            position = len(self.tree.get_children()) + 1
            if position <= 20:  # Limiter à 20 éléments
                self.tree.insert("", tk.END, values=(new_name, new_group, position))
                # Ajouter la nouvelle catégorie à la base de données
                conn = sqlite3.connect('services.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO services (nom, groupe, position) VALUES (?, ?, ?)", (new_name, new_group, position))
                conn.commit()
                conn.close()
                messagebox.showinfo("Ajouté", f"La catégorie '{new_name}' a été ajoutée avec succès.")
            else:
                messagebox.showwarning("Limite atteinte", "Vous ne pouvez pas ajouter plus de 20 catégories.")

    def delete_category(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une catégorie", "Veuillez sélectionner une catégorie à supprimer.")
            return

        category_name = self.tree.item(selected_item, 'values')[0]

        # Demander une confirmation avant de supprimer
        confirm = messagebox.askyesno("Supprimer", f"Voulez-vous vraiment supprimer la catégorie '{category_name}' ?")
        if confirm:
            # Supprimer la catégorie de l'affichage
            self.tree.delete(selected_item)
            # Supprimer la catégorie de la base de données
            conn = sqlite3.connect('services.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE nom = ?", (category_name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Supprimé", f"La catégorie '{category_name}' a été supprimée avec succès.")

    def edit_category(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une catégorie", "Veuillez sélectionner une catégorie à modifier.")
            return

        current_name, current_group, _ = self.tree.item(selected_item, 'values')

        # Demander à l'utilisateur le nouveau nom et le nouveau groupe
        new_name = simpledialog.askstring("Modifier Nom", f"Modifier le nom de la catégorie (actuel: {current_name}):")
        new_group = simpledialog.askstring("Modifier Groupe", f"Modifier le groupe de la catégorie (actuel: {current_group}):")

        if new_name and new_group:
            self.tree.item(selected_item, values=(new_name, new_group, self.tree.item(selected_item, 'values')[2]))

    def move_up(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une catégorie", "Veuillez sélectionner une catégorie à déplacer.")
            return

        index = self.tree.index(selected_item)
        if index == 0:
            messagebox.showwarning("Déplacement", "La catégorie est déjà en haut.")
            return

        prev_item = self.tree.get_children()[index - 1]
        self.swap_items(selected_item, prev_item)

    def move_down(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une catégorie", "Veuillez sélectionner une catégorie à déplacer.")
            return

        index = self.tree.index(selected_item)
        if index == len(self.tree.get_children()) - 1:
            messagebox.showwarning("Déplacement", "La catégorie est déjà en bas.")
            return

        next_item = self.tree.get_children()[index + 1]
        self.swap_items(selected_item, next_item)

    def swap_items(self, item1, item2):
        values1 = self.tree.item(item1, 'values')
        values2 = self.tree.item(item2, 'values')
        self.tree.item(item1, values=values2)
        self.tree.item(item2, values=values1)

    def save_changes(self):
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()

        # Réorganiser les catégories
        for index, item in enumerate(self.tree.get_children()):
            category_name, category_group, _ = self.tree.item(item, 'values')
            cursor.execute(''' 
                UPDATE services
                SET nom = ?, groupe = ?, position = ?
                WHERE nom = ?
            ''', (category_name, category_group, index + 1, category_name))

        conn.commit()
        conn.close()
        messagebox.showinfo("Sauvegarde", "Les modifications ont été sauvegardées.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CategoryManager(root)
    root.mainloop()
