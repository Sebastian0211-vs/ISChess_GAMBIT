import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
LOG_FILE = 'Bots/gambit_logs.csv'
OUTPUT_IMAGE = 'gambit_comparison.png'


def generate_plots():
    if not os.path.exists(LOG_FILE):
        print(f"Erreur : Le fichier {LOG_FILE} est introuvable.")
        return

    # 1. Chargement des données
    df = pd.read_csv(LOG_FILE)
    print(f"{len(df)} entrées chargées.")

    # 2. Identification des colonnes de config
    config_cols = [c for c in df.columns if c.startswith('USE_')]

    if not config_cols:
        print("Pas de configuration trouvée, impossible de comparer.")
        return

    # --- FILTRAGE AJOUTÉ ICI ---
    # On compte le nombre de features désactivées (False) pour chaque ligne
    false_counts = (df[config_cols] == False).sum(axis=1)

    # On garde :
    # - 0 False : La configuration "Tout Activé" (Référence)
    # - 1 False : Les configurations "Sans X" (Pour l'étude d'impact)
    # On élimine les cas où 2 ou plusieurs features sont désactivées en même temps
    df = df[false_counts <= 1].copy()

    print(f"{len(df)} entrées conservées après filtrage (Baseline + Ablations uniques).")

    # ---------------------------

    # 3. Création des étiquettes (Labels)
    def make_label(row):
        disabled_features = []
        for col in config_cols:
            if not row[col]:  # Si la feature est à FALSE
                name = col.replace('USE_', '')
                shortcuts = {
                    'MOVE_ORDERING': 'MoveOrd',
                    'KILLER_MOVES': 'Killer',
                    'QUIESCENCE': 'Quiesc',
                    'TT': 'TT'
                }
                disabled_features.append(shortcuts.get(name, name))

        if not disabled_features:
            return "Tout Activé"

        return "Sans " + " & ".join(disabled_features)

    df['Config_Label'] = df.apply(make_label, axis=1)

    # 4. Création des Graphiques
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(16, 10))

    # Titre global
    plt.suptitle('Impact des Optimisations', fontsize=20, y=0.98)

    # --- GRAPHIQUE 1 : Vitesse (NPS) ---
    plt.subplot(2, 2, 1)
    sns.barplot(data=df, x='Config_Label', y='NPS', palette="viridis", errorbar='sd')
    plt.title('Vitesse de calcul (Nœuds/Seconde)', fontsize=14)
    plt.ylabel('NPS')
    plt.xticks(rotation=15)
    plt.xlabel('')

    # --- GRAPHIQUE 2 : Efficacité (Nombre de Nœuds) ---
    plt.subplot(2, 2, 2)
    sns.barplot(data=df, x='Config_Label', y='Nodes', palette="rocket", errorbar='sd')
    plt.title('Nœuds visités (Moins = Meilleur élagage)', fontsize=14)
    plt.ylabel('Nombre de Nœuds')
    plt.xticks(rotation=15)
    plt.xlabel('')

    # --- GRAPHIQUE 3 : Profondeur Atteinte ---
    plt.subplot(2, 2, 3)
    sns.barplot(data=df, x='Config_Label', y='Depth', palette="magma", errorbar='sd')
    plt.title('Profondeur Moyenne Atteinte', fontsize=14)
    plt.ylabel('Profondeur')
    plt.ylim(0, df['Depth'].max() + 1)
    plt.xticks(rotation=15)
    plt.xlabel('Configuration')

    # --- GRAPHIQUE 4 : Coupures TT ---
    if 'TT_Cuts' in df.columns and df['TT_Cuts'].sum() > 0:
        plt.subplot(2, 2, 4)
        sns.barplot(data=df, x='Config_Label', y='TT_Cuts', palette="coolwarm", errorbar='sd')
        plt.title('Coupures Mémoire (TT Cuts)', fontsize=14)
        plt.ylabel('Nombre de Coupures')
        plt.xticks(rotation=15)
        plt.xlabel('Configuration')
    else:
        plt.subplot(2, 2, 4)
        sns.barplot(data=df, x='Config_Label', y='Time', palette="coolwarm", errorbar='sd')
        plt.title('Temps de réflexion moyen (s)', fontsize=14)
        plt.ylabel('Secondes')
        plt.xticks(rotation=15)
        plt.xlabel('Configuration')

    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"Graphique sauvegardé : {OUTPUT_IMAGE}")
    plt.show()


if __name__ == "__main__":
    generate_plots()