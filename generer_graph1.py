import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def generer_graphique():
    # Connexion à la base de données
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()

    # Récupérer les données des coûts avec les services et les groupes associés
    query = '''
    SELECT s.nom, s.groupe, c.cout, c.date_debut, c.date_fin
    FROM couts c
    JOIN services s ON c.service_id = s.id
    '''
    data = pd.read_sql_query(query, conn)
    conn.close()

    # Convertir les dates en format datetime
    data['date_debut'] = pd.to_datetime(data['date_debut'])
    data['date_fin'] = pd.to_datetime(data['date_fin'])

    def calculate_monthly_costs(row):
        start_date = row['date_debut']
        end_date = row['date_fin']
        total_cost = row['cout']

        # Calcul du nombre total de jours
        total_days = (end_date - start_date).days + 1

        # Calcul du coût par jour
        daily_cost = total_cost / total_days

        # Créer un DataFrame pour stocker les coûts mensuels
        monthly_costs = []

        # On itère sur chaque mois inclus dans la période
        current_date = start_date
        while current_date <= end_date:
            # Déterminer le dernier jour du mois en cours
            last_day_of_month = pd.Timestamp(current_date.year, current_date.month,
                                             pd.Timestamp(current_date.year, current_date.month, 1).days_in_month)
            # Déterminer le nombre de jours à considérer dans ce mois
            end_of_period = min(last_day_of_month, end_date)
            days_in_month = (end_of_period - current_date).days + 1

            # Calculer le coût pour ce mois
            monthly_cost = daily_cost * days_in_month
            monthly_costs.append({
                'nom': row['nom'],
                'groupe': row['groupe'],
                'mois': current_date.to_period('M'),
                'cout': monthly_cost
            })

            # Passer au mois suivant
            current_date = last_day_of_month + pd.Timedelta(days=1)

        return pd.DataFrame(monthly_costs)

    # Appliquer la fonction à chaque ligne
    monthly_costs_df = pd.concat(data.apply(calculate_monthly_costs, axis=1).tolist(), ignore_index=True)

    # Grouper par mois et groupe, puis additionner les coûts
    grouped_data = monthly_costs_df.groupby(['mois', 'groupe'])['cout'].sum().unstack()

    # Générer le graphique empilé
    ax = grouped_data.plot(kind='bar', stacked=False, figsize=(10, 8), color = ['#FFFF00', '#FFD700', '#00FF00', '#228B22', '#808080', '#00CED1'])
    # Générer le graphique d'aires empilé
    #ax = grouped_data.plot(kind='area', stacked=True, figsize=(10, 8), color = ['#FFFF00', '#FFD700', '#00FF00', '#228B22', '#808080', '#00CED1'])


    # Ajouter des titres et des étiquettes
    plt.title('Monthly costs grouped by service')
    plt.xlabel('Month')
    plt.ylabel('Costs ($)')
    plt.xticks(rotation=45)
    plt.legend(title="Services", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Ajouter les valeurs sur les barres
    for container in ax.containers:
        # Utiliser ax.bar_label pour chaque barre dans les conteneurs
        labels = [f'${int(v)}' for v in container.datavalues]  # Formater les labels sans décimales avec $
        ax.bar_label(container, labels=labels, label_type='center', fontsize=8)

    # Afficher le graphique
    plt.show()

# Exécuter la fonction pour générer le graphique
generer_graphique()
