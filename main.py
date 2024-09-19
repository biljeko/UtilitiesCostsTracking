import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface de Gestion")

        # Création de la barre de boutons en haut
        self.create_buttons()

        # Zone d'affichage en dessous
        self.display_frame = tk.Frame(root)
        self.display_frame.pack(fill=tk.BOTH, expand=True)

        # Initialiser le formulaire d'ajout de données
        self.add_data_frame = None

    def create_buttons(self):
        # Barre de boutons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X)

        self.add_data_button = tk.Button(button_frame, text="Ajout de données", command=self.show_add_data_form)
        self.add_data_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.generate_graph_button = tk.Button(button_frame, text="Graphique", command=self.run_generate_graph)
        self.generate_graph_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.config_button = tk.Button(button_frame, text="Configuration", command=self.show_config_menu)
        self.config_button.pack(side=tk.LEFT, padx=5, pady=5)

    def show_add_data_form(self):
        self.clear_display_frame()
        if self.add_data_frame is None:
            self.add_data_frame = self.create_add_data_form()
        self.add_data_frame.pack(fill=tk.BOTH, expand=True)

    def create_add_data_form(self):
        frame = tk.Frame(self.display_frame)

        try:
            # Connexion à la base de données pour récupérer les services groupés
            conn = sqlite3.connect('services.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nom, groupe, id FROM services ORDER BY groupe, nom")
            services = cursor.fetchall()  # Liste de tuples (nom, groupe, id)
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à la base de données: {e}")
            return frame

        # Variables pour stocker les champs de coût et les noms de services
        cost_entries = {}
        grouped_services = {}

        # Organiser les services par groupe
        for nom, groupe, service_id in services:
            if groupe not in grouped_services:
                grouped_services[groupe] = []
            grouped_services[groupe].append((service_id, nom))

        # Champs de date
        tk.Label(frame, text="Date de début (AAAA-MM-JJ)").grid(row=0, column=0, padx=10, pady=30)
        date_debut_entry = tk.Entry(frame)
        date_debut_entry.grid(row=0, column=1)

        tk.Label(frame, text="Date de fin (AAAA-MM-JJ)").grid(row=0, column=2, padx=10, pady=10)
        date_fin_entry = tk.Entry(frame)
        date_fin_entry.grid(row=0, column=3)

        # Affichage des groupes en 3 colonnes
        column_index = 0
        row_index = 1
        max_groups_per_column = 2  # Limiter à 2 groupes par colonne
        current_group = 0  # Compteur de groupes affichés dans une colonne

        for groupe, services_liste in grouped_services.items():
            if current_group == max_groups_per_column:
                # Si 2 groupes sont déjà dans une colonne, passer à la colonne suivante
                column_index += 2
                current_group = 0
                row_index = 1  # Réinitialiser l'index de ligne pour la nouvelle colonne

            # Afficher le titre du groupe
            tk.Label(frame, text=groupe, font=('Arial', 12, 'bold')).grid(row=row_index, column=column_index, pady=0)
            row_index += 1

            # Afficher chaque service dans le groupe
            for service_id, service_name in services_liste:
                tk.Label(frame, text=service_name).grid(row=row_index, column=column_index)

                # Champ de saisie du coût
                entry = tk.Entry(frame)
                entry.grid(row=row_index, column=column_index + 1)

                # Stocker l'entrée dans le dictionnaire avec le service_id comme clé
                cost_entries[service_id] = entry
                row_index += 1

            current_group += 1

        # Bouton pour soumettre les coûts
        ajouter_button = tk.Button(frame, text="Ajouter coûts",
                                   command=lambda: self.ajouter_couts(cost_entries, date_debut_entry, date_fin_entry))
        ajouter_button.grid(row=row_index, column=0, columnspan=6, pady=10)

        # Message de confirmation
        confirmation_label = tk.Label(frame, text="")
        confirmation_label.grid(row=row_index + 1, column=0, columnspan=6)

        return frame

    def ajouter_couts(self, cost_entries, date_debut_entry, date_fin_entry):
        # Se connecter à la base de données
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()

        try:
            # Parcourir tous les services et leurs coûts associés
            for service_id, entry in cost_entries.items():
                cout = entry.get()

                if cout:  # Si un coût a été entré
                    try:
                        cout = float(cout)  # Convertir en float
                        date_debut = date_debut_entry.get()
                        date_fin = date_fin_entry.get()

                        # Vérifier que les dates sont au bon format
                        if len(date_debut) != 10 or len(date_fin) != 10:
                            messagebox.showerror("Erreur de saisie", "Les dates doivent être au format AAAA-MM-JJ")
                            return

                        # Insertion dans la base de données
                        cursor.execute('''
                            INSERT INTO couts (service_id, cout, date_debut, date_fin)
                            VALUES (?, ?, ?, ?)
                        ''', (service_id, cout, date_debut, date_fin))

                    except ValueError:
                        messagebox.showerror("Erreur de saisie", f"Le coût pour le service n'est pas un nombre valide.")
                        return

            # Sauvegarder et fermer la connexion
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout des coûts: {e}")
        finally:
            conn.close()

        # Message de confirmation
        self.clear_display_frame()
        tk.Label(self.display_frame, text="Coûts ajoutés avec succès !").pack()

    def run_generate_graph(self):
        try:
            # Exécute le script generer_graph.py dans une fenêtre séparée
            subprocess.Popen(['python', 'generer_graph.py'])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def show_config_menu(self):
        self.clear_display_frame()
        config_frame = tk.Frame(self.display_frame)
        config_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(config_frame, text="Configuration", font=("Arial", 16)).pack(pady=10)

        tk.Button(config_frame, text="Modifier Catégories", command=self.open_edit_categories).pack(pady=5)
        tk.Button(config_frame, text="Éditer Données", command=lambda: self.show_config_message("Éditer Données")).pack(
            pady=5)

    def open_edit_categories(self):
        try:
            # Exécute le script EditCategory.py dans une fenêtre séparée
            subprocess.Popen(['python', 'EditCategory.py'])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def show_config_message(self, option):
        messagebox.showinfo("Information", f"La fonction '{option}' est prévue pour plus tard.")

    def clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.add_data_frame = None

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
