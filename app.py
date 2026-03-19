import streamlit as st
import pandas as pd
import numpy as np
import holidays
import datetime
import math
import io
from pathlib import Path    
from PIL import Image


# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Générateur de Gardes - Medical Stats",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# BARRE LATÉRALE (SIDEBAR) - NAVIGATION
# ==========================================

# Construction du chemin absolu de manière dynamique
image_folder = Path(__file__).parent / "props"
try:
    # 1. On met ".jpg" en minuscules pour faire plaisir à Linux
    logo = Image.open(image_folder / "logo.jpg") 
    # 2. On utilise width="stretch" pour faire plaisir à la nouvelle mise à jour de Streamlit
    st.sidebar.image(logo, width="stretch") 
    
except FileNotFoundError:
    st.sidebar.warning("Logo non trouvé. Vérifiez le dossier 'props' et l'extension (.jpg ou .png).")


st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Navigation")
st.sidebar.markdown("""
- [🏠 Accueil & Présentation](#accueil-pr-sentation)
- [⚙️ 1. Paramètres du Stage](#1-param-tres-du-stage)
- [👥 2. Liste des Médecins](#2-liste-des-m-decins)
- [🎯 3. Système de Points](#3-syst-me-de-points)
- [🔄 4. Historique & Contraintes](#4-historique-contraintes-individuelles)
- [🚀 5. Génération du Tableau](#5-g-n-ration-du-tableau)
""")
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Un outil développé par**")
st.sidebar.markdown("**Medical Stats Tunisie**")

# ==========================================
# SECTION : ACCUEIL & PRÉSENTATION
# ==========================================
st.title("🏥 Générateur de Tableaux de Garde Équitables")
st.header("Accueil & Présentation", anchor="accueil-pr-sentation")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Bienvenue !
    Fini les conflits et les heures passées à équilibrer les plannings. Cet outil a été conçu pour générer des tableaux de garde de manière **100% transparente, mathématique et équitable**.
    
    **Qui sommes-nous ?**
    **Medical Stats Tunisie** est une société spécialisée dans l'accompagnement des professionnels de santé. Nous proposons des services d'analyse de données, de statistiques médicales et d'aide à la méthodologie pour vos thèses, mémoires et publications scientifiques.
    """)
    st.link_button("🌐 Visiter notre page Facebook", "https://www.facebook.com/profile.php?id=61559703801939", type="primary")

with col2:
    st.info("📺 **Guide d'utilisation**")
    st.markdown("*(La vidéo tutoriel sera bientôt disponible ici pour vous guider pas à pas)*")

st.markdown("---")

# ==========================================
# SECTION 1 : PARAMÈTRES DU STAGE
# ==========================================
st.header("⚙️ 1. Paramètres du Stage", anchor="1-param-tres-du-stage")

col_date1, col_date2, col_param1, col_param2 = st.columns(4)
with col_date1:
    date_debut = st.date_input("Date de début", datetime.date.today(), format="DD/MM/YYYY")
with col_date2:
    date_fin = st.date_input("Date de fin", datetime.date.today() + datetime.timedelta(days=30), format="DD/MM/YYYY")
with col_param1:
    nombre_medecin_par_garde = st.number_input("Médecins par garde", min_value=1, value=1, step=1)
with col_param2:
    repartition_par_secteur = st.checkbox("Répartition par secteur", value=False)

if repartition_par_secteur:
    noms_des_secteurs_input = st.text_input(
        "Noms des secteurs (séparés par des virgules)", 
        value="Maternité, Neonat, Réanimation",
        help="Assurez-vous d'avoir autant de secteurs que de médecins par garde."
    )
    noms_des_secteurs = [s.strip() for s in noms_des_secteurs_input.split(',')]
else:
    noms_des_secteurs = [f"Médecin_{i+1}" for i in range(nombre_medecin_par_garde)]

# Avertissement pour le lendemain férié
lendemain = date_fin + datetime.timedelta(days=1)
tn_holidays = holidays.TN(years=[date_debut.year, date_fin.year, lendemain.year])

if lendemain in tn_holidays:
    nom_ferie = tn_holidays.get(lendemain)
    st.warning(f"⚠️ **Anticipation :** Attention, le lendemain de ce tableau ({lendemain.strftime('%d/%m/%Y')}) est un jour férié (**{nom_ferie}**). Prenez-le en compte pour vos repos de garde !")

# ==========================================
# SECTION 2 : LISTE DES MÉDECINS
# ==========================================
st.header("👥 2. Liste des Médecins", anchor="2-liste-des-m-decins")
noms_input = st.text_area(
    "Entrez les noms des médecins (séparés par des virgules ou retours à la ligne)", 
    value="Ali, Sami, Ahmed, Sonia, Nadia",
    height=100
)

# 1. Nettoyage basique
noms_bruts = [nom.strip() for nom in noms_input.replace('\n', ',').split(',') if nom.strip()]

# 2. Détection des doublons
doublons = []
vus = set()
for nom in noms_bruts:
    if nom in vus and nom not in doublons:
        doublons.append(nom)
    vus.add(nom)

if doublons:
    st.error(f"⚠️ **Noms identiques détectés : {', '.join(doublons)}**\n\nPour éviter que l'algorithme ne confonde deux médecins différents (ex: deux personnes s'appelant 'Mohamed'), veuillez les différencier dans la liste ci-dessus en ajoutant l'initiale de leur nom de famille ou un numéro (ex: 'Mohamed B.', 'Mohamed_2').")

# 3. Création de la liste unique pour l'interface
noms_liste = list(dict.fromkeys(noms_bruts))
st.caption(f"Nombre de médecins uniques prêts pour le tableau : **{len(noms_liste)}**")

# ==========================================
# SECTION 3 : SYSTÈME DE POINTS
# ==========================================
st.header("🎯 3. Système de Points", anchor="3-syst-me-de-points")

col_pt1, col_pt2, col_pt3, col_pt4, col_pt5 = st.columns(5)
with col_pt1:
    points_normal = st.number_input("Jour Normal", value=1.0, step=0.5)
with col_pt2:
    points_premier_jour = st.number_input("Premier Jour", value=3.0, step=0.5)
with col_pt3:
    points_samedi = st.number_input("Samedi", value=1.5, step=0.5)
with col_pt4:
    points_dimanche = st.number_input("Dimanche", value=2.0, step=0.5)
with col_pt5:
    points_ferie_standard = st.number_input("Férié par défaut", value=2.0, step=0.5)

with st.expander("🛠️ Paramètres de calcul avancés (Recommandé de ne pas modifier)"):
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        tolerance_gardes = st.number_input("Tolérance d'écart de gardes", min_value=0, value=2, step=1)
    with col_adv2:
        poids_de_presence = st.number_input("Poids de présence (Fatigue)", min_value=0.0, value=1.5, step=0.1)

st.subheader("🗓️ Jours Fériés et Dates Exceptionnelles")
dates_range = pd.date_range(date_debut, date_fin)
feries_in_range = [{"Date": d.date(), "Description": tn_holidays.get(d), "Points": points_ferie_standard} for d in dates_range if d in tn_holidays]

df_feries = pd.DataFrame(feries_in_range) if feries_in_range else pd.DataFrame(columns=["Date", "Description", "Points"])

df_points_exceptionnels = st.data_editor(
    df_feries, 
    num_rows="dynamic", 
    #use_container_width=True,
    width="stretch", 
    column_config={
        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY", required=True),
        "Description": st.column_config.TextColumn("Description"),
        "Points": st.column_config.NumberColumn("Points attribués", step=0.5, default=2.0)
    }
)

# ==========================================
# SECTION 4 : HISTORIQUE & CONTRAINTES
# ==========================================
st.header("🔄 4. Historique & Contraintes individuelles", anchor="4-historique-contraintes-individuelles")
st.info("Séparez les dates par des virgules au format **JJ/MM/AAAA** (ex: 03/04/2026, 05/04/2026).")

if noms_liste:
    df_init = pd.DataFrame({
        "Médecin": noms_liste,
        "Points initiaux": [0.0] * len(noms_liste),
        "Gardes déjà effectuées": [0] * len(noms_liste),
        "Obligatoires (JJ/MM/AAAA)": [""] * len(noms_liste),
        "Interdites (JJ/MM/AAAA)": [""] * len(noms_liste)
    })
    
    df_historique_et_contraintes = st.data_editor(
        df_init, hide_index=True, width='stretch',
        column_config={
            "Médecin": st.column_config.TextColumn("Médecin", disabled=True),
            "Points initiaux": st.column_config.NumberColumn("Points précédents", step=0.5),
            "Gardes déjà effectuées": st.column_config.NumberColumn("Gardes précédentes", step=1)
        }
    )

# ==========================================
# SECTION 5 : GÉNÉRATION DU TABLEAU
# ==========================================
st.header("🚀 5. Génération du Tableau", anchor="5-g-n-ration-du-tableau")

if st.button("✨ GÉNÉRER LE PLANNING ÉQUITABLE", type="primary", width='stretch'):
    if not noms_liste:
        st.error("Veuillez entrer au moins un nom de médecin.")
    elif doublons:  # <--- LE NOUVEAU BOUCLIER EST ICI
        st.error("🚨 Impossible de générer le tableau : Veuillez différencier les noms en double dans la Section 2.")
    elif repartition_par_secteur and len(noms_des_secteurs) != nombre_medecin_par_garde:
        st.error("Le nombre de secteurs doit être égal au nombre de médecins par garde.")
    elif date_fin < date_debut:
        st.error("La date de fin doit être postérieure à la date de début.")
    else:
        with st.spinner('Le moteur mathématique de Medical Stats calcule le meilleur planning...'):
        
            # 1. PRÉPARATION DES DONNÉES DE L'INTERFACE VERS LE MOTEUR
            points_exceptionnels = {}
            for _, row in df_points_exceptionnels.iterrows():
                if pd.notna(row["Date"]):
                    points_exceptionnels[row["Date"].strftime("%Y-%m-%d")] = row["Points"]

            def parse_dates_fr(date_str):
                dates_list = []
                if pd.notna(date_str) and date_str.strip():
                    for d in str(date_str).split(','):
                        d = d.strip()
                        if d:
                            try:
                                dates_list.append(datetime.datetime.strptime(d, "%d/%m/%Y").strftime("%Y-%m-%d"))
                            except ValueError:
                                pass # Ignore silently format errors
                return dates_list

            points_initiaux = {}
            gardes_initiales = {}
            dates_obligatoires = {}
            dates_interdites = {}
            dernier_jour_garde = {med: pd.NaT for med in noms_liste}

            for _, row in df_historique_et_contraintes.iterrows():
                med = row["Médecin"]
                points_initiaux[med] = row["Points initiaux"]
                gardes_initiales[med] = row["Gardes déjà effectuées"]
                dates_obligatoires[med] = parse_dates_fr(row["Obligatoires (JJ/MM/AAAA)"])
                dates_interdites[med] = parse_dates_fr(row["Interdites (JJ/MM/AAAA)"])


            # =========================================================
            # BOUCLIER ANTI-TROU NOIR (Nouveau bloc à insérer ici)
            # =========================================================
            paradoxe_temporel = False
            for date_verif in pd.date_range(start=date_debut, end=date_fin):
                jour_str_verif = date_verif.strftime('%Y-%m-%d')
                inscrits_obligatoires = [m for m, d_obl in dates_obligatoires.items() if jour_str_verif in d_obl]
                
                if len(inscrits_obligatoires) > nombre_medecin_par_garde:
                    st.error(f"🌌 **Alerte Trou Noir !** Le {date_verif.strftime('%d/%m/%Y')}, vous avez rendu la garde obligatoire pour **{len(inscrits_obligatoires)} médecins** ({', '.join(inscrits_obligatoires)}), alors qu'il n'y a que **{nombre_medecin_par_garde} place(s)** ! Le continuum espace-temps a été préservé, l'application s'est arrêtée. Veuillez corriger ce paradoxe dans le tableau.")
                    paradoxe_temporel = True
                    break # On arrête de chercher
                    
            if paradoxe_temporel:
                st.stop() # Arrête le code net ici sans faire planter l'application

            # 2. PRÉPARATION DU CALENDRIER
            dates = pd.date_range(start=date_debut, end=date_fin)
            df_calendrier = pd.DataFrame(index=dates)

            def attribuer_points_jour(date_obj, index_jour):
                date_str = date_obj.strftime('%Y-%m-%d')
                if date_str in points_exceptionnels: return points_exceptionnels[date_str]
                if index_jour == 0: return points_premier_jour
                if date_obj in tn_holidays: return points_ferie_standard
                if date_obj.weekday() == 6: return points_dimanche
                if date_obj.weekday() == 5: return points_samedi
                return points_normal

            df_calendrier['Valeur_Points'] = [attribuer_points_jour(d, i) for i, d in enumerate(dates)]
            df_calendrier['Est_Ferie_ou_Exceptionnel'] = [(d in tn_holidays) or (d.strftime('%Y-%m-%d') in points_exceptionnels) for d in dates]

            # 3. LE MOTEUR D'AFFECTATION
            total_postes = len(dates) * nombre_medecin_par_garde
            moyenne_gardes_periode = total_postes / len(noms_liste)
            plafond_gardes_periode = math.ceil(moyenne_gardes_periode) + tolerance_gardes

            compteurs = {med: {
                'points': points_initiaux.get(med, 0.0), 
                'gardes_cumulees': gardes_initiales.get(med, 0),
                'gardes_ce_mois': 0, 'samedi': 0, 'dimanche': 0, 'ferie': 0
            } for med in noms_liste}

            historique_affectations = []

            for date in dates:
                jour_str = date.strftime('%Y-%m-%d')
                medecins_du_jour = []
                
                for med, dates_obl in dates_obligatoires.items():
                    if jour_str in dates_obl: medecins_du_jour.append(med)
                        
                places_restantes = nombre_medecin_par_garde - len(medecins_du_jour)
                
                if places_restantes > 0:
                    candidats_dispo = []
                    for med in noms_liste:
                        if med in medecins_du_jour: continue
                        if med in dates_interdites and jour_str in dates_interdites[med]: continue
                        
                        dernier_jour = dernier_jour_garde[med]
                        if pd.notna(dernier_jour) and (date - dernier_jour).days <= 1: continue
                        candidats_dispo.append(med)
                        
                    candidats_sous_plafond = [m for m in candidats_dispo if compteurs[m]['gardes_ce_mois'] < plafond_gardes_periode]
                    candidats_a_trier = candidats_sous_plafond if len(candidats_sous_plafond) >= places_restantes else candidats_dispo
                        
                    candidats_a_trier.sort(key=lambda x: (
                        compteurs[x]['points'] + ((compteurs[x]['gardes_cumulees'] + compteurs[x]['gardes_ce_mois']) * poids_de_presence),
                        compteurs[x]['points']
                    ))
                    
                    selection = candidats_a_trier[:places_restantes]
                    medecins_du_jour.extend(selection)
                    
                decalage = date.day % nombre_medecin_par_garde
                medecins_du_jour = medecins_du_jour[decalage:] + medecins_du_jour[:decalage]
                
                val_jour = df_calendrier.loc[date, 'Valeur_Points']
                est_special = df_calendrier.loc[date, 'Est_Ferie_ou_Exceptionnel']
                
                for med in medecins_du_jour:
                    compteurs[med]['points'] += val_jour
                    compteurs[med]['gardes_ce_mois'] += 1
                    dernier_jour_garde[med] = date
                    
                    if est_special: compteurs[med]['ferie'] += 1
                    elif date.weekday() == 5: compteurs[med]['samedi'] += 1
                    elif date.weekday() == 6: compteurs[med]['dimanche'] += 1
                        
                historique_affectations.append(medecins_du_jour)

            # 4. FORMATAGE DES OUTPUTS
            df_brut = pd.DataFrame(historique_affectations, index=dates, columns=noms_des_secteurs)
            df_brut['Jour'] = df_brut.index.day
            df_brut['Mois'] = df_brut.index.strftime('%Y-%m')

            df_planning = df_brut.pivot(index='Jour', columns='Mois', values=noms_des_secteurs)
            df_planning = df_planning.swaplevel(axis=1).sort_index(axis=1, level=0)
            df_planning = df_planning.reindex(columns=noms_des_secteurs, level=1)
            df_planning.fillna('', inplace=True)
            df_planning.index.name = 'Jour du mois'

            # =========================================================
            # NOUVEAU : FONCTION DE COLORATION (Styler)
            # =========================================================
            def coloriser_cellules(df_pivot):
                # Crée un tableau vide de la même forme pour stocker les styles CSS
                styles = pd.DataFrame('', index=df_pivot.index, columns=df_pivot.columns)
                
                # On parcourt les dates réelles pour savoir qui est quoi
                for d in dates:
                    jour = d.day
                    mois = d.strftime('%Y-%m')
                    date_str = d.strftime('%Y-%m-%d')
                    
                    est_special = (d in tn_holidays) or (date_str in points_exceptionnels)
                    est_weekend = d.weekday() in [5, 6] # 5 = Samedi, 6 = Dimanche
                    
                    # Hiérarchie des couleurs avec texte noir forcé pour la lisibilité
                    if est_special:
                        # Vert doux avec texte noir
                        couleur = 'background-color: #a8e6cf; color: #000000;' 
                    elif est_weekend:
                        # Bleu ciel avec texte noir
                        couleur = 'background-color: #bae1ff; color: #000000;' 
                    else:
                        couleur = ''
                        
                    # Si une couleur est définie, on l'applique à toutes les colonnes de ce jour
                    if couleur:
                        for secteur in noms_des_secteurs:
                            if (mois, secteur) in styles.columns:
                                styles.loc[jour, (mois, secteur)] = couleur
                return styles

            # On applique la coloration à notre tableau
            df_planning_colore = df_planning.style.apply(coloriser_cellules, axis=None)
            # =========================================================

            data_recap = []
            for med, data in compteurs.items():
                data_recap.append({
                    'Médecin': med,
                    'Points Totaux': data['points'],
                    'Gardes de la période': data['gardes_ce_mois'],
                    'Samedis': data['samedi'],
                    'Dimanches': data['dimanche'],
                    'Fériés/Exceptions': data['ferie']
                })
            df_recap = pd.DataFrame(data_recap).set_index('Médecin')

            # 5. AFFICHAGE ET BOUTON EXCEL
            st.success("Planning généré avec succès ! Voici les résultats :")
            st.balloons()
            
            st.subheader("🗓️ Tableau de Garde")
            # On affiche la version colorée dans Streamlit
            st.dataframe(df_planning_colore, width='stretch') 
            
            st.subheader("📊 Tableau Récapitulatif")
            st.dataframe(df_recap, width='stretch')

            # --- GÉNÉRATION DU FICHIER EXCEL EN MÉMOIRE ---
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # On exporte la version colorée vers Excel !
                df_planning_colore.to_excel(writer, sheet_name='Planning')
                df_recap.to_excel(writer, sheet_name='Récapitulatif')
            
            st.markdown("---")
            st.download_button(
                label="📥 TÉLÉCHARGER LES TABLEAUX AU FORMAT EXCEL",
                data=buffer.getvalue(),
                file_name=f"Tableau_Garde_MedicalStats_{date_debut.strftime('%b_%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                width='stretch'
            )