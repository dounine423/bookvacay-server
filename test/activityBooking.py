bookingData={
    "operationId": "f3b17f8a66bf2e0a",
    "auditData": {
        "processTime": 0.0,
        "time": "2023-06-15T22:11:03.155Z",
        "serverId": "blank",
        "environment": "blank"
    },
    "booking": {
        "reference": "1-5398434",
        "status": "CONFIRMED",
        "currency": "EUR",
        "pendingAmount": 646.05,
        "agency": {
            "code": 99994,
            "branch": 1,
            "comments": "",
            "sucursal": {
                "name": "HOTELBEDS SPAIN - PRUEBAS",
                "street": "PEREZ GALDOS 32",
                "zip": "07006",
                "city": "PALMA DE MALLORCA",
                "phone": "971771700",
                "region": "BALEARES"
            }
        },
        "creationDate": "2023-06-16T00:11:02.000Z",
        "paymentData": {
            "paymentType": {
                "code": "C"
            },
            "invoicingCompany": {
                "code": "E14",
                "name": "HOTELBEDS S.L.U.",
                "registrationNumber": "ESB57218372"
            },
            "description": "Name Hotelbeds, S.L.U, Bank: BBVA(PL. DE L'OLIVAR, 6. PALMA 07002) Account:ES73 0182 4899 14 0200712789,  SWIFT:BBVAESMMXXX,  7 days prior to clients arrival (except group bookings with fixed days in advance at the time of the confirmation) . Please indicate our reference number when making payment. Thank you for your cooperation."
        },
        "extraData": [
            {
                "id": "WEBIP",
                "value": "188.43.14.13, 35.227.250.134, 35.191.2.186,34.76.108.203"
            },
            {
                "id": "ATLAS_USER",
                "value": "ATLAS+"
            }
        ],
        "clientReference": "TESTEDAG",
        "holder": {
            "name": "TEST",
            "title": "",
            "email": "x.bibiloni@hotelbeds.com",
            "mailing": False,
            "surname": "TESTER",
            "telephones": [
                "123456789"
            ]
        },
        "total": 646.05,
        "totalNet": 646.05,
        "activities": [
            {
                "status": "CONFIRMED",
                "supplier": {
                    "name": "HOTELBEDS SPAIN, S.L.U",
                    "vatNumber": "ESB28916765"
                },
                "comments": [
                    {
                        "type": "CONTRACT_REMARKS",
                        "text": "Meeting point: Mallorca Balloons Airport - Globodromo Son Parot. Carretera Manacor, S14 Autovia Ma-15, exit 44 - Manacor, Mallorca // Hot air ballooning is weather dependent. \nPlease call 24 hours in advance to confirm the exact start time the following phone numbers:+34 971818182 / +34 971596969 (or Whatssapp) from 10am to 9pm Monday - Sunday // End point: same as the starting point // Duration: Between 3-4 hours. Hot Air Balloon Ride: Between 50 and 60 minutes // Inclusions: Equipment. Guide. Tickets // Mandatory instructions: Make sure you have answered the mandatory questions during the booking process to ensure correct service provision // Supplier name: Mallorca Balloons // Supplier emergency phone: +34 639818109 // Voucher type: Printed voucher or E-voucher. Print and bring the voucher or show the voucher on your mobile device to enjoy the activity // Voucher validity: Service date // Recommendations: In case of bad weather the supplier will postpone the excursion. Not recommended for people in wheelchairs / pregnant women. Dress code: casual and comfortable. Closed shoes //"
                    }
                ],
                "type": "TICKET",
                "vouchers": [],
                "activityReference": "1-5398434",
                "code": "E-E10-000200526",
                "name": "Balloom",
                "modality": {
                    "code": "TOUR1@STANDARD||06:30",
                    "name": "Tour 60 minutes 06:30",
                    "amountUnitType": "PAX"
                },
                "dateFrom": "2023-06-22",
                "dateTo": "2023-06-22",
                "cancellationPolicies": [
                    {
                        "dateFrom": "2023-06-15T00:00:00.000Z",
                        "amount": 515.22
                    }
                ],
                "paxes": [
                    {
                        "name": "Testito",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "3",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    },
                    {
                        "name": "Testito",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "2",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    },
                    {
                        "name": "Test",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "1",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    }
                ],
                "questions": [
                    {
                        "question": {
                            "code": "EMAIL",
                            "text": "Please, provide the email address",
                            "required": True
                        },
                        "answer": "EMAIL"
                    },
                    {
                        "question": {
                            "code": "EMAILCONTACTO",
                            "required": True
                        },
                        "answer": "x.bibiloni@hotelbeds.com"
                    },
                    {
                        "question": {
                            "code": "PHONENUMBER",
                            "text": "Please provide a contact number for the guests to be reached in case of emergency (including international code)",
                            "required": True
                        },
                        "answer": "PHONENUMBER"
                    },
                    {
                        "question": {
                            "code": "TLFCONTACTO",
                            "required": True
                        },
                        "answer": "123456789"
                    },
                    {
                        "question": {
                            "code": "PAX_WEIGHT",
                            "text": "Please advise weights of guests travelling",
                            "required": True
                        },
                        "answer": "WEIGHT"
                    }
                ],
                "id": "1#O#1",
                "agencyCommission": {
                    "percentage": 0.00,
                    "amount": 0.000,
                    "vatAmount": 0.000
                },
                "contactInfo": {
                    "address": "Globodromo, Exit 44 Es Caparo MA15 Palma - Manacor",
                    "postalCode": "07023",
                    "city": "Manacor",
                    "country": {
                        "destinations": [
                            {
                                "code": "PMI",
                                "name": "Mallorca"
                            }
                        ]
                    }
                },
                "amountDetail": {
                    "paxAmounts": [
                        {
                            "paxType": "ADULT",
                            "amount": 171.74
                        }
                    ],
                    "totalAmount": {
                        "amount": 515.22
                    }
                },
                "extraData": [
                    {
                        "id": "INFO_TTOO_BEARING_AMOUNT",
                        "value": "646.050"
                    },
                    {
                        "id": "INFO_TTOO_BEARING_AMOUNT_CURRENCY",
                        "value": "EUR"
                    },
                    {
                        "id": "INFO_TTOO_SERVICE_AMOUNT",
                        "value": "0.00"
                    }
                ],
                "providerInformation": {
                    "name": "RICARDO ARACIL ROMERO"
                }
            },
            {
                "status": "CONFIRMED",
                "supplier": {
                    "name": "HOTELBEDS SPAIN, S.L.U",
                    "vatNumber": "ESB28916765"
                },
                "comments": [
                    {
                        "type": "CONTRACT_REMARKS",
                        "text": "Meeting point: At your hotel  // Meeting point instructions: The pick-up timetable range between 8am and 9:15am, depending on the meeting point assigned. Hotel pick-up service included from: Eastern area: Calas – Cala d’Or: Porto Cristo, Cala Mandía, Punta Reina, Calas de Mallorca, Porto Colom, Cala Ferrera, Cala D’Or, Cala Egos, Porto Petro, Cala Barca, Colonia Sant Jordi, Cala Figuera and Cala Santanyí. Levante - Cala Mesquida, Cala Ratjada, Font de Sa Cala, Cantamel, Cala Bona, Cala Millor, Sa Coma and S’Illot. Northern area: Cala Sant Vicenç, Puerto de Pollença, Puerto de Alcúdia and Can Picafort. Southern area: From Arenal to Calvià // End point: same as start point  // Duration: 6 hours // Inclusions: Assistant guide. Admission to the caves. Lago Martel live concert on a wooden boat. Free time in Porto Cristo. Visit the Majorica Pearls Factory. // Mandatory instructions: Please provide your hotel name, phone number and email. A few days before the activity, you will receive a message with the details of your pick-up service. // Supplier name: TOUR2B DMC // Supplier emergency phone: +34 610895221 // Voucher type: E-voucher. Show the voucher on your mobile device to enjoy the activity. // Voucher validity: Service day.\n."
                    }
                ],
                "type": "TICKET",
                "vouchers": [],
                "activityReference": "1-5398434",
                "code": "E-E10-A1GMNO0125",
                "name": "CityXperience Bus Half day  Tour to Cuevas del Drach",
                "modality": {
                    "code": "SUR1@STANDARD|ENG|",
                    "name": "Pick Up from the South english",
                    "rates": [
                        {
                            "freeCancellation": False,
                            "rateDetails": [
                                {
                                    "languages": [
                                        {
                                            "code": "en"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "amountUnitType": "PAX"
                },
                "dateFrom": "2023-06-23",
                "dateTo": "2023-06-23",
                "cancellationPolicies": [
                    {
                        "dateFrom": "2023-06-22T00:00:00.000Z",
                        "amount": 130.83
                    }
                ],
                "paxes": [
                    {
                        "name": "Testito",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "3",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    },
                    {
                        "name": "Testito",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "2",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    },
                    {
                        "name": "Test",
                        "mailing": False,
                        "surname": "Tested",
                        "customerId": "1",
                        "age": 30,
                        "paxType": "AD",
                        "passport": ""
                    }
                ],
                "questions": [
                    {
                        "question": {
                            "code": "EMAIL",
                            "text": "Please, provide the email address",
                            "required": True
                        },
                        "answer": "EMAIL"
                    },
                    {
                        "question": {
                            "code": "EMAILCONTACTO",
                            "required": True
                        },
                        "answer": "x.bibiloni@hotelbeds.com"
                    },
                    {
                        "question": {
                            "code": "HOTEL_NAME",
                            "text": "Please advise the name of your hotel",
                            "required": True
                        },
                        "answer": "HOTEL"
                    },
                    {
                        "question": {
                            "code": "PHONENUMBER",
                            "text": "PLEASE INDICATE YOUR MOBILE NUMBER",
                            "required": True
                        },
                        "answer": "MOBILE"
                    },
                    {
                        "question": {
                            "code": "TLFCONTACTO",
                            "required": True
                        },
                        "answer": "123456789"
                    }
                ],
                "id": "1#O#2",
                "agencyCommission": {
                    "percentage": 0.00,
                    "amount": 0.000,
                    "vatAmount": 0.000
                },
                "contactInfo": {
                    "country": {
                        "destinations": [
                            {
                                "code": "PMI",
                                "name": "Mallorca"
                            }
                        ]
                    }
                },
                "amountDetail": {
                    "paxAmounts": [
                        {
                            "paxType": "ADULT",
                            "amount": 43.61
                        }
                    ],
                    "totalAmount": {
                        "amount": 130.83
                    }
                },
                "extraData": [
                    {
                        "id": "INFO_TTOO_BEARING_AMOUNT",
                        "value": "646.050"
                    },
                    {
                        "id": "INFO_TTOO_BEARING_AMOUNT_CURRENCY",
                        "value": "EUR"
                    },
                    {
                        "id": "INFO_TTOO_SERVICE_AMOUNT",
                        "value": "0.00"
                    }
                ],
                "providerInformation": {
                    "name": "TOURADVISOR DMC SLU"
                }
            }
        ]
    }

}