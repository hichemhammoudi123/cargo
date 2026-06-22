Scénario métier complet (étapes réalistes)
Étape 1 — Admin : Ajouter un transporteur
POST http://localhost:8000/api/v1/cargo/carriers

{
  "code": "DHL",
  "name": "DHL Express",
  "website": "https://www.dhl.com"
}
Étape 2 — Admin : Tester la connexion
POST http://localhost:8000/api/v1/cargo/carriers/DHL/test (pas de body)

Étape 3 — Admin : Ajouter un service au transporteur
POST http://localhost:8000/api/v1/cargo/carriers/DHL/services

{
  "code": "DHL_EXP",
  "name": "DHL Express Worldwide",
  "maxWeight": 70,
  "transitDays": 2
}
Étape 4 — Client : Valider une adresse (optionnel)
POST http://localhost:8000/api/v1/cargo/addresses/validate

{
  "country": "DE",
  "zipCode": "10115",
  "city": "Berlin",
  "address": "Friedrichstr. 100"
}
Étape 5 — Client : Comparer les tarifs
POST http://localhost:8000/api/v1/cargo/rates

{
  "sender": {"country":"FR","zipCode":"75001","city":"Paris","address":"Rue Test"},
  "recipient": {"country":"DE","zipCode":"10115","city":"Berlin","address":"Str Test"},
  "packages": [{"weight":2.5,"weightUnit":"KG"}]
}
Étape 6 — Client : Créer l'expédition
POST http://localhost:8000/api/v1/cargo/shipments

{
  "carrierCode": "DHL",
  "serviceCode": "DHL_EXP",
  "reference": "CMD-2026-001",
  "sender": {
    "company":"TechCorp SAS",
    "country":"FR","zipCode":"75001","city":"Paris","address":"12 Rue de Rivoli"
  },
  "recipient": {
    "company":"Berlin GmbH",
    "country":"DE","zipCode":"10115","city":"Berlin","address":"Friedrichstr. 100"
  },
  "packages": [{"weight":2.5,"weightUnit":"KG"}],
  "options": {"signatureRequired":true}
}
→ Récupère id et carrierTrackingNumber

Étape 7 — Client : Voir le détail
GET http://localhost:8000/api/v1/cargo/shipments/{id}

Étape 8 — Client : Générer l'étiquette
POST http://localhost:8000/api/v1/cargo/shipments/{id}/label

{"format": "PDF"}
Étape 9 — Client : Planifier un enlèvement
POST http://localhost:8000/api/v1/cargo/pickups

{
  "carrierCode": "DHL",
  "shipmentIds": ["{id}"],
  "pickupDate": "2026-06-23",
  "readyTime": "09:00",
  "closeTime": "17:00",
  "location": {
    "country":"FR","zipCode":"75001","city":"Paris","address":"12 Rue de Rivoli"
  }
}
Étape 10 — Transporteur envoie : Colis pris en charge
POST http://localhost:8000/api/v1/cargo/webhooks/DHL

{
  "trackingNumber": "{carrierTrackingNumber}",
  "status": "PICKED_UP",
  "timestamp": "2026-06-23T10:00:00Z"
}
Étape 11 — Client : Suivre en direct
GET http://localhost:8000/api/v1/cargo/shipments/{id}/tracking

Étape 12 — Transporteur envoie : Colis livré
POST http://localhost:8000/api/v1/cargo/webhooks/DHL

{
  "trackingNumber": "{carrierTrackingNumber}",
  "status": "DELIVERED",
  "timestamp": "2026-06-24T14:30:00Z"
}
Étape 13 — Client : Vérifier le statut final
GET http://localhost:8000/api/v1/cargo/shipments/{id} → internalStatus = DELIVERED

Étape 14 (optionnel) — Client : Annuler l'enlèvement
POST http://localhost:8000/api/v1/cargo/pickups/{pickupId}/cancel (pas de body)

Résumé des 10 endpoints métier utilisés :

Étape	Méthode	Endpoint	Rôle
1	POST	/carriers	Ajouter transporteur
2	POST	/carriers/{code}/test	Tester connexion
3	POST	/carriers/{code}/services	Ajouter service
4	POST	/addresses/validate	Valider adresse
5	POST	/rates	Comparer prix
6	POST	/shipments	Créer expédition
8	POST	/shipments/{id}/label	Générer étiquette
9	POST	/pickups	Planifier enlèvement
10/12	POST	/webhooks/{carrierCode}	Recevoir mise à jour
7/11/13	GET	/shipments/{id} ou /tracking	Consulter statut