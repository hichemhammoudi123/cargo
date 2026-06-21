# Explication détaillée de chaque endpoint

---

## 1. Shipments (Expéditions) — 7 endpoints

### `POST /api/v1/cargo/shipments`
**Créer une expédition**

**Quand ?** L'utilisateur a choisi un transporteur (DHL/UPS/...) via la page Rates, et veut expédier un colis.

**Ce qui se passe :**
```
1. Tu envoies les données (destinataire, colis, assurance...)
2. L'Adapter du transporteur choisi transforme ces données dans le format JSON attendu par l'API du transporteur
   Ex: "country":"FR" → DHL attend "countryCode":"FR", UPS attend "country":"FR"
3. L'Adapter appelle l'API du transporteur (POST /shipments)
4. Le transporteur répond avec un numéro de suivi, une étiquette, un prix
5. L'Adapter normalise la réponse dans notre format commun
6. Le Core System sauvegarde l'expédition avec status = "SUBMITTED"
7. L'utilisateur reçoit l'ID interne, le numéro de suivi et l'URL de l'étiquette
```

**Règles métier :**
- Le transporteur doit être actif et connecté (vérifié via CarrierRegistry)
- L'adresse doit être validée (optionnel mais recommandé)
- Si l'API transporteur est injoignable → erreur 502 + retry automatique

---

### `GET /api/v1/cargo/shipments`
**Lister les expéditions**

**Quand ?** Page d'accueil, tableau de bord, recherche.

**Ce qui se passe :**
```
1. Requête paginée avec filtres optionnels (statut, transporteur, date)
2. Le Core System interroge la base de données
3. Retourne la liste avec pagination
```

**Filtres disponibles :**
```
?status=IN_PROGRESS       → Statut interne (PENDING, PICKED_UP, IN_PROGRESS, DELIVERED...)
&carrier=UPS              → Code transporteur
&from=2026-06-01          → Date de création min
&to=2026-06-14            → Date de création max
&q=CMD-2026               → Recherche texte (référence, nom destinataire)
&page=1&limit=20          → Pagination
```

---

### `GET /api/v1/cargo/shipments/{id}`
**Détail d'une expédition**

**Quand ?** L'utilisateur clique sur une expédition pour voir tous ses détails.

**Ce qui se passe :**
```
1. Récupère l'expédition par son ID
2. Retourne toutes les infos : statut, historique, prix, colis, adresses
3. Le statut affiché est le statut INTERNE (PENDING, IN_PROGRESS, DELIVERED...)
4. Le statut brut du transporteur est conservé à côté (OnTheWay, Yolda...)
```

**Pourquoi deux statuts ?** Le `internalStatus` est notre statut normalisé (6 valeurs). Le `carrierStatus` est le statut brut retourné par le transporteur — utile pour le debug et la traçabilité.

---

### `PUT /api/v1/cargo/shipments/{id}`
**Modifier une expédition**

**Quand ?** L'utilisateur veut changer la référence, les options (signature, assurance) avant que le colis soit pris en charge.

**Règles métier :**
- Modification possible seulement si status = `SUBMITTED` (pas encore pris en charge)
- Impossible de changer le transporteur ou le destinataire après création
- Les modifications ne sont pas synchronisées avec le transporteur (sauf si son API le permet)

---

### `DELETE /api/v1/cargo/shipments/{id}`
**Supprimer une expédition**

**Quand ?** L'utilisateur veut supprimer définitivement une expédition (brouillon, test, erreur).

**Règles métier :**
- Suppression possible seulement si status = `SUBMITTED` ou `PENDING`
- Si le colis est déjà en transit → utiliser `POST /cancel` à la place

---

### `POST /api/v1/cargo/shipments/{id}/cancel`
**Annuler une expédition**

**Quand ?** Le colis est déjà pris en charge mais on veut l'annuler (client annule sa commande, erreur d'envoi).

**Ce qui se passe :**
```
1. Vérifie que l'expédition n'est pas déjà livrée ou annulée
2. Appelle l'Adapter → API du transporteur pour annuler
3. Le transporteur confirme l'annulation (ou refuse si déjà livré)
4. Le statut passe à "CANCELLED" dans le Core
5. Un événement "shipment.cancelled" est publié → notification client
```

**Règles métier :**
- Impossible si status = `DELIVERED` (déjà livré)
- Impossible si status = `CANCELLED` (déjà annulé)
- Le transporteur peut refuser l'annulation (ex: colis déjà en livraison finale)

---

### `POST /api/v1/cargo/shipments/{id}/label`
**Générer l'étiquette d'expédition**

**Quand ?** L'utilisateur veut télécharger ou réimprimer l'étiquette.

**Ce qui se passe :**
```
1. Appelle l'Adapter → API du transporteur pour récupérer l'étiquette
2. Retourne l'URL de l'étiquette au format demandé (PDF, ZPL, PNG)
3. L'URL peut être une URL directe ou un lien temporaire signé
```

---

## 2. Tracking (Suivi) — 2 endpoints

### `GET /api/v1/cargo/shipments/{id}/tracking`
**Suivi détaillé d'une expédition**

**Quand ?** L'utilisateur clique sur "Suivre" ou la page Tracking se rafraîchit.

**Ce qui se passe :**
```
1. Appelle l'Adapter → API du transporteur pour récupérer les événements récents
2. Pour chaque événement, le StatusMapper traduit le statut brut → statut interne
   Ex: "OnTheWay" (UPS) → "IN_PROGRESS"
   Ex: "Yolda" (Yurtiçi) → "IN_PROGRESS"
   Ex: "En cours d'acheminement" (Chronopost) → "IN_PROGRESS"
3. Les événements sont regroupés en milestones (étapes clés du cycle de vie)
4. Retourne la timeline complète avec localisation et horodatage
```

**Ce qui est retourné :**
- `currentStatus` → le dernier statut (interne + brut transporteur)
- `events[]` → tous les événements depuis la création
- `milestones` → les étapes clés (prise en charge, transit, livraison)
- `carrierRawStatus` conservé pour chaque événement → debug possible

---

### `POST /api/v1/cargo/webhooks/{carrierCode}`
**Webhook entrant (push du transporteur)**

**Quand ?** Le transporteur notifie automatiquement le système quand un événement se produit (colis pris en charge, livré, etc.).

**Ce qui se passe :**
```
1. Le transporteur envoie une requête HTTP POST avec son format JSON brut
   Ex: UPS → { "shipment_id": "1Z999...", "state": "Completed" }
   Ex: DHL → { "trackingNumber": "12345", "status": "DELIVERED" }
   Ex: Yurtiçi → { "takipNo": "12345", "durum": "Teslim Edildi" }
2. Validation de la signature HMAC (sécurité)
3. L'Adapter parse le payload → format normalisé { tracking_no, carrier_raw_status, ... }
4. Le StatusMapper traduit le statut brut → statut interne
   "Completed" → DELIVERED
   "Teslim Edildi" → DELIVERED
5. Core : crée un TrackingEvent, met à jour le Shipment.status
6. Si le statut est terminal (DELIVERED, FAILED, RETURNED, CANCELLED) :
   - Publie un événement (notification client, webhook sortant, audit)
   - Déclenche les actions post-livraison (archivage, facturation)
7. Retourne 200 au transporteur (accusé réception)
```

**Pourquoi toujours 200 ?** Le transporteur considère qu'un webhook non-200 est un échec et le renvoie. Même si le traitement échoue côté serveur, on répond 200 et on log l'erreur.

**Sécurité :** Chaque transporteur a un `webhookSecret` stocké dans ses credentials. La signature HMAC-SHA256 du payload est validée avant tout traitement.

---

## 3. Rates (Tarifs) — 1 endpoint

### `POST /api/v1/cargo/rates`
**Comparer les prix des transporteurs**

**Quand ?** L'utilisateur remplit le formulaire (expéditeur, destinataire, colis) et clique "Obtenir les prix".

**Ce qui se passe :**
```
1. Récupère tous les transporteurs actifs (ou ceux demandés dans carrierCodes[])
2. Pour chaque transporteur, appelle son Adapter : adapter.getRates(rateRequest)
   → L'Adapter transforme la requête dans le format de son API
   → Appelle l'API du transporteur
   → Normalise la réponse
3. Tous les appels sont parallélisés (Promise.all) pour la performance
4. Les résultats sont agrégés et triés par prix croissant
5. Retourne le tableau comparatif
```

**Cas où un transporteur ne répond pas :**
- Si un transporteur est injoignable → il est exclu des résultats avec une erreur dans `errors[]`
- Les autres transporteurs sont quand même retournés

```json
{
  "success": true,
  "data": [ /* transporteurs qui ont répondu */ ],
  "errors": [
    { "carrierCode": "ARAMEX", "message": "Connection timeout" }
  ]
}
```

---

## 4. Pickups (Enlèvements) — 2 endpoints

### `POST /api/v1/cargo/pickups`
**Planifier un enlèvement**

**Quand ?** L'utilisateur a créé des expéditions et veut que le transporteur vienne chercher les colis à son entrepôt.

**Ce qui se passe :**
```
1. Vérifie que les expéditions référencées (shipmentIds) existent et sont au statut SUBMITTED
2. Appelle l'Adapter → API du transporteur pour planifier l'enlèvement
3. Le transporteur confirme avec un numéro de confirmation
4. Le Pickup est créé en base avec status = "CONFIRMED"
```

**Règles métier :**
- Les expéditions doivent appartenir au même transporteur
- `pickupDate` ne peut pas être dans le passé
- `readyTime` doit être avant `closeTime`
- Le transporteur peut refuser si le créneau est indisponible

---

### `POST /api/v1/cargo/pickups/{id}/cancel`
**Annuler un enlèvement**

**Quand ?** L'utilisateur veut annuler la venue du transporteur.

**Règles métier :**
- Annulation possible seulement si le pickup n'a pas encore eu lieu (pickupDate >= today)
- Appelle l'Adapter → API du transporteur pour annuler
- Passe le statut à "CANCELLED"

---

## 5. Carriers (Transporteurs) — 7 endpoints

### `POST /api/v1/cargo/carriers`
**Ajouter un nouveau transporteur**

**Quand ?** L'administrateur veut intégrer un nouveau transporteur (ex: MNG Kargo, Aramex, etc.).

**Ce qui se passe :**
```
1. Reçoit les infos du transporteur (nom, API endpoint, clés, services...)
2. Sauvegarde en base avec status = "PENDING_TEST" (pas encore testé)
3. L'Adapter correspondant doit être codé et déployé avant de pouvoir utiliser ce transporteur
4. Retourne un message : "Run a connection test before using"
```

**Champs importants :**
- `adapterName`: le nom de la classe Adapter (ex: "MngKargoAdapter") — permet au Registry de charger le bon adaptateur
- `credentials`: stocké chiffré en base (AES-256-GCM)
- `services[]`: les services disponibles (ex: "MNG_STANDARD", "MNG_EXPRESS")

---

### `GET /api/v1/cargo/carriers`
**Lister les transporteurs**

**Quand ?** Page de gestion des transporteurs.

**Filtres :**
- `?active=true` → transporteurs actifs uniquement
- `?feature=TRACKING` → transporteurs qui supportent le tracking
- `?zone=TR` → transporteurs qui livrent en Turquie

---

### `GET /api/v1/cargo/carriers/{code}`
**Détail d'un transporteur**

**Quand ?** L'administrateur clique sur un transporteur pour voir/configurer ses paramètres.

Retourne : services, capabilities, settings, contact. (Les credentials ne sont jamais retournés — seulement la date de dernière màj.)

---

### `PUT /api/v1/cargo/carriers/{code}`
**Modifier les paramètres d'un transporteur**

**Quand ?** L'administrateur veut changer le timeout, le nombre de retry, ou activer/désactiver le suivi polling.

```json
{ "settings": { "timeoutMs": 15000, "retryMaxAttempts": 5 } }
```

---

### `DELETE /api/v1/cargo/carriers/{code}`
**Supprimer un transporteur**

**Quand ?** L'administrateur veut retirer définitivement un transporteur.

**Règles métier :**
- Ne supprime pas les expéditions existantes (elles restent en lecture seule)
- Le transporteur n'est plus disponible pour les nouvelles expéditions
- Les credentials sont définitivement supprimés

---

### `PATCH /api/v1/cargo/carriers/{code}/toggle`
**Activer / désactiver un transporteur**

**Quand ?** Le transporteur a une panne API (ex: FedEx API down) → on le désactive temporairement. Quand l'API revient → on le réactive.

**Ce qui se passe :**
```
Quand active = false :
  - Le transporteur n'est plus appelé pour les rates
  - Plus de nouvelles expéditions possibles avec ce transporteur
  - Les expéditions en cours continuent normalement
  - Un événement "carrier.disconnected" est publié

Quand active = true :
  - Le transporteur redevient disponible
  - Un événement "carrier.connected" est publié
  - Recommandé : tester la connexion avant de réactiver
```

---

### `POST /api/v1/cargo/carriers/{code}/test`
**Tester la connexion à l'API du transporteur**

**Quand ?** Juste après avoir ajouté un transporteur, ou après une màj des credentials, ou périodiquement.

**Ce qui se passe :**
```
1. Appelle l'Adapter → adapter.testConnection()
2. L'Adapter fait un appel léger à l'API du transporteur (ex: GET /health)
3. Mesure la latence
4. Vérifie que les credentials sont valides
5. Met à jour le statut du transporteur :
   - Succès → "CONNECTED"
   - Échec → "ERROR" (avec le message d'erreur)
```

---

### `PUT /api/v1/cargo/carriers/{code}/credentials`
**Mettre à jour les clés API**

**Quand ?** La clé API a expiré, a été compromise, ou l'administrateur fait une rotation de clés.

**Ce qui se passe :**
```
1. Les nouvelles clés sont chiffrées et stockées
2. La date de mise à jour est enregistrée
3. Le statut repasse à "PENDING_TEST" (les anciennes clés ne sont plus valides)
4. Il est recommandé de tester la connexion après la màj
```

---

### `POST /api/v1/cargo/carriers/{code}/services`
**Ajouter un service au catalogue**

**Quand ?** Le transporteur a lancé un nouveau service (ex: "UPS Standard" en plus de "UPS Express Saver").

---

## 6. Address (Adresse) — 1 endpoint

### `POST /api/v1/cargo/addresses/validate`
**Valider et normaliser une adresse**

**Quand ?** Avant de créer une expédition, l'utilisateur peut vérifier que l'adresse du destinataire est correcte.

**Ce qui se passe :**
```
1. Appelle l'Adapter du transporteur → API du transporteur pour valider l'adresse
2. Le transporteur peut normaliser l'adresse (corriger la casse, compléter le code postal)
3. Il peut aussi suggérer des adresses alternatives si l'adresse est ambiguë
4. Retourne :
   - valid: true/false
   - normalizedAddress: l'adresse normalisée par le transporteur
   - suggestions: [] si valide, [adresses suggérées] si invalide
```

**Pourquoi passer par le transporteur ?**
- DHL valide mieux les adresses allemandes
- Yurtiçi valide mieux les adresses turques (İstanbul, İzmir...)
- Le transporteur aura les dernières données de codification postale

---

## Résumé : Qui fait quoi ?

| Endpoint | Appel API externe ? | Utilise le Mapper ? | Met à jour le statut ? |
|---|---|---|---|
| POST create | ✅ → transporteur | ❌ | ✅ SUBMITTED |
| GET list | ❌ | ❌ | ❌ |
| GET detail | ❌ | ❌ | ❌ |
| PUT update | ❌ (sauf si API le permet) | ❌ | ❌ |
| DELETE delete | ❌ | ❌ | ❌ |
| POST cancel | ✅ → transporteur | ❌ | ✅ CANCELLED |
| POST label | ✅ → transporteur | ❌ | ❌ |
| GET tracking | ✅ → transporteur | ✅ | ❌ (juste consultation) |
| POST webhook | ❌ (le transporteur nous appelle) | ✅ | ✅ (met à jour) |
| POST rates | ✅ → tous les transporteurs | ❌ | ❌ |
| POST pickup | ✅ → transporteur | ❌ | ❌ |
| POST pickup cancel | ✅ → transporteur | ❌ | ✅ |
| POST carriers | ❌ | ❌ | ❌ |
| GET carriers | ❌ | ❌ | ❌ |
| GET carrier detail | ❌ | ❌ | ❌ |
| PUT carrier | ❌ | ❌ | ❌ |
| DELETE carrier | ❌ | ❌ | ❌ |
| PATCH toggle | ❌ | ❌ | ❌ |
| POST test | ✅ → transporteur | ❌ | ✅ (status = CONNECTED/ERROR) |
| PUT credentials | ❌ | ❌ | ❌ |
| POST service | ❌ | ❌ | ❌ |
| POST address | ✅ → transporteur | ❌ | ❌ |

**Rappel :** Les 3 endpoints qui utilisent le StatusMapper sont :
1. `GET /tracking` → pour traduire chaque événement
2. `POST /webhooks/{carrierCode}` → pour traduire le statut reçu
3. (optionnel) `GET /shipments/{id}` → pour afficher le statut interne
