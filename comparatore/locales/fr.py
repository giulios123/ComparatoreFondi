"""Catalogue français. Les clés doivent correspondre exactement à
`comparatore.locales.it` - `tests/test_i18n.py` vérifie que les quatre
catalogues restent synchronisés."""

LINGUA = "fr"
NOME = "Français"

MESSAGGI: dict[str, str] = {
    # --- En-tête -------------------------------------------------
    "app.page_title": "Comparateur de fonds",
    "app.title": "📈 Comparateur de fonds",
    "app.subtitle": (
        "Backtest de fonds et ETF sur plusieurs sources de données, avec l'impact du TER."
    ),

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

    # --- Barre latérale : PAC (versements périodiques) ---------------------
    "pac.rebalance_caption": (
        "Un versement périodique entre aux poids cibles : c'est un "
        "rééquilibrage doux, donc avec « Aucun » le portefeuille dérive "
        "moins qu'il ne le ferait sans PAC."
    ),
    "pac.expander": "📅 Versements périodiques (PAC)",
    "pac.enable_checkbox": "Activer le plan de versements",
    "pac.help": (
        "Ajoute des versements récurrents au capital initial. Avec le PAC "
        "activé, le rendement de l'instrument (CAGR, Sharpe, drawdown, ...) "
        "reste calculé hors versements ; l'XIRR mesure lui le rendement de "
        "votre argent, versements inclus."
    ),
    "pac.amount_label": "Montant par versement",
    "pac.amount_help": "La somme versée à chaque échéance, dans la devise de référence.",
    "pac.frequency_label": "Fréquence",
    "pac.step_up_label": "Revalorisation annuelle du versement (%)",
    "pac.step_up_help": (
        "Augmente le versement de ce pourcentage une fois par an, par "
        "exemple pour suivre l'inflation ou la progression du salaire."
    ),
    "pac.limit_window_checkbox": "Limiter les versements à une période",
    "pac.start_label": "Premier versement",
    "pac.end_label": "Dernier versement",

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
    "history.caption_usd": (
        "Devise USD : la reconstitution peut utiliser toute la profondeur du proxy."
    ),

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
    "sidebar.risk_free_label": "Taux sans risque annuel % (pour Sharpe)",

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
    "about.credit": "Créé avec curiosité par [Giulio](https://www.gshake.net)",

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
    "editor.col_distribuzione": "Distribution",
    "editor.col_replica": "Réplication",
    "editor.col_peso": "Poids %",
    "editor.col_importo": "Montant ({ccy})",
    "editor.col_ter": "TER %",
    "editor.col_extra": "Coûts extra %",
    "editor.col_fonte": "Source",
    "editor.col_proxy": "Proxy historique",
    "metadata.distribution_accumulating": "Capitalisation",
    "metadata.distribution_distributing": "Distribution",
    "metadata.replication_physical": "Physique",
    "metadata.replication_synthetic": "Synthétique",
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
    "weight.error_importo_min": (
        "Le capital total du portefeuille ne peut pas descendre sous {minimo}."
    ),
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
    "history.reconstructed_note": (
        "**{symbol}** reconstitué depuis le {data} avec {proxy_label}{caveat}"
    ),
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

    # --- Intégrité du backtest --------------------------------------------------------
    "engine.error_quote_non_valide": (
        "Cours invalides (zéro, négatifs ou non finis) pour : {elenco}."
    ),
    "engine.error_date_duplicate": "Dates dupliquées dans l'historique pour : {elenco}.",
    "engine.error_simboli_duplicati": "Symboles dupliqués dans le portefeuille : {elenco}.",
    "engine.error_simboli_senza_prezzi": "Aucune donnée de prix disponible pour : {elenco}.",
    "engine.error_pesi_non_validi": "Pondération invalide pour : {elenco}.",
    "integrita.error_fondi_assenti": (
        "🚫 Le backtest ne peut pas démarrer : aucune donnée de prix pour "
        "{elenco}. Un problème temporaire de la source changerait sinon "
        "l'allocation réellement simulée sans que vous l'ayez choisi."
    ),
    "integrita.allocazione_reale": (
        "En retirant ces fonds, le portefeuille deviendrait : {elenco}."
    ),
    "integrita.button_rimuovi": "Retirer les fonds sans données et continuer",

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
    "help.pac_saldo": (
        "Ce que vaut le portefeuille à la fin, versements compris : "
        "la somme du versé et du gain."
    ),
    "help.pac_versato": "Capital initial plus tous les versements effectués à ce jour.",
    "help.pac_guadagno": "Valeur finale du portefeuille moins le total versé.",
    "help.pac_xirr": (
        "Rendement annuel de votre argent (XIRR) : contrairement au CAGR, "
        "il tient compte de la date de chaque versement, pas seulement du "
        "capital initial."
    ),

    # --- Graphiques (onglet Portefeuille) -----------------------------------------------------
    "chart.legend_reconstructed": "Portefeuille (reconstitué)",
    "chart.legend_net": "Portefeuille (net de TER)",
    "chart.legend_gross": "Portefeuille (brut, sans TER)",
    "chart.hover_reconstructed_suffix": " (reconstitué)",
    "chart.annotation_real_start": "début des données réelles",
    "chart.annotation_initial_capital": "capital initial",
    "chart.legend_invested": "Versements cumulés",
    "chart.legend_pic": "Versement unique",
    "chart.pic_caption": (
        "La ligne **versement unique** montre ce qu'aurait donné le placement, "
        "le premier jour et en une seule fois, du même total que le plan verse "
        "au fil du temps ({totale}) : **{valore_pic}** contre **{valore_pac}** "
        "pour le plan. C'est une comparaison hypothétique : elle suppose que "
        "toute la somme était disponible dès le départ."
    ),
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

    "bilancio.overlap_expander": "🔗 Recoupement des positions",
    "bilancio.overlap_caption": (
        "Le recoupement additionne seulement les positions reconnues : avec une "
        "couverture partielle, c'est une borne inferieure et la part inconnue reste visible."
    ),
    "bilancio.overlap_fund": "Fonds",
    "bilancio.overlap_coverage": "Couverture connue",
    "bilancio.overlap_source": "Source des positions",
    "bilancio.overlap_date": "Date",
    "bilancio.overlap_note": "Note",
    "bilancio.overlap_unknown_date": "date non fournie",
    "bilancio.overlap_stale": "donnees anciennes",
    "bilancio.overlap_ambiguous": "{n} identites ambigues",
    "bilancio.overlap_unavailable": "donnees insuffisantes",
    "bilancio.overlap_ok": "disponible",
    "bilancio.overlap_matrix_header": "**Matrice : recoupement observe (borne inferieure)**",
    "bilancio.overlap_lower_bound": "borne inferieure, pas le recoupement complet",
    "bilancio.overlap_pair": "Paire",
    "bilancio.overlap_value": "Recoupement observe",
    "bilancio.overlap_pair_coverage": "Couvertures",
    "bilancio.overlap_exposure_header": "**Exposition agregee aux positions connues**",
    "bilancio.overlap_position": "Position",
    "bilancio.overlap_portfolio_weight": "Poids dans le portefeuille",
    "bilancio.overlap_unknown": "Part totale non couverte : **{quota}**.",

    "profile.expander": "🧭 Profil personnel (local uniquement)",
    "profile.caption": "Facultatif : il sépare les faits observes des preferences declarees.",
    "profile.horizon_label": "Horizon",
    "profile.objective_label": "Objectif",
    "profile.loss_enable": "Declarer une perte temporaire maximale",
    "profile.loss_label": "Perte maximale toleree (%)",
    "profile.withdrawals_label": "Prelevements prevus",
    "profile.limit_enable": "Declarer une limite par position",
    "profile.limit_label": "Limite par position (%)",
    "profile.preference_label": "Preference",
    "profile.bonds_label": "Obligations autorisees",
    "profile.excluded_classes_label": "Classes exclues",
    "profile.excluded_sectors_label": "Secteurs exclus",
    "profile.save_button": "Enregistrer le profil local",
    "profile.saved_toast": "Profil enregistre uniquement sur cet appareil.",
    "profile.invalid": "Profil non enregistre : {errore}",
    "profile.not_set": "Non defini",
    "profile.years": "{n} ans",
    "profile.yes": "Oui",
    "profile.no": "Non",
    "profile.objective_growth": "Croissance",
    "profile.objective_income": "Revenus",
    "profile.objective_preservation": "Conservation",
    "profile.preference_simplicity": "Simplicite",
    "profile.preference_balanced": "Equilibre",
    "profile.preference_diversification": "Diversification",
    "profile.class_equity": "Actions",
    "profile.class_bond": "Obligations",
    "profile.class_cash": "Liquidites",
    "profile.class_commodities": "Matieres premieres",
    "profile.class_real_estate": "Immobilier",
    "profile.sector_technology": "Technologie",
    "profile.sector_finance": "Finance",
    "profile.sector_health": "Sante",
    "profile.sector_energy": "Energie",
    "profile.sector_industry": "Industrie",
    "profile.sector_consumer": "Biens de consommation",
    "profile.sector_utilities": "Services publics",
    "profile.sector_real_estate": "Immobilier",
    "profile.sector_materials": "Materiaux",
    "profile.sector_communication": "Communications",
    "tab.diagnosi": "🧭 Diagnostic",
    "diagnostic.header": "**Diagnostic local et deterministe**",
    "diagnostic.no_profile": "Aucun profil personnel : les champs manquants sont {campi}.",
    "diagnostic.warning": "Attention selon le profil",
    "diagnostic.info": "Information",
    "diagnostic.portfolio": "Portefeuille",
    "diagnostic.no_evidence": "Aucune preuve numerique",
    "diagnostic.severity_column": "Type",
    "diagnostic.finding_column": "Constat",
    "diagnostic.asset_column": "Instrument",
    "diagnostic.evidence_column": "Preuve",
    "diagnostic.payload_header": "**Apercu du payload anonyme**",
    "diagnostic.payload_caption": (
        "Voici la forme complete qui pourrait etre partagee plus tard ; "
        "rien n'est envoye ici."
    ),
    "diagnostic.generic": "Fait du rapport",
    "diagnostic.profile_missing": "Profil non rempli : aucun seuil personnel applique.",
    "diagnostic.weight_observation": "Poids observe dans le portefeuille.",
    "diagnostic.ter_missing": "TER indisponible pour cet instrument.",
    "diagnostic.ter_observation": "TER et provenance disponibles pour cet instrument.",
    "diagnostic.drawdown_observation": "Drawdown historique maximal observe.",
    "diagnostic.holdings_missing": "Positions sous-jacentes indisponibles.",
    "diagnostic.position_limit_exceeded": "Le poids depasse la limite declaree.",
    "diagnostic.drawdown_exceeds_tolerance": "Le drawdown historique depasse la perte toleree.",
    "diagnostic.history_shorter_than_horizon": "L'historique observe est plus court que l'horizon.",
    "diagnostic.excluded_exposure": "Exposition a une classe ou un secteur exclu.",
    "diagnostic.bonds_not_allowed": "Le profil n'autorise pas les obligations.",
    "diagnostic.correlation_observation": "Des correlations historiques sont disponibles.",
    "diagnostic.rolling_observation": "Des rendements rolling historiques sont disponibles.",
    "diagnostic.benchmark_observation": (
        "Une comparaison historique avec un benchmark est disponible."
    ),
    "diagnostic.inflation_observation": "Des donnees historiques d'inflation sont disponibles.",
    "diagnostic.overlap_observation": "Une analyse historique du recoupement est disponible.",

    # --- Onglet Comparaison de fonds ------------------------------------
    "confronto.caption": (
        "Évolution de {capitale} investis intégralement dans chaque fonds, "
        "pour une comparaison à capital égal."
    ),
    "confronto.caption_pac": (
        "Évolution de {capitale} investis entièrement dans chaque fonds, avec "
        "le même plan de versements que le portefeuille : la comparaison reste "
        "à capital et versements égaux."
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
    "confronto.col_valore_finale_pac": "Valeur finale (de {capitale} + versements)",
    "confronto.stesso_capitale_caption_pac": (
        "Toutes les lignes reçoivent le même capital initial (**{capitale}**) "
        "et le même plan de versements. *Valeur finale* est le solde réel à la "
        "fin, versements compris, et *XIRR* est le rendement de votre argent, "
        "qui tient compte de la date d'entrée de chaque versement. Toutes les "
        "autres mesures sont calculées **hors versements** : un versement "
        "n'est pas un gain de marché."
    ),
    "confronto.footnote": (
        "La colonne *Reconstitué* signale les lignes dont les métriques "
        "comprennent une période estimée par un proxy."
    ),
    "confronto.riga_portafoglio": "🎯 PORTEFEUILLE",
    "si": "oui",
    "no": "non",
    "nd": "n/d",
    "benchmark.expander": "🎯 Benchmark et analyses comparatives",
    "benchmark.label": "Référence",
    "benchmark.option_none": "Aucun",
    "benchmark.option_VT": "Actions mondiales (VT, rendement total)",
    "benchmark.option_VFINX": "S&P 500 (VFINX, rendement total)",
    "benchmark.option_custom": "Rechercher un instrument",
    "benchmark.search_label": "Rechercher le benchmark",
    "benchmark.search_placeholder": "Symbole, nom ou ISIN",
    "benchmark.selected": "Benchmark sélectionné : **{symbol}**",
    "benchmark.remove_button": "Retirer le benchmark",
    "benchmark.failed": "Benchmark indisponible : {errore}",
    "benchmark.source": "Source du benchmark : {source} · cotation : {symbol}",
    "benchmark.attempts": "Tentatives de résolution : {elenco}",
    "benchmark.legend": "Benchmark {symbol}",
    "benchmark.metrics_header": "Comparaison sur la période commune",
    "benchmark.metric": "Série",
    "benchmark.portfolio_label": "Votre portefeuille",
    "benchmark.growth": "Rendement total",
    "benchmark.cagr": "CAGR",
    "benchmark.volatility": "Volatilité",
    "benchmark.max_drawdown": "Drawdown max",
    "benchmark.active_return": "Rendement actif",
    "benchmark.tracking_error": "Tracking error",
    "benchmark.information_ratio": "Information ratio",
    "benchmark.common_period": "Période commune : {start} → {end} · {n} observations mensuelles",
    "benchmark.common_period_short": "la période commune compte moins de deux observations",
    "benchmark.metric_reason": "Note : {motivo}.",
    "benchmark.reason_common_empty": "la période commune est vide",
    "benchmark.reason_insufficient": "l'échantillon mensuel est insuffisant",
    "benchmark.reason_tracking_error_zero": "le tracking error est nul",
    "benchmark.reason_generic": "la métrique ne peut pas être calculée",
    "benchmark.correlation_header": "Corrélations des rendements mensuels",
    "benchmark.correlation_portfolio_header": "Corrélations entre portefeuille et instruments",
    "benchmark.rolling_header": "Rendements glissants annualisés",
    "benchmark.rolling_period": "Fenêtre",
    "benchmark.rolling_worst": "Pire",
    "benchmark.rolling_median": "Médiane",
    "benchmark.rolling_best": "Meilleur",
    "benchmark.rolling_positive": "Fenêtres positives",
    "benchmark.rolling_observations": "Observations",
    "benchmark.years": "{n} ans",
    "inflation.expander": "📉 Rendement réel et inflation",
    "inflation.enable_checkbox": "Afficher les valeurs nettes de l'inflation",
    "inflation.enable_help": "Utilise l'indice HICP mensuel officiel d'Eurostat.",
    "inflation.area_label": "Zone du pouvoir d'achat",
    "inflation.area_it": "Italie",
    "inflation.area_ea": "Zone euro",
    "inflation.retry_button": "Réessayer Eurostat",
    "inflation.real_curve": "Portefeuille en pouvoir d'achat réel",
    "inflation.metrics_header": "Comparaison nominale et réelle",
    "inflation.metric_kind": "Valeurs",
    "inflation.metric_total_return": "Rendement total",
    "inflation.metric_cagr": "CAGR",
    "inflation.metric_final": "Valeur finale",
    "inflation.nominal": "Nominal",
    "inflation.real": "Réel",
    "inflation.coverage_caption": (
        "Source : {source} · zone : {area} · couverture : {first} → {last}"
    ),
    "inflation.pac_caption": "PAC versé : {nominal} nominaux · {real} au pouvoir d'achat initial.",
    "inflation.failed": "Analyse réelle indisponible : {errore}",
    "inflation.coverage_missing": "L'indice HICP ne couvre pas la période du portefeuille.",
    "inflation.stale_caption": (
        "Eurostat ne répond pas : des données en cache potentiellement obsolètes sont affichées."
    ),

    # --- Onglet Drawdown -----------------------------------------------------------------------
    "drawdown.legend_portafoglio": "Portefeuille",
    "drawdown.yaxis": "Drawdown (%)",
    "drawdown.pac_caption": (
        "Avec le plan actif, la perte maximale et les rendements annuels sont "
        "calculés hors versements : sinon chaque versement apparaîtrait comme "
        "un gain de marché et les baisses sembleraient plus douces qu'elles "
        "ne l'ont été."
    ),
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
    "previdenza.pac_caption": (
        "**Avec le plan actif**, dans cet onglet : les courbes des "
        "compartiments sur le graphique du portefeuille reçoivent le même plan "
        "de versements ; le rendement de votre portefeuille est celui hors "
        "versements, car c'est ainsi que la COVIP calcule les siens ; "
        "l'érosion des frais et le capital projeté utilisent votre versement "
        "pendant dix ans, maintenu **constant** — la revalorisation annuelle "
        "n'entre pas dans cette projection."
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
    "previdenza.col_orizzonte": "{etichetta} · {periodo}",
    "previdenza.legenda_caption": (
        "Chaque colonne est une fenêtre fermée en soi, pas une période "
        "cumulative : les dates sont dans l'en-tête. Une valeur à 10 ans "
        "inférieure à celle à 5 ans signifie que la première moitié de la "
        "décennie a moins rapporté, pas que le fonds s'est dégradé récemment. "
        "**ISC 10a** est l'indicateur synthétique des coûts, l'équivalent du "
        "TER pour la retraite : le poids moyen annuel des frais sur un horizon "
        "de dix ans."
    ),
    "previdenza.portafoglio_periodo_proprio": (
        "Votre backtest couvre **{inizio} → {fine}** ({anni} ans) et a rapporté "
        "**{rendimento}** par an : un chiffre non comparable aux colonnes "
        "ci-dessus. Les fenêtres COVIP sont des **années civiles entières**, du "
        "1er janvier au 31 décembre : une période qui commence ou finit en "
        "milieu d'année ne les couvre pas, même quand les années du calendrier "
        "semblent les mêmes."
    ),
    "previdenza.allinea_button": "📐 Régler la période sur {inizio} → {fine}",
    "previdenza.allinea_caption": (
        "Modifie les dates du backtest pour couvrir les fenêtres COVIP. Le "
        "backtest démarre de toute façon à la première date où **tous** les "
        "fonds sélectionnés ont des données : les fenêtres les plus longues "
        "restent **n/d** si un fonds est plus récent."
    ),
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
    "previdenza.anno_suffix": "{a} an",
    "previdenza.anni_suffix": "{a} ans",
    "previdenza.il_tuo_portafoglio": "Votre portefeuille",
    "previdenza.yaxis_rendimento": "Rendement annuel moyen (%)",
    "previdenza.costi_header": "**Le poids des coûts**",
    "previdenza.col_comparto": "Compartiment",
    "previdenza.col_isc_annuo": "ISC annuel",
    "previdenza.col_rendimento_10a": "Rendement 10a",
    "previdenza.col_eroso": "Érodé sur {capitale} en 10 ans",
    "previdenza.col_eroso_pac": "Érodé sur {capitale} versés en 10 ans",
    "previdenza.col_quota_rendimento": "Part du rendement",
    "previdenza.col_montante_pac_10a": "Montant projeté (PAC, 10 ans)",
    "previdenza.costi_caption": (
        "L'ISC est l'équivalent du TER pour la retraite. La dernière "
        "colonne montre la fraction du rendement net obtenu absorbée "
        "chaque année par les coûts."
    ),
    "previdenza.curve_checkbox": (
        "Afficher les courbes des fonds de pension dans le graphique du portefeuille"
    ),
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

    "directa.expander": "Importer un portefeuille Directa",
    "directa.caption": (
        "Chargez un CSV/XLSX, mappez les colonnes et vérifiez l'aperçu avant l'import."
    ),
    "directa.upload_label": "Fichier exporté de Directa",
    "directa.sheet_label": "Feuille",
    "directa.header_row_label": "Ligne d'en-tête (0 = première ligne)",
    "directa.header_row_help": (
        "Si des lignes descriptives précèdent le tableau, indiquez ici la ligne d'en-tête."
    ),
    "directa.file_error": "Fichier Directa illisible : {errore}",
    "directa.movements_file": (
        "Ce fichier est un export des mouvements, pas des positions : il "
        "contient les achats et les commissions, mais pas la valeur actuelle. "
        "Pour importer le portefeuille, utilisez l'export des positions de Directa."
    ),
    "directa.no_column": "(aucune)",
    "directa.value_column": "Colonne valeur actuelle",
    "directa.isin_column": "Colonne ISIN",
    "directa.ticker_column": "Colonne ticker",
    "directa.name_column": "Colonne nom",
    "directa.currency_column": "Colonne devise (optionnelle)",
    "directa.quantity_column": "Colonne quantité (optionnelle)",
    "directa.average_column": "Colonne prix de revient (optionnelle)",
    "directa.preview_identifier": "Identifiant",
    "directa.preview_name": "Nom",
    "directa.preview_value": "Valeur actuelle",
    "directa.issue_row": "Ligne",
    "directa.issue_column": "Colonne",
    "directa.issue_message": "Problème",
    "directa.issue_invalid_isin": "ISIN non valide.",
    "directa.issue_missing_identifier": "ISIN ou ticker manquant.",
    "directa.issue_summary_row": (
        "Ligne récapitulative sans instrument : excluez-la de l'importation."
    ),
    "directa.issue_invalid_value": "La valeur actuelle doit être positive.",
    "directa.issue_invalid_quantity": "La quantité doit être positive.",
    "directa.issue_invalid_average": "Le prix moyen de revient doit être positif.",
    "directa.value_currency": "Devise des valeurs",
    "directa.mapping_error": "Mappage incomplet : {errore}",
    "directa.issues": "{n} lignes ne peuvent pas être importées",
    "directa.instrument_label": "Cotation pour {nome}",
    "directa.exclude_unresolved": "Exclure explicitement les lignes non importables",
    "directa.unresolved": "Sans cotation ou non pris en charge : {elenco}",
    "directa.import_button": "Importer les positions résolues",
    "directa.import_success": "{n} positions Directa importées",
    "costs.pic_expander": "Frais d'entrée et de sortie du PIC",
    "costs.pic_caption": "Estimation séparée : le backtest et ses métriques ne changent pas.",
    "costs.pic_enable": "Calculer l'estimation des frais PIC",
    "costs.mode_label": "Type de frais",
    "costs.mode_none": "Aucun frais",
    "costs.mode_fixed": "Montant fixe par ordre",
    "costs.mode_percentage": "Pourcentage par ordre",
    "costs.fixed_label": "Montant fixe",
    "costs.rate_label": "Pourcentage %",
    "costs.minimum_label": "Minimum",
    "costs.maximum_label": "Maximum (0 = sans limite)",
    "costs.maximum_help": "Zéro signifie qu'aucun plafond ne s'applique.",
    "costs.buy_title": "Entrée",
    "costs.sell_title": "Sortie",
    "costs.pic_error": "Impossible de calculer les frais PIC : {errore}",
    "costs.pic_result_expander": "Impact estimé des commissions PIC",
    "costs.pic_result_caption": (
        "Les frais d'entrée sont réservés dans le budget ; les frais de sortie "
        "sont calculés par fonds."
    ),
    "costs.pic_budget": "Budget",
    "costs.pic_buy_total": "Total entrée",
    "costs.pic_sell_total": "Total sortie",
    "costs.pic_net_final": "Montant net",
    "costs.pic_line_investable": "Capital réellement investi",
    "costs.pic_line_before_sell": "Montant avant sortie",
    "costs.pic_line_without": "Montant sans frais",
    "costs.pic_line_difference": "Différence totale",
    "costs.pic_column_item": "Élément",
    "costs.pic_column_value": "Valeur",
    "costs.pic_column_side": "Opération",
    "costs.pic_column_symbol": "Symbole",
    "costs.pic_column_notional": "Valeur de l'ordre",
    "costs.pic_column_fee": "Frais",
    "ter_warning.retry_button": "Réessayer la récupération du TER",
    "ter_warning.attempts": "{symbol} : {esiti}",
    "ter_warning.sources": "Source TER : {elenco}",
    "search.info_button": "Fiche",
    "editor.col_scheda": "Fiche",
    "editor.scheda_help": (
        "Afficher les données descriptives, les sources et les conflits de l'instrument."
    ),
    "instrument.title": "Fiche informative de l'instrument",
    "instrument.loading": "Récupération des données de l'instrument…",
    "instrument.not_available": "Indisponible",
    "instrument.date_not_available": "date indisponible",
    "instrument.date_placeholder": "AAAA-MM-JJ",
    "instrument.fact_provenance": "Source : {source} · observé : {observed} · qualité : {quality}",
    "instrument.fact_conflict_entry": "{source} : {value} · observé : {observed}",
    "instrument.quality_reported": "déclaré par la source",
    "instrument.quality_document": "vérifié dans le document",
    "instrument.quality_manual": "saisi manuellement",
    "instrument.quality_derived": "dérivé",
    "instrument.no_conflicts": "Aucun conflit entre les faits acquis.",
    "instrument.fact_generic": "Donnée",
    "instrument.fact_name": "Nom",
    "instrument.fact_ter": "TER",
    "instrument.fact_issuer": "Émetteur",
    "instrument.fact_category": "Catégorie",
    "instrument.fact_index": "Indice suivi",
    "instrument.fact_domicile": "Domicile",
    "instrument.fact_fund_currency": "Devise du fonds",
    "instrument.fact_inception": "Date de lancement",
    "instrument.fact_aum": "Actifs",
    "instrument.fact_kid_url": "Lien KID",
    "instrument.fact_kid_date": "Date du KID",
    "instrument.fact_sri": "Risque synthétique (1–7)",
    "instrument.fact_history_start": "Début de couverture observée",
    "instrument.fact_history_end": "Fin de couverture observée",
    "instrument.identity_section": "Identité et cotation",
    "instrument.identity_field": "Champ",
    "instrument.identity_value": "Valeur",
    "instrument.identity_symbol": "Symbole actif",
    "instrument.identity_isin": "ISIN",
    "instrument.identity_exchange": "Marché",
    "instrument.identity_currency": "Devise de cotation",
    "instrument.costs_section": "Coûts et KID",
    "instrument.characteristics_section": "Caractéristiques",
    "instrument.allocation_section": "Allocation et participations",
    "instrument.holdings_missing": "Les principales participations sont indisponibles.",
    "instrument.holding_symbol": "Symbole",
    "instrument.holding_name": "Nom",
    "instrument.holding_weight": "Part",
    "instrument.history_section": "Couverture historique",
    "instrument.related_section": "Cotations liées",
    "instrument.related_missing": "Aucune autre cotation avec le même ISIN n'est disponible.",
    "instrument.related_symbol": "Symbole",
    "instrument.related_exchange": "Marché",
    "instrument.related_currency": "Devise",
    "instrument.related_source": "Source",
    "instrument.sources_section": "Sources et conflits",
    "instrument.attempt": "{source} : {outcome}",
    "instrument.kid_section": "Données vérifiées dans le KID",
    "instrument.kid_ter_enabled": "Définir le TER depuis le KID",
    "instrument.kid_url_label": "URL du KID",
    "instrument.kid_date_label": "Date du document (AAAA-MM-JJ)",
    "instrument.sri_label": "Indicateur synthétique de risque (1–7)",
    "instrument.kid_save": "Enregistrer les données KID",
    "instrument.kid_url_invalid": "L'URL doit commencer par http:// ou https://.",
    "instrument.kid_date_invalid": "La date du KID doit être au format AAAA-MM-JJ.",
    "instrument.kid_date_future": "La date du KID ne peut pas être future.",
    "instrument.kid_saved": "Données KID enregistrées.",
    "instrument.kid_clear": "Supprimer les données KID",
    "instrument.retry_button": "Réessayer l'acquisition",
    "instrument.add_button": "Ajouter au portefeuille",
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
    "balance": "Solde final",
    "invested": "Versé",
    "gain": "Gain",
    "xirr": "XIRR",
}

ESITI: dict[str, str] = {
    "ok": "ok",
    "no_data": "aucune donnée",
    "not_configured": "non configurée",
    "isin_required": "ISIN requis",
    "found": "trouvé",
    "no_ter": "TER absent",
    "blocked": "bloqué par le forfait",
    "symbol_unresolved": "symbole non résolu",
    "temporary_error": "erreur temporaire",
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
    "manual": "Saisie manuelle",
    "kid": "KID",
    "missing": "Indisponible",
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
