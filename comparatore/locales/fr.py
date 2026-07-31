"""Catalogue français. Les clés doivent correspondre exactement à
`comparatore.locales.it` - `tests/test_i18n.py` vérifie que les quatre
catalogues restent synchronisés."""

LINGUA = "fr"
NOME = "Français"

MESSAGGI: dict[str, str] = {
    # --- En-tête -------------------------------------------------
    "app.page_title": "Comparateur de fonds",
    "app.title": "📈 Comparateur de fonds",
    "app.subtitle": "Backtest de fonds et ETF sur plusieurs sources de données, avec l'impact du TER.",

    # --- Rééquilibrage (aide du menu) --------------------------
    "rebalance.help": (
        "Ramène périodiquement les poids à ceux fixés, en vendant ce qui a "
        "le plus progressé pour racheter ce qui est resté à la traîne.\n\n"
        "- **Aucun (buy & hold)** : on achète une seule fois et on ne "
        "touche plus à rien. Les poids dérivent : le fonds le plus "
        "performant finit par peser de plus en plus, et le portefeuille "
        "devient progressivement plus concentré.\n"
        "- **Mensuel / Trimestriel / Annuel** : au premier jour de bourse "
        "de chaque période, les poids reviennent aux valeurs fixées.\n\n"
        "Le backtest n'applique aucuns frais de transaction ni imposition "
        "des plus-values réalisées : rééquilibrer souvent est donc ici plus "
        "avantageux que dans la réalité."
    ),

    # --- Barre latérale : paramètres généraux ------------------------------------
    "sidebar.header": "⚙️ Paramètres",
    "sidebar.lingua_label": "Langue",
    "sidebar.periodo_caption": "Période",
    "preset.1y": "1a",
    "preset.5y": "5a",
    "preset.10y": "10a",
    "preset.20y": "20a",
    "preset.max": "Max",
    "sidebar.data_inizio": "Date de début",
    "sidebar.data_fine": "Date de fin",
    "sidebar.valore_iniziale": "Valeur initiale du portefeuille",
    "sidebar.valuta_riferimento": "Devise de référence",
    "sidebar.ribilanciamento_label": "Rééquilibrage",
    "sidebar.rebalance_caption_none": (
        "Les poids fixés sont un point de départ : sans rééquilibrage, ils "
        "dérivent dans le temps avec les rendements relatifs des fonds."
    ),
    "sidebar.rebalance_caption_active": (
        "Les poids reviennent aux valeurs fixées au premier jour de bourse "
        "de chaque période (aucun frais de transaction appliqué)."
    ),

    # --- Barre latérale : coûts --------------------------------------------------
    "costs.subheader": "Coûts",
    "costs.caption": (
        "Les VL publiées sont **déjà nettes du TER**. "
        "La courbe *brute* reconstitue le fonds sans frais : "
        "l'écart entre les deux courbes est le coût du TER."
    ),
    "costs.show_gross_checkbox": "Afficher aussi la courbe brute (sans TER)",

    # --- Barre latérale : historique étendu ------------------------------------
    "history.subheader": "Historique étendu",
    "history.checkbox": "Reconstituer la période précédant la création du fonds",
    "history.help": (
        "Prolonge la série vers le passé à l'aide d'un indice ou d'un fonds "
        "plus ancien. C'est une reconstitution, pas une donnée réelle : "
        "elle apparaît en pointillés dans les graphiques."
    ),
    "history.caption_non_usd": (
        "⚠️ Les proxys sont cotés en dollars. Avec une devise de référence "
        "autre que l'USD, la reconstitution ne peut pas descendre "
        "avant **{anno}**, première date des taux de change officiels de la BCE."
    ),
    "history.caption_usd": "Devise USD : la reconstitution peut utiliser toute la profondeur du proxy.",

    # --- Barre latérale : sources de données -----------------------------------------------
    "sources.subheader": "Sources de données",
    "sources.justetf_info": (
        "**Ce qu'implique l'activation de justETF**\n\n"
        "justETF ne propose pas d'API publique documentée pour cette "
        "fonction. Si vous activez l'intégration, pour les ETF identifiés "
        "par ISIN, l'application l'essaiera automatiquement **avant "
        "Yahoo** et enverra, depuis l'ordinateur ou le serveur exécutant "
        "l'application :\n\n"
        "- l'ISIN de l'ETF, la période et la devise demandées ;\n"
        "- l'adresse IP et les données techniques habituelles de la connexion HTTP.\n\n"
        "Aucun capital, poids du portefeuille, fichier CSV ni clé API n'est "
        "envoyé. Les séries reçues sont conservées dans le cache local. "
        "Le point d'accès peut changer ou cesser de fonctionner, et son "
        "utilisation reste soumise aux [conditions de justETF]"
        "(https://www.justetf.com/it/about/legal-terms.html) et aux droits "
        "des fournisseurs de données. Le consentement est mémorisé sur cet "
        "ordinateur jusqu'à sa révocation ; en laissant la case décochée, "
        "justETF ne sera contacté que si vous le choisissez explicitement "
        "comme source "
        "pour un fonds particulier."
    ),
    "sources.justetf_checkbox": "J'accepte les requêtes automatiques vers justETF",
    "sources.justetf_help": (
        "Ajoute justETF avant Yahoo dans l'ordre automatique pour les ETF "
        "identifiés par ISIN. Vous pouvez révoquer le consentement en "
        "décochant la case."
    ),
    "sources.status_optin_off": " — opt-in désactivé",
    "sources.status_not_configured": " — non configurée",
    "sources.order_caption": (
        "Ordre automatique : CSV → Yahoo → EODHD → Twelve Data ; justETF "
        "n'intervient qu'avec l'opt-in ci-dessus. Vous pouvez toujours "
        "forcer une source par fonds depuis le tableau. Les caches EODHD "
        "et Twelve Data expirent après {giorni} jours."
    ),
    "sources.eodhd_hint": (
        "Pour les **fonds domiciliés en Italie** (Mediolanum, Fineco, "
        "banques), il est utile de configurer EODHD : Yahoo n'en couvre "
        "qu'une partie, avec un historique depuis 2018. Entrez la clé "
        "ci-dessus, dans **🔑 Clés API**."
    ),
    "sources.used_caption": "📚 Sources utilisées : {elenco}",

    # --- Barre latérale : clés API -------------------------------------------------
    "api_keys.expander": "🔑 Clés API (EODHD, Twelve Data)",
    "api_keys.caption": (
        "Conservées uniquement sur cet ordinateur, dans "
        "`.streamlit/api_keys.json` (permissions restreintes à votre "
        "utilisateur, déjà exclu du dépôt). Elles survivent au redémarrage "
        "et à **Vider le cache**, ci-dessous."
    ),
    "api_keys.eodhd_label": "Clé EODHD",
    "api_keys.td_label": "Clé Twelve Data",
    "api_keys.save_button": "Enregistrer",
    "api_keys.saved_toast": "Clés enregistrées",
    "api_keys.saved_caption": "Clés enregistrées : {elenco}",
    "api_keys.forget_button": "Oublier les clés enregistrées",
    "api_keys.forgotten_toast": "Clés et cache associé supprimés",

    # --- Barre latérale : CSV ---------------------------------------------------------
    "csv.expander": "📄 Charger une série depuis un CSV",
    "csv.caption": (
        "Pour les fonds qu'aucune source ne couvre. Deux colonnes : date "
        "et valeur de la part. Séparateur, décimale et format de date "
        "détectés automatiquement."
    ),
    "csv.symbol_label": "Symbole ou ISIN à lui associer",
    "csv.symbol_placeholder": "ex. IT0001234567",
    "csv.currency_label": "Devise de la série",
    "csv.file_label": "Fichier CSV",
    "csv.success": "{n} observations du {inizio} au {fine}.",
    "csv.loaded_caption": "Chargées : {elenco}",
    "csv.remove_button": "Supprimer les séries chargées",

    # --- Barre latérale : cache, licences, taux sans risque ------------------------------------
    "cache.caption": "💾 Cache sur disque : {n} séries, {mb:.1f} Mo",
    "cache.clear_button": "Vider le cache",
    "cache.cleared_toast": "Cache vidé",
    "sidebar.risk_free_label": "Taux sans risque annuel (pour Sharpe)",

    # --- Barre latérale : informations et licences --------------------------------------
    "about.expander": "ℹ️ Informations et licences",
    "about.version": "Comparateur de fonds version {versione}",
    "about.license_caption": (
        "Code source distribué sous licence "
        "[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)."
    ),
    "about.third_party_header": "Bibliothèques tierces",
    "about.third_party_caption": (
        "Le projet utilise les bibliothèques listées ci-dessous, chacune "
        "sous sa propre licence. Le texte complet, notices légales "
        "incluses, se trouve dans le fichier téléchargeable."
    ),
    "about.third_party_missing": (
        "Liste des licences non disponible dans cette installation."
    ),
    "about.download_button": "⬇️ Télécharger les licences tierces (.txt)",
    "about.col_package": "Paquet",
    "about.col_version": "Version",
    "about.col_license": "Licence",

    # --- Barre latérale : portefeuille (export/import) ---------------------------------
    "portfolio_io.expander": "💼 Portefeuille : enregistrer et charger",
    "portfolio_io.caption": (
        "Enregistrez dans un fichier les fonds, les poids et les "
        "paramètres du backtest, pour les rouvrir dans une autre session "
        "ou sur un autre ordinateur."
    ),
    "portfolio_io.download_button": "⬇️ Télécharger le portefeuille (.json)",
    "portfolio_io.download_empty_hint": "Ajoutez au moins un fonds pour pouvoir le télécharger.",
    "portfolio_io.upload_label": "Charger un portefeuille (.json)",
    "portfolio_io.import_success": "Portefeuille chargé : {n} fonds.",
    "portfolio_io.import_error": "Fichier invalide : {errore}",

    # --- Recherche --------------------------------------------------------------
    "search.expander": "🔎 Rechercher des fonds et ETF",
    "search.query_label": "Nom, symbole ou ISIN",
    "search.query_placeholder": "ex. 'Vanguard S&P 500', 'VUSA.AS' ou 'IE00B3XXRP09'",
    "search.funds_only_toggle": "Fonds/ETF uniquement",
    "search.spinner": "Recherche en cours…",
    "search.no_results": "Aucun résultat. Essayez l'ISIN ou le symbole complet.",
    "search.isin_hint": (
        "🔗 L'ISIN ne permet d'utiliser justETF que si vous avez activé "
        "l'opt-in dans Sources de données, ou choisi la source pour ce fonds."
    ),
    "search.add_button": "Ajouter",

    # --- Toast ------------------------------------------------------------------
    "toast.fund_exists": "{symbol} est déjà dans le portefeuille",
    "toast.fund_added": "{symbol} ajouté",
    "toast.fund_removed": "{elenco} supprimé",

    # --- Composition du portefeuille ---------------------------------------------------
    "portfolio.subheader": "Composition du portefeuille",
    "portfolio.empty_hint": "Recherchez et ajoutez au moins un fonds pour commencer.",

    "editor.col_rimuovi": "Retirer",
    "editor.col_fondo": "Fonds",
    "editor.col_simbolo": "Symbole",
    "editor.col_isin": "ISIN",
    "editor.col_valuta": "Devise",
    "editor.col_peso": "Poids %",
    "editor.col_importo": "Montant ({ccy})",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Coûts extra %",
    "editor.col_fonte": "Source",
    "editor.col_proxy": "Proxy historique",
    "editor.rimuovi_help": (
        "Retire le fonds du portefeuille et redistribue son poids sur les "
        "autres, en conservant leurs proportions."
    ),
    "editor.isin_help": (
        "Nécessaire pour utiliser justETF quand la source est activée ou "
        "explicitement sélectionnée pour le fonds."
    ),
    "editor.peso_help": (
        "Part du portefeuille attribuée au fonds. En le modifiant, les autres "
        "poids s'ajustent automatiquement entre eux, proportionnellement, pour "
        "que le total reste à 100%."
    ),
    "editor.importo_help": (
        "Capital attribué au fonds dans cette devise. Le modifier met à jour "
        "les poids et la valeur initiale du portefeuille."
    ),
    "editor.ter_help": (
        "Frais courants annuels. Pré-rempli quand la source le fournit : "
        "vérifiez toujours sur le DIC du fonds."
    ),
    "editor.extra_help": (
        "Coûts annuels NON déjà inclus dans la VL (garde, conseil). Ils "
        "sont déduits de la performance."
    ),
    "editor.fonte_help": "'Automatique' essaie les sources par ordre de priorité.",
    "editor.proxy_help": (
        "Instrument plus ancien pour reconstituer la période précédant la "
        "création du fonds."
    ),
    "editor.equalize_button": "⚖️ Poids égaux",
    "editor.clear_button": "🗑️ Vider",
    "editor.total_weight_metric": "Poids total",
    "editor.total_value_metric": "Capital investi",

    # --- Avertissements TER, poids, dates -------------------------------------------------
    "ter_warning.reason_eodhd_blocked": (
        "le plan EODHD configuré n'inclut pas `/fundamentals` (un plan "
        "payant est requis), donc ni le TER ni la classification n'en "
        "proviennent. "
    ),
    "ter_warning.reason_none": "aucune source configurée ne l'expose pour ces instruments. ",
    "ter_warning.message": (
        "TER introuvable pour : {elenco}. {motivo}"
        "Saisissez-le manuellement depuis le DIC pour voir l'impact des coûts."
    ),
    "weight.error_zero": "Attribuez au moins un poids supérieur à zéro.",
    "weight.warning_normalized": "Les poids totalisent {tot:.1f}% : ils seront normalisés à 100%.",
    "weight.error_importo_min": "Le capital total du portefeuille ne peut pas descendre sous {minimo}.",
    "dates.error_order": "La date de début doit précéder la date de fin.",

    # --- Récupération des prix -----------------------------------------------------------
    "prices.spinner": "Téléchargement des séries historiques…",
    "prices.error_none": "Aucune donnée de prix disponible pour les fonds sélectionnés.",
    "prices.missing_expander": "🚫 {n} fonds sans données",
    "prices.missing_hint": (
        "Suggestion : chargez une série CSV, ou après avoir vérifié les "
        "conditions du service, activez justETF et renseignez l'ISIN."
    ),

    # --- Conversion de devise -------------------------------------------------------
    "fx.error_none": "Aucune série convertible dans la devise de référence.",
    "fx.error_failed": "Exclus du backtest (devise non résolue) : {elenco}.",
    "fx.error_failed_eodhd_cause": (
        " Le plan EODHD configuré n'inclut pas `/fundamentals` (un plan "
        "payant est requis) : si ces fonds proviennent d'une recherche "
        "EODHD, vérifiez s'ils existent aussi sur Yahoo sous un autre "
        "symbole, ou chargez une série CSV en indiquant vous-même la devise."
    ),
    "fx.converted_caption": "💱 Convertis en {ccy} aux taux de change quotidiens : {elenco}",
    "fx.truncated_detail_item": "{symbol} depuis le {data}",
    "fx.truncated_warning": (
        "Taux de change disponibles seulement à partir d'une date "
        "postérieure à celle demandée : {dettaglio}. La période a été "
        "raccourcie plutôt que d'utiliser un taux rétro-rempli."
    ),

    # --- Historique étendu (bloc d'exécution) ------------------------------------------
    "history.expander": "🧩 Historique reconstitué",
    "history.reconstructing_spinner": "Reconstitution de l'historique de {symbol} avec {proxy}…",
    "history.proxy_unavailable": "{symbol} : proxy {proxy} non disponible",
    "history.proxy_not_older": (
        "{symbol} : {proxy} n'est pas plus ancien que le fonds, rien à reconstituer"
    ),
    "history.reconstructed_note": "**{symbol}** reconstitué depuis le {data} avec {proxy_label}{caveat}",
    "history.reconstructed_caption": (
        "Les tronçons reconstitués sont des estimations basées sur un "
        "instrument différent du fonds, pas des données réelles. Ils "
        "apparaissent en pointillés dans les graphiques."
    ),
    "proxy.caveat_price_only": (
        "indice prix uniquement : le tronçon reconstitué exclut les "
        "dividendes et sous-estime le rendement"
    ),
    "coverage_warning": "{symbol} : données disponibles seulement à partir du {data}",

    # --- Résultats du backtest --------------------------------------------------------
    "results.subheader": "Résultats · {inizio} → {fine}",
    "results.reconstructed_info": (
        "🧩 Les métriques ci-dessus incluent la période reconstituée "
        "({inizio} → {fine}) : elles sont indicatives, pas la performance "
        "réellement obtenue par les fonds."
    ),
    "metrics.explainer_expander": "❓ Comment lire ces métriques",
    "costs.impact_info": (
        "💸 **Impact du TER** : sur {anni:.1f} ans, les frais courants ont "
        "coûté **{costo}**, soit **{pct}** du montant que vous auriez eu "
        "sans coûts ({lordo} brut contre {netto} net)."
    ),

    # --- Textes d'aide des métriques ---------------------------------------------------
    "help.valore_finale": (
        "Ce que seraient devenus les {capitale} initiaux à la fin de la "
        "période, net du TER."
    ),
    "help.rendimento_totale": (
        "Variation globale sur toute la période, **non** annualisée."
    ),
    "help.cagr": (
        "Taux de croissance annuel composé : le taux constant qui, "
        "appliqué chaque année, mène de la valeur initiale à la valeur "
        "finale dans le même temps réellement écoulé."
    ),
    "help.volatilita": (
        "Amplitude annualisée des rendements quotidiens (écart-type × "
        "√252). Indique à quel point le parcours a bougé, pas combien a "
        "été gagné : deux courbes avec le même CAGR peuvent avoir une "
        "volatilité très différente."
    ),
    "help.sharpe": (
        "Rendement excédentaire par rapport au taux sans risque (fixé "
        "actuellement à {rf_pct}) par unité de volatilité supportée. "
        "Au-dessus de 1, c'est généralement considéré comme un bon résultat."
    ),
    "help.sortino": (
        "Comme le Sharpe (taux sans risque à {rf_pct}), mais le "
        "dénominateur ne compte que l'oscillation à la baisse : il ne "
        "pénalise pas les hausses brusques, seulement les baisses."
    ),
    "help.max_drawdown": (
        "La pire baisse entre un sommet historique et le creux suivant : "
        "la perte la plus profonde qu'il aurait fallu supporter en restant investi."
    ),
    "help.calmar": (
        "CAGR divisé par le max drawdown en valeur absolue : rendement "
        "obtenu par unité de perte maximale subie."
    ),
    "help.miglior_anno": "Le meilleur rendement sur une année civile de la période.",
    "help.peggior_anno": "Le pire rendement sur une année civile de la période.",
    "help.costo_ter": (
        "Différence, en {ccy}, en fin de période entre le montant sans "
        "frais (courbe brute) et celui réellement obtenu (courbe nette)."
    ),
    "help.ricostruito": (
        "Cette ligne inclut un tronçon estimé avec un instrument proxy, "
        "pas des données réelles du fonds : ses métriques doivent être "
        "lues comme indicatives."
    ),

    # --- Graphiques (onglet Portefeuille) -----------------------------------------------------
    "chart.legend_reconstructed": "Portefeuille (reconstitué)",
    "chart.legend_net": "Portefeuille (net de TER)",
    "chart.legend_gross": "Portefeuille (brut, sans TER)",
    "chart.hover_reconstructed_suffix": " (reconstitué)",
    "chart.annotation_real_start": "début des données réelles",
    "chart.annotation_initial_capital": "capital initial",
    "chart.legend_synthetic": "{comparto} (synthétique)",
    "chart.hover_constant_growth": " · croissance constante",
    "chart.yaxis_value": "Valeur ({ccy})",
    "chart.composition_header": "**Composition dans le temps**",
    "chart.synthetic_caption": (
        "⚠️ Les courbes des fonds de pension sont des **droites à "
        "croissance constante**, dérivées du rendement annuel moyen COVIP : "
        "elles montrent où l'on serait arrivé, pas comment on y serait "
        "arrivé. Le parcours réel a fluctué, mais COVIP ne publie pas de "
        "séries historiques."
    ),
    "chart.weights_set_final": "Poids fixés : {pesi} → en fin de période : {pesi_finali}.",
    "chart.rebalance_caption_active": (
        "Rééquilibrage {tipo} : {n} interventions sur la période, la "
        "dernière le {data} (poids fixés : {pesi})."
    ),
    "chart.rebalance_caption_none_yet": (
        "Rééquilibrage {tipo} : aucune intervention encore déclenchée, la "
        "période choisie est plus courte que la première échéance."
    ),

    # --- Onglets -----------------------------------------------------------------------------
    "tab.portafoglio": "📊 Portefeuille",
    "tab.bilanciamento": "⚖️ Répartition",
    "tab.confronto": "🆚 Comparaison de fonds",
    "tab.drawdown": "📉 Drawdown",
    "tab.dati": "📋 Données",
    "tab.previdenza": "🏦 Fonds de pension",

    # --- Onglet Répartition -----------------------------------------------------------------
    "bilancio.header": "**Classification**",
    "bilancio.col_classe": "Classe",
    "bilancio.col_area": "Zone",
    "bilancio.col_settore": "Secteur",
    "bilancio.col_valuta": "Devise",
    "bilancio.peso_help": "Modifiable dans le tableau de composition, en haut de la page.",
    "bilancio.tendina_help": (
        "**{automatica}** conserve la classification déduite, qui peut se "
        "répartir sur plusieurs entrées (un fonds mondial n'est pas "
        "entièrement sur une seule zone). Choisir une entrée lui attribue "
        "l'intégralité de l'instrument."
    ),
    "bilancio.provenienza_prefix": "🏷️ Classification : ",
    "bilancio.provenienza_eodhd": "**{n}** d'EODHD",
    "bilancio.provenienza_yahoo": "**{n}** de Yahoo",
    "bilancio.provenienza_nome": "**{n}** déduits du nom",
    "bilancio.provenienza_manuali": "**{n}** avec corrections manuelles",
    "bilancio.titolo_classe": "Classe d'actifs",
    "bilancio.titolo_area": "Zone géographique",
    "bilancio.titolo_settore": "Secteur",
    "bilancio.titolo_valuta": "Devise de cotation",
    "bilancio.titolo_paesi": "Pays (estimation d'après les principales positions)",
    "bilancio.dettaglio_expander": "🔍 Détail par instrument",
    "bilancio.col_strumento": "Instrument",
    "bilancio.posizioni_expander": "📌 Principales positions",
    "bilancio.posizioni_caption": (
        "Les principales positions lues chez Yahoo pour chaque fonds (ETF "
        "et fonds communs reconnus comme tels) : la base de l'estimation "
        "géographique ci-dessus, utile aussi pour voir les recoupements "
        "entre différents fonds."
    ),
    "bilancio.col_titolo": "Titre",
    "bilancio.col_peso_nel_fondo": "Poids dans le fonds",
    "bilancio.posizioni_none": (
        "Aucune position disponible pour les fonds du portefeuille : cela "
        "nécessite des données de composition de Yahoo, pas toujours présentes."
    ),
    "bilancio.esclusi_caption_one": (
        "ℹ️ {elenco} : compte dans la répartition mais pas dans le backtest, faute de prix."
    ),
    "bilancio.esclusi_caption_many": (
        "ℹ️ {elenco} : comptent dans la répartition mais pas dans le backtest, faute de prix."
    ),
    "bilancio.disclaimer": (
        "⚠️ La classification automatique est **indicative** et doit être "
        "vérifiée sur le DIC : sans EODHD (avec clé) et sans données de "
        "composition de Yahoo, elle est déduite du nom du fonds, ce qui "
        "est souvent insuffisant. Le donut **Pays** est une estimation "
        "basée uniquement sur les principales positions lues chez Yahoo "
        "(généralement un cinquième ou un quart du fonds) : la répartition "
        "géographique complète nécessite un plan EODHD payant. La "
        "**devise** est celle de cotation, pas l'exposition monétaire : un "
        "ETF sur le marché mondial coté en euros reste exposé au dollar."
    ),

    # --- Onglet Comparaison de fonds -----------------------------------------------------------------
    "confronto.caption": (
        "Évolution de {capitale} investis intégralement dans chaque fonds, "
        "pour une comparaison à capital égal."
    ),
    "confronto.legend_reconstructed": "{col} (reconstitué)",
    "confronto.legend_gross": "{col} (brut)",
    "confronto.col_valore_finale": "Valeur finale (depuis {capitale})",
    "confronto.stesso_capitale_caption": (
        "Chaque ligne part du même capital : **{capitale}** investis à "
        "100% dans un seul fonds, et les mêmes **{capitale}** investis "
        "dans le portefeuille avec les poids fixés et le rééquilibrage "
        "choisi. Les valeurs finales sont donc directement comparables "
        "ligne par ligne."
    ),
    "confronto.footnote": (
        "La colonne *Reconstitué* signale les lignes dont les métriques "
        "comprennent une période estimée par un proxy."
    ),
    "confronto.riga_portafoglio": "🎯 PORTEFEUILLE",
    "si": "oui",
    "no": "non",
    "nd": "n/d",

    # --- Onglet Drawdown -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portefeuille",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.yearly_header": "**Rendements par année civile**",
    "drawdown.yaxis_yearly": "Rendement (%)",

    # --- Onglet Données -----------------------------------------------------------------------
    "dati.col_netto": "Portefeuille (net)",
    "dati.col_lordo": "Portefeuille (brut)",
    "dati.col_solo_prefix": "Seulement ",
    "dati.download_button": "⬇️ Télécharger le CSV complet",

    # --- Onglet Fonds de pension -----------------------------------------------------------------
    "previdenza.header_con_anno": "### Retraite complémentaire · données COVIP au 31/12/{anno}",
    "previdenza.header_senza_anno": "### Retraite complémentaire · données COVIP",
    "previdenza.fiscalita_warning": (
        "**La comparaison ne prend pas en compte la fiscalité.** Les "
        "fonds de pension bénéficient d'une déductibilité jusqu'à "
        "5 164,57 € par an, d'une imposition des rendements à 20% au lieu "
        "de 26%, et d'un impôt final qui descend de 15% à 9%. Ce sont des "
        "avantages en leur faveur, donc les chiffres ci-dessous les "
        "**sous-estiment**."
    ),
    "previdenza.rendimenti_caption": (
        "COVIP ne publie que des rendements annuels moyens sur des "
        "horizons fixes, pas de séries historiques : pour ces instruments, "
        "volatilité, drawdown et Sharpe ne peuvent être calculés à partir "
        "d'aucune donnée publique. Pour les obtenir, chargez la valeur de "
        "part de votre fonds avec l'outil de chargement CSV dans la barre "
        "latérale."
    ),
    "previdenza.catalogo_error": (
        "Catalogue COVIP non disponible : vérifiez la connexion et réessayez."
    ),
    "previdenza.forma_label": "Forme de retraite",
    "previdenza.col_tipo": "Type",
    "previdenza.riga_portafoglio": "🎯 VOTRE PORTEFEUILLE",
    "previdenza.categoria_label": "Catégorie",
    "previdenza.cerca_label": "Rechercher par nom de fonds ou de société",
    "previdenza.cerca_placeholder": "ex. 'previgest', 'cometa', 'mediolanum'",
    "previdenza.risultati_caption": "{n} compartiments correspondent aux filtres.",
    "previdenza.comparti_label": "Compartiments à comparer",
    "previdenza.seleziona_hint": (
        "Sélectionnez un ou plusieurs compartiments pour les comparer à "
        "votre portefeuille."
    ),
    "previdenza.rendimento_header": "**Rendement annuel moyen, sur les mêmes fenêtres COVIP**",
    "previdenza.col_help_orizzonte": (
        "Rendement annuel moyen COVIP sur la fenêtre à {anni} ans ({periodo})."
    ),
    "previdenza.col_isc": "ISC 10a",
    "previdenza.col_help_isc": (
        "L'équivalent du TER pour la retraite : incidence annuelle des "
        "coûts sur l'horizon à 10 ans."
    ),
    "previdenza.mancanti_caption": (
        "Votre portefeuille affiche **n/d** sur {elenco_anni} car il ne "
        "couvre pas toute la fenêtre ({dettaglio}). Le calculer sur une "
        "période plus courte donnerait un chiffre non comparable."
    ),
    "previdenza.anni_suffix": "{a} ans",
    "previdenza.il_tuo_portafoglio": "Votre portefeuille",
    "previdenza.yaxis_rendimento": "Rendement annuel moyen (%)",
    "previdenza.costi_header": "**Le poids des coûts**",
    "previdenza.col_comparto": "Compartiment",
    "previdenza.col_isc_annuo": "ISC annuel",
    "previdenza.col_rendimento_10a": "Rendement 10a",
    "previdenza.col_eroso": "Érodé sur {capitale} en 10 ans",
    "previdenza.col_quota_rendimento": "Part du rendement",
    "previdenza.costi_caption": (
        "L'ISC est l'équivalent du TER pour la retraite. La dernière "
        "colonne montre la fraction du rendement net obtenu absorbée "
        "chaque année par les coûts."
    ),
    "previdenza.curve_checkbox": "Afficher les courbes des fonds de pension dans le graphique du portefeuille",
    "previdenza.curve_help": (
        "Droites à croissance constante dérivées du rendement annuel "
        "moyen : elles montrent le point d'arrivée, pas le parcours."
    ),
    "previdenza.orizzonte_label": "Horizon pour dériver le taux",
    "previdenza.fonte_caption": (
        "Source : [COVIP](https://www.covip.it/open-data), données "
        "ouvertes sous licence "
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Le "
        "projet normalise et agrège les jeux de données et calcule "
        "comparaisons et courbes synthétiques ; ces élaborations ne sont "
        "pas des données COVIP originales."
    ),

    # --- Pied de page --------------------------------------------------------------------------
    "footer.disclaimer": (
        "Prix *total return* (dividendes réinvestis). Les VL des fonds "
        "sont déjà nettes du TER ; la courbe brute est une reconstitution "
        "théorique. Les taux de change sont les taux officiels de la BCE "
        "depuis 1999, obtenus via Frankfurter, avec repli sur Yahoo pour "
        "les devises hors panier. Les frais d'entrée/sortie, les spreads "
        "et la fiscalité ne sont pas pris en compte. Les performances "
        "passées ne préjugent pas des performances futures."
    ),
}

METRICHE: dict[str, str] = {
    "final_value": "Valeur finale",
    "total_return": "Rendement total",
    "cagr": "TCAC",
    "volatility": "Volatilité",
    "sharpe": "Sharpe",
    "sortino": "Sortino",
    "max_drawdown": "Drawdown max",
    "calmar": "Calmar",
    "best_year": "Meilleure année",
    "worst_year": "Pire année",
    "ter_cost": "Coût du TER",
    "reconstructed": "Reconstitué",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "aucune donnée",
    "not_configured": "non configurée",
    "isin_required": "ISIN requis",
}

TERMINI: dict[str, str] = {
    "Azionario": "Actions",
    "Obbligazionario": "Obligations",
    "Liquidità": "Liquidités",
    "Materie prime": "Matières premières",
    "Immobiliare": "Immobilier",
    "Non classificato": "Non classé",
    "Globale": "Mondial",
    "Nord America": "Amérique du Nord",
    "Europa": "Europe",
    "Italia": "Italie",
    "Giappone": "Japon",
    "Asia-Pacifico": "Asie-Pacifique",
    "Mercati emergenti": "Marchés émergents",
    "Diversificato": "Diversifié",
    "Tecnologia": "Technologie",
    "Finanza": "Finance",
    "Sanità": "Santé",
    "Energia": "Énergie",
    "Industria": "Industrie",
    "Beni di consumo": "Biens de consommation",
    "Utility": "Services publics",
    "Materiali": "Matériaux",
    "Comunicazioni": "Communications",
    "Resto del fondo": "Reste du fonds",
    "(automatica)": "(automatique)",
    "(nessuno)": "(aucun)",
    "Taiwan": "Taïwan",
    "Hong Kong": "Hong Kong",
    "Corea del Sud": "Corée du Sud",
    "India": "Inde",
    "Regno Unito": "Royaume-Uni",
    "Svizzera": "Suisse",
    "Australia": "Australie",
    "Paesi Bassi": "Pays-Bas",
    "Germania": "Allemagne",
    "Spagna": "Espagne",
    "Francia": "France",
    "Canada": "Canada",
    "Cina": "Chine",
    "Danimarca": "Danemark",
    "Svezia": "Suède",
    "Norvegia": "Norvège",
    "Brasile": "Brésil",
    "Messico": "Mexique",
    "Stati Uniti": "États-Unis",
}

FONTI: dict[str, str] = {
    "auto": "Automatique",
    "yahoo": "Yahoo Finance",
    "justetf": "justETF",
    "eodhd": "EODHD",
    "twelvedata": "Twelve Data",
    "csv": "CSV chargé",
    "openfigi": "OpenFIGI",
    "nome": "Déduit du nom",
}

RIBILANCIAMENTO: dict[str, str] = {
    "none": "Aucun (buy & hold)",
    "monthly": "Mensuel",
    "quarterly": "Trimestriel",
    "yearly": "Annuel",
}
