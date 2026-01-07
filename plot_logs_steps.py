import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
LOG_FILE = 'Bots/gambit_logs.csv'
OUTPUT_IMAGE = 'gambit_steps_evolution.png'


def generate_step_plots():
    if not os.path.exists(LOG_FILE):
        print(f"Erreur : Le fichier {LOG_FILE} est introuvable.")
        return

    # 1. Chargement des données
    df = pd.read_csv(LOG_FILE)
    print(f"{len(df)} entrées chargées.")

    # 2. Définition des Étapes (Ordre strict)
    # On définit exactement quelle combinaison de drapeaux correspond à quelle étape
    steps = [
        {
            "name": "1. Baseline (Aucune Optim)",
            "criteria": {"USE_TT": False, "USE_QUIESCENCE": False, "USE_MOVE_ORDERING": False,
                         "USE_KILLER_MOVES": False}
        },
        {
            "name": "2. + Table Transposition",
            "criteria": {"USE_TT": True, "USE_QUIESCENCE": False, "USE_MOVE_ORDERING": False, "USE_KILLER_MOVES": False}
        },
        {
            "name": "3. + Quiescence",
            "criteria": {"USE_TT": True, "USE_QUIESCENCE": True, "USE_MOVE_ORDERING": False, "USE_KILLER_MOVES": False}
        },
        {
            "name": "4. + Move Ordering",
            "criteria": {"USE_TT": True, "USE_QUIESCENCE": True, "USE_MOVE_ORDERING": True, "USE_KILLER_MOVES": False}
        },
        {
            "name": "5. + Killer Moves (Tout Activé)",
            "criteria": {"USE_TT": True, "USE_QUIESCENCE": True, "USE_MOVE_ORDERING": True, "USE_KILLER_MOVES": True}
        }
    ]

    # 3. Filtrage et Tri des données
    filtered_data = []

    for step in steps:
        # On crée un masque pour filtrer le DataFrame
        mask = pd.Series([True] * len(df))
        for col, val in step["criteria"].items():
            if col in df.columns:
                mask = mask & (df[col] == val)

        step_df = df[mask].copy()

        if not step_df.empty:
            step_df['Step_Label'] = step["name"]
            step_df['Step_Order'] = steps.index(step)  # Pour forcer l'ordre de tri
            filtered_data.append(step_df)
        else:
            print(f"⚠️ Attention : Aucune donnée trouvée pour l'étape '{step['name']}'")

    if not filtered_data:
        print("Aucune donnée ne correspond aux étapes définies. Vérifiez vos logs.")
        return

    plot_df = pd.concat(filtered_data)
    # Tri explicite par l'ordre défini
    plot_df = plot_df.sort_values('Step_Order')

    # 4. Création des Graphiques
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 10))

    # Titre global
    plt.suptitle("Évolution des Performances du Bot Gambit", fontsize=20, y=0.98)

    # Couleurs progressives (du clair au foncé ou divergent)
    palette = sns.color_palette("viridis", len(steps))

    # --- GRAPHIQUE 1 : Efficacité (Nœuds) ---
    plt.subplot(2, 2, 1)
    sns.barplot(data=plot_df, x='Step_Label', y='Nodes', palette=palette, errorbar='sd')
    plt.title('Nœuds Visités (Efficacité)', fontsize=14)
    plt.ylabel('Nombre de Nœuds')
    plt.xticks(rotation=25, ha='right')
    plt.xlabel('')

    # --- GRAPHIQUE 2 : Profondeur ---
    plt.subplot(2, 2, 2)
    sns.barplot(data=plot_df, x='Step_Label', y='Depth', palette=palette, errorbar='sd')
    plt.title('Profondeur Atteinte', fontsize=14)
    plt.ylabel('Profondeur Moyenne')
    plt.ylim(0, plot_df['Depth'].max() + 1)
    plt.xticks(rotation=25, ha='right')
    plt.xlabel('')

    # --- GRAPHIQUE 3 : Vitesse (NPS) ---
    plt.subplot(2, 2, 3)
    sns.barplot(data=plot_df, x='Step_Label', y='NPS', palette=palette, errorbar='sd')
    plt.title('Vitesse de Calcul (NPS)', fontsize=14)
    plt.ylabel('Nœuds / Seconde')
    plt.xticks(rotation=25, ha='right')
    plt.xlabel('')

    # --- GRAPHIQUE 4 : Impact Mémoire (TT Cuts) ---
    if 'TT_Cuts' in plot_df.columns:
        plt.subplot(2, 2, 4)
        sns.barplot(data=plot_df, x='Step_Label', y='TT_Cuts', palette=palette, errorbar='sd')
        plt.title('Utilisation de la Table de Transposition', fontsize=14)
        plt.ylabel('Coupures (Cuts)')
        plt.xticks(rotation=25, ha='right')
        plt.xlabel('')

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"Graphique d'évolution généré : {OUTPUT_IMAGE}")
    plt.show()


if __name__ == "__main__":
    generate_step_plots()