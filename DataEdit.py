import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Consultation de la Base de Données")

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Création de la vue en tableau pour afficher les données
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nom", "Groupe", "Coût"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Groupe", text="Groupe")
        self.tree.heading("Coût", text="Coût")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Barre de défilement verticale
        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.scrollbar.set)

        # Boutons de gestion
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="Ajouter", command=self.add_data)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.edit_button = tk.Button(self.button_frame, text="Modifier", command=self.edit_data)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Supprimer", command=self.delete_data)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_data(self):
        # Connexion à la base de données et chargement des données
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, groupe, cout FROM services")
        rows = cursor.fetchall()
        conn.close()

        # Afficher les données dans la table
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_data(self):
        # Ajouter une nouvelle entrée à la base de données
        new_nom = simpledialog.askstring("Ajouter", "Nom du service:")
        new_groupe = simpledialog.askstring("Ajouter", "Groupe du service:")
        new_cout = simpledialog.askstring("Ajouter", "Coût du service:")

        if new_nom and new_groupe and new_cout:
            try:
                conn = sqlite3.connect('services.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO services (nom, groupe, cout) VALUES (?, ?, ?)",
                               (new_nom, new_groupe, float(new_cout)))
                conn.commit()
                conn.close()
                self.tree.insert("", tk.END, values=(cursor.lastrowid, new_nom, new_groupe, new_cout))
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ajouter le service : {e}")
        else:
            messagebox.showwarning("Annulé", "Ajout annulé.")

    def edit_data(self):
        # Modifier une entrée existante
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une entrée", "Veuillez sélectionner une entrée à modifier.")
            return

        item = self.tree.item(selected_item)
        current_id, current_nom, current_groupe, current_cout = item['values']

        new_nom = simpledialog.askstring("Modifier", f"Modifier le nom (actuel: {current_nom}):")
        new_groupe = simpledialog.askstring("Modifier", f"Modifier le groupe (actuel: {current_groupe}):")
        new_cout = simpledialog.askstring("Modifier", f"Modifier le coût (actuel: {current_cout}):")

        if new_nom and new_groupe and new_cout:
            try:
                conn = sqlite3.connect('services.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE services 
                    SET nom = ?, groupe = ?, cout = ? 
                    WHERE id = ?''', (new_nom, new_groupe, float(new_cout), current_id))
                conn.commit()
                conn.close()
                self.tree.item(selected_item, values=(current_id, new_nom, new_groupe, new_cout))
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de modifier le service : {e}")
        else:
            messagebox.showwarning("Annulé", "Modification annulée.")

    def delete_data(self):
        # Supprimer une entrée
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélectionnez une entrée", "Veuillez sélectionner une entrée à supprimer.")
            return

        item = self.tree.item(selected_item)
        current_id = item['values'][0]

        confirm = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette entrée ?")
        if confirm:
            try:
                conn = sqlite3.connect('services.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM services WHERE id = ?", (current_id,))
                conn.commit()
                conn.close()
                self.tree.delete(selected_item)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer le service : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()
