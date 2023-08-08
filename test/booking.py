bookingData= {
    "auditData": {
        "processTime": "1666",
        "timestamp": "2023-06-25 17:26:31.214",
        "requestHost": "188.43.14.13, 35.227.250.134, 35.191.17.233, 10.197.232.34",
        "serverId": "ip-10-185-88-66.eu-west-1.compute.internal#A+",
        "environment": "[awseuwest1, awseuwest1a, ip_10_185_88_66]",
        "release": "",
        "token": "CBDE5C309A84439A8BC46DE4C2C31FCC",
        "internal": "0|06~~204118~656925542~N~~~NOR~D6B228D1334543E168769603998700AAUK00000730000000001204118|UK|01|73|1|||||||||||R|1|2|~1~2~0|0|0||0|d0a0be59559bf8d5765a43fc2db2e8f4||||"
    },
    "booking": {
        "reference": "1-5410363",
        "clientReference": "INTEGRATIONAGENCY",
        "creationDate": "2023-06-25",
        "status": "CONFIRMED",
        "modificationPolicies": {
            "cancellation": True,
            "modification": True
        },
        "creationUser": "d0a0be59559bf8d5765a43fc2db2e8f4",
        "holder": {
            "name": "HOLDERFIRSTNAME",
            "surname": "HOLDERLASTNAME"
        },
        "hotel": {
            "checkOut": "2023-06-29",
            "checkIn": "2023-06-27",
            "code": 1533,
            "name": "Mirador",
            "categoryCode": "4EST",
            "categoryName": "4 STARS",
            "destinationCode": "PMI",
            "destinationName": "Majorca",
            "zoneCode": 10,
            "zoneName": "Palma",
            "latitude": "39.5681",
            "longitude": "2.6312",
            "rooms": [
                {
                    "status": "CONFIRMED",
                    "id": 1,
                    "code": "DBT.ST",
                    "name": "DOUBLE OR TWIN STANDARD",
                    "paxes": [
                        {
                            "roomId": 1,
                            "type": "AD",
                            "name": "First Adult Name",
                            "surname": "Surname"
                        },
                        {
                            "roomId": 1,
                            "type": "AD",
                            "name": "First Adult Name",
                            "surname": "Surname"
                        }
                    ],
                    "rates": [
                        {
                            "rateClass": "NOR",
                            "net": "280.04",
                            "rateComments": "1x Double or Twin Estimated total amount of taxes & fees for this booking: 13.20 Euro   payable on arrival. Car park YES (with additional debit notes) 12.00 EUR Per unit/night. Check-in hour 14:00 - . Due to the pandemic, many accommodation and service providers may implement processes and policies to help protect the safety of all of us. This may result in the unavailability or changes in certain services and amenities that are normally available from them.More info here https://cutt.ly/MT8BJcv (15/05/2020-30/06/2023).",
                            "paymentType": "AT_WEB",
                            "packaging": True,
                            "boardCode": "RO",
                            "boardName": "ROOM ONLY",
                            "cancellationPolicies": [
                                {
                                    "amount": "134.30",
                                    "from": "2023-06-24T23:59:00+02:00"
                                }
                            ],
                            "taxes": {
                                "taxes": [
                                    {
                                        "included": False,
                                        "amount": "13.20",
                                        "currency": "EUR",
                                        "clientAmount": "13.20",
                                        "clientCurrency": "EUR"
                                    }
                                ],
                                "allIncluded": False
                            },
                            "rateBreakDown": {
                                "rateDiscounts": [
                                    {
                                        "code": "PQ",
                                        "name": "Opaque Package",
                                        "amount": "-7.06"
                                    }
                                ]
                            },
                            "rooms": 1,
                            "adults": 2,
                            "children": 0
                        }
                    ]
                }
            ],
            "totalNet": "280.04",
            "currency": "EUR",
            "supplier": {
                "name": "HOTELBEDS PRODUCT,S.L.U.",
                "vatNumber": "ESB38877676"
            }
        },
        "remark": "Booking remarks are to be written here.",
        "invoiceCompany": {
            "code": "E14",
            "company": "HOTELBEDS S.L.U.",
            "registrationNumber": "ESB57218372"
        },
        "totalNet": 280.04,
        "pendingAmount": 280.04,
        "currency": "EUR"
    }
}